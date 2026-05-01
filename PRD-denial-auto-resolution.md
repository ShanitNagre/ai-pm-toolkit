# PRD: AI-Powered Denial Auto-Resolution Engine
**Product:** SPRY Billing Intelligence  
**Author:** Shanit Nagre — AI Product Manager  
**Status:** ✅ Shipped — Sprint 12  
**Last Updated:** February 2026  
**Version:** 2.1

---

## 📌 TL;DR

Build an AI engine that automatically resolves healthcare claim denials without human intervention — for cases where confidence is high enough. Target: auto-resolve 70%+ of denials, escalate the rest with full context pre-filled.

**Why now:** The billing team is resolving 2,847 denials/week manually. At current headcount, we cannot scale beyond 4,000/week. Revenue is gating on ops capacity, not market demand.

---

## 🎯 Problem Statement

### User Problem
Billing coordinators at SPRY spend 60–70% of their day on denial management — reviewing ERA files, identifying denial reasons, manually drafting appeals, and resubmitting claims. This is:
- **Slow:** Average 14 days from denial to resolution
- **Error-prone:** Manual review misses 18% of rebillable denials
- **Unscalable:** Linear relationship between claim volume and headcount

### Business Problem
- ~$180K/month in AR aging beyond 90 days due to denial backlog
- 3 billing FTEs spending >50% time on denial resolution
- Client churn risk: providers leave when claim reimbursement slows

### Root Cause
No system exists to:
1. Catch errors **before** submission (pre-scrubbing)
2. Automatically triage denials by resolution complexity
3. Generate payer-specific appeal content without manual drafting

---

## 👥 Users

### Primary: Billing Coordinators
- **Profile:** Non-technical, process-driven, work in billing queue
- **Pain:** Overwhelming denial volume, repetitive tasks, high cognitive load
- **Goal:** Clear their queue faster, recover more revenue
- **Success signal:** "I can handle 3× the claims without working longer hours"

### Secondary: Revenue Cycle Manager
- **Profile:** Manages billing team, reports to CFO
- **Pain:** Can't predict AR recovery, no visibility into denial trends
- **Goal:** Predictable revenue, clear metrics for leadership
- **Success signal:** "I can tell the CFO exactly how much AR we'll recover this month"

### Tertiary: Provider Clients
- **Profile:** Clinic administrators and practice managers
- **Pain:** Delayed reimbursement affects cash flow
- **Goal:** Faster claim resolution, less back-and-forth
- **Success signal:** "We're getting paid faster than with our previous billing platform"

---

## ✅ Goals & Success Metrics

### Primary Metrics (North Star)
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Denial resolution TAT | 14 days | ≤ 5 days | Median days denial → resolution |
| Auto-resolution rate | 0% | ≥ 70% | % denials resolved without human touch |
| Denial rate (pre-submission) | 18% | ≤ 12% | Denials / total claims submitted |

### Secondary Metrics
| Metric | Baseline | Target |
|--------|----------|--------|
| AR > 90 days | $180K/mo | < $80K/mo |
| Billing coordinator time on denials | 65% | < 30% |
| Appeal success rate | 34% | ≥ 55% |
| False auto-resolution rate | — | < 2% |

### Guardrail Metrics (must NOT degrade)
- Overall claim acceptance rate: must stay ≥ current baseline
- HIPAA audit compliance: 100%
- Human review queue SLA: < 48hr response for escalated cases

---

## 🔧 Solution Overview

### Core Components

**1. Pre-Submission Scrubbing**
- Run claims through rule engine before submission
- Flag likely rejections with specific fix recommendations
- Block submission if critical errors detected

**2. ERA Ingestion & Parsing**
- Auto-ingest 835 ERA files from payer portals
- Extract ICD-10/CPT codes, denial codes, adjustment amounts
- Structured output for downstream processing

**3. Denial Classification Engine**
- ML model classifying denials by type, rebillability, complexity
- Confidence score per classification (0.0–1.0)
- Route to auto-resolution or human queue based on threshold

**4. Auto-Resolution Logic**
- For high-confidence, simple denials: auto-correct and resubmit
- For appeal candidates: generate payer-specific appeal narrative
- For complex cases: pre-fill context and route to coordinator

**5. Monitoring Dashboard**
- Real-time view of denial queue, auto-resolution rate, AR aging
- Alerts for low-confidence spikes or payer rule changes
- Performance metrics by payer, denial type, and coordinator

