---
type: Service
id: https://example.test/knowledge/services/orders-api
title: Orders API
description: Serves order data.
dependsOn:
  - https://example.test/knowledge/glossary/order
references:
  - https://example.test/knowledge/glossary/order
generated:
  by: process:ktl-librarian
  at: "2026-01-01T05:00:00Z"
verified:
  - by: process:ktl-librarian
    at: "2026-01-02T05:00:00Z"
  - by: human:ada
    at: "2026-01-03T09:00:00Z"
stale_after: 2099-01-01
---

# Orders API

Confirmed by a person after the librarian's own check. It names the glossary term twice, which counts once.
