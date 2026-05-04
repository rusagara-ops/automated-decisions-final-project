"""
Interactive command-line interface for the career decision support system.

Usage:
    python -m advisor                   # interactive prompts
    python -m advisor --preset swe      # run a preset sample profile
    python -m advisor --list            # list available presets

The interactive mode walks the user through the inputs in five small
chunks (technical skills, non-technical skills, interests, work style,
constraints, goals), then runs the full pipeline: ranked recommendations
with confidence bands, alternatives, head-to-head, and counterfactuals.

This is the system's primary live-demo entry point — it lets a grader (or
anyone) test the decision engine with their own profile in under a minute,
without needing Jupyter.
"""
import argparse
import sys
from typing import List

from .alternatives import alternatives
from .explanation import (
    counterfactuals,
    explain_top,
    head_to_head,
    heat_map,
)
from .profile import UserProfile
from .scoring import ranked, score


# --------------------------------------------------------------------------
# Catalogs of valid input values (must match the rule base)
# --------------------------------------------------------------------------

TECH_SKILLS = [
    "python", "machine_learning", "math", "statistics", "system_design",
    "linux", "frontend", "backend", "security", "finance", "design_visual",
]
NON_TECH_SKILLS = [
    "communication", "writing", "leadership", "public_speaking",
    "creativity", "sales",
]
INTERESTS = [
    "ai", "building", "products", "strategy", "business", "research",
    "theory", "finance", "markets", "users", "security", "open_source",
    "infrastructure", "llms", "healthcare", "climate", "education",
    "gaming", "privacy", "ethics",
]
WORK_STYLES = [
    "collaborative", "independent", "fast_paced", "ambiguous",
    "strategic", "hands_on", "structured", "ic_focused",
]
CONSTRAINTS = [
    "no_phd", "needs_visa_sponsor", "no_relocation",
    "risk_averse", "no_coding",
]


# --------------------------------------------------------------------------
# Prompt helpers
# --------------------------------------------------------------------------

def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"  {label}{suffix}: ").strip()
    return raw or default


def _prompt_skill_block(skills: List[str]) -> dict:
    """Ask for each skill; accept 0-5 or blank to skip."""
    out = {}
    for skill in skills:
        while True:
            raw = input(f"  {skill:<22s} (0-5, blank=skip): ").strip()
            if not raw:
                break
            if raw.isdigit() and 0 <= int(raw) <= 5:
                level = int(raw)
                if level > 0:
                    out[skill] = level
                break
            print("    please enter 0-5 (or blank to skip)")
    return out


def _prompt_multichoice(label: str, options: List[str]) -> List[str]:
    """Ask for a comma-separated subset of options."""
    print(f"\n== {label} ==")
    print(f"  Options: {', '.join(options)}")
    raw = input("  Your selection (comma-separated, blank=none): ").strip()
    if not raw:
        return []
    chosen = [s.strip() for s in raw.split(",") if s.strip()]
    invalid = [s for s in chosen if s not in options]
    if invalid:
        print(f"  ⚠ ignoring unknown values: {', '.join(invalid)}")
    return [s for s in chosen if s in options]


def _prompt_goal(label: str) -> List[str]:
    raw = input(f"  {label} (free text, blank=skip): ").strip()
    return [raw] if raw else []


# --------------------------------------------------------------------------
# Interactive profile-building flow
# --------------------------------------------------------------------------

def build_profile_interactive() -> UserProfile:
    print("=" * 70)
    print("CAREER DECISION SUPPORT SYSTEM — INTERACTIVE MODE")
    print("=" * 70)
    print("\nI'll ask a few questions about your background and goals,")
    print("then recommend career paths with full explanations.")
    print("Press Enter at any prompt to skip / accept the default.\n")

    name = _prompt("Your name", default="anonymous")

    print("\n== TECHNICAL SKILLS (rate 0-5) ==")
    tech = _prompt_skill_block(TECH_SKILLS)

    print("\n== NON-TECHNICAL SKILLS (rate 0-5) ==")
    non_tech = _prompt_skill_block(NON_TECH_SKILLS)

    interests = _prompt_multichoice("INTERESTS", INTERESTS)
    work_style = _prompt_multichoice("WORK STYLE", WORK_STYLES)
    constraints = _prompt_multichoice("CONSTRAINTS", CONSTRAINTS)

    print("\n== GOALS (free text, used for keyword matching) ==")
    short = _prompt_goal("Short-term goal")
    long_ = _prompt_goal("Long-term goal")

    return UserProfile(
        name=name,
        technical_skills=tech,
        non_technical_skills=non_tech,
        interests=interests,
        work_style=work_style,
        short_term_goals=short,
        long_term_goals=long_,
        constraints=constraints,
    )


# --------------------------------------------------------------------------
# Output rendering
# --------------------------------------------------------------------------

def show_recommendation(profile: UserProfile, top_n: int = 3) -> None:
    scores, firings = score(profile)
    print("\n")
    print(profile.summary())
    print()
    print(explain_top(scores, firings, top_n=top_n))
    print()
    print(heat_map(scores))
    print()
    print(alternatives(profile, scores, firings))
    print()
    top_two = ranked(scores)[:2]
    if len(top_two) == 2:
        print(head_to_head(top_two[0][0], top_two[1][0], firings))
        print()
    print(counterfactuals(profile, scores))


# --------------------------------------------------------------------------
# CLI entrypoint
# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m advisor",
        description="Explainable career decision support system. "
                    "Run with no arguments for interactive mode.",
    )
    parser.add_argument(
        "--preset", metavar="NAME",
        help="Run a preset sample profile instead of prompting "
             "(see --list for valid names)",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available preset sample profiles and exit",
    )
    parser.add_argument(
        "--top-n", type=int, default=3,
        help="How many recommendations to show in the top-N section "
             "(default: 3)",
    )
    args = parser.parse_args(argv)

    # Lazy import — only needed for preset mode.
    from sample_profiles import PROFILES

    if args.list:
        print("Available preset profiles:")
        for name, fn in PROFILES.items():
            print(f"  {name:14s} - {fn().name}")
        return 0

    if args.preset:
        if args.preset not in PROFILES:
            print(f"Unknown preset: {args.preset!r}")
            print(f"Run with --list to see available presets.")
            return 1
        profile = PROFILES[args.preset]()
    else:
        profile = build_profile_interactive()

    show_recommendation(profile, top_n=args.top_n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
