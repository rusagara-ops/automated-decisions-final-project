"""Scoring engine: fire all rules and aggregate per-career scores."""
from typing import Dict, List, Tuple

from .careers import CAREERS, Career
from .profile import UserProfile
from .rules import RULES, Rule, RuleFiring


def fire_rules(profile: UserProfile, rules: List[Rule] = None) -> List[RuleFiring]:
    """Run every rule against the profile, returning a structured trace."""
    if rules is None:
        rules = RULES
    firings = []
    for rule in rules:
        match = rule.condition(profile)
        if match is None or match.strength <= 0:
            continue
        contribs = {career: weight * match.strength for career, weight in rule.effects.items()}
        firings.append(RuleFiring(rule=rule, match=match, contributions=contribs))
    return firings


def score(
    profile: UserProfile,
    rules: List[Rule] = None,
    careers: List[Career] = None,
) -> Tuple[Dict[str, float], List[RuleFiring]]:
    """Score every career for the profile.

    Returns:
        scores: dict mapping career_id -> total score
        firings: ordered list of every rule that fired (for explanation)
    """
    if rules is None:
        rules = RULES
    if careers is None:
        careers = CAREERS

    firings = fire_rules(profile, rules)
    scores = {c.id: c.base_score for c in careers}
    for firing in firings:
        for career_id, delta in firing.contributions.items():
            if career_id in scores:
                scores[career_id] += delta
    return scores, firings


def ranked(scores: Dict[str, float]) -> List[Tuple[str, float]]:
    return sorted(scores.items(), key=lambda kv: -kv[1])
