# Project Write-Up — Explainable Career Decision Support System

**Course:** CS 4580/5580 — Automated Decision Systems
**Author:** Kevin Rusagara Iraguha
**Project type:** Individual

---

## 1. Problem statement

Choosing a career path is a high-stakes decision driven by many interacting
factors: skills, interests, prior experience, work-style preferences,
short-term and long-term goals, and practical constraints (visa status,
location, credentials). Most career-advice tools either reduce this to a
keyword-matching quiz, or — increasingly — feed the same inputs into an
opaque ML classifier and surface a recommendation with no reasoning.

This project builds a structured automated decision system for the same
problem, with one defining property: **every recommendation it makes can be
fully explained**, traced back through specific rules to the specific
profile attributes that triggered them. There is no black box.

## 2. What the system does

Given a `UserProfile` (technical skills 0–5, non-technical skills 0–5,
interests, work experience, work-style preferences, goals, and constraints),
the system:

1. Runs a hand-authored rule base of **64 rules** spanning skills, interests,
   work styles, goals, experience, and constraints.
2. Aggregates per-career scores across **13 career paths** (software
   engineering, data science, ML engineering, product management, UX design,
   consulting, quantitative finance, industry research, academic research,
   DevOps/SRE, cybersecurity, entrepreneurship, technical program management).
3. Outputs a ranked recommendation accompanied by **six explanation
   surfaces**:
   - **Top reasons** — the highest-impact positive and negative factors per career
   - **Head-to-head** — what differentiates the #1 from #2
   - **Counterfactuals** — minimal profile changes that would flip the recommendation
   - **Tradeoffs** — rules that simultaneously favor one career and penalize another
   - **Heat map** — qualitative GREEN/YELLOW/RED confidence band per career
   - **Alternatives** — hybrid roles, dark-horse options, weak-match warnings

## 3. How this satisfies the course requirements

The course syllabus and project handout call out specific properties an
automated decision system should have. Each one is addressed below.

### 3.1 "Use one of the techniques discussed in the course"

The system uses **three** of the suggested techniques from the project handout:

- **Rule-based reasoning** (handout: *"Build a rule base expert system"*).
  Forty-six skill/interest/style/goal/experience/constraint rules and
  eighteen extended/compound rules, each with a typed condition and a
  weighted-effect dict. A small DSL (`any_skill`, `all_skills`,
  `lacks_skill`, `has_interest`, `has_work_style`, `has_constraint`,
  `has_experience_in`, `goal_mentions`, `either`) keeps rule definitions
  declarative and easy to inspect.

