"""Open a built page in headless Chrome, measure what the reader will see, and take screenshots.

Usage: python3 render.py page.html [shots-folder]

check.py reads the HTML source. This script reads the rendered page, so it finds what only layout
shows: text drawn smaller than the floor (a diagram scaled down), a screenshot cut off by its frame,
a page wider than a phone. It writes <stem>-desktop.png, <stem>-phone.png, <stem>-dark.png and, for
a flow page, <stem>-open.png (the first screen at full size). Prints ERROR and WARN lines and exits 1
if there is any ERROR. Uses only the Python standard library and a Chrome or Chromium binary;
set SHOW_ME_BROWSER to its path if it is not found.
"""
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

DESKTOP = (1280, 900)
PHONE = (390, 844)
MAX_SHOT_HEIGHT = 12000
SVG_TEXT_FLOOR = 12
BROWSERS = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"]


class RenderFailed(Exception):
    pass


# ---------- a minimal WebSocket client, enough for the DevTools protocol ----------

class Socket:
    def __init__(self, url):
        rest = url.split("://", 1)[1]
        hostport, path = rest.split("/", 1)
        host, port = hostport.rsplit(":", 1)
        self.s = socket.create_connection((host, int(port)), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RenderFailed("browser closed the DevTools connection")
            head += chunk
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise RenderFailed("browser refused the DevTools connection: " + head.split(b"\r\n", 1)[0].decode())
        self.buf = head.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise RenderFailed("browser closed the DevTools connection")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _frame(self, opcode, data):
        mask = os.urandom(4)
        n = len(data)
        head = bytes([0x80 | opcode])
        head += bytes([0x80 | n]) if n < 126 else (bytes([0x80 | 126]) + struct.pack(">H", n) if n < 1 << 16
                                                   else bytes([0x80 | 127]) + struct.pack(">Q", n))
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def send(self, text):
        self._frame(0x1, text.encode())

    def recv(self):
        message = b""
        while True:
            b0, b1 = self._read(2)
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            data = self._read(n)
            opcode = b0 & 0x0F
            if opcode == 0x9:
                self._frame(0xA, data)
                continue
            if opcode == 0x8:
                raise RenderFailed("browser closed the DevTools connection")
            message += data
            if b0 & 0x80:
                return message.decode()


class Page:
    def __init__(self, ws_url):
        self.ws = Socket(ws_url)
        self.next_id = 0

    def call(self, method, **params):
        self.next_id += 1
        self.ws.send(json.dumps({"id": self.next_id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.next_id:
                if "error" in msg:
                    raise RenderFailed(f"{method}: {msg['error'].get('message')}")
                return msg.get("result", {})

    def wait_event(self, name, timeout=20):
        end = time.time() + timeout
        while time.time() < end:
            if json.loads(self.ws.recv()).get("method") == name:
                return
        raise RenderFailed(f"timed out waiting for {name}")

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            raise RenderFailed("page script failed: " + r["exceptionDetails"].get("text", ""))
        return r["result"].get("value")

    def open(self, url, size, dark=False, phone=False):
        w, h = size
        self.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=2, mobile=phone)
        self.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])
        self.call("Page.navigate", url="about:blank")
        self.call("Page.navigate", url=url)
        self.wait_event("Page.loadEventFired")
        self.js("Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 3000))]).then(() => true)")

    def shot(self, path, full=True):
        w, h = self.js("[innerWidth, innerHeight]")
        if full:
            h = min(self.js("document.documentElement.scrollHeight"), MAX_SHOT_HEIGHT)
        r = self.call("Page.captureScreenshot", format="png", captureBeyondViewport=full,
                      clip={"x": 0, "y": 0, "width": w, "height": h, "scale": 1})
        Path(path).write_bytes(base64.b64decode(r["data"]))


def find_browser():
    tried = []
    for name in ([os.environ["SHOW_ME_BROWSER"]] if os.environ.get("SHOW_ME_BROWSER") else []) + BROWSERS:
        path = shutil.which(name) or (name if os.path.isfile(name) else None)
        if path:
            tried.append(path)
    snap = [p for p in tried if "/snap/" in os.path.realpath(p) or os.path.realpath(p).endswith("/snap")]
    return [p for p in tried if p not in snap] + snap


def launch(browser, profile):
    proc = subprocess.Popen([browser, "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={profile}",
                             "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    port_file = Path(profile) / "DevToolsActivePort"
    end = time.time() + 15
    while time.time() < end and proc.poll() is None:
        if port_file.is_file() and port_file.read_text().strip():
            port = port_file.read_text().split()[0]
            pages = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=10))
            target = next(t for t in pages if t["type"] == "page")
            return proc, target["webSocketDebuggerUrl"]
        time.sleep(0.2)
    lines = proc.stderr.read().decode(errors="replace").splitlines() if proc.poll() is not None else []
    err = [ln.strip() for ln in lines if len(ln.strip()) > 3][-1:]
    proc.kill()
    snap = " A snap browser often cannot run headless; install Chrome from a .deb or set SHOW_ME_BROWSER." if "snap" in browser else ""
    raise RenderFailed("did not start" + (f": {err[0]}" if err else "") + "." + snap)


# Runs in the page. Returns [level, message] pairs.
PROBE = r"""
(async () => {
  const out = [], floor = %d, phone = %s;
  const name = (el) => (el.closest('section.panel h2, details.step h3, .flowsec .fname')?.textContent
                        || el.closest('figure')?.querySelector('svg')?.getAttribute('aria-label') || '').trim().slice(0, 50);
  // A part past the right edge of the window is cut off or makes the page scroll sideways, unless
  // it sits in a box that scrolls on its own (a wide table, a diagram, the flow map).
  const scrolls = (el) => { for (let a = el.parentElement; a; a = a.parentElement) {
    const o = getComputedStyle(a).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
  const past = [...document.querySelectorAll('body *')].filter((el) => {
    if (el.closest('dialog,.thumb')) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.right > innerWidth + 1 && !scrolls(el);
  });
  const outer = past.filter((el) => !past.includes(el.parentElement));
  outer.slice(0, 3).forEach((el) => out.push(['ERROR', `<${el.tagName.toLowerCase()} class="${el.className}"> ends at ` +
    `${Math.round(el.getBoundingClientRect().right)}px in a ${innerWidth}px window; it is cut off or the page scrolls sideways`]));
  document.querySelectorAll('figure.diagram svg').forEach((svg) => {
    const vb = svg.viewBox.baseVal, r = svg.getBoundingClientRect();
    if (!vb || !vb.width || !r.width) return;
    const scale = r.width / vb.width;
    const sizes = [...svg.querySelectorAll('text')].map((t) => parseFloat(getComputedStyle(t).fontSize) * scale);
    const small = Math.min(...sizes);
    if (sizes.length && small < floor - 0.05)
      out.push(['ERROR', `diagram '${name(svg)}': text shows at ${small.toFixed(1)}px (floor ${floor}px); ` +
                `it is ${Math.round(vb.width)}px wide and drawn ${Math.round(r.width)}px wide. Fold it with col/row or split it`]);
    const box = svg.closest('.scroll');
    if (!phone && box && box.scrollWidth > box.clientWidth + 1)
      out.push(['WARN', `diagram '${name(svg)}' is ${Math.round(r.width)}px wide in a ${box.clientWidth}px panel; ` +
                `readers must scroll it. Fold it with col/row`]);
  });
  const dlg = document.querySelector('dialog.fover');
  if (dlg) {
    const picker = document.querySelector('.fpick select');
    const secs = [...document.querySelectorAll('.flowsec')];
    for (let i = 0; i < secs.length; i++) {
      if (picker) { picker.value = String(i); picker.dispatchEvent(new Event('change')); }
      for (const node of secs[i].querySelectorAll('.fnode')) {
        node.click();
        const box = dlg.querySelector('.foscreen');
        for (const img of box.querySelectorAll('img')) {
          try { await img.decode(); } catch (_) {}
          const b = box.getBoundingClientRect(), r = img.getBoundingClientRect();
          if (r.right > b.right + 1 || r.width < 1)
            out.push(['ERROR', `flow screen '${node.dataset.id}': the full-size view cuts the screenshot off ` +
                      `(${Math.round(r.width)}px image in a ${Math.round(b.width)}px frame)`]);
        }
        if (box.scrollWidth > box.clientWidth + 1 && !box.classList.contains('actual'))
          out.push(['ERROR', `flow screen '${node.dataset.id}': content is ${box.scrollWidth}px wide in a ` +
                    `${box.clientWidth}px full-size view and is cut off`]);
        dlg.close();
      }
    }
    if (picker) { picker.value = '0'; picker.dispatchEvent(new Event('change')); }
  }
  return out;
})()
"""


def main():
    page_path = Path(sys.argv[1]).resolve()
    shots = Path(sys.argv[2]) if len(sys.argv) > 2 else page_path.parent / "shots"
    shots.mkdir(parents=True, exist_ok=True)
    url = page_path.as_uri()
    browsers = find_browser()
    if not browsers:
        print("WARN NOT RENDERED: no Chrome or Chromium found. Install one, or set SHOW_ME_BROWSER to its path. "
              "Do not report the page as looking right.")
        return 0
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "show-me"
    cache.mkdir(parents=True, exist_ok=True)
    reasons = []
    for browser in browsers:
        profile = tempfile.mkdtemp(prefix="profile-", dir=cache)
        proc = None
        try:
            proc, ws = launch(browser, profile)
            page = Page(ws)
            page.call("Page.enable")
            found = []
            for label, size, dark, phone in (("desktop", DESKTOP, False, False), ("phone", PHONE, False, True),
                                             ("dark", DESKTOP, True, False)):
                page.open(url, size, dark, phone)
                if not dark:
                    found += [(lvl, f"{label}: {msg}") for lvl, msg in page.js(PROBE % (SVG_TEXT_FLOOR, str(phone).lower()))]
                page.shot(shots / f"{page_path.stem}-{label}.png", full=not dark)
            if page.js("!!document.querySelector('dialog.fover')"):
                page.open(url, DESKTOP)
                page.js("document.querySelector('.fnode')?.click(), true")
                page.shot(shots / f"{page_path.stem}-open.png", full=False)
            for lvl, msg in dict.fromkeys(found):
                print(f"{lvl} {msg}")
            names = ", ".join(f"{page_path.stem}-{k}.png" for k in ("desktop", "phone", "dark"))
            print(f"rendered in {Path(browser).name}; screenshots in {shots}: {names}"
                  + (f", {page_path.stem}-open.png" if (shots / f'{page_path.stem}-open.png').exists() else ""))
            return 1 if any(lvl == "ERROR" for lvl, _ in found) else 0
        except (RenderFailed, OSError, StopIteration, ValueError) as err:
            reasons.append(f"{browser}: {err}")
        finally:
            if proc:
                proc.kill()
                proc.wait()
            shutil.rmtree(profile, ignore_errors=True)
    print("WARN NOT RENDERED: no browser could open the page. Set SHOW_ME_BROWSER to a working Chrome. "
          "Do not report the page as looking right.\n  " + "\n  ".join(reasons))
    return 0


if __name__ == "__main__":
    sys.exit(main())
