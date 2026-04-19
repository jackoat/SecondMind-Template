---
name: wiki-query
description: "Answer questions using GitHub/Notion wiki. Reads from Notion hot cache and index, then relevant pages. Synthesizes with citations. Files answers to Notion."
allowed-tools: GitHub Contents API, Notion API, GreP
---

# wiki-query: Query the GitHub/Notion Wiki

The wiki has already done synthesis work. Read strategically, answer precisely, file answers to Notion.

---

# Query Modes

| Mode | Trigger | Reads | Token cost | Best for |
|---|---|---|---|---|
| **Quick** | `quick: ...` or simple factual Q&A | hot.md + index.md only | ~1,500 | Quick facts |
| **Standard** | default (no flag) | hot.md + index + 3-5 Notion pages | ~3,000 | Most questions |
| **Deep** | `deep: ...` or thorough, comprehensive | Full wiki + optional web | ~8,000+ | Comparisons, synthesis |

---

# Quick Mode

1. Read Notion `/wiki/hot` page
2. If it answers, respond immediately
3. If not, read Notion `/wiki/index` page
4. If found in index summary, respond
5. If not found, say "Not in quick cache. Run as standard query?"

Do not read individual Notion pages in quick mode.

---

# Standard Query Workflow

1. **Read** Notion `/wiki/hot` first
2. **Read** Notion `/wiki/index` to find relevant pages
3. **Read** those Notion pages
4. **Synthesize** answer in chat with citations: `(Source: Notion page name)`
5. **Offer to file** answer to Notion: "Should I save as Notion page `wiki/questions/answer-name`?"
6. If reveals **gap**, say "I don't have enough on X. Want to find a source?"

---

# Deep Mode

1. Read Notion `/wiki/hot` and `/wiki/index`
2. Identify all relevant sections
3. Read every relevant Notion page
4. If wiki coverage is thin, offer web search
5. Synthesize comprehensive answer with full citations
6. Always file result to Notion page

---

# Token Discipline

| Start with | Cost | When to stop |
|---|---|---|
| Notion `/wiki/hot` | ~500 tokens | If it has the answer |
| Notion `/wiki/index` | ~1000 tokens | If you can identify 3-5 pages |
| 3-5 Notion pages | ~300 tokens each | Usually sufficient |
| 10+ Notion pages | expensive | Only for full synthesis |

---

# Filing Answers to Notion

When filing an answer to Notion:

**Notion database properties**:
```yaml
type: question
title: "Short descriptive title"
question: "The exact query as asked"nswer_quality: solid
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
tags: [question, domain]
related:
  - "Notion Page referenced"
sources:
  - "Notion page for source"
status: developing
```

After filing to Notion, append to Notion `/wiki/log`.

---

# Gap Handling

If question cannot be answered from wiki:

1. Say: "I don't have enough in the wiki to answer well."
2. Identify specific gap: "I have nothing on {{subtopic}}"
3. Suggest: Want to find source? I can help search or process one.
4. Do not fabricate. Do not answer from training data for wiki domain.