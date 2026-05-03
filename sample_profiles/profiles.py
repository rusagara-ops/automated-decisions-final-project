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


PROFILES = {
    "swe": swe_candidate,
    "research": research_candidate,
    "consulting": consulting_candidate,
    "conflicted": conflicted_candidate,
    "early_career": early_career_candidate,
}
