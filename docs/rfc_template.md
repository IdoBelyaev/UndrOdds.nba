# RFC: `<Project Name>`{=html}

-   **Author(s):** \<Name, Handle\>
-   **Date:** \<YYYY‑MM‑DD\>
-   **Status:** Draft \| Review \| Approved \| Rejected \| Superseded
-   **Owners:** `<Directly responsible people>`{=html}
-   **Reviewers:** `<Who should LGTM this>`{=html}
-   **Version:** v0.1

------------------------------------------------------------------------

## 1) Summary (TL;DR)

One paragraph: what we're building, for whom, and the one-sentence
outcome we want.

**Decision in one line:** We will `<do X>`{=html} so that
`<user Y>`{=html} can `<achieve Z>`{=html}, measured by
`<metric>`{=html}.

------------------------------------------------------------------------

## 2) Problem & Context

-   **Problem statement:** What pain exists today?
-   **Who is impacted:** Primary users / stakeholders.
-   **Why now:** Triggering events, deadlines, dependencies.
-   **Prior art:** Links to previous attempts, docs, or relevant repos.

------------------------------------------------------------------------

## 3) Goals / Non‑Goals

-   **Goals:**
    1.  \<Clear, testable outcome\>
    2.  \<...\>
-   **Non‑Goals:** (explicitly out of scope)
    -   \<What this is *not*\>

------------------------------------------------------------------------

## 4) Requirements

-   **Functional:** bullet list of behaviors & edge cases.
-   **Non‑Functional:** performance, latency, cost, portability,
    accessibility, maintainability.
-   **Constraints:** tech, licensing, data availability, privacy.

------------------------------------------------------------------------

## 5) User Stories

-   *As a `<user type>`{=html}, I want `<capability>`{=html} so that
    `<benefit>`{=html}.*
-   *As a ...*

------------------------------------------------------------------------

## 6) Proposed Solution

### 6.1 Architecture (overview)

Describe the big picture. Include a diagram if helpful.

    [client/UI] → [service/API] → [storage] → [batch/cron]
                           ↘︎ [model/inference]

### 6.2 Components

-   **UI / CLI:** \<tech stack, commands, flows\>
-   **Service / API:** endpoints, request/response schema, auth.
-   **Data:** sources, schemas, retention, lineage.
-   **Modeling (if any):** features, training schedule, evaluation.
-   **Infra:** hosting, scaling strategy, environment (conda, Docker),
    secrets.

### 6.3 Alternatives Considered

-   Option A --- Pros/Cons
-   Option B --- Pros/Cons
-   \[Decision\] Why chosen.

------------------------------------------------------------------------

## 7) Detailed Design

### 7.1 Data Schemas (tables / objects)

  Entity              Key             Important Fields   Notes
  ------------------- --------------- ------------------ ------------------------
  `<entity>`{=html}   `<id>`{=html}   \<f1, f2, f3\>     `<constraints>`{=html}

### 7.2 API Spec (example)

**POST** `/v1/predict` - **Request**

``` json
{
  "game_id": "<id>",
  "features": {"...": "..."}
}
```

-   **Response**

``` json
{
  "p_home_win": 0.57,
  "ev": 0.032,
  "explanations": ["rest_diff=+1", "injuries=-0.03"]
}
```

### 7.3 Algorithms / Formulas

Document scoring, EV, calibration, etc. Include references.

### 7.4 Security & Privacy

Data classification, PII handling, authZ/authN, key management.

### 7.5 Observability

Logs, metrics, tracing, dashboards, alerts. SLOs & error budgets.

------------------------------------------------------------------------

## 8) Risks & Mitigations

  Risk                           Impact     Likelihood Mitigation
  ------------------------------ -------- ------------ ---------------------------
  `<dependency outage>`{=html}   High              Med cache / fallback
  `<data drift>`{=html}          Med               Med monitoring, recalibration

------------------------------------------------------------------------

## 9) Rollout Plan

-   **Milestones:**
    -   M1: Prototype (date)
    -   M2: Beta (date)
    -   M3: GA (date)
-   **Feature flags / staged launch**
-   **Backout plan**

------------------------------------------------------------------------

## 10) Test Plan

-   Unit, integration, e2e.
-   Golden datasets / fixtures.
-   Acceptance criteria tied to Goals.

------------------------------------------------------------------------

## 11) Success Metrics

-   **Primary:** \<e.g., log loss ≤ X, EV \> 0 on N% of bets\>
-   **Secondary:** latency, cost, adoption.
-   **Guardrails:** regressions we won't accept.

------------------------------------------------------------------------

## 12) Open Questions

-   List unknowns, blockers, decisions awaiting input.

------------------------------------------------------------------------

## 13) Appendix

-   Glossary, links, prior docs, notes.
