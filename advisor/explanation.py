"""
Explanation engine. Turns the rule-firing trace into human-readable output.

Five explanation modes:
  - explain_top: top positive and negative factors per career
  - head_to_head: which factors push #1 above #2 (or any A vs B)
  - counterfactuals: minimal profile changes that would flip the ranking
  - detect_tradeoffs: rules that boost one career while hurting another
  - heat_map: qualitative GREEN/YELLOW/RED confidence band per career
    (qualitative arithmetic over the numeric scores — directly inspired by
    the equity-portfolio risk-management heat-map example in the project
    handout)
"""
from copy import deepcopy
from typing import Dict, List, Tuple

from .careers import CAREERS, career_name
from .profile import UserProfile
from .rules import RULES, RuleFiring
from .scoring import ranked, score


# --------------------------------------------------------------------------
# Qualitative confidence bands (the "heat map")
# --------------------------------------------------------------------------

GREEN_THRESHOLD = 10.0
YELLOW_THRESHOLD = 5.0

BAND_LABEL = {
    "GREEN": "GREEN  (strong fit, well-supported by multiple rules)",
    "YELLOW": "YELLOW (moderate fit, some support but mixed signal)",
    "RED": "RED    (weak fit, profile lacks signal for this path)",
}


def confidence_band(score_value: float) -> str:
    """Map a numeric career score to a qualitative confidence band.

    The thresholds (GREEN >= 10, YELLOW >= 5, RED < 5) are calibrated against
    the sample profiles: a strong-fit career typically accumulates 10+ points
    of evidence across multiple rules, while a weak-signal profile struggles
    to clear 5 points anywhere. Adjusting the thresholds is a single-line
    change at the top of this module.
    """
    if score_value >= GREEN_THRESHOLD:
        return "GREEN"
    if score_value >= YELLOW_THRESHOLD:
        return "YELLOW"
    return "RED"