---

## 🚫 Out of Scope (v1)

- Manual claim editing UI (v2)
- Patient billing integration (separate product)
- Automated payer portal submission (API limitations — v2)
- Multi-tenant support (single client focus for v1)

---

## 📐 Technical Requirements

### Confidence Threshold Logic
```
IF confidence ≥ 0.94:  AUTO_RESOLVE
IF confidence 0.75-0.93: HUMAN_REVIEW (context pre-filled)
IF confidence < 0.75:  ESCALATE (flag for senior review)
```

**Rationale:** Threshold set at 0.94 based on eval results showing this minimizes false auto-resolutions to < 2% while maximizing auto-resolution rate to ~70%.

### Performance Requirements
| Requirement | Target |
|-------------|--------|
| Batch processing latency | < 10s for 5,000 claims |
| Real-time single claim | < 2s |
| System uptime | 99.5% |
| Data retention | 7 years (HIPAA) |

### Integration Points
- **Input:** ERA 835 files (SFTP / API), CMS-1500 claim data
- **Output:** Corrected claims → clearinghouse, Appeals → payer portal
- **Monitoring:** Mixpanel for product metrics, PagerDuty for system alerts
- **Compliance:** HIPAA BAA required for all data processors

---

## 🗺️ Phased Rollout Plan

### Phase 1 — Controlled (Week 1–2)
- 5% of claim volume (≈ 140 claims/week)
- Manual review of all auto-resolutions
- Establish baseline precision/recall metrics
- **Go/No-Go:** Auto-resolution accuracy ≥ 92%

### Phase 2 — Expanded (Week 3–4)
- 20% of claim volume (≈ 570 claims/week)
- Remove manual review for HIGH confidence cases only
- Monitor false auto-resolution rate daily
- **Go/No-Go:** False auto-resolution rate < 2%

### Phase 3 — Full Rollout (Week 5–6)
- 100% of eligible claim volume
- Full auto-resolution for qualified cases
- Weekly model performance review

### Phase 4 — Optimization (Ongoing)
- Continuous model retraining on new denials
- Payer rule refresh pipeline (quarterly)
- Expand to new payer types

---

## ⚠️ Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model auto-resolves incorrectly | Medium | High | Confidence threshold + daily monitoring + rollback capability |
| Payer rule changes break logic | High | Medium | Quarterly rule refresh process + change detection alerts |
| Billing team doesn't trust system | Medium | High | Phased rollout + transparency dashboard + early wins |
| HIPAA data handling violation | Low | Critical | BAA with all vendors + encryption at rest/transit + audit log |
| Clearinghouse API downtime | Medium | Medium | Queue-based retry with 24hr SLA |

---

## 🔄 Dependencies

| Dependency | Owner | Required By | Status |
|-----------|-------|-------------|--------|
| ERA file access / SFTP setup | Engineering | Week 1 | ✅ Done |
| Payer rule database | Data team | Week 2 | ✅ Done |
| Training data — historical denials | Billing ops | Week 3 | ✅ Done |
| Clearinghouse API integration | Engineering | Week 4 | 🔄 In progress |
| HIPAA BAA — model vendor | Legal | Week 1 | ✅ Done |

---

## 📊 Post-Launch Review (Sprint 12 Actuals)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Auto-resolution rate | 70% | 73% | ✅ |
| Denial resolution TAT | ≤ 5 days | 4.2 days | ✅ |
| False auto-resolution rate | < 2% | 1.4% | ✅ |
| Pre-submission denial catch rate | — | 28% of would-be denials | 🎉 |
| Billing coordinator time on denials | < 30% | 34% | ⚠️ (improving) |

**What worked:**  
The confidence threshold held well. Phase 1's 5% controlled rollout built trust faster than expected — coordinators were advocates by week 3.

**What didn't:**  
Payer rule freshness was a bigger problem than anticipated. BCBS-TX published rule updates mid-sprint that weren't caught, causing a 2-day accuracy dip. Added quarterly rule refresh to backlog.

**Next sprint focus:**  
Expand to 100% of eligible claims. Build rule change detection. Start payer-specific model fine-tuning.

---

*SPRY Billing Intelligence — AI Product Portfolio*  
*Shanit Nagre · shanitnagre@gmail.com · [shanitnagre.github.io](https://shanitnagre.github.io)*
