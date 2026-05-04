# Career Decision Support System

Final project for CS 4580/5580 — Automated Decision Systems. A Python
program that recommends careers from a user's profile (skills, interests,
work style, goals, constraints) and explains why. Rule-based — every
recommendation traces back to specific rules and the specific profile
attributes that triggered them. No black box.

The full write-up is in [`PROJECT.md`](PROJECT.md).

## Quick start

```bash
python3 -m advisor                  # interactive prompts
python3 -m advisor --preset swe     # run a sample profile
python3 -m advisor --list           # list all 9 sample profiles
```

Or open the notebook:
```bash
jupyter notebook career_advisor.ipynb
```

## What's where

```
advisor/                  rule engine, scoring, explanations
sample_profiles/          9 example user profiles
tests/                    test suite (run: python3 -m unittest tests.test_engine)
career_advisor.ipynb      notebook walkthrough (executed, outputs included)
PROJECT.md                project write-up
docs/screenshots/         6 screenshots of the notebook
```

## Zoo compatibility

The CLI and engine use only the Python standard library. The notebook
needs `jupyter` and `ipywidgets`, both standard in the Zoo's Jupyter
environment.

## Tests

```bash
python3 -m unittest tests.test_engine
```

27 tests, runs in under 10ms.

## Screenshots

In [`docs/screenshots/`](docs/screenshots/):
1. System overview (13 careers, 64 rules)
2. Rule base grouped by category
3. SWE candidate — top 3 with `[GREEN]/[YELLOW]` band tags
4. Research candidate — counterfactual reports the recommendation is robust
5. Consulting candidate — `no_relocation` constraint flips the ranking
6. Confidence heat map (qualitative GREEN/YELLOW/RED summary)
