"""Career catalog. Each career has an id (used by rules) and a description."""
from dataclasses import dataclass


@dataclass
class Career:
    id: str
    name: str
    description: str
    base_score: float = 0.0


CAREERS = [
    Career("software_engineering", "Software Engineering",
           "Designing and building software products and systems."),
    Career("data_science", "Data Science",
           "Extracting insights and predictions from data using statistics and ML."),
    Career("ml_engineering", "Machine Learning Engineering",
           "Building production ML systems, pipelines, and infrastructure."),
    Career("product_management", "Product Management",
           "Owning product strategy, prioritization, and cross-functional execution."),
    Career("ux_design", "UX / Product Design",
           "Researching users and designing interfaces and experiences."),
    Career("consulting", "Management Consulting",
           "Advising organizations on strategy, operations, and transformation."),
    Career("finance_quant", "Quantitative Finance",
           "Quantitative research, trading, or risk in financial markets."),
    Career("research_industry", "Industry Research",
           "Applied research at scale in industry R&D labs."),
    Career("research_academic", "Academic Research",
           "PhD-track research, publications, and faculty paths."),
    Career("devops_sre", "DevOps / SRE",
           "Reliability, infrastructure, and developer-platform engineering."),
    Career("cybersecurity", "Cybersecurity",
           "Securing systems — defensive, offensive, or governance."),
    Career("entrepreneurship", "Entrepreneurship",
           "Founding or joining early-stage startups."),
    Career("technical_program_management", "Technical Program Management",
           "Leading complex cross-team technical programs end-to-end."),
]

CAREER_BY_ID = {c.id: c for c in CAREERS}


def career_name(career_id: str) -> str:
    c = CAREER_BY_ID.get(career_id)
    return c.name if c else career_id
