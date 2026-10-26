"""Layered layout for boxes joined by arrows, shared by flow pages and sheet diagrams.

Sugiyama method, small form: a depth-first search marks the links that close a loop, each box goes
one column after its furthest parent, then four sweeps order each column by the mean place of its
neighbours. A box can pin its own `col` or `row`.
"""
import sys


def find_returns(order, links, starts):
    """Depth-first from each start, then from any box not reached. A link to a box still on the stack is a return."""
    out = {i: [] for i in order}
    for n, ln in enumerate(links):
        out[ln["from"]].append(n)
    seen, on_stack, back, visit = set(), set(), set(), []

    def dfs(v):
        seen.add(v)
        on_stack.add(v)
        visit.append(v)
        for n in out[v]:
            w = links[n]["to"]
            if w in on_stack:
                back.add(n)
            elif w not in seen:
                dfs(w)
        on_stack.discard(v)

    sys.setrecursionlimit(10000)
    for s in [*starts, *order]:
        if s not in seen:
            dfs(s)
    return back, visit


def columns(visit, links, back, pinned):
    """Column of each box, and each column's boxes in order. `pinned[id]` may hold `col` and `row`."""
    fwd = [ln for n, ln in enumerate(links) if n not in back]
    col = {v: pinned.get(v, {}).get("col", 0) for v in visit}
    changed = True
    while changed:
        changed = False
        for ln in fwd:
            a, b = ln["from"], ln["to"]
            if "col" not in pinned.get(b, {}) and col[b] < col[a] + 1:
                col[b] = col[a] + 1
                changed = True
    cols = {}
    for v in visit:
        cols.setdefault(col[v], []).append(v)
    parents = {v: [ln["from"] for ln in fwd if ln["to"] == v] for v in visit}
    children = {v: [ln["to"] for ln in fwd if ln["from"] == v] for v in visit}
    place = {v: n for c in cols.values() for n, v in enumerate(c)}

    def sweep(keys, nbrs):
        for c in keys:
            def mean(v):
                ns = [place[u] for u in nbrs[v] if col[u] != col[v]]
                return sum(ns) / len(ns) if ns else place[v]
            cols[c].sort(key=lambda v: (pinned.get(v, {}).get("row", 1e9), mean(v)))
            for n, v in enumerate(cols[c]):
                place[v] = n
    keys = sorted(cols)
    for _ in range(4):
        sweep(keys[1:], parents)
        sweep(keys[-2::-1], children)
    return col, {c: cols[c] for c in keys}, parents
