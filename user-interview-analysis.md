# User Interview Analysis — AI Claims Dashboard
**Product:** SPRY Billing Intelligence  
**Research Round:** R3 — Post-Launch Validation  
**Author:** Shanit Nagre  
**Date:** March 2026  
**Participants:** 8 billing coordinators across 4 clinic clients

---

## Research Goals

1. Understand how billing coordinators actually use the auto-resolution dashboard day-to-day
2. Identify friction points in the human review queue workflow
3. Validate whether the confidence score display is helping or confusing users
4. Discover unmet needs not captured in initial discovery

---

## Participants

| ID | Role | Clinic Type | Experience | Claims/week |
|----|------|------------|------------|-------------|
| P1 | Sr. Billing Coordinator | Orthopedics | 8 years | ~400 |
| P2 | Billing Coordinator | PT Clinic | 3 years | ~200 |
| P3 | Revenue Cycle Manager | Multi-specialty | 12 years | ~800 |
| P4 | Billing Coordinator | Chiro | 2 years | ~150 |
| P5 | Sr. Billing Coordinator | Cardiology | 6 years | ~350 |
| P6 | Billing Coordinator | PT Clinic | 1 year | ~120 |
| P7 | Revenue Cycle Manager | Orthopedics | 9 years | ~600 |
| P8 | Billing Coordinator | Multi-specialty | 4 years | ~250 |

---

## Key Findings

### Finding 1: Confidence scores are trusted — but not understood
**Signal strength: High (7/8 participants)**

All participants said they trust the system's auto-resolutions. But when asked what the confidence score (e.g., "0.94") meant, 6/8 gave incorrect or vague answers.

> *"I see the number but I don't know if 0.94 is good or bad. Is it out of 100? I just assumed higher was better."* — P4

> *"I don't look at the number anymore. I just look at whether it's in the green or red bucket."* — P2

**Implication:** The confidence score display is decorative for most users. They're relying on the visual tier (green/amber/red) to make decisions. The number adds noise, not value.

**Recommendation:** Replace raw confidence score with plain language: "High confidence — auto-resolved" / "Needs your review — uncertain payer rule" / "Escalate — complex case". Consider hiding the raw score behind a tooltip for power users.

---

### Finding 2: The human review queue is a bottleneck — not because of volume, but because of context gaps
**Signal strength: High (6/8 participants)**

When claims land in the human review queue, coordinators have to re-read the original ERA, look up the denial code, and mentally reconstruct context before they can act. This takes 4–8 minutes per claim.

> *"The system tells me 'review this claim' but it doesn't tell me why it flagged it or what I should look for. I have to figure that out myself."* — P1

> *"I wish it just told me: 'This was denied because CO-97, here are the two things you need to check before resubmitting.' That would cut my time in half."* — P5

**Implication:** The human review queue is missing actionable context. Surfacing the specific reason for escalation + a suggested next action would dramatically reduce resolution time.

**Recommendation:** Add "Why this needs review" and "Suggested action" fields to every escalated claim. This is a prompt engineering problem, not a UI problem — the LLM already has this context.

---

### Finding 3: Payer-specific trust varies significantly
**Signal strength: Medium (5/8 participants)**

Coordinators have developed intuitions about which payers the system handles well vs poorly. They manually review auto-resolved claims from specific payers they don't trust.

> *"I always double-check anything auto-resolved from United. They change their rules all the time and the system doesn't always catch it."* — P3

> *"BCBS-TX is fine. Aetna is fine. But Humana — I always review those myself."* — P7

**Implication:** Users have discovered the system's weak spots through experience. This is valuable signal we're not capturing. These payer-specific trust gaps represent real accuracy issues.

**Recommendation:** Build a payer accuracy leaderboard in the analytics dashboard. Track precision/recall by payer. Proactively alert the product team when a payer's accuracy drops below threshold. Use the coordinators' intuitions to prioritize model improvement.

---

