from .profile import UserProfile
from .careers import CAREERS, Career
from .rules import RULES, Rule, Match, RuleFiring
from .scoring import score, fire_rules
from .explanation import (
    explain_top, head_to_head, counterfactuals, detect_tradeoffs,
    heat_map, confidence_band,
)
from .alternatives import alternatives

__all__ = [
    "UserProfile",
    "CAREERS",
    "Career",
    "RULES",
    "Rule",
    "Match",
    "RuleFiring",
    "score",
    "fire_rules",
    "explain_top",
    "head_to_head",
    "counterfactuals",
    "detect_tradeoffs",
    "heat_map",
    "confidence_band",
    "alternatives",
]
