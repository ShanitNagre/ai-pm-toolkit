"""
sprint_metrics.py
=================
Sprint velocity, burndown, and delivery health calculator for AI product teams.
Tracks story points, AI-specific tasks (model training, eval runs, data prep),
and flags at-risk items based on historical velocity.

Author: Shanit Nagre — AI Product Manager
Usage: python sprint_metrics.py --sprint 12 --team spry-billing
"""

import json
import statistics
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta


# ── DATA CLASSES ──────────────────────────────────────────────────────────────

@dataclass
class Story:
    id: str
    title: str
    points: float
    category: str          # feature | bug | tech_debt | ai_research | data_prep | eval
    status: str            # todo | in_progress | review | done | blocked
    assignee: str
    sprint: int
    blocked_reason: Optional[str] = None
    ai_dependency: bool = False   # depends on model/data team

    @property
    def is_complete(self): return self.status == "done"
    @property
    def is_blocked(self): return self.status == "blocked"
    @property
    def is_ai_work(self): return self.category in ["ai_research", "data_prep", "eval"]


@dataclass
class Sprint:
    number: int
    team: str
    start_date: str
    end_date: str
    capacity_points: float
    stories: list[Story] = field(default_factory=list)
    goal: str = ""

    @property
    def total_points(self): return sum(s.points for s in self.stories)
    @property
    def completed_points(self): return sum(s.points for s in self.stories if s.is_complete)
    @property
    def blocked_points(self): return sum(s.points for s in self.stories if s.is_blocked)
    @property
    def velocity(self): return self.completed_points
    @property
    def completion_rate(self):
        return (self.completed_points / self.total_points * 100) if self.total_points else 0
    @property
    def ai_points(self): return sum(s.points for s in self.stories if s.is_ai_work)
    @property
    def ai_completion_rate(self):
        ai = [s for s in self.stories if s.is_ai_work]
        done = sum(s.points for s in ai if s.is_complete)
        total = sum(s.points for s in ai)
        return (done / total * 100) if total else 0


# ── METRICS ENGINE ────────────────────────────────────────────────────────────

