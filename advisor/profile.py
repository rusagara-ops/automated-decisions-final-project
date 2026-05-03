"""User profile data structure for the career decision support system."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UserProfile:
    name: str
    technical_skills: Dict[str, int] = field(default_factory=dict)
    non_technical_skills: Dict[str, int] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    experience: List[dict] = field(default_factory=list)
    work_style: List[str] = field(default_factory=list)
    short_term_goals: List[str] = field(default_factory=list)
    long_term_goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    def skill_level(self, skill: str) -> int:
        return max(
            self.technical_skills.get(skill, 0),
            self.non_technical_skills.get(skill, 0),
        )

    def summary(self) -> str:
        lines = [f"Profile: {self.name}"]
        if self.technical_skills:
            top = sorted(self.technical_skills.items(), key=lambda kv: -kv[1])[:5]
            lines.append("  Technical: " + ", ".join(f"{k}({v})" for k, v in top))
        if self.non_technical_skills:
            top = sorted(self.non_technical_skills.items(), key=lambda kv: -kv[1])[:5]
            lines.append("  Non-technical: " + ", ".join(f"{k}({v})" for k, v in top))
        if self.interests:
            lines.append("  Interests: " + ", ".join(self.interests))
        if self.work_style:
            lines.append("  Work style: " + ", ".join(self.work_style))
        if self.short_term_goals:
            lines.append("  Short-term goals: " + "; ".join(self.short_term_goals))
        if self.long_term_goals:
            lines.append("  Long-term goals: " + "; ".join(self.long_term_goals))
        if self.constraints:
            lines.append("  Constraints: " + ", ".join(self.constraints))
        return "\n".join(lines)
