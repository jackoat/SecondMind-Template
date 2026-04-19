---
name: wiki-lint
description: "Health check GitHub/Notion wiki. Find orphan pages, dead wikilinks, stale claims, missing cross-references, frontmatter gaps."
allowed-tools: GitHub Contents API, Notion API, GreP
---

# wiki-lint: Wiki Health Check for GitHub/Notion

Run lint after every 10-15 ingests, or weekly. Create Notion report.

---

# Lint Checks

Work through these in order:

1. **Orphan pages**: Notion pages with no inbound links
2. **Dead links**: Wikilinks referencing non-existent Notion pages
3. **Stale claims**: Old Notion pages contradicted by newer GitHub sources
4. **Missing pages**: Entities/concepts mentioned but no Notion page
5. **Missing cross-references**: Entities mentioned but not linked
6. **Frontmatter gaps**: Missing type, status, created, updated, tags
7. **Empty sections**: Headers with no content
8. **Stale index entries**: Notion index pointing to renamed/deleted pages

---

# Lint Report (Notion/Markdown hybrid)

Create at Notion: `/wiki/meta/lint-report-{{YYYY-MM-DD}}.md`

Format:
```
---
type: meta
title: "Lint Report {{YYYY-MM-DD}}"
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
tags: [meta, lint]
status: developing
---

# Lint Report: {{YYYY-MM-DD}}

# Summary
- GitHub pages scanned: N
- Notion pages scanned: N
- Issues found: N
- Auto-fixed: N
- Needs review: N

# Orphan Pages (Notion)
- Notion /Page Name: no inbound links

# Dead Links (GitHub wiki/)
- Notion [[Missing Page]]: referenced in GitHub file but doesn't exist

# Missing Pages (Notion)
- "concept name": mentioned in GitHub and Notion pages

# Frontmatter Gaps (GitHub wiki/)
- GitHub wiki/Page.md: missing fields: status, tags

# Stale Claims (Notion)
- Notion /Page Name: claim "X" may conflict with newer GitHub source

# Cross-Reference Gaps
- {{Entity Name}} mentioned in GitHub wiki/ without wikilink
```

---

# Naming Conventions

| Element | Convention | Example |
|---|---|---|
| File Names | Title Case | `Machine Learning.md` |
| Folders | lowercase-dashes | `wiki/data-models/` |
| Tags | lowercase-hierarchy | `#domain/architecture` |
| Wikilinks | match filename exactly | `[[Machine Learning]]` |
| Notion Page Titles | Match file names | `Machine Learning` |

---

# Dataview Dashboard (Notion)

Create Notion database query:

```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15

LIST FROM "wiki" WHERE status = "seen" SORT updated ASC

LIST FROM "/wiki/entities" WHERE !sources OR sources.length = 0

LIST FROM "wiki/questions" WHERE answer_quality = "draft" SORT created DESC
```

---

# Before Auto-Fixing

Show lint report first. Ask: "Should I fix these automatically or review?"

Safe to auto-fix:
- Adding missing frontmatter fields
- Creating stub Notion pages
- Adding wikilinks

Needs review:
- Deleting orphan pages
- Resolving contradictions
- Merging duplicate Notion pages