class SprintMetricsEngine:

    def __init__(self, sprint_history: list[Sprint]):
        self.history = sprint_history

    def rolling_velocity(self, n: int = 3) -> float:
        """Average velocity over last n sprints."""
        recent = self.history[-n:] if len(self.history) >= n else self.history
        return statistics.mean([s.velocity for s in recent]) if recent else 0

    def velocity_trend(self) -> str:
        """Is velocity improving, stable, or declining?"""
        if len(self.history) < 3:
            return "INSUFFICIENT_DATA"
        recent = [s.velocity for s in self.history[-3:]]
        if recent[-1] > recent[0] * 1.1:
            return "↑ IMPROVING"
        elif recent[-1] < recent[0] * 0.9:
            return "↓ DECLINING"
        return "→ STABLE"

    def predictive_completion(self, current_sprint: Sprint) -> dict:
        """Predict if current sprint will complete based on historical velocity."""
        avg_velocity = self.rolling_velocity()
        days_elapsed = self._days_elapsed(current_sprint)
        total_days = self._sprint_duration(current_sprint)
        expected_completion = avg_velocity * (days_elapsed / total_days) if total_days else 0
        actual_completion = current_sprint.completed_points
        delta = actual_completion - expected_completion

        return {
            "expected_by_now": round(expected_completion, 1),
            "actual_by_now": round(actual_completion, 1),
            "delta": round(delta, 1),
            "status": "ON_TRACK" if abs(delta) < avg_velocity * 0.15 else ("AHEAD" if delta > 0 else "AT_RISK"),
            "projected_final": round(actual_completion / max(days_elapsed, 0.1) * total_days, 1),
            "will_complete_goal": actual_completion / max(days_elapsed, 0.1) * total_days >= current_sprint.total_points * 0.8,
        }

    def blocked_items_report(self, sprint: Sprint) -> list[dict]:
        """Surface blocked items with escalation recommendations."""
        blocked = [s for s in sprint.stories if s.is_blocked]
        return [
            {
                "story_id": s.id,
                "title": s.title,
                "points": s.points,
                "blocked_reason": s.blocked_reason or "Unknown",
                "ai_dependency": s.ai_dependency,
                "escalation": "ESCALATE_TO_DATA_TEAM" if s.ai_dependency else "ESCALATE_TO_ENGINEERING",
                "impact": "HIGH" if s.points >= 5 else "MEDIUM" if s.points >= 3 else "LOW",
            }
            for s in blocked
        ]

    def category_breakdown(self, sprint: Sprint) -> dict:
        """Breakdown of work by category — useful for identifying overloaded categories."""
        breakdown = {}
        for story in sprint.stories:
            if story.category not in breakdown:
                breakdown[story.category] = {"total": 0, "done": 0, "blocked": 0, "count": 0}
            breakdown[story.category]["total"] += story.points
            breakdown[story.category]["count"] += 1
            if story.is_complete:
                breakdown[story.category]["done"] += story.points
            if story.is_blocked:
                breakdown[story.category]["blocked"] += story.points
        return {k: {**v, "completion_rate": round(v["done"]/v["total"]*100 if v["total"] else 0, 1)} for k, v in breakdown.items()}

    def team_load_distribution(self, sprint: Sprint) -> dict:
        """Check if work is evenly distributed across team."""
        load = {}
        for story in sprint.stories:
            load.setdefault(story.assignee, {"total": 0, "done": 0, "count": 0})
            load[story.assignee]["total"] += story.points
            load[story.assignee]["count"] += 1
            if story.is_complete:
                load[story.assignee]["done"] += story.points
        avg = statistics.mean([v["total"] for v in load.values()]) if load else 0
        for assignee in load:
            load[assignee]["vs_avg"] = round(((load[assignee]["total"] - avg) / avg * 100) if avg else 0, 1)
            load[assignee]["overloaded"] = load[assignee]["total"] > avg * 1.3
        return load

    def ai_specific_health(self, sprint: Sprint) -> dict:
        """Special health check for AI/ML tasks — these have unique failure modes."""
        ai_stories = [s for s in sprint.stories if s.is_ai_work]
        return {
            "ai_points_pct": round(sprint.ai_points / sprint.total_points * 100 if sprint.total_points else 0, 1),
            "ai_completion_rate": round(sprint.ai_completion_rate, 1),
            "data_dependency_count": sum(1 for s in ai_stories if s.ai_dependency),
            "eval_tasks": [s.title for s in ai_stories if s.category == "eval"],
            "at_risk_ai_tasks": [s.title for s in ai_stories if s.is_blocked or s.status == "in_progress"],
            "recommendation": self._ai_recommendation(sprint, ai_stories),
        }

    def _ai_recommendation(self, sprint: Sprint, ai_stories: list[Story]) -> str:
        blocked_ai = [s for s in ai_stories if s.is_blocked]
        if not ai_stories:
            return "No AI tasks this sprint."
        if len(blocked_ai) > len(ai_stories) * 0.3:
            return "WARNING: >30% of AI tasks blocked. Check data/model team dependencies."
        if sprint.ai_completion_rate < 50:
            return "AI tasks behind. Consider moving eval tasks to next sprint."
        return "AI task health looks good."

    def _days_elapsed(self, sprint: Sprint) -> float:
        try:
            start = datetime.strptime(sprint.start_date, "%Y-%m-%d")
            today = datetime.now()
            end = datetime.strptime(sprint.end_date, "%Y-%m-%d")
            elapsed = min((today - start).days, (end - start).days)
            return max(elapsed, 0)
        except Exception:
            return 7  # default mid-sprint

    def _sprint_duration(self, sprint: Sprint) -> float:
        try:
            start = datetime.strptime(sprint.start_date, "%Y-%m-%d")
            end = datetime.strptime(sprint.end_date, "%Y-%m-%d")
            return (end - start).days
        except Exception:
            return 14


