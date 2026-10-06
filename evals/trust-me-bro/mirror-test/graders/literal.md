---
type: llm
weight: 2
---
The rewrite asserts literal expected values computed by hand, such as apply_discount(200, 10) == 180, and includes the 50% cap case such as apply_discount(200, 80) == 100.
