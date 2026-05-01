"""
ab_test_analyzer.py
===================
A/B test analysis for AI product features.
Handles the unique challenges of testing AI features:
- Non-binary outcomes (confidence scores, quality ratings)
- Slow feedback loops (claim resolution takes days)
- Multiple metrics that can conflict (accuracy vs speed)

Author: Shanit Nagre — AI Product Manager
Usage: python ab_test_analyzer.py --test denial_classifier_v2
"""

import math
import statistics
import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Variant:
    name: str
    description: str
    users: int = 0
    conversions: int = 0
    metric_values: list[float] = field(default_factory=list)

    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.users if self.users else 0

    @property
    def mean(self) -> float:
        return statistics.mean(self.metric_values) if self.metric_values else 0

    @property
    def std_dev(self) -> float:
        return statistics.stdev(self.metric_values) if len(self.metric_values) > 1 else 0

    @property
    def std_error(self) -> float:
        n = len(self.metric_values)
        return self.std_dev / math.sqrt(n) if n > 1 else 0


@dataclass
class ABTest:
    name: str
    hypothesis: str
    primary_metric: str
    control: Variant
    treatment: Variant
    min_detectable_effect: float = 0.05   # 5% minimum effect worth detecting
    significance_level: float = 0.05      # p < 0.05
    power: float = 0.80                   # 80% statistical power
    guardrail_metrics: list[str] = field(default_factory=list)

    def relative_lift(self) -> float:
        if self.control.mean == 0:
            return 0
        return (self.treatment.mean - self.control.mean) / self.control.mean

    def z_score(self) -> float:
        """Two-sample z-test for continuous metrics."""
        se = math.sqrt(self.control.std_error**2 + self.treatment.std_error**2)
        if se == 0:
            return 0
        return (self.treatment.mean - self.control.mean) / se

    def p_value(self) -> float:
        """Approximate p-value from z-score (two-tailed)."""
        z = abs(self.z_score())
        # Approximation using error function
        p = 2 * (1 - self._normal_cdf(z))
        return min(max(p, 0.0001), 1.0)

    def is_significant(self) -> bool:
        return self.p_value() < self.significance_level

    def required_sample_size(self) -> int:
        """Minimum sample size per variant for valid results."""
        z_alpha = 1.96   # 95% confidence
        z_beta = 0.84    # 80% power
        p = self.control.conversion_rate or 0.5
        mde = self.min_detectable_effect
        n = (2 * p * (1 - p) * (z_alpha + z_beta)**2) / (mde**2)
        return math.ceil(n)

    def is_sample_sufficient(self) -> bool:
        required = self.required_sample_size()
        return self.control.users >= required and self.treatment.users >= required

    def recommendation(self) -> dict:
        lift = self.relative_lift()
        significant = self.is_significant()
        sufficient = self.is_sample_sufficient()

        if not sufficient:
            return {
                "decision": "WAIT",
                "reason": f"Insufficient sample. Need {self.required_sample_size()} per variant, have {min(self.control.users, self.treatment.users)}.",
                "confidence": "N/A",
            }
        if significant and lift > self.min_detectable_effect:
            return {
                "decision": "SHIP_TREATMENT",
                "reason": f"Treatment outperforms control by {lift*100:.1f}% (p={self.p_value():.4f}).",
                "confidence": f"{(1-self.p_value())*100:.1f}%",
            }
        if significant and lift < -self.min_detectable_effect:
            return {
                "decision": "KEEP_CONTROL",
                "reason": f"Treatment underperforms control by {abs(lift)*100:.1f}% (p={self.p_value():.4f}).",
                "confidence": f"{(1-self.p_value())*100:.1f}%",
            }
        return {
            "decision": "NO_SIGNIFICANT_DIFFERENCE",
            "reason": f"Lift of {lift*100:.1f}% is not statistically significant (p={self.p_value():.4f}).",
            "confidence": f"{(1-self.p_value())*100:.1f}%",
        }

    def _normal_cdf(self, x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def print_test_report(test: ABTest):
    rec = test.recommendation()
    decision_emoji = {"SHIP_TREATMENT": "🚀", "KEEP_CONTROL": "⏪", "WAIT": "⏳", "NO_SIGNIFICANT_DIFFERENCE": "➡️"}.get(rec["decision"], "")

    print(f"\n{'═'*65}")
    print(f"  A/B TEST REPORT: {test.name.upper()}")
    print(f"{'═'*65}")
    print(f"\n  HYPOTHESIS: {test.hypothesis}")
    print(f"  PRIMARY METRIC: {test.primary_metric}\n")

    print(f"  {'VARIANT':<20} {'N':<8} {'MEAN':<10} {'STD DEV':<10} {'STD ERR'}")
    print(f"  {'─'*60}")
    for v in [test.control, test.treatment]:
        label = "CONTROL" if v == test.control else "TREATMENT"
        print(f"  {label:<20} {v.users:<8} {v.mean:<10.4f} {v.std_dev:<10.4f} {v.std_error:.4f}")

    print(f"\n  STATISTICAL ANALYSIS")
    print(f"  ├─ Relative lift:     {test.relative_lift()*100:+.2f}%")
    print(f"  ├─ Z-score:           {test.z_score():.3f}")
    print(f"  ├─ P-value:           {test.p_value():.4f}")
    print(f"  ├─ Significant:       {'✅ YES' if test.is_significant() else '❌ NO'} (α={test.significance_level})")
    print(f"  └─ Sample sufficient: {'✅ YES' if test.is_sample_sufficient() else f'❌ NO (need {test.required_sample_size()}/variant)'}")

    print(f"\n  RECOMMENDATION: {decision_emoji} {rec['decision']}")
    print(f"  Reason:          {rec['reason']}")
    print(f"  Confidence:      {rec['confidence']}\n")
    print(f"{'═'*65}\n")


# ── SAMPLE TESTS ──────────────────────────────────────────────────────────────

def build_sample_tests() -> list[ABTest]:
    random.seed(42)

    # Test 1: Denial classifier v2 vs v1
    control_scores = [random.gauss(0.82, 0.08) for _ in range(1200)]
    treatment_scores = [random.gauss(0.89, 0.07) for _ in range(1200)]

    test1 = ABTest(
        name="denial_classifier_v2",
        hypothesis="Classifier v2 (fine-tuned on BCBS-TX data) will improve auto-resolution accuracy by ≥5%",
        primary_metric="auto_resolution_accuracy",
        control=Variant("Classifier v1", "Base GPT-4 classifier", users=1200,
                        conversions=984, metric_values=control_scores),
        treatment=Variant("Classifier v2", "Fine-tuned on payer-specific data", users=1200,
                          conversions=1068, metric_values=treatment_scores),
        min_detectable_effect=0.05,
        guardrail_metrics=["false_auto_resolution_rate", "processing_latency"],
    )

    # Test 2: Appeal letter length (short vs detailed)
    short_appeal_scores = [random.gauss(0.54, 0.15) for _ in range(450)]
    detailed_appeal_scores = [random.gauss(0.61, 0.14) for _ in range(450)]

    test2 = ABTest(
        name="appeal_letter_length",
        hypothesis="Detailed appeal letters (350 words) will have higher payer acceptance than short ones (150 words)",
        primary_metric="appeal_acceptance_rate",
        control=Variant("Short appeal", "150-word concise appeal", users=450,
                        conversions=243, metric_values=short_appeal_scores),
        treatment=Variant("Detailed appeal", "350-word detailed appeal with clinical evidence", users=450,
                          conversions=275, metric_values=detailed_appeal_scores),
        min_detectable_effect=0.08,
    )

    # Test 3: Confidence threshold (underpowered — shows WAIT scenario)
    test3 = ABTest(
        name="confidence_threshold_tuning",
        hypothesis="Lowering confidence threshold from 0.94 to 0.90 will increase auto-resolution rate without increasing error rate",
        primary_metric="net_resolution_rate",
        control=Variant("Threshold 0.94", "Current production threshold", users=180,
                        conversions=126, metric_values=[random.gauss(0.71, 0.09) for _ in range(180)]),
        treatment=Variant("Threshold 0.90", "Lower threshold — more auto-resolutions", users=180,
                          conversions=139, metric_values=[random.gauss(0.74, 0.10) for _ in range(180)]),
        min_detectable_effect=0.05,
    )

    return [test1, test2, test3]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A/B Test Analyzer — Shanit Nagre")
    parser.add_argument("--test", default="all", help="Test name or 'all'")
    args = parser.parse_args()

    tests = build_sample_tests()

    if args.test == "all":
        for test in tests:
            print_test_report(test)
    else:
        match = next((t for t in tests if t.name == args.test), None)
        if match:
            print_test_report(match)
        else:
            print(f"Test '{args.test}' not found. Available: {[t.name for t in tests]}")
