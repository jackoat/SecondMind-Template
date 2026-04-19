---
name: wiki-ingest
description: "Ingest sources into GitHub/Notion wiki. Reads from GitHub .raw/, creates Notion pages, cross-references, logs operations."
allowed-tools: GitHub Contents API, Notion API, WebFetch, GreP
---

# wiki-ingest: Source Ingestion to GitHub/Notion

Read the source from GitHub .raw/, write to Notion wiki. Cross-reference everything.

---

# Delta Tracking (GitHub manifest)

Check `.raw/.manifest.json` in GitHub repo to avoid re-processing:

```bash
# Check manifest from GitHub
GET /repos/jackoat/SovereignSecondMind/contents/.raw/.manifest.json
```

**Manifest format:**:
```json
{
  "sources": {
    ".raw/articles/article-slug-2026-04-08.md": {
      "hash": "abc123",
      "ingested_at": "2026-04-08",
      "notion_pages_created": ["wiki/sources/article-slug", "wiki/entities/Person"],
      "notion_pages_updated": ["wiki/index"]
    }
  }
}
```

**Process**:
1. Get manifest from GitHub
2. Compute hash: `md5sum [file]` or `sha256sum`
3. Check if hash exists in manifest
4. If matches, skip
5. If not, proceed with ingest

---

# URL Ingestion

Trigger: user passes URL `https://domain.com/article`

Steps:
1. Fetch page using WebFetch
2. Derive slug from URL path
3. Save to GitHub `.raw/articles/[slug]-{{YYYY-MM-DD}}.md` with:
   ```markdown
   ---
   source_url: {{url}}
   fetched: {{YYYY-MM-DD}}
   ---
   ```
4. Commit to GitHub
5. Proceed with single source ingest

---

# Single Source Ingest to GitHub + Notion

Steps:
1. **Read** source from GitHub `.raw/` using GitHub Contents API
2. **Discuss** key takeaways with user
3. **Create source summary** in Notion as page under `/wiki/sources/`
4. **Create or update** entity pages in Notion (people, orgs, products)
5. **Create or update** concept pages in Notion
6. **Update** Notion domain pages and their `_index` sub-pages
7. **Update** Notion `/wiki/overview` if big picture changed
8. **Update** Notion `/wiki/index` (master catalog)
9. **Update** Notion `/wiki/hot` with ingest context
10. **Append to Notion `/wiki/log`** (new entries at top):
   ```
   ## {{YYYY-MM-DD}} ingest | Source Title
   - Source: .raw/filename.md
   - Summary: Wiki Page Name
   - Pages created: Page 1, Page 2
   - Pages updated: Page 3
   - Key insight: One sentence
   ```
11. **Check contradictions** - flag if new info conflicts with existing Notion pages
12. **Update GitHub manifest** with new entries

---

# Batch Ingest (multiple sources)

Steps:
1. List all sources from GitHub `.raw/`
2. Confirm with user
3. Process each source (single ingest flow)
4. After all: cross-reference pass between new sources
5. Update Notion index, hot, log once at end
6. Report: "Processed N sources. Created X Notion pages, updated Y Notion pages."

---

# Token Disciplina

- Read Notion `/wiki/hot` first (~500 tokens)
- Read Notion `/wiki/index` to find existing pages (~1000 tokens)
- Read only 3-5 Notion pages per ingest
- Use PATCH for surgical edits
- Keep wiki pages short (100-300 lines)

---

# Contradictions in Notion

When new info contradicts existing Notion page:

On existing Notion page, add callout:
```
> [contradiction] Conflict with [Source Name]
[Existing Page] claims X. [New Source] says Y.
Needs resolution.
```

On new source summary, reference:
```
> [contradiction] Contradicts [Existing Page]
This source says Y, but wiki says X.
```

---

# What Not to Do

- Do not modify anything in GitHub `.raw/`
- Do not create duplicate Notion pages
- Do not skip the log entry
- Do not skip hot cache update