### Finding 4: The 5% rollout created unexpected trust-building dynamics
**Signal strength: Medium (4/8 participants)**

Several coordinators mentioned that the phased rollout — where they could see both the AI decision and their own decision for the same claims — was key to building trust.

> *"For the first two weeks I was reviewing everything the system auto-resolved. When I saw it was right 95% of the time I stopped second-guessing it."* — P1

> *"I liked that I could turn it off if I wanted to. Knowing I had control made me more willing to trust it."* — P8

**Implication:** The rollout strategy was a product decision, not just a technical one. Giving users control during transition is a feature.

**Recommendation:** Document this as a pattern for future AI feature rollouts at SPRY. The "compare mode" — where users can see AI decision vs their decision for the same case — is worth building as a permanent feature for onboarding new clinics.

---

### Finding 5: There's an unmet need for proactive alerts on payer rule changes
**Signal strength: Medium (5/8 participants)**

Multiple participants mentioned situations where they discovered a payer had changed their rules through increased denials — after the fact.

> *"I found out Cigna changed their prior auth requirements because I suddenly got 40 denials in one week. I wish the system had warned me."* — P3

> *"We don't get notified when payers update their policies. We just notice when things start failing."* — P5

**Implication:** There's an opportunity for a proactive intelligence layer — monitoring denial rate anomalies by payer and surfacing potential rule changes before they cause large denial batches.

**Recommendation:** Add payer anomaly detection to the monitoring dashboard. If denial rate for a specific payer spikes >20% week-over-week, trigger an alert: "Unusual denial pattern from [Payer] — possible rule change. Review recent denials."

---

## Affinity Map

```
TRUST & CONFIDENCE
├── Trusts auto-resolutions (7/8)
├── Doesn't understand confidence score number (6/8)
└── Built trust through watching system be right (4/8)

WORKFLOW FRICTION
├── Human review queue lacks context (6/8)
├── Manual payer-specific double-checking (5/8)
└── Re-reading ERA to reconstruct context (6/8)

PAYER INTELLIGENCE
├── Payer-specific trust gaps (5/8)
├── Rule change discovery through failure (5/8)
└── Want proactive payer alerts (5/8)

CONTROL & AUTONOMY
├── Values ability to override system (4/8)
├── Phased rollout built trust (4/8)
└── Wants transparency on why decisions made (6/8)
```

---

## Prioritized Recommendations

| Recommendation | Impact | Effort | Priority |
|----------------|--------|--------|----------|
| Replace confidence score with plain language | High | Low | 🔴 P0 — Sprint 13 |
| Add "Why escalated + suggested action" to review queue | High | Medium | 🔴 P0 — Sprint 13 |
| Payer anomaly detection alerts | High | Medium | 🟡 P1 — Sprint 14 |
| Payer accuracy leaderboard in analytics | Medium | Low | 🟡 P1 — Sprint 14 |
| "Compare mode" for new clinic onboarding | Medium | High | 🟢 P2 — Backlog |

---

## What We Got Wrong in Discovery

Looking back at our initial assumptions from R1 discovery (September 2025):

**Assumption:** "Billing coordinators want maximum automation — they'll be happy to hand off everything to the system."  
**Reality:** They want automation for the boring stuff, but want to stay in the loop on complex cases. They don't want to be removed from the process — they want the process to be faster.

**Assumption:** "The confidence score display will build trust by being transparent."  
**Reality:** Transparency requires comprehension. A number without explanation isn't transparent — it's noise. Users built trust through watching outcomes, not reading scores.

**Assumption:** "Payer rule freshness is a backend problem the product team doesn't need to surface."  
**Reality:** Payer rule changes directly affect user trust. When the system fails on a specific payer, users stop trusting it globally. Surfacing rule change detection as a user-facing feature is necessary.

---

*SPRY Billing Intelligence — User Research*  
*Shanit Nagre · shanitnagre@gmail.com · [shanitnagre.github.io](https://shanitnagre.github.io)*
