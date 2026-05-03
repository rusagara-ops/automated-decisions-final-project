"""
Option generation. When the top recommendation is weak, conflicted, or
nearly tied with the runner-up, suggest alternatives:

  - Hybrid roles when two strong careers are close in score.
  - "Build toward" paths when the top score itself is low.
  - Conflict resolution when the user's skills point one way but their
    work-style or goals point the other.
"""
from typing import Dict, List

from .careers import career_name
from .profile import UserProfile
from .rules import RuleFiring
from .scoring import ranked


# Curated hybrid roles for adjacent career pairs.
HYBRID_ROLES = {
    frozenset(["software_engineering", "data_science"]):
        "ML Engineering or applied data engineering",
    frozenset(["software_engineering", "product_management"]):
        "Technical Product Manager or developer-tools PM",
    frozenset(["consulting", "data_science"]):
        "Analytics / data consulting",
    frozenset(["software_engineering", "ux_design"]):
        "Design Engineering / front-end specialist",
    frozenset(["product_management", "ux_design"]):
        "Design-led PM",
    frozenset(["data_science", "research_industry"]):
        "Applied research scientist",
    frozenset(["consulting", "product_management"]):
        "Product strategy",
    frozenset(["finance_quant", "data_science"]):
        "Quantitative researcher",
    frozenset(["software_engineering", "research_academic"]):
        "Research engineer (industry lab)",
    frozenset(["entrepreneurship", "software_engineering"]):
        "Technical founder",
    frozenset(["entrepreneurship", "product_management"]):
        "Founding PM at an early-stage startup",
    frozenset(["ml_engineering", "research_industry"]):
        "Applied research engineer",
    frozenset(["consulting", "technical_program_management"]):
        "Tech-strategy consulting / transformation lead",
}


def hybrid_for(a: str, b: str) -> str:
    return HYBRID_ROLES.get(
        frozenset([a, b]),
        f"a hybrid role combining {career_name(a)} and {career_name(b)}",
    )


def alternatives(
    profile: UserProfile,
    scores: Dict[str, float],
    firings: List[RuleFiring],
    close_threshold: float = 1.5,
    weak_threshold: float = 5.0,
) -> str:
    """Generate alternative options based on score patterns."""
    rank = ranked(scores)
    suggestions: List[str] = []

    top_id, top_score = rank[0]
    second_id, second_score = rank[1] if len(rank) > 1 else (None, -float("inf"))

    # 1. Close-call: top two are nearly tied.
    if second_id is not None and (top_score - second_score) < close_threshold:
        hybrid = hybrid_for(top_id, second_id)
        suggestions.append(
            f"  CLOSE CALL: {career_name(top_id)} ({top_score:+.2f}) and "
            f"{career_name(second_id)} ({second_score:+.2f}) are very close.\n"
            f"     Consider: {hybrid}"
        )

    # 2. Weak-match: even the top option scores poorly.
    if top_score < weak_threshold:
        suggestions.append(
            f"  WEAK MATCH: even the top option ({career_name(top_id)}) "
            f"scores only {top_score:+.2f}.\n"
            f"     The profile may need more skill or experience signal before "
            f"any of these careers becomes a strong fit. Use the counterfactuals "
            f"below to see which additions would most change the picture."
        )

    # 3. Conflict: rules with negative contributions to the top recommendation.
    blockers = [
        f for f in firings
        if f.contributions.get(top_id, 0) < -0.5
    ]
    if blockers:
        suggestions.append(
            f"  CONFLICT: factors in your profile actively work against "
            f"{career_name(top_id)} despite it ranking first. Resolving these "
            f"would meaningfully strengthen the match:"
        )
        for f in blockers[:3]:
            suggestions.append(
                f"     - {f.rule.description}  ({f.contributions[top_id]:+.2f})"
            )

    # 4. Surface a "dark horse" — a career with strong positive support that
    #    didn't crack the top three because of a single big penalty.
    top3_ids = {c for c, _ in rank[:3]}
    for cid, total in rank[3:]:
        positives_only = sum(
            max(0, f.contributions.get(cid, 0)) for f in firings
        )
        if positives_only >= 6 and cid not in top3_ids:
            suggestions.append(
                f"  DARK HORSE: {career_name(cid)} has substantial positive support "
                f"({positives_only:+.2f} of positive evidence) but is held back by "
                f"penalties. Worth considering if those constraints can be addressed."
            )
            break

    lines = ["=" * 70, "ALTERNATIVE OPTIONS", "=" * 70]
    if not suggestions:
        lines.append("  No alternative-option suggestions — the top recommendation "
                     "is a clear, well-supported fit.")
    else:
        lines.extend(suggestions)
    return "\n".join(lines)
