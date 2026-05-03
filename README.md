# Explainable Career Decision Support System

Final project for **CS 4580/5580 — Automated Decision Systems**.
An automated decision system that recommends career paths from a structured
user profile, written in pure Python (stdlib only — Jupyter is the only
non-stdlib dependency, for the notebook walkthrough).

The system's defining property is that **every recommendation is fully
explainable**: scores trace back to specific rules, and rules trace back to
specific profile attributes. There is no black box.

## What the system does

1. Takes a `UserProfile` containing technical skills, non-technical skills,
   interests, work experience, work-style preferences, short-term and long-term
   goals, and practical constraints.
2. Runs a rule base (~40 rules across skills, interests, work styles, goals,
   experience, and constraints) and produces a per-career score.
3. Outputs a **ranked recommendation** with:
   - the top positive factors (with the evidence that triggered them)
   - the top negative factors
   - **head-to-head** comparison: which factors push #1 above #2
   - **counterfactuals**: minimal profile changes that would flip the ranking
   - **tradeoffs**: rules that simultaneously favor one career and penalize another
   - **alternatives**: hybrid roles, dark-horse options, weak-match warnings

## Why this counts as automated decision-making

The project implements two of the techniques discussed in the course:

- **Rule-based reasoning** — a hand-authored rule base with conditions and
  weighted effects. Every rule firing is structured (`Match` + `RuleFiring`
  records) so the decision trace can be reconstructed after the fact.
- **Option generation** — when the top recommendation is weak, conflicted,
  or nearly tied with the runner-up, the system actively proposes hybrid
  paths, dark-horse careers, or guidance on what to develop.

The explanation engine adds counterfactual generation, head-to-head
comparison, and tradeoff detection on top of that.

## How to run

### In Jupyter (preferred — matches professor's preference)

```bash
pip install jupyter
jupyter notebook career_advisor.ipynb
```

The notebook walks through five sample profiles and a custom-input cell.
Outputs are pre-rendered so it can also be read top-to-bottom without
running.

### From a Python REPL or script

```python
from advisor import score, explain_top, alternatives, counterfactuals
from sample_profiles import swe_candidate

profile = swe_candidate()
scores, firings = score(profile)
print(explain_top(scores, firings, top_n=3))
print(alternatives(profile, scores, firings))
print(counterfactuals(profile, scores))
```

### Zoo compatibility

The core engine uses only the Python standard library, so `import advisor`
works on the zoo with no setup. The notebook walkthrough requires `jupyter`,
which is already available in the zoo's standard environment.

## Project layout

```
automated-decisions-final-project/
├── career_advisor.ipynb        # Main walkthrough notebook
├── advisor/
│   ├── profile.py              # UserProfile dataclass
│   ├── careers.py              # Career catalog (13 paths)
│   ├── rules.py                # Rule base (~40 rules) + DSL helpers
│   ├── scoring.py              # Rule-firing + score aggregation
│   ├── explanation.py          # Top-reasons / head-to-head / counterfactuals / tradeoffs
│   └── alternatives.py         # Option generation (hybrids, dark horses, weak match)
├── sample_profiles/
│   └── profiles.py             # Five sample profiles for demonstration
├── requirements.txt
└── README.md
```

## How the system explains its decisions

Each `Rule` declares a `condition` (a callable that returns either `None` or
a `Match` object) and a dict of `effects` mapping career IDs to weights.
When a rule fires, it produces a `RuleFiring` record containing:

- the rule's human-readable description
- the `Match` object's `evidence` list (e.g. `["python: 5/5", "java: 4/5"]`)
- the per-career contributions (`weight × match.strength`)

Aggregation is just `sum(contribution for firing in firings if career in firing)`.
Because every step is structured data, the explanation engine can:

- **Rank positive vs. negative factors** for any career (`explain_top`).
- **Compute the difference** in contributions between two careers and surface
  the top distinguishing rules (`head_to_head`).
- **Search for minimal perturbations** to the profile that would change the
  top recommendation, by re-running the engine on perturbed copies
  (`counterfactuals`).
- **Identify rules with simultaneous positive and negative effects**
  (`detect_tradeoffs`).

This contrasts directly with neural-network classifiers, which can only
explain themselves through post-hoc methods like LIME or SHAP. Here the
explanation *is* the model.

## Five sample profiles

The notebook walks through:

| Profile | Designed to demonstrate |
|---|---|
| `swe_candidate` | Clean SWE / founder fit with a close-call between top two |
| `research_candidate` | Robust top recommendation (counterfactuals find no flip) |
| `consulting_candidate` | A constraint (no relocation) overrides a stated goal |
| `conflicted_candidate` | Skills and stated preferences point different directions |
| `early_career_candidate` | Weak-match warning + counterfactuals as career guidance |

## Scope

This is an individual project. Focus is on a working, fully explainable
prototype with a clear reasoning process — not a large dataset or
predictive black-box model.
