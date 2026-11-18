---
type: Service
id: https://example.test/knowledge/services/notifications
title: Notifications Service
description: Sends order updates.
relations:
  - predicate: dependsOn
    target: https://example.test/knowledge/glossary/order
generated:
  by: process:ktl-librarian
  at: "2019-06-01T05:00:00Z"
verified:
  - by: human:ada
    at: "2019-07-01T05:00:00Z"
stale_after: 2020-01-01
---

# Notifications Service

Confirmed by a person, and past its review date.
