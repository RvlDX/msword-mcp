# Research Audit Schema

Copy the `audit.json.template` in the workspace to `audit.json`, then fill it in after the reviewer has read `manuscript_numbered.md` in full. The validator checks structure and quotes, not academic correctness.

All `RC01`–`RC10` checks are required, with status `found`, `not_found`, `not_assessable`, or `not_applicable`. `found`/`not_found` require coverage `full`, `partial`, or `limited`. `not_assessable` must name the missing input. All checks must include `basis`.

Findings must include: `id`, `check`, `title`, `severity`, `status`, `confidence`, `location.line`, `quote`, `problem`, `impact`, and `recommendation`. Optional: `related_sections`, `evidence_needed`, `reviewers`.

- Severity: `critical`, `major`, `moderate`, `minor`.
- Finding status: `confirmed`, `likely`, `potential`.
- Confidence: `high`, `medium`, `low`.
- Critical requires confirmed + high. Major may not be potential.
- Quote must be at least 8 characters and must appear in `manuscript.md`.
- Finding IDs must be unique and stable while the same root cause remains.
- A check with status `found` must have at least one valid finding; other statuses must have no findings.

Example structure: see the `audit.json.template` created by `prepare_research_audit.py`.
