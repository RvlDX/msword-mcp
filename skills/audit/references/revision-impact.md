# Revision Impact Review

Compare the manuscript before and after revision. A change in one section can leave old numbers, terms, methods, problem statements, or conclusions in other sections.

```bash
python skills/audit/scripts/revision_impact.py old.md new.md
python skills/audit/scripts/revision_impact.py old-workspace new-workspace --output impact.md
```

Procedure: (1) compare questions, objectives, scope, methods, samples/materials, indicators, results, and conclusions; (2) check each candidate old number/acronym; (3) check sections that depend on the changed sections; (4) re-run the audit on the affected sections; (5) keep the IDs of unresolved root causes; (6) record new findings. A repeated value is only a candidate, not automatically an error.
