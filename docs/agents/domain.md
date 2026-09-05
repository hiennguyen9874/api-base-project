# Domain Docs

How engineering skills should consume this repository's domain documentation.

## Before exploring, read these

- `CONTEXT-MAP.md` at the repository root. It points to a `CONTEXT.md` for each relevant context.
- Relevant context ADRs, such as `api/docs/adr/` or `web/docs/adr/`.
- `docs/adr/` for system-wide decisions.

If these files do not exist, proceed silently. The `/domain-modeling` skill creates them when terms or decisions are actually resolved.

## File structure

```text
/
├── CONTEXT-MAP.md
├── docs/adr/                 ← system-wide decisions
├── api/
│   ├── CONTEXT.md
│   └── docs/adr/             ← API-specific decisions
└── web/
    ├── CONTEXT.md
    └── docs/adr/             ← web-specific decisions
```

## Use the glossary's vocabulary

When naming a domain concept in an issue, proposal, hypothesis, or test, use the term defined in the relevant `CONTEXT.md`. If a needed term is absent, reconsider whether existing terminology applies or note the gap for `/domain-modeling`.

## Flag ADR conflicts

Explicitly surface output that contradicts an ADR rather than silently overriding it.