# ── REPORT GENERATOR ──────────────────────────────────────────────────────────

def print_sprint_report(engine: SprintMetricsEngine, current: Sprint):
    print(f"\n{'═'*65}")
    print(f"  SPRINT {current.number} HEALTH REPORT — {current.team.upper()}")
    print(f"  {current.start_date} → {current.end_date}")
    print(f"{'═'*65}\n")

    print(f"  GOAL: {current.goal or 'No goal set'}\n")

    # Velocity
    rv = engine.rolling_velocity()
    trend = engine.velocity_trend()
    print(f"  VELOCITY")
    print(f"  ├─ This sprint (so far):  {current.velocity:.1f} pts")
    print(f"  ├─ Rolling avg (3 sprint): {rv:.1f} pts")
    print(f"  └─ Trend:                 {trend}\n")

    # Completion
    pred = engine.predictive_completion(current)
    status_color = {"ON_TRACK": "✅", "AHEAD": "🚀", "AT_RISK": "⚠️"}.get(pred["status"], "")
    print(f"  COMPLETION FORECAST")
    print(f"  ├─ Expected by now:  {pred['expected_by_now']} pts")
    print(f"  ├─ Actual by now:    {pred['actual_by_now']} pts")
    print(f"  ├─ Delta:            {pred['delta']:+.1f} pts")
    print(f"  ├─ Status:           {status_color} {pred['status']}")
    print(f"  └─ Projected final:  {pred['projected_final']} / {current.total_points} pts\n")

    # Blocked items
    blocked = engine.blocked_items_report(current)
    if blocked:
        print(f"  BLOCKED ITEMS ({len(blocked)})")
        for b in blocked:
            print(f"  ├─ [{b['impact']}] {b['title']} ({b['points']}pts)")
            print(f"  │   Reason: {b['blocked_reason']}")
            print(f"  │   Action: {b['escalation']}")
        print()

    # Category breakdown
    breakdown = engine.category_breakdown(current)
    print(f"  CATEGORY BREAKDOWN")
    for cat, data in sorted(breakdown.items(), key=lambda x: x[1]["total"], reverse=True):
        bar = "█" * int(data["completion_rate"] / 10) + "░" * (10 - int(data["completion_rate"] / 10))
        print(f"  ├─ {cat:<15} [{bar}] {data['completion_rate']:.0f}% ({data['done']:.0f}/{data['total']:.0f}pts)")
    print()

    # AI health
    ai_health = engine.ai_specific_health(current)
    print(f"  AI/ML TASK HEALTH")
    print(f"  ├─ AI work % of sprint:  {ai_health['ai_points_pct']}%")
    print(f"  ├─ AI completion rate:   {ai_health['ai_completion_rate']}%")
    print(f"  └─ Recommendation:       {ai_health['recommendation']}\n")

    print(f"{'═'*65}\n")


# ── SAMPLE DATA ───────────────────────────────────────────────────────────────

