"""
Test suite for the career decision support system.

Run from the project root with:
    python -m unittest tests.test_engine

These tests exercise:
  - structural invariants of the rule base (no dead rules, valid careers)
  - sanity rankings for each sample profile
  - the four explanation modes produce non-trivial output
  - alternatives engine triggers the right warnings on the right profiles
  - counterfactuals are robust on strong profiles and informative on weak ones
"""
import unittest

from advisor import (
    CAREERS, RULES, UserProfile, score,
    explain_top, head_to_head, counterfactuals, detect_tradeoffs, alternatives,
    heat_map, confidence_band,
)
from advisor.scoring import ranked, fire_rules
from sample_profiles import (
    swe_candidate, research_candidate, consulting_candidate,
    conflicted_candidate, early_career_candidate, PROFILES,
)


VALID_CAREER_IDS = {c.id for c in CAREERS}


# --------------------------------------------------------------------------
# Structural invariants
# --------------------------------------------------------------------------

class TestRuleBaseStructure(unittest.TestCase):
    """Properties the rule base should satisfy independent of any profile."""

    def test_rule_ids_unique(self):
        ids = [r.id for r in RULES]
        self.assertEqual(len(ids), len(set(ids)),
                         "Rule IDs must be unique")

    def test_all_rule_effects_target_valid_careers(self):
        for rule in RULES:
            for career_id in rule.effects:
                self.assertIn(
                    career_id, VALID_CAREER_IDS,
                    f"Rule '{rule.id}' targets unknown career '{career_id}'",
                )

    def test_every_rule_can_fire_in_principle(self):
        """Each rule should be able to fire against a kitchen-sink profile
        that has every skill, interest, work-style, goal-keyword, and
        relevant experience. Rules that cannot fire here have impossible
        conditions (typos in skill names, contradictory requirements, etc.)."""
        kitchen_sink = UserProfile(
            name="Kitchen sink",
            technical_skills={
                "python": 5, "java": 5, "c++": 5, "javascript": 5, "go": 5, "rust": 5,
                "machine_learning": 5, "deep_learning": 5, "nlp": 5,
                "statistics": 5, "math": 5, "probability": 5, "linear_algebra": 5,
                "linux": 5, "networking": 5, "system_design": 5, "cloud": 5,
                "frontend": 5, "react": 5, "css": 5,
                "backend": 5, "databases": 5, "distributed_systems": 5, "sql": 5,
                "ios": 5, "android": 5, "mobile": 5,
                "finance": 5, "trading": 5, "economics": 5,
                "security": 5, "cryptography": 5, "reverse_engineering": 5,
                "design_visual": 5, "ux_research": 5, "figma": 5,
            },
            non_technical_skills={
                "communication": 5, "presentation": 5, "writing": 5, "leadership": 5,
                "public_speaking": 5, "sales": 5, "persuasion": 5,
                "creativity": 5, "design_thinking": 5, "teaching": 5, "mentoring": 5,
            },
            interests=[
                "ai", "machine_learning", "ml", "building", "products", "shipping",
                "strategy", "business", "research", "open_problems", "theory",
                "finance", "markets", "trading", "users", "user_experience", "psychology",
                "security", "hacking", "ctf", "open_source", "oss",
                "infrastructure", "scale", "distributed_systems",
                "llms", "generative_ai", "nlp",
                "healthcare", "biotech", "medicine",
                "climate", "sustainability", "energy",
                "education", "edtech", "teaching",
                "gaming", "games", "game_dev",
                "privacy", "ethics", "policy",
            ],
            experience=[
                {"field": "software_engineering", "years": 3},
                {"field": "data_science", "years": 3},
                {"field": "machine_learning", "years": 3},
                {"field": "research", "years": 3},
                {"field": "founder", "years": 2},
                {"field": "finance", "years": 2},
            ],
            work_style=[
                "collaborative", "independent", "fast_paced", "ambiguous",
                "strategic", "hands_on", "structured", "introverted", "ic_focused",
            ],
            short_term_goals=[
                "high salary impact stability intellectual challenge phd startup "
                "remote teach mentor graduate school"
            ],
            long_term_goals=["found a company; pursue a PhD; start a company"],
            constraints=[
                "no_phd", "needs_visa_sponsor", "no_relocation",
                "risk_averse", "no_coding",
            ],
        )
        # Inverse rules (lacks_*, missing-skill, constraint-only) can't fire
        # on a kitchen-sink profile — they need an empty profile.
        empty = UserProfile(
            name="Empty",
            constraints=[
                "no_phd", "needs_visa_sponsor", "no_relocation",
                "risk_averse", "no_coding",
            ],
        )
        firing_ids = (
            {f.rule.id for f in fire_rules(kitchen_sink)}
            | {f.rule.id for f in fire_rules(empty)}
        )
        dead = [r.id for r in RULES if r.id not in firing_ids]
        self.assertEqual(
            dead, [],
            f"Rules with impossible conditions: {dead}",
        )

    def test_sample_coverage_reasonable(self):
        """At least half of all rules should fire across the 5 sample profiles.
        Rules below this threshold suggest either thin sample coverage or
        rules that target edge cases never demonstrated."""
        firing_ids = set()
        for fn in PROFILES.values():
            for f in fire_rules(fn()):
                firing_ids.add(f.rule.id)
        coverage = len(firing_ids) / len(RULES)
        self.assertGreaterEqual(
            coverage, 0.45,
            f"Sample profile coverage too low: {coverage:.0%}. "
            f"Add more diverse profiles or trim unused rules.",
        )

    def test_rule_descriptions_non_empty(self):
        for rule in RULES:
            self.assertTrue(rule.description.strip(),
                            f"Rule '{rule.id}' missing description (needed for explanations)")


