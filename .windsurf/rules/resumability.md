---
trigger: always_on
---

## Resumability

Goal: this project must be resumable after weeks or months with zero prior context.

### After every non-trivial change, update docs

- `documentation/adr/` — why a decision was made, what alternatives were considered, tradeoffs
- `documentation/changelog/` — what changed, one line per item
- `documentation/docs/` — how-to guides and technical references

### ADR rules

- Filename format: `YYYY-MM-DD-short-description.md`
- Body must include a `**Date:**` field
- Answer: what problem, why this solution, what alternatives, what's next

### Changelog rules

- One line per change, prefixed with `Added:`, `Changed:`, `Fixed:`, `Removed:`, or `Note:`
- No `###` subheadings inside a version block
- No implementation details — those belong in ADRs
- Bad: "Refactored the token service to use a new internal helper that calls the refresh endpoint"
- Good: "Changed: token auto-refresh now uses a 5-minute safety window"

### General

- Keep README up to date with links to docs
- Use TODO comments with reasons: `# TODO: add caching — currently ~600ms per request`
- If stopping mid-feature, add a note in `documentation/docs/` describing partial progress