"""
Rule base for the explainable career decision system.

Each Rule has:
  - id: short identifier
  - description: human-readable rationale shown in explanations
  - condition: callable(profile) -> Optional[Match]
       returns None if the rule does not fire,
       or a Match(strength 0..1, evidence list) if it does
  - effects: dict mapping career_id -> base weight (positive favors, negative penalizes)

When a rule fires, each effect is scaled by `match.strength` to produce
the actual score contribution. The Match.evidence list is what powers the
human-readable explanation — every score change can be traced back to the
specific profile attributes that triggered it.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


# --------------------------------------------------------------------------
# Core types
# --------------------------------------------------------------------------

@dataclass
class Match:
    strength: float
    evidence: List[str]


@dataclass
class Rule:
    id: str
    description: str
    condition: Callable
    effects: Dict[str, float]


@dataclass
class RuleFiring:
    rule: Rule
    match: Match
    contributions: Dict[str, float] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Condition helpers — small DSL for writing rules concisely
# --------------------------------------------------------------------------

def any_skill(*skills, min_level: int = 3):
    """Fires if user has any of the listed skills at min_level or higher.
    Strength = highest matching skill / 5."""
    def cond(profile):
        evidence, max_level = [], 0
        for s in skills:
            level = profile.skill_level(s)
            if level >= min_level:
                evidence.append(f"{s.replace('_', ' ')}: {level}/5")
                max_level = max(max_level, level)
        if not evidence:
            return None
        return Match(strength=max_level / 5.0, evidence=evidence)
    return cond


def all_skills(*skills, min_level: int = 3):
    """Fires only if user has ALL listed skills at min_level. Strength = weakest / 5."""
    def cond(profile):
        evidence, levels = [], []
        for s in skills:
            level = profile.skill_level(s)
            if level < min_level:
                return None
            evidence.append(f"{s.replace('_', ' ')}: {level}/5")
            levels.append(level)
        return Match(strength=min(levels) / 5.0, evidence=evidence)
    return cond


def lacks_skill(skill: str, max_level: int = 1):
    """Fires when user is missing or weak in a skill. Used for negative effects."""
    def cond(profile):
        level = profile.skill_level(skill)
        if level > max_level:
            return None
        return Match(strength=1.0, evidence=[f"low {skill.replace('_', ' ')}: {level}/5"])
    return cond


def has_interest(*tags):
    def cond(profile):
        matches = [t for t in tags if t in profile.interests]
        if not matches:
            return None
        return Match(strength=1.0, evidence=[f"interest: {m}" for m in matches])
    return cond


def has_work_style(*styles):
    def cond(profile):
        matches = [s for s in styles if s in profile.work_style]
        if not matches:
            return None
        return Match(strength=1.0, evidence=[f"work style: {m}" for m in matches])
    return cond


def has_constraint(*constraints):
    def cond(profile):
        matches = [c for c in constraints if c in profile.constraints]
        if not matches:
            return None
        return Match(strength=1.0, evidence=[f"constraint: {m}" for m in matches])
    return cond


def has_experience_in(field_name: str, min_years: float = 0):
    def cond(profile):
        matches = [e for e in profile.experience if e.get("field") == field_name]
        if not matches:
            return None
        years = sum(e.get("years", 0) for e in matches)
        if years < min_years:
            return None
        return Match(
            strength=min(1.0, years / 3.0),
            evidence=[f"{years} year(s) experience in {field_name}"],
        )
    return cond


def goal_mentions(*keywords):
    def cond(profile):
        text = " ".join(profile.short_term_goals + profile.long_term_goals).lower()
        hits = [k for k in keywords if k.lower() in text]
        if not hits:
            return None
        return Match(strength=1.0, evidence=[f"goal mentions '{k}'" for k in hits])
    return cond


def either(*conds):
    """Fires if any sub-condition fires. Strength = max sub-strength."""
    def cond(profile):
        evidence, strength = [], 0.0
        for c in conds:
            m = c(profile)
            if m is not None:
                evidence.extend(m.evidence)
                strength = max(strength, m.strength)
        if not evidence:
            return None
        return Match(strength=strength, evidence=evidence)
    return cond


# --------------------------------------------------------------------------
# Rule base
# --------------------------------------------------------------------------

RULES: List[Rule] = [
    # ---- Skill-driven positive rules ----
    Rule(
        id="strong_programming",
        description="Strong general-purpose programming supports engineering roles.",
        condition=any_skill("python", "java", "c++", "javascript", "go", "rust", min_level=4),
        effects={
            "software_engineering": 3.0,
            "ml_engineering": 2.0,
            "data_science": 1.5,
            "devops_sre": 1.5,
            "cybersecurity": 1.0,
            "entrepreneurship": 0.5,
        },
    ),
    Rule(
        id="ml_skills",
        description="Hands-on machine learning experience is core to ML/DS roles.",
        condition=any_skill("machine_learning", "deep_learning", "nlp", min_level=3),
        effects={
            "ml_engineering": 3.0,
            "data_science": 2.5,
            "research_industry": 2.0,
            "research_academic": 1.5,
        },
    ),
    Rule(
        id="stats_math",
        description="Strong statistics / math underpins data and quantitative work.",
        condition=any_skill("statistics", "math", "probability", "linear_algebra", min_level=4),
        effects={
            "data_science": 3.0,
            "finance_quant": 3.0,
            "research_industry": 2.0,
            "research_academic": 2.0,
            "ml_engineering": 1.5,
        },
    ),
    Rule(
        id="systems_skills",
        description="Systems / infrastructure skills support reliability and security work.",
        condition=any_skill("linux", "networking", "system_design", "cloud", min_level=3),
        effects={
            "devops_sre": 3.0,
            "cybersecurity": 2.0,
            "software_engineering": 1.0,
            "ml_engineering": 1.0,
        },
    ),
    Rule(
        id="strong_communication",
        description="Strong communication is critical for client-facing and cross-functional roles.",
        condition=any_skill("communication", "presentation", min_level=4),
        effects={
            "consulting": 3.0,
            "product_management": 3.0,
            "technical_program_management": 3.0,
            "entrepreneurship": 1.5,
            "ux_design": 1.0,
        },
    ),
    Rule(
        id="strong_writing",
        description="Strong writing is leveraged in research, PM specs, and consulting decks.",
        condition=any_skill("writing", min_level=4),
        effects={
            "research_academic": 2.0,
            "research_industry": 1.5,
            "product_management": 2.0,
            "consulting": 2.0,
        },
    ),
    Rule(
        id="design_skills",
        description="Visual / interaction design skills are central to UX and helpful for PM.",
        condition=any_skill("design_visual", "ux_research", "figma", min_level=3),
        effects={
            "ux_design": 3.0,
            "product_management": 1.5,
            "entrepreneurship": 0.5,
        },
    ),
    Rule(
        id="leadership",
        description="Demonstrated leadership supports management-track roles.",
        condition=any_skill("leadership", min_level=3),
        effects={
            "product_management": 2.0,
            "technical_program_management": 2.5,
            "consulting": 1.5,
            "entrepreneurship": 2.0,
        },
    ),
    Rule(
        id="finance_skills",
        description="Finance / market knowledge supports quantitative finance roles.",
        condition=any_skill("finance", "trading", "economics", min_level=3),
        effects={
            "finance_quant": 3.0,
            "consulting": 1.0,
        },
    ),
    Rule(
        id="security_skills",
        description="Security-specific skills point directly to cybersecurity roles.",
        condition=any_skill("security", "cryptography", "reverse_engineering", min_level=3),
        effects={
            "cybersecurity": 3.5,
            "devops_sre": 1.0,
        },
    ),

    # ---- Interest-driven rules ----
    Rule(
        id="interest_ai",
        description="Interest in AI/ML drives toward ML, DS, and research paths.",
        condition=has_interest("ai", "machine_learning", "ml"),
        effects={
            "ml_engineering": 2.0,
            "data_science": 2.0,
            "research_industry": 1.5,
            "research_academic": 1.0,
        },
    ),
    Rule(
        id="interest_building",
        description="Loving to build products favors engineering and founder paths.",
        condition=has_interest("building", "products", "shipping"),
        effects={
            "software_engineering": 2.0,
            "product_management": 1.5,
            "entrepreneurship": 2.0,
            "ml_engineering": 1.0,
        },
    ),
    Rule(
        id="interest_strategy",
        description="Interest in strategy fits consulting and product roles.",
        condition=has_interest("strategy", "business"),
        effects={
            "consulting": 3.0,
            "product_management": 2.0,
            "entrepreneurship": 1.0,
        },
    ),
    Rule(
        id="interest_research",
        description="Curiosity about open problems fits research-oriented careers.",
        condition=has_interest("research", "open_problems", "theory"),
        effects={
            "research_academic": 3.0,
            "research_industry": 2.0,
            "data_science": 0.5,
        },
    ),
    Rule(
        id="interest_finance",
        description="Interest in markets points to quant and finance roles.",
        condition=has_interest("finance", "markets", "trading"),
        effects={
            "finance_quant": 3.0,
            "consulting": 1.0,
        },
    ),
    Rule(
        id="interest_users",
        description="Interest in users / human factors supports UX and PM.",
        condition=has_interest("users", "user_experience", "psychology"),
        effects={
            "ux_design": 2.5,
            "product_management": 2.0,
        },
    ),
    Rule(
        id="interest_security",
        description="Interest in security / hacking points to cybersecurity.",
        condition=has_interest("security", "hacking", "ctf"),
        effects={
            "cybersecurity": 3.0,
        },
    ),

    # ---- Work-style rules ----
    Rule(
        id="style_collaborative",
        description="Collaborative preference suits cross-functional roles.",
        condition=has_work_style("collaborative"),
        effects={
            "product_management": 1.5,
            "consulting": 2.0,
            "technical_program_management": 2.0,
            "ux_design": 1.0,
        },
    ),
    Rule(
        id="style_independent",
        description="Independent / focused preference suits research and IC engineering.",
        condition=has_work_style("independent"),
        effects={
            "research_academic": 2.0,
            "research_industry": 1.0,
            "software_engineering": 1.0,
            "data_science": 0.5,
        },
    ),
    Rule(
        id="style_fast_paced",
        description="Fast-paced preference suits startups and consulting sprints.",
        condition=has_work_style("fast_paced"),
        effects={
            "entrepreneurship": 2.5,
            "consulting": 1.5,
            "product_management": 1.0,
        },
    ),
    Rule(
        id="style_ambiguous",
        description="Comfort with ambiguity is a strong fit for founder and consultant roles.",
        condition=has_work_style("ambiguous"),
        effects={
            "entrepreneurship": 2.0,
            "consulting": 2.0,
            "product_management": 1.0,
            "research_industry": 0.5,
        },
    ),
    Rule(
        id="style_strategic",
        description="Strategic thinkers gravitate to product and consulting roles.",
        condition=has_work_style("strategic"),
        effects={
            "product_management": 2.5,
            "consulting": 2.0,
            "technical_program_management": 1.5,
            "entrepreneurship": 1.0,
        },
    ),
    Rule(
        id="style_hands_on",
        description="Hands-on builders prefer engineering-track roles.",
        condition=has_work_style("hands_on"),
        effects={
            "software_engineering": 2.0,
            "ml_engineering": 1.5,
            "devops_sre": 1.0,
        },
    ),

    # ---- Experience rules ----
    Rule(
        id="exp_swe",
        description="Prior software engineering experience strengthens SWE recruiting.",
        condition=has_experience_in("software_engineering"),
        effects={
            "software_engineering": 2.5,
            "ml_engineering": 1.0,
            "devops_sre": 0.5,
        },
    ),
    Rule(
        id="exp_data",
        description="Prior data / ML experience strengthens data and ML applications.",
        condition=either(
            has_experience_in("data_science"),
            has_experience_in("machine_learning"),
        ),
        effects={
            "data_science": 2.5,
            "ml_engineering": 2.0,
            "research_industry": 1.0,
        },
    ),
    Rule(
        id="exp_research",
        description="Research experience signals fit for academic and industry research.",
        condition=has_experience_in("research"),
        effects={
            "research_academic": 3.0,
            "research_industry": 2.0,
        },
    ),
    Rule(
        id="exp_founder",
        description="Founder / startup experience signals strong fit for entrepreneurship.",
        condition=has_experience_in("founder"),
        effects={
            "entrepreneurship": 3.5,
            "product_management": 1.0,
        },
    ),
    Rule(
        id="exp_finance",
        description="Finance internship experience supports quant recruiting.",
        condition=has_experience_in("finance"),
        effects={
            "finance_quant": 2.5,
            "consulting": 1.0,
        },
    ),

    # ---- Goal-driven rules ----
    Rule(
        id="goal_high_salary",
        description="Wanting high early-career compensation favors SWE / quant / consulting.",
        condition=goal_mentions("high salary", "high pay", "compensation", "high comp"),
        effects={
            "software_engineering": 1.0,
            "finance_quant": 2.0,
            "consulting": 1.5,
            "ml_engineering": 1.0,
            "research_academic": -2.0,  # academia pays poorly relative to industry
        },
    ),
    Rule(
        id="goal_impact",
        description="Wanting impact / mission alignment supports research and founder paths.",
        condition=goal_mentions("impact", "mission", "change the world"),
        effects={
            "research_industry": 1.0,
            "research_academic": 1.0,
            "entrepreneurship": 1.5,
            "product_management": 1.0,
        },
    ),
    Rule(
        id="goal_stability",
        description="Wanting stable / predictable work conflicts with startup paths.",
        condition=goal_mentions("stability", "stable", "predictable", "balance"),
        effects={
            "software_engineering": 1.0,
            "finance_quant": 0.5,
            "consulting": 0.5,
            "entrepreneurship": -2.5,
        },
    ),
    Rule(
        id="goal_intellectual",
        description="Seeking intellectual challenge fits research and quant paths.",
        condition=goal_mentions("intellectual", "challenge", "hard problems", "deep"),
        effects={
            "research_academic": 2.0,
            "research_industry": 1.5,
            "finance_quant": 1.5,
            "ml_engineering": 1.0,
        },
    ),
    Rule(
        id="goal_phd",
        description="Wanting a PhD strongly favors the academic track.",
        condition=goal_mentions("phd", "doctorate", "academia"),
        effects={
            "research_academic": 4.0,
            "research_industry": 1.0,
        },
    ),
    Rule(
        id="goal_startup",
        description="Wanting to start a company favors the founder path.",
        condition=goal_mentions("startup", "founder", "found a company", "start a company"),
        effects={
            "entrepreneurship": 4.0,
            "product_management": 1.0,
            "software_engineering": 0.5,
        },
    ),

    # ---- Constraint-driven negative rules ----
    Rule(
        id="lacks_coding",
        description="Without coding skills, technical engineering paths are not realistic short-term.",
        condition=either(
            lacks_skill("python", max_level=1),
            has_constraint("no_coding"),
        ),
        effects={
            "software_engineering": -3.5,
            "ml_engineering": -3.0,
            "data_science": -2.0,
            "devops_sre": -2.0,
            "cybersecurity": -1.0,
        },
    ),
    Rule(
        id="lacks_math",
        description="Weak quantitative background limits quant and DS paths.",
        condition=lacks_skill("math", max_level=1),
        effects={
            "finance_quant": -3.0,
            "data_science": -2.0,
            "ml_engineering": -1.5,
            "research_academic": -1.0,
        },
    ),
    Rule(
        id="constraint_no_phd",
        description="Without a PhD, academic research roles are largely unavailable.",
        condition=has_constraint("no_phd"),
        effects={
            "research_academic": -4.0,
            "research_industry": -1.5,
        },
    ),
    Rule(
        id="constraint_visa",
        description="Visa / sponsorship constraints reduce viable employer pool for some paths.",
        condition=has_constraint("needs_visa_sponsor"),
        effects={
            "entrepreneurship": -2.0,
            "consulting": -0.5,
            "research_academic": -0.5,
        },
    ),
    Rule(
        id="constraint_no_relocate",
        description="Inability to relocate cuts options concentrated in specific cities.",
        condition=has_constraint("no_relocation"),
        effects={
            "consulting": -2.0,
            "finance_quant": -1.5,
        },
    ),
    Rule(
        id="constraint_risk_averse",
        description="Risk-averse profile is a poor fit for founder paths.",
        condition=has_constraint("risk_averse"),
        effects={
            "entrepreneurship": -3.0,
        },
    ),
]