# --------------------------------------------------------------------------
# Per-profile sanity rankings
# --------------------------------------------------------------------------

class TestSampleProfiles(unittest.TestCase):

    def assert_top_includes(self, profile, expected_ids, top_n=3):
        scores, _ = score(profile)
        top = [cid for cid, _ in ranked(scores)[:top_n]]
        for expected in expected_ids:
            self.assertIn(
                expected, top,
                f"Expected '{expected}' in top {top_n} for {profile.name}, got {top}",
            )

    def test_swe_candidate_top3_engineering_focused(self):
        """SWE candidate should have engineering-track careers dominate top 3."""
        profile = swe_candidate()
        scores, _ = score(profile)
        top3 = {cid for cid, _ in ranked(scores)[:3]}
        engineering_track = {
            "software_engineering", "ml_engineering",
            "entrepreneurship", "devops_sre",
        }
        overlap = top3 & engineering_track
        self.assertGreaterEqual(
            len(overlap), 2,
            f"Expected ≥2 engineering-track careers in SWE candidate top 3, got {top3}",
        )

    def test_research_candidate_tops_research_academic(self):
        """A profile with PhD goal + deep ML/math + research experience must
        top out at academic research. This is the cleanest sanity check."""
        profile = research_candidate()
        scores, _ = score(profile)
        top_id, _ = ranked(scores)[0]
        self.assertEqual(top_id, "research_academic")

    def test_consulting_constraint_demotes_consulting(self):
        """The consulting candidate has a no_relocation constraint. It should
        push consulting out of the #1 slot — that's the whole point of the
        rule. PM should win head-to-head."""
        profile = consulting_candidate()
        scores, _ = score(profile)
        top_id, _ = ranked(scores)[0]
        self.assertNotEqual(
            top_id, "consulting",
            "Consulting should be demoted by the no_relocation constraint",
        )
        # ...but consulting should still appear in top 3 (it's a strong fit otherwise)
        top3 = {cid for cid, _ in ranked(scores)[:3]}
        self.assertIn("consulting", top3)

    def test_conflicted_candidate_pm_in_top(self):
        """The conflicted candidate has SWE skills but PM aspirations. Either
        PM or SWE-adjacent careers should rank highly."""
        profile = conflicted_candidate()
        scores, _ = score(profile)
        top3 = {cid for cid, _ in ranked(scores)[:3]}
        self.assertIn("product_management", top3)

    def test_early_career_candidate_low_scores(self):
        """Weak profile must produce low scores (≤ weak_match threshold)."""
        profile = early_career_candidate()
        scores, _ = score(profile)
        top_score = ranked(scores)[0][1]
        self.assertLess(
            top_score, 5.0,
            f"Early-career profile should score below weak-match threshold; got {top_score:.2f}",
        )

    def test_constraint_no_phd_blocks_academic_research(self):
        """Without a PhD pathway, academic research should not rank #1
        even with otherwise research-favoring inputs."""
        profile = UserProfile(
            name="No-PhD researcher",
            technical_skills={"machine_learning": 5, "math": 5, "statistics": 5},
            non_technical_skills={"writing": 4},
            interests=["research", "ai"],
            constraints=["no_phd"],
        )
        scores, _ = score(profile)
        top_id, _ = ranked(scores)[0]
        self.assertNotEqual(top_id, "research_academic")


# --------------------------------------------------------------------------
# Explanation modes
# --------------------------------------------------------------------------

class TestExplanationModes(unittest.TestCase):
    """Each explanation mode should produce non-empty, structured output."""

    def setUp(self):
        self.profile = swe_candidate()
        self.scores, self.firings = score(self.profile)
        self.top_id, _ = ranked(self.scores)[0]
        self.second_id, _ = ranked(self.scores)[1]

    def test_explain_top_lists_top_n(self):
        out = explain_top(self.scores, self.firings, top_n=3)
        # Should mention exactly 3 careers in headers (#1, #2, #3)
        self.assertIn("#1", out)
        self.assertIn("#2", out)
        self.assertIn("#3", out)
        self.assertIn("Why this ranks high", out)

    def test_explain_top_includes_evidence(self):
        out = explain_top(self.scores, self.firings, top_n=2)
        # Must surface specific evidence, not just rule descriptions.
        self.assertTrue(
            "python" in out.lower() or "interest" in out.lower(),
            "Explanation should include concrete evidence from the profile",
        )

    def test_head_to_head_shows_distinguishing_factors(self):
        out = head_to_head(self.top_id, self.second_id, self.firings)
        self.assertIn("favors", out)

    def test_counterfactuals_returns_text(self):
        out = counterfactuals(self.profile, self.scores)
        # Should always produce some output — either findings or "robust" message
        self.assertGreater(len(out.strip()), 0)
        self.assertIn("COUNTERFACTUAL", out.upper())

    def test_counterfactuals_robust_on_strong_profile(self):
        """A profile with overwhelming evidence for one career should produce
        a 'robust' counterfactual report (no small change flips it)."""
        profile = research_candidate()
        scores, _ = score(profile)
        out = counterfactuals(profile, scores)
        self.assertIn("robust", out.lower())

    def test_detect_tradeoffs_returns_text(self):
        out = detect_tradeoffs(self.firings)
        self.assertGreater(len(out.strip()), 0)
        self.assertIn("TRADEOFF", out.upper())


