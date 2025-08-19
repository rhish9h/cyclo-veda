---
trigger: always_on
---

# 🧠 Resumability Guidelines

**Goal**: Ensure that this project can be resumed after long gaps (weeks or months) *without requiring prior context or re-reading the entire codebase*.

---

## ✅ General Rule

- Assume Future You (or any engineer) has **zero context**.
- For every non-trivial change, update the documentation with **context and rationale**.

---

## 📁 Documentation Structure

| Folder | Purpose |
|-------|---------------------------------------------|
| `documentation/adr/` | Architectural decisions and rationale (**include a date in each ADR**) |
| `documentation/changelog/` | Chronological list of meaningful changes |
| `documentation/docs/` | General technical/usage docs and guides |

> 💡 ADR filenames should start with the date, and the ADR body should include a `**Date:**` field for clarity, e.g.  
> `2025-08-18-use-authlib-for-oidc.md`

---

## 🔧 For Every Feature or Refactor

Before finishing a task, answer the following:

- What problem is being solved?
- Why was this solution chosen?
- What alternatives/tradeoffs were considered?
- What could be improved in the future?

➡ Add these answers to the appropriate documentation location (`adr`, `changelog`, or `docs`).

---

## 🚨 Examples

| ✅ Good | ❌ Bad |
|------------------|----------------|
| “Use AuthLib to replace custom OIDC validator (simplifies token handling).” | “Refactored API” |
| `[2025-08-18] Added retry logic for external API to handle intermittent failures.` | “Fixed bug” |

---

## 💡 Tips

- Keep **README** up to date with links to relevant documentation.
- If stopping mid-feature, add a `docs/resume-guide.md` that describes partial progress.
- Use TODO comments **with reasons** (e.g., `# TODO: add caching – requests ~600ms`).

---

*“Write as if future you is a new hire.”*