def build_sample_data() -> tuple[list[Sprint], Sprint]:
    """Sample data based on SPRY Therapeutics billing AI sprint."""

    history = [
        Sprint(number=9, team="spry-billing", start_date="2026-01-05", end_date="2026-01-18",
               capacity_points=52, goal="Ship ERA ingestion v1",
               stories=[
                   Story("S9-1","ERA file parser",8,"feature","done","Rajan",9),
                   Story("S9-2","ICD-10 extraction NLP",13,"ai_research","done","Priya",9,ai_dependency=True),
                   Story("S9-3","Payer rule DB schema",5,"feature","done","Amit",9),
                   Story("S9-4","Unit tests — parser",3,"feature","done","Rajan",9),
                   Story("S9-5","Eval framework setup",8,"eval","done","Priya",9,ai_dependency=True),
                   Story("S9-6","Admin dashboard v1",5,"feature","done","Kavya",9),
                   Story("S9-7","Data pipeline docs",3,"data_prep","done","Amit",9),
               ]),
        Sprint(number=10, team="spry-billing", start_date="2026-01-19", end_date="2026-02-01",
               capacity_points=52, goal="Denial classifier v1",
               stories=[
                   Story("S10-1","Denial classification model",13,"ai_research","done","Priya",10,ai_dependency=True),
                   Story("S10-2","Training data pipeline",8,"data_prep","done","Amit",10,ai_dependency=True),
                   Story("S10-3","Confidence threshold logic",5,"feature","done","Rajan",10),
                   Story("S10-4","Human review queue UI",8,"feature","done","Kavya",10),
                   Story("S10-5","Model eval — payer A",5,"eval","done","Priya",10,ai_dependency=True),
                   Story("S10-6","Bug: duplicate claim IDs",2,"bug","done","Rajan",10),
                   Story("S10-7","Perf optimization",3,"tech_debt","done","Amit",10),
               ]),
        Sprint(number=11, team="spry-billing", start_date="2026-02-02", end_date="2026-02-15",
               capacity_points=52, goal="Appeal generation engine",
               stories=[
                   Story("S11-1","Appeal letter NLP model",13,"ai_research","done","Priya",11,ai_dependency=True),
                   Story("S11-2","Payer-specific templates",8,"feature","done","Kavya",11),
                   Story("S11-3","Appeal submission API",5,"feature","done","Rajan",11),
                   Story("S11-4","Eval — appeal quality",8,"eval","done","Priya",11,ai_dependency=True),
                   Story("S11-5","Training data — appeals",5,"data_prep","blocked","Amit",11,
                         blocked_reason="Waiting for payer policy docs from ops team",ai_dependency=True),
                   Story("S11-6","Dashboard — appeal status",5,"feature","done","Kavya",11),
               ]),
    ]

    current = Sprint(
        number=12, team="spry-billing",
        start_date="2026-02-16", end_date="2026-02-29",
        capacity_points=52,
        goal="Auto-resolution engine — production rollout to 20% of claims",
        stories=[
            Story("S12-1","Auto-resolution logic v2",13,"feature","done","Rajan",12),
            Story("S12-2","Prod rollout — 5% claims",8,"feature","done","Amit",12),
            Story("S12-3","Real-time monitoring dashboard",5,"feature","in_progress","Kavya",12),
            Story("S12-4","Eval — auto-resolution accuracy",8,"eval","in_progress","Priya",12,ai_dependency=True),
            Story("S12-5","Payer rule refresh — Q1 2026",5,"data_prep","blocked","Amit",12,
                  blocked_reason="Payer BCBS-TX hasn't published Q1 rule updates",ai_dependency=True),
            Story("S12-6","Alert system for low-confidence claims",5,"feature","todo","Rajan",12),
            Story("S12-7","Rollback mechanism",3,"tech_debt","todo","Amit",12),
            Story("S12-8","Load testing — 50K claims/day",5,"feature","blocked","Kavya",12,
                  blocked_reason="Staging environment capacity issue"),
        ]
    )
    return history, current


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sprint Metrics Engine — Shanit Nagre")
    parser.add_argument("--sprint", type=int, default=12)
    parser.add_argument("--team", default="spry-billing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    history, current = build_sample_data()
    engine = SprintMetricsEngine(history)

    if args.json:
        report = {
            "sprint": current.number,
            "velocity": engine.rolling_velocity(),
            "trend": engine.velocity_trend(),
            "prediction": engine.predictive_completion(current),
            "blocked": engine.blocked_items_report(current),
            "categories": engine.category_breakdown(current),
            "ai_health": engine.ai_specific_health(current),
        }
        print(json.dumps(report, indent=2))
    else:
        print_sprint_report(engine, current)