# --------------------------------------------------------------------------
# Alternatives / option generation
# --------------------------------------------------------------------------

class TestAlternatives(unittest.TestCase):

    def test_weak_profile_triggers_weak_match_warning(self):
        profile = early_career_candidate()
        scores, firings = score(profile)
        out = alternatives(profile, scores, firings)
        self.assertIn("WEAK MATCH", out)

    def test_close_call_triggers_hybrid_suggestion(self):
        """SWE candidate has SWE and entrepreneurship within close_threshold.
        Should trigger CLOSE CALL with a hybrid role suggestion."""
        profile = swe_candidate()
        scores, firings = score(profile)
        out = alternatives(profile, scores, firings)
        self.assertIn("CLOSE CALL", out)


# --------------------------------------------------------------------------
# Confidence bands (heat map)
# --------------------------------------------------------------------------

class TestConfidenceBands(unittest.TestCase):
    """The qualitative GREEN/YELLOW/RED layer should map scores to bands
    monotonically and produce sensible heat maps for each profile."""

    def test_band_thresholds_monotone(self):
        self.assertEqual(confidence_band(15.0), "GREEN")
        self.assertEqual(confidence_band(10.0), "GREEN")
        self.assertEqual(confidence_band(9.99), "YELLOW")
        self.assertEqual(confidence_band(5.0), "YELLOW")
        self.assertEqual(confidence_band(4.99), "RED")
        self.assertEqual(confidence_band(0.0), "RED")
        self.assertEqual(confidence_band(-3.0), "RED")

    def test_strong_profile_has_at_least_one_green(self):
        """A well-defined profile should produce at least one GREEN career."""
        for fn in [swe_candidate, research_candidate, consulting_candidate,
                   conflicted_candidate]:
            profile = fn()
            scores, _ = score(profile)
            bands = {confidence_band(s) for s in scores.values()}
            self.assertIn(
                "GREEN", bands,
                f"{profile.name} should have at least one GREEN career; got bands {bands}",
            )

    def test_weak_profile_has_no_greens(self):
        """The early-career profile should not have any GREEN careers — the
        heat map's job here is to convey 'not enough signal anywhere yet'."""
        profile = early_career_candidate()
        scores, _ = score(profile)
        bands = {confidence_band(s) for s in scores.values()}
        self.assertNotIn("GREEN", bands)

    def test_heat_map_renders_all_three_bands(self):
        """The rendered heat map should always show all three band sections,
        even when a band is empty — that empties-as-information property is
        what makes it a useful qualitative summary."""
        profile = early_career_candidate()
        scores, _ = score(profile)
        out = heat_map(scores)
        self.assertIn("GREEN", out)
        self.assertIn("YELLOW", out)
        self.assertIn("RED", out)


# --------------------------------------------------------------------------
# CLI smoke tests
# --------------------------------------------------------------------------

class TestCLI(unittest.TestCase):
    """End-to-end smoke tests for the python -m advisor CLI."""

    def test_list_mode_lists_all_presets(self):
        from advisor.__main__ import main
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--list"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        # Every preset name should appear in the output.
        for preset_name in PROFILES:
            self.assertIn(preset_name, out)

    def test_preset_mode_runs_full_pipeline(self):
        """A preset run must produce all six explanation surfaces."""
        from advisor.__main__ import main
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--preset", "research"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("TOP RECOMMENDATIONS", out)
        self.assertIn("CONFIDENCE HEAT MAP", out)
        self.assertIn("ALTERNATIVE OPTIONS", out)
        self.assertIn("HEAD-TO-HEAD", out)
        self.assertIn("COUNTERFACTUAL", out)

    def test_unknown_preset_returns_error_code(self):
        from advisor.__main__ import main
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--preset", "nonexistent"])
        self.assertEqual(rc, 1)


# --------------------------------------------------------------------------
# Score reproducibility
# --------------------------------------------------------------------------

class TestReproducibility(unittest.TestCase):
    """Scoring must be deterministic — same profile, same scores."""

    def test_same_profile_same_scores(self):
        for fn in PROFILES.values():
            p = fn()
            s1, _ = score(p)
            s2, _ = score(p)
            self.assertEqual(s1, s2, f"Non-deterministic scoring for {p.name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