def heat_map(scores: Dict[str, float]) -> str:
    """Render the full heat map: every career grouped by confidence band."""
    bands: Dict[str, List[Tuple[str, float]]] = {"GREEN": [], "YELLOW": [], "RED": []}
    for career_id, sc in ranked(scores):
        bands[confidence_band(sc)].append((career_id, sc))

    lines = ["=" * 70, "CONFIDENCE HEAT MAP", "=" * 70]
    for band in ("GREEN", "YELLOW", "RED"):
        lines.append(f"\n  {BAND_LABEL[band]}")
        if not bands[band]:
            lines.append("    (none)")
            continue
        for career_id, sc in bands[band]:
            lines.append(f"    - {career_name(career_id):<35}  {sc:+6.2f}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Top-N explanation
# --------------------------------------------------------------------------

def explain_top(
    scores: Dict[str, float],
    firings: List[RuleFiring],
    top_n: int = 3,
    reasons_per_career: int = 5,
    show_negatives: int = 3,
) -> str:
    """Return a human-readable explanation of the top N recommendations.

    Each career header is annotated with its confidence band ([GREEN] /
    [YELLOW] / [RED]) so the qualitative meaning of the score is visible
    inline without reading a separate heat map.
    """
    lines = ["=" * 70, "TOP RECOMMENDATIONS", "=" * 70]
    top = ranked(scores)[:top_n]
    for rank, (career_id, total) in enumerate(top, 1):
        band = confidence_band(total)
        lines.append(
            f"\n#{rank}  {career_name(career_id)}  [{band}]   (score: {total:+.2f})"
        )
        relevant = [f for f in firings if career_id in f.contributions
                    and abs(f.contributions[career_id]) > 0.001]
        positives = sorted(
            [f for f in relevant if f.contributions[career_id] > 0],
            key=lambda f: -f.contributions[career_id],
        )[:reasons_per_career]
        negatives = sorted(
            [f for f in relevant if f.contributions[career_id] < 0],
            key=lambda f: f.contributions[career_id],
        )[:show_negatives]

        if positives:
            lines.append("    Why this ranks high:")
            for f in positives:
                delta = f.contributions[career_id]
                lines.append(f"      {delta:+5.2f}  {f.rule.description}")
                for ev in f.match.evidence[:3]:
                    lines.append(f"             - {ev}")
        if negatives:
            lines.append("    Working against this option:")
            for f in negatives:
                delta = f.contributions[career_id]
                lines.append(f"      {delta:+5.2f}  {f.rule.description}")
                for ev in f.match.evidence[:2]:
                    lines.append(f"             - {ev}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Head-to-head comparison
# --------------------------------------------------------------------------

def head_to_head(
    career_a: str,
    career_b: str,
    firings: List[RuleFiring],
    max_rows: int = 10,
) -> str:
    """Show the rules that distinguish career_a from career_b."""
    diffs: List[Tuple[float, RuleFiring]] = []
    for f in firings:
        a = f.contributions.get(career_a, 0.0)
        b = f.contributions.get(career_b, 0.0)
        if abs(a - b) > 0.01:
            diffs.append((a - b, f))
    diffs.sort(key=lambda x: -abs(x[0]))

    lines = [
        "=" * 70,
        f"HEAD-TO-HEAD: {career_name(career_a)}  vs  {career_name(career_b)}",
        "=" * 70,
    ]
    if not diffs:
        lines.append("  No rules differentiate these two careers.")
        return "\n".join(lines)

    for diff, f in diffs[:max_rows]:
        favors = career_name(career_a) if diff > 0 else career_name(career_b)
        a_str = f"{f.contributions.get(career_a, 0):+.2f}"
        b_str = f"{f.contributions.get(career_b, 0):+.2f}"
        lines.append(
            f"  Δ {diff:+5.2f}  ({a_str} vs {b_str})  →  favors {favors}"
        )
        lines.append(f"             {f.rule.description}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Counterfactual generation
# --------------------------------------------------------------------------

# Skills we'll try toggling in counterfactual search. Tagged by skill type
# so we add them to the right bucket on the profile.
COUNTERFACTUAL_SKILLS = [
    ("python", "tech"),
    ("machine_learning", "tech"),
    ("statistics", "tech"),
    ("system_design", "tech"),
    ("finance", "tech"),
    ("security", "tech"),
    ("design_visual", "non_tech"),
    ("communication", "non_tech"),
    ("writing", "non_tech"),
    ("leadership", "non_tech"),
]


def counterfactuals(
    profile: UserProfile,
    scores: Dict[str, float],
    target_level: int = 4,
    max_results: int = 5,
) -> str:
    """Find minimal profile changes that would shift the top recommendation."""
    current_top = ranked(scores)[0][0]
    findings: List[str] = []

    # Try boosting individual skills.
    for skill, kind in COUNTERFACTUAL_SKILLS:
        existing = profile.skill_level(skill)
        if existing >= target_level:
            continue
        modified = deepcopy(profile)
        bucket = modified.technical_skills if kind == "tech" else modified.non_technical_skills
        bucket[skill] = target_level
        new_scores, _ = score(modified)
        new_top = ranked(new_scores)[0][0]
        if new_top != current_top:
            findings.append(
                f"  If you raised {skill.replace('_', ' ')} to {target_level}/5, "
                f"top recommendation would shift to {career_name(new_top)}."
            )

    # Try removing each constraint.
    for constraint in profile.constraints:
        modified = deepcopy(profile)
        modified.constraints = [c for c in modified.constraints if c != constraint]
        new_scores, _ = score(modified)
        new_top = ranked(new_scores)[0][0]
        if new_top != current_top:
            findings.append(
                f"  If the constraint '{constraint}' were removed, "
                f"top recommendation would shift to {career_name(new_top)}."
            )

    lines = ["=" * 70, "COUNTERFACTUALS — what would change the recommendation?", "=" * 70]
    if not findings:
        lines.append("  The top recommendation is robust — no single small change "
                     "to the profile would flip it.")
    else:
        lines.extend(findings[:max_results])
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Tradeoff detection
# --------------------------------------------------------------------------

def detect_tradeoffs(firings: List[RuleFiring]) -> str:
    """Find rules that simultaneously boost one career and penalize another."""
    tradeoffs = []
    for f in firings:
        positives = [(c, v) for c, v in f.contributions.items() if v > 0.01]
        negatives = [(c, v) for c, v in f.contributions.items() if v < -0.01]
        if positives and negatives:
            tradeoffs.append((f, positives, negatives))

    lines = ["=" * 70, "TRADEOFFS — rules that pull in opposing directions", "=" * 70]
    if not tradeoffs:
        lines.append("  No active rules create opposing pressures on careers.")
        return "\n".join(lines)

    for f, pos, neg in tradeoffs:
        lines.append(f"\n  Rule: {f.rule.description}")
        for c, v in sorted(pos, key=lambda x: -x[1]):
            lines.append(f"      favors  {career_name(c):<32}  ({v:+.2f})")
        for c, v in sorted(neg, key=lambda x: x[1]):
            lines.append(f"      against {career_name(c):<32}  ({v:+.2f})")
    return "\n".join(lines)
