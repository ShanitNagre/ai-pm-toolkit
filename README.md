# 🧰 AI PM Toolkit

> A collection of scripts, templates, and frameworks for AI Product Managers — built from real work shipping AI products in HealthTech and FinTech.

**Author:** Shanit Nagre — AI Product Manager  
**Portfolio:** [shanitnagre.github.io](https://shanitnagre.github.io)

---

## What's Inside

| File | Type | Description |
|------|------|-------------|
| `sprint_metrics.py` | Python | Sprint velocity, burndown, and AI task health tracking |
| `ab_test_analyzer.py` | Python | A/B test analysis built for AI feature testing |
| `PRD-denial-auto-resolution.md` | Markdown | Full PRD with post-launch actuals for SPRY claims pipeline |
| `user-interview-analysis.md` | Markdown | 8-participant research report with affinity mapping |

---

## Tools

### `sprint_metrics.py`
Sprint health dashboard for AI product teams. Tracks velocity, predicts completion, surfaces blocked items, and adds AI-specific health checks (data dependencies, eval task tracking).

```bash
python sprint_metrics.py --team spry-billing
python sprint_metrics.py --json   # machine-readable output
```

**Why AI teams need this differently:**  
AI sprints have unique failure modes — data not ready, eval runs blocked, model accuracy below threshold mid-sprint. Standard velocity tracking misses these. This tool adds AI-specific category breakdown and dependency tracking.

---

### `ab_test_analyzer.py`
Statistical significance calculator for AI features. Handles continuous metrics (accuracy scores, confidence values), calculates required sample sizes, and gives clear SHIP / WAIT / KEEP_CONTROL recommendations.

```bash
python ab_test_analyzer.py --test denial_classifier_v2
python ab_test_analyzer.py --test all
```

**Why AI features need different A/B testing:**  
Traditional A/B testing assumes binary conversion events. AI features produce continuous outputs (confidence scores, quality ratings) with slow feedback loops (claim resolution takes days). This tool is built for that reality.

---

### `PRD-denial-auto-resolution.md`
A complete PRD for the SPRY denial auto-resolution engine — from problem statement through phased rollout plan to post-launch actuals. Includes real metrics, guardrail conditions, and an honest retrospective on what we got wrong.

---

### `user-interview-analysis.md`
Research synthesis from 8 billing coordinator interviews post-launch. Includes affinity mapping, prioritized recommendations, and a "what we got wrong in discovery" section — because that's the most useful part of any research report.

---

## Philosophy

These tools reflect how I think about AI product work:

**Measure before you ship.** Every AI feature needs an eval framework before the model touches production. `ab_test_analyzer.py` is the tool I wish existed when I was setting up the first eval pipeline.

**Sprint health is different for AI teams.** Data dependencies and model accuracy are first-class blockers. `sprint_metrics.py` treats them as such.

**PRDs should have post-launch sections.** A PRD that stops at launch is a hypothesis document. The post-launch actuals are where learning happens.

**User research should be honest about its failures.** The most useful section of `user-interview-analysis.md` is "What We Got Wrong in Discovery."

---

*Part of Shanit Nagre's AI PM portfolio — [shanitnagre.github.io](https://shanitnagre.github.io)*
