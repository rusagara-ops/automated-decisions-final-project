"""
Sample user profiles. Each one is designed to exercise a different
decision-making scenario in the advisor:

  - swe_candidate: clean software-engineering fit
  - research_candidate: PhD-track / academic-research fit
  - consulting_candidate: strategy / communication-driven, less technical
  - conflicted_candidate: skills point to SWE, preferences point to PM/consulting
  - early_career_candidate: weak signal across the board (triggers WEAK MATCH)
"""
from advisor import UserProfile


def swe_candidate() -> UserProfile:
    return UserProfile(
        name="Alex (SWE-leaning senior)",
        technical_skills={
            "python": 5, "java": 4, "javascript": 4, "system_design": 4,
            "linux": 4, "machine_learning": 3, "math": 3, "statistics": 3,
        },
        non_technical_skills={"communication": 3, "writing": 3, "leadership": 2},
        interests=["building", "products", "ai"],
        experience=[
            {"field": "software_engineering", "role": "SWE intern", "years": 2},
        ],
        work_style=["hands_on", "collaborative", "fast_paced"],
        short_term_goals=[
            "land a high-impact engineering role at a product company",
            "earn a competitive starting salary",
        ],
        long_term_goals=["become a tech lead and eventually start a company"],
        constraints=[],
    )


def research_candidate() -> UserProfile:
    return UserProfile(
        name="Priya (research-track)",
        technical_skills={
            "python": 4, "machine_learning": 5, "deep_learning": 5,
            "math": 5, "statistics": 5, "linear_algebra": 4, "writing": 4,
        },
        non_technical_skills={"writing": 5, "communication": 3},
        interests=["research", "ai", "open_problems", "theory"],
        experience=[
            {"field": "research", "role": "undergrad researcher", "years": 2},
            {"field": "machine_learning", "role": "ML intern", "years": 1},
        ],
        work_style=["independent", "strategic"],
        short_term_goals=["apply to top PhD programs in machine learning"],
        long_term_goals=["pursue a PhD and contribute to fundamental AI research"],
        constraints=[],
    )


def consulting_candidate() -> UserProfile:
    return UserProfile(
        name="Jordan (strategy / consulting)",
        technical_skills={"python": 2, "math": 3, "statistics": 3},
        non_technical_skills={
            "communication": 5, "presentation": 5, "writing": 4, "leadership": 4,
        },
        interests=["strategy", "business", "users"],
        experience=[
            {"field": "consulting", "role": "case-comp leader", "years": 2},
        ],
        work_style=["collaborative", "fast_paced", "strategic", "ambiguous"],
        short_term_goals=["land an offer at a top management consulting firm"],
        long_term_goals=["move into product strategy or general management"],
        constraints=["no_relocation"],
    )


def conflicted_candidate() -> UserProfile:
    """Skills strongly support SWE, but goals + work style support PM/consulting.
    Designed to trigger CLOSE CALL and CONFLICT alternatives output."""
    return UserProfile(
        name="Sam (conflicted: SWE skills, PM aspirations)",
        technical_skills={
            "python": 5, "java": 4, "system_design": 3, "machine_learning": 3,
        },
        non_technical_skills={
            "communication": 4, "presentation": 4, "leadership": 4, "writing": 3,
        },
        interests=["building", "products", "strategy", "users"],
        experience=[
            {"field": "software_engineering", "role": "SWE intern", "years": 1},
        ],
        work_style=["collaborative", "strategic"],
        short_term_goals=["find a role that combines technical depth with product impact"],
        long_term_goals=["become a product leader at a major tech company"],
        constraints=[],
    )


def early_career_candidate() -> UserProfile:
    """Weak signal across the board — designed to trigger WEAK MATCH path."""
    return UserProfile(
        name="Morgan (exploring options)",
        technical_skills={"python": 2},
        non_technical_skills={"communication": 3},
        interests=["ai"],
        experience=[],
        work_style=["collaborative"],
        short_term_goals=["explore what kinds of work I might enjoy"],
        long_term_goals=[],
        constraints=["no_phd"],
    )


def cybersecurity_candidate() -> UserProfile:
    """Strong security background — should top out at cybersecurity."""
    return UserProfile(
        name="Riley (cybersecurity-focused)",
        technical_skills={
            "python": 4, "security": 5, "cryptography": 3,
            "linux": 5, "networking": 4, "reverse_engineering": 3,
            "system_design": 3,
        },
        non_technical_skills={"writing": 3, "communication": 3},
        interests=["security", "hacking", "ctf", "privacy", "ethics"],
        experience=[
            {"field": "software_engineering", "role": "appsec intern", "years": 1},
        ],
        work_style=["independent", "hands_on", "ic_focused"],
        short_term_goals=["land a security engineering role at a tech company"],
        long_term_goals=["become a senior security researcher"],
        constraints=[],
    )


def founder_candidate() -> UserProfile:
    """Aspiring founder with prior startup experience and complementary skills."""
    return UserProfile(
        name="Taylor (aspiring founder)",
        technical_skills={
            "python": 4, "system_design": 3, "frontend": 3, "backend": 3,
        },
        non_technical_skills={
            "leadership": 5, "sales": 4, "communication": 4,
            "public_speaking": 4, "design_thinking": 3, "creativity": 4,
            "writing": 3,
        },
        interests=["building", "products", "strategy", "climate", "shipping"],
        experience=[
            {"field": "founder", "role": "co-founded a small SaaS", "years": 1},
            {"field": "software_engineering", "role": "SWE intern", "years": 2},
        ],
        work_style=["ambiguous", "fast_paced", "strategic", "hands_on"],
        short_term_goals=["start a company with mission impact"],
        long_term_goals=["build a venture-backed climate-tech company"],
        constraints=[],
    )


def quant_candidate() -> UserProfile:
    """Strong math + finance background — quant or industry research fit."""
    return UserProfile(
        name="Devin (quant-track)",
        technical_skills={
            "python": 5, "math": 5, "statistics": 5, "probability": 5,
            "linear_algebra": 5, "machine_learning": 4, "finance": 4, "trading": 3,
        },
        non_technical_skills={"writing": 3, "communication": 3},
        interests=["finance", "markets", "trading", "theory"],
        experience=[
            {"field": "finance", "role": "quant intern at a hedge fund", "years": 1},
        ],
        work_style=["independent", "structured", "ic_focused"],
        short_term_goals=[
            "land a quant research role with intellectual challenge and high salary",
        ],
        long_term_goals=["become a senior quant researcher"],
        constraints=[],
    )


def designer_candidate() -> UserProfile:
    """Design-leaning candidate with some technical chops."""
    return UserProfile(
        name="Emerson (design-leaning)",
        technical_skills={
            "design_visual": 5, "ux_research": 4, "figma": 5,
            "frontend": 3, "css": 4, "python": 3,
        },
        non_technical_skills={
            "communication": 4, "creativity": 5,
            "design_thinking": 4, "writing": 3,
        },
        interests=["users", "user_experience", "products", "building", "psychology"],
        experience=[
            {"field": "software_engineering", "role": "design-engineering intern", "years": 1},
        ],
        work_style=["collaborative", "hands_on"],
        short_term_goals=["land a product design role at a consumer-product company"],
        long_term_goals=["lead a design team"],
        constraints=[],
    )


PROFILES = {
    "swe": swe_candidate,
    "research": research_candidate,
    "consulting": consulting_candidate,
    "conflicted": conflicted_candidate,
    "early_career": early_career_candidate,
    "cybersecurity": cybersecurity_candidate,
    "founder": founder_candidate,
    "quant": quant_candidate,
    "designer": designer_candidate,
}
