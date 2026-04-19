# SECONDMIND‑TEMPLATE — Blueprints for the People

> An OS for building your own sovereign system of thought. 👠🛡️⚖️

*Not a product you buy. A template you fill.*

---

## 🧭 THE WHY

*The world is an ocean of noise. Most people drift. SecondMind is the raft you build yourself.*

**SOVEREIGNTY** — Your thoughts, your data, your system. No vendor lock‑in. No black boxes. No surrender of agency. This is the third way between a private vault and an open post.

**OCEAN OF NOISE** — We are drowning in content that asks us to be consumers, not builders. This project is an alternative operating system for life: think, choose, assemble.

**AN OS FOR LIFE** — Not a note‑taking app. Not a task manager. A meta‑framework that helps you connect memory, memory‑to‑action, and action‑to‑meaning. You provide the marrow; we gave the bones.

---

## ⚙️ THE HOW

### 3‑Layer Memory Architecture

Build your personal intelligence in three complementary layers:

| Layer | Purpose | Format | Example |
|-------|---------|--------|---------|
| **Episodic** | Raw experience — logs, captures, moments | Chronological notes, journals, snapshots | Daily logs, meeting notes, photo captions, voice transcripts |
| **Semantic** | Knowledge — concepts, rules, maps | Structured references, ontologies, mappings | Topic pages, SOPs, glossaries, project charts |
| **Working** | Action — current decisions, experiments, drafts | Tasks, checklists, canvases, WIPs | Current sprints, research questions, A/B tests |

**Rule:** Capture in Episodic. Distill to Semantic. Execute in Working.

### The 8 Mandates

These are the core principles that keep the system honest:

1. **Own the data** — You control exports, backups, and platform choice.
2. **Write plainly** — Clarity beats cleverness; write for a future stranger.
3. **Small steps beat big plans** — Micro‑actions compound faster than epics.
4. **Memory is a muscle** — You must practice retrieval, not just capture.
5. **Context before tools** — Choose tools to fit your reasoning, not the reverse.
6. **Iterate publicly (when useful)** — Transparent builds teach and attract help.
7. **Delete deliberately** — Pruning is as important as adding.
8. **Ship something** — If you don't ship, it's not systems work, it's hoarding.

### Process Discovery Protocol (PDP)

When you don't know how to proceed, follow this loop:

1. **Capture** → Grab the raw event/idea (Episodic).
2. **Clarify** → Ask: What is this about? What outcome do I want?
3. **Classify** → Tag it: Episodic/Semantic/Working, plus domain tags.
4. **Connect** → Link to related items (past memories, current tasks).
5. **Act** → Create small, concrete next steps in Working.
6. **Review** → Revisit weekly; convert recurring actions into systems.
7. **Distill** → Turn proven routines into Semantic references (SOPs).
8. **Archive** → Move completed or dormant items out of Working.

Use PDP when stuck, when overwhelmed, or to rebuild a messy folder.

---

## 🏗️ ARCHITECTURE: Steel / Soul / Bones

A resilient life system uses three domains. This template is designed to integrate with them.

| Layer | Name | Tech | Role |
|-------|------|------|------|
| **Steel** | Persistence, access control, audit | GitHub (repos, issues, PRs, Actions) | Stores knowledge as versioned files; enforces guardrails via CI and reviews. |
| **Soul** | Experience, meaning, human layer | Notion / paper journal / voice | The place where you think, reflect, and connect ideas. |
| **Bones** | Medium‑sized assets, media, documents | Google Drive / Dropbox | Images, PDFs, datasets, templates, large binaries. |

**How they fit:**

- GitHub is the "source of truth" for your knowledge base and SOPs (Markdown files).
- Notion is your thinking board where you do the work before committing to code/docs.
- GitHub Actions enforce formatting, naming, and checklist requirements.
- Drive holds the binaries that GitHub doesn't love (large media, PDFs).
- Cross‑links: GitHub → Drive via shortlinks; Notion → GitHub via links to files/PRs.

### Why This Mix?

- **Not vendor‑dependent:** If one service becomes toxic, you can export and rebuild.
- **Layered resilience:** Loss of Soul doesn't mean loss of Steel; loss of Bones is survivable if Steel has the links.
- **Human‑first:** The hard part isn't storage; it's attention, memory, and discipline. This architecture supports those.

---

## 🚀 QUICK START (Start here)

1. **Star ⭐ this repo** so you can find it easily.