- **Option generation** (handout: *"Option generation: if a or b, why not
  c?"*). When the top two careers fall within `close_threshold` of each
  other, the system surfaces a curated **hybrid role** for the pair (e.g.
  SWE + DS → "ML Engineering"; SWE + PM → "Technical Product Manager"). It
  also flags **dark-horse careers** (high positive evidence held back by
  penalties) and **weak-match warnings** when even the top option scores
  below `weak_threshold`.

- **Qualitative arithmetic / heat-map summary** (handout: *"Qualitative
  arithmetic — when is a number a 'good number' or a 'bad number'?"* and
  the equity-portfolio example: *"summary heat map analysis (Green,
  Yellow, Red) indicating the risk level of the portfolio"*). The
  numeric per-career score is collapsed into a **GREEN / YELLOW / RED**
  confidence band via thresholds calibrated against the sample profiles
  (GREEN ≥ 10, YELLOW ≥ 5, RED < 5). Every recommendation in
  `explain_top` is annotated inline with its band, and `heat_map(scores)`
  renders the full picture: which careers are GREEN, which are YELLOW,
  which are RED. An all-RED heat map is the system saying *"the profile
  doesn't yet give enough signal for any of these careers"* — a single
  qualitative summary that the numeric scores alone do not convey.

### 3.2 "The program's ability to explain its decision is a grading criterion"

This is the central design goal of the project. Each rule firing produces a
structured `RuleFiring` record containing the rule, a `Match` object with
`evidence` (human-readable strings naming the exact profile attributes
that triggered the rule), and per-career contributions. The explanation
engine reads this trace and produces:

- `explain_top(...)`: positive and negative factors per career, sorted by
  contribution magnitude, each annotated with the underlying evidence.
- `head_to_head(a, b, firings)`: subtracts contributions and surfaces the
  rules that most strongly differentiate two careers.
- `counterfactuals(profile, scores)`: searches the space of single-attribute
  perturbations (boosting one skill at a time, removing one constraint at
  a time) and reports any change that would shift the top recommendation.
- `detect_tradeoffs(firings)`: identifies rules with simultaneous positive
  and negative effects.

This contrasts directly with neural-network classifiers, which can only be
made interpretable through *post-hoc* methods like LIME or SHAP. Here the
explanation **is** the model — there is nothing to approximate after the
fact.

### 3.3 "Your project should run in the zoo"

The core engine (`advisor/`) and the **interactive command-line interface**
(`python -m advisor`) use **only the Python standard library**, so the
system runs on the zoo with no setup. The notebook walkthrough additionally
requires `jupyter` and `ipywidgets`, both standard in the zoo's Jupyter
environment. No custom libraries needed clearance from the TF.

The CLI is the system's primary live-demo entry point — it walks the user
through inputs in five small chunks (technical skills, non-technical skills,
interests, work style, constraints, goals), then runs the full pipeline.
This lets a grader test the system with their own profile in under a minute,
which is the most direct demonstration that the project is genuinely an
automated *decision* system rather than a static notebook.

### 3.4 "Include a write-up explaining your project, including how to run it"

This file plus `README.md` cover the write-up. The `career_advisor.ipynb`
notebook is fully executed with output baked in so a grader can read it
top-to-bottom without running anything.

## 4. What is interesting / important about it

Three things make this project worth submitting beyond "a thing that
returns a ranked list."

### 4.1 The constraint-flips-the-recommendation case

The `consulting_candidate` sample has strong communication skills, a stated
goal of consulting, **and** a `no_relocation` constraint. The system ranks
**Product Management above Consulting** because the relocation constraint
penalizes consulting, where jobs cluster in a few major cities. Counterfactual
analysis then says: *if you removed the no_relocation constraint, the
recommendation would shift back to consulting.* This is the kind of insight
a black-box recommender would hide — the user gets the full picture and
can decide for themselves whether to relax the constraint.

### 4.2 The compound-rule case

Compound rules like `ml_plus_systems` (fires only when the user has both
machine learning ≥ 3 *and* system design ≥ 3) recognize career fits that
single-attribute matching would miss. For the `swe_candidate` profile
(strong SWE skills + ML basics + systems depth + "start a company" goal),
the system surfaces **ML Engineering** as the top recommendation —
correctly identifying a synthesis that an attribute-by-attribute scorer
would miss. The decision trace then shows exactly which compound rules
fired and why.

### 4.3 The weak-match honesty case

The `early_career_candidate` profile is intentionally underspecified:
beginner Python, one interest, one constraint, no experience. Rather than
recommending the highest-scoring career as if it were a confident pick, the
system flags this with a **`WEAK MATCH` warning**: *"even the top option
scores only +2.00 — the profile may need more skill or experience signal
before any of these careers becomes a strong fit."* Counterfactual analysis
then doubles as **career guidance**: it lists the specific skills that, if
developed, would most change the picture.

## 5. How the system explains its decisions (deep dive)

### 5.1 Data structures

```python
@dataclass
class Match:
    strength: float          # 0..1 — scales the rule's effects
    evidence: list[str]      # human-readable triggers (e.g. "python: 5/5")

@dataclass
class Rule:
    id: str
    description: str         # surfaced verbatim in explanations
    condition: Callable      # Profile -> Optional[Match]
    effects: dict[str, float]  # career_id -> base weight

@dataclass
class RuleFiring:
    rule: Rule
    match: Match
    contributions: dict[str, float]  # career_id -> weight * strength
```

Every score is the sum of some `RuleFiring.contributions`. Every contribution
points back to a `Rule` (with description) and a `Match.evidence` list
(with the triggering attributes). There is no path from a number on screen
to a black box — every step is named, typed, and inspectable.

### 5.2 Counterfactual generation

Counterfactuals are computed by **search**, not by gradient: the engine
tries individually boosting each of ten "common" skills to level 4 and
removing each constraint, re-scores under each perturbation, and reports
any case where the top-1 recommendation changes. Because scoring runs in
sub-millisecond time, brute-force search is fast enough that no
approximation is needed.

The output naturally serves two distinct purposes depending on the
profile:

- For strong, well-supported profiles (e.g. `research_candidate`), the
  engine reports that **no small change would flip the recommendation** —
  this is a robustness signal.
- For weak or borderline profiles, the engine lists the specific
  perturbations that would change the answer — these double as
  actionable advice.

### 5.3 Head-to-head comparison

Subtracting contribution dicts isolates *only* the rules that distinguish
two careers. A rule that boosts both SWE and PM equally drops out; a rule
that boosts SWE +3 and PM 0 surfaces with a delta of +3 favoring SWE.
The result is a sorted, signed list of distinguishing factors — usually
3–8 items, easy to read.

## 6. Implementation notes

- **Language:** pure Python (3.x). The core engine has zero non-stdlib
  dependencies; the notebook needs only `jupyter`.
- **Layout:** see `README.md` for the file tree.
- **Tests:** `tests/test_engine.py` (20 tests, runs in <10 ms with
  `python -m unittest tests.test_engine`). Covers structural invariants
  (no rules with impossible conditions, ≥45% sample-profile coverage),
  per-profile sanity rankings, all four explanation modes producing
  non-trivial output, alternative-engine triggers, counterfactual
  robustness, and score reproducibility.
- **Rule base:** 64 rules, organized into seven thematic blocks
  (skill-driven, interest-driven, work-style, experience, goal-driven,
  constraint-driven, and extended/compound). Each rule has a unique ID
  and a human-readable description that is surfaced verbatim in
  explanations.
- **Sample profiles:** five profiles in `sample_profiles/profiles.py`,
  each designed to exercise a different decision scenario (clean SWE
  fit, robust research fit, constraint-driven demotion,
  skills-vs-preferences conflict, weak-match warning).

## 7. Limitations and future work

- **Rule weights are hand-set.** With user-feedback data they could be
  fit empirically — but doing so without losing explainability would
  require a constrained learner (e.g. monotone GBMs).
- **Goal matching is keyword-based, not semantic.** Goals are matched by
  literal substrings — e.g. `goal_high_salary` fires on the keywords
  `"high salary"`, `"high pay"`, `"compensation"`, `"high comp"`. A user
  who writes *"financial freedom"* will not trigger this rule, even
  though the intent is the same. Discovered when testing the system
  against a real user profile in the live CLI: the user's goals
  *"financial freedom"* and *"job security"* fired no goal-rules at all,
  silently weakening the recommendation. Fixing this without losing
  explainability would mean either expanding the keyword lists or
  layering a small intent-classifier on top — both straightforward but
  out of scope for a one-week build.
- **No cross-temporal reasoning.** The system makes a single point-in-time
  recommendation; it does not model the user's career trajectory or
  account for how their profile would evolve.
- **Career catalog is fixed at 13 paths.** Adding a new career means
  adding new rule effects to existing rules.
- **The user profile is structured input.** Real users would type free
  text; the project does not include a general NLP layer to parse free
  text into a `UserProfile` — the goal-matching keyword limitation above
  is one consequence of this.

The primary scope choice was depth of explanation over breadth of
domain. Adding more careers, more rules, semantic goal-matching, or a
free-text input layer are all straightforward extensions.

## 8. Summary

The project implements an explainable career recommendation system with a
64-rule rule base, five explanation modes, and an option-generation layer.
It runs on the Zoo using only the Python standard library, ships with a
20-test suite, and demonstrates three substantive capabilities — surfacing
hidden constraints, recognizing compound profile patterns, and warning
honestly about weak-signal inputs — that distinguish it from a
keyword-matching quiz on one side and a black-box ML classifier on the
other.