2. **Fork → Create your own copy**  
   Click "Fork" on GitHub. Rename to `SecondMind-<yourname>` (optional) to personalize.

3. **Set up the 3 lanes**  
   - **GitHub:** Keep this repo as your canonical knowledge store.  
   - **Notion:** Create a "SecondMind" workspace; paste your thinking here first. Link to GitHub docs.  
   - **Drive:** Create folder `2nd_mind_assets` for media and docs to reference from Markdown.

4. **Initialize your folders (create these in the repo root):**  
   - `00_INBOX/` — Raw captures going to Semantics or Episodic  
   - `01_EPISODIC/` — Journals, logs, meeting notes (date‑prefixed)  
   - `02_SEMANTIC/` — Concepts, SOPs, maps  
   - `03_WORKING/` — Active projects, tasks, experiments  
   - `09_ARCHIVE/` — Completed or dormant items  
   - `DOCS/` — This template's documentation and PDP notes

5. **Add your first items (minimal viable system):**

   - `01_EPISODIC/YYYY-MM-DD-notes.md` (daily log)  
   - `02_SEMANTIC/NOTES-GUIDE.md` (your writing rules)  
   - `03_WORKING/Current-Sprint.md` (3‑item max list of current focus)

6. **Enable GitHub Actions** if you forked. They will run checks on push/PR.

7. **Run PDP once a week** on your Working lane. Prune old tasks, promote learnings to Semantic.

8. **Optional: Add a Notion sync checklist** in `03_WORKING/` to track your manual reviews.

> You now have a skeleton. Fill it with your life over weeks.

---

## ⚠️ DISCLAIMER — TEMPLATE ≠ PRODUCT

*This is a scaffold, not a finished product. There is no support ticket. No onboarding call. No promise.*

- You must **build the marrow**: write the notes, do the reviews, delete the clutter.
- You must **own the plumbing**: backups, export routines, access management.
- You must **adapt the model**: change folder names, PDP steps, or workflows to fit your brain.
- **No guarantees.** If files disappear or services change, you fix it.

This template is released to help you **start**. Mastery comes from **doing**, not downloading.

---

## 🔐 SECURITY NOTES

Follow these to keep your system safe and portable:

- **Enable 2FA** on all accounts (GitHub, Notion, Drive) and use a password manager.
- **Never commit secrets** (API keys, tokens, passwords) to this repo. Use environment variables or secure vaults.
- **Export regularly** — monthly zips to an external drive or secure backup service.
- **Audit collaborators** — treat access like a key ring; remove old keys.
- **Use分支 protection** on sensitive branches (`main`, `secure`) via branch rules.
- **Pin critical dependencies** in CI workflows; don't use `latest` tags.
- **Log out of shared devices** and review active sessions quarterly.
- **Plan for vendor lock‑in** — keep at least one Markdown export copy outside the primary tool.

If a secret leaks, revoke immediately and rotate. Assume breach is a question of when, not if.

---

## 🤝 CONTRIBUTING

We appreciate experiments, patches, and real‑world reports. Use this process:

1. **Open an issue** describing the change or problem (keep it brief and kind).
2. **Fork the repo** and create a branch: `feat/description` or `fix/description`.
3. **Make minimal changes** with clear commit messages (subject <50 chars; body explains why).
4. **Run checks** (CI runs on PR); fix any failures.
5. **Open a PR** with title referencing the issue. Link the issue number.
6. **Wait for review** — small teams; respond promptly.

**What we look for:**
- Clarity, not bravado.
- Small, reversible changes.
- Documentation updates are encouraged.

**What we don't want:**
- Large refactors without discussion.
- Breaking the default folder structure without strong justification.
- Adding features that break the 3‑layer model.

**License:** See LICENSE file for terms. By contributing, you license your changes under the same terms.

---

## 🧩 EMBLEM

*The symbol of what this stands for:*

- 👠 **Heel** — Stand upright. Assert your presence in the world.
- 🛡️ **Shield** — Protect your mind, data, and boundaries.
- ⚖️ **Scales** — Balance capture vs. action, privacy vs. openness, depth vs. speed.

We build **with dignity**, not fear.

---

## 📚 FURTHER READING & LINKS

- PDP (Process Discovery Protocol) — see `DOCS/PDP.md` if created locally  
- Memory Layer Deep Dive — you can adapt this template's pages to your Notion  
- Notion→GitHub patterns — link your Notion pages to this repo via relative Markdown links

---

**Built for people who want agency over their attention.**  
**Your life is too important to outsource to a tool.** 👠🛡️⚖️
