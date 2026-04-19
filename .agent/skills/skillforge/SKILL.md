# SkillForge - Create New Skills for the Agent (UPDATED WITH SELF-REWRITE PROTOCOL)

# Overview

SkillForge is the meta-skill that allows Aisling Protocol to create, test, and deploy new skills automatically. It follows a strict 6-step process ensuring every new skill is validated before activation.

# Self-rewrite Protocol Template

# Overview

All skills **MUST** include this self-rewrite protocol to enable compound interest evolution. It ensures skills evolve after:
- Every 5 successful uses (optimization)
- Any failure with pain_score > 5 (immediate correction)

The protocol activates **ONLY** when evidence is clear (no guesses).

---

# The 5-Step Self-rewrite Process

# # Step 1: Read Memory (Read AGENT_LEARNINGS.jsonl)

**Purpose:** Gather all failure/usage data for the skill

**Actions:**
```python
learnings = load_jsonl(".agent/memory/episodic/AGENT_LEARNINGS.jsonl")
filter(learning for learning in learnings if learning["skill_name"] == "current_skill")
```

**Output:** All failure and success events for the skill

---

# # Step 2: Read Knowledge (Read KNOWLEDGE.md)

**Purpose:** Load current skill knowledge and procedures

**Actions:**
```python
current_knowledge = Path(".agent/skills/{skill_name}/KNOWLEDGE.md")
knowledge_base = current_knowledge.read_text()
```

**Output:** Current skill knowledge (procedures, examples, patterns)

---

# # Step 3: Check Patterns

**Purpose:** Identify patterns that require evolution

**Actions:**
1. **Analyze failures:** Group by error_type, calculate pain_scores
2. **Count usage:** Total successful uses since last rewrite
3. **Check thresholds:**
   - `usage_count >= 5` 4⁠†‡ optimization trigger
   - `pain_score > 5` 4⁠†‡ immediate correction trigger
   - `failure_count >= 3 in 14_days` 4⁠†‡ rewrite_priority trigger

**Pattern Detection:**
```python
if usage_count >= 5 and recent_failures == 0:
    # Optimization: add efficiency improvements
elif pain_score > 5:
    # Emergency: fix critical bug
elif failure_count >= 3:
    # Structural rewrite: fundamental redesign
```

**Output:** Determined rewrite type (optimization, correction, or structural rewrite)

---

# # Step 4: Update Manifest & Procedures

**Purpose:** Apply changes to skill implementation

# ## 4a. Append Lessons to KNOWLEDGE.md

**Location:** End of KNOWLEDGE.md

**Template:**
```markdown
---
# Lessons Learned: {date}

**Pattern:** {identified pattern from failures}

**Insight:** {what we learned from this failure}

**Solution:** {how we fixed it}

**Validation:** {tests added to confirm fix}

**Effectiveness:** {observed improvement after fix}
```

# ## 4b. Update `_index.md` with new constraints (if needed)

**Location:** `_.index.md` in skill folder

**Template:**
```markdown
- **Constraints:** {updated constraints list including new lessons learned}
- **Status:** active | rewrite_priority | deprecated
- **Version:** {increment version} (e.g., v1.2.0 4⁠†‡ v1.3.0)
```

# ## 4c. Update `_manifest.jsonl` with new triggers (if needed)

**Location:** `.agent/skills/_manifest.jsonl`

**Template:**
```json
{
  "name": "{skill_name}",
  "triggers": {updated trigger list},
  "constraints": {updated constraints},
  "version": "{new_version}",
  "last_updated": "{timestamp}"
}
```

# ## 4d. Update Procedures in `execute.py`

**Location:** `.agent/skills/{skill_name}/execute.py`

**Template:**
```python
# Updated procedures based on lessons learned
# {new_version}: {change description}

def new_improved_procedure(context):
    """Implementation based on lessons learned"""
    # Apply the insight from pattern analysis
    pass
```

---

# # Step 5: Escalate & Commit

**Purpose:** Promote changes to production

**Actions:**
1. **Validate Changes:** Run tests to confirm fix works
2. **Update _manifest.jsonl:** Register new version
3. **Commit to Git:**
    ```bash
    git add .
    git commit -m "refactor({skill_name}): self-rewrite after {usage_count} uses - v{new_version}"
    git push origin main
    ```
4. **Notify User:** "Skill {skill_name} self-rewrite after {usage_count} uses, version {new_version}"

**Example Commit Message:**
```
refactor(memory-manager): self-rewrite after 5 successful uses - v1.3.0

- Added memory capacity monitoring (>200 lines threshold)
- Improved archival safety (never delete without archive first)
- Updated constraints: 3-strike rewrite rule
- Added lessons from AGENT_LEARNINGS.jsonl
- Tests: 85% coverage (up from 80%)
```

---

# When to Trigger Self-Rewrite

# # Optimization Trigger (Every 5 Uses)

**Condition:** Skill has been used successfully 5+ times since last rewrite

**Action:** Improve efficiency, add features, optimize code

**Example:**
```
Skill: api-safeguard
Uses: 7 times
Pattern: Repeated validation errors on edge cases
Trigger: Optimization (efficiency improvement)
```

# # Correction Trigger (Any Failure with pain > 5)

**Condition:** Single failure with pain_score > 5

**Action:** Emergency fix immediately

**Example:**
```
Skill: deploy-checklist
Failure: Deployed without validation
Pain: 9 (critical production issue)
Trigger: Immediate correction
```

# # Structural Rewrite Trigger (3+ Failures in 14 Days)

**Condition:** 3+ failures within 14-day window

**Action:** Fundamental redesign of skill logic

**Example:**
```
Skill: debug-investigator
Failures: 4 in 10 days
Pain: Avg 7.5
Trigger: Structural rewrite
```

---

# Evidence Requirements

**The protocol activates ONLY when evidence is clear:**

1. **Clear Failure Pattern:** 3+ failures in AGENT_LEARNINGS.jsonl with same error_type
2. **Clear Usage Count:** 5+ successful uses tracked in Episodic.jsonl
3. **Clear Pain Threshold:** pain_score > 5 in at least one failure event
4. **Clear Time Window:** Failures within 14-day window

**No Evidence** 4⁠†‡ No Rewrite

**Example:**
```
👍 Evidence exists: 3 failures, same error_type, pain > 7, within 14 days
4⁠†‡ No evidence: 1 failure, pain = 3, last seen 30 days ago (ignore for now)
```

---

# Template for KNOWLEDGE.md Lessons Section

Always append new lessons at the end of KNOWLEDGE.md:

```markdown
---
# Lessons Learned: 2026-04-17

**Pattern:** Validation errors on API endpoints with missing fields

**Insight:** API safeguard wasn't generating required field validation in OpenAPI spec

**Solution:** Added schema validation to POST/PUT endpoints

**Validation:** 
- New test: test_missing_field_rejection()
- Coverage increased from 80% to 85%

**Effectiveness:** 0 validation errors since fix (was 3 before)

**Code Change:** 
- File: `.agent/skills/api-safeguard/execute.py`
- Lines modified: 12
- Functions added: `validate_required_fields()`, `generate_field_validation()`
```

---

# Versioning Convention

**Semantic Versioning** for all skills:

- **MAJOR** (v2.0.0): Breaking changes (skill behavior changed)
- **MINOR** (v1.1.0): New features (backward compatible)
- **PATCH** (v1.0.1): Bug fixes (backward compatible)

**Self-rewrite triggers version increment:**
- Optimization 4⁠†‡ PATCH (v1.0.0 4⁠†‡ v1.0.1)
- Correction 4⁠†‡ PATCH (v1.0.0 4⁠†‡ v1.0.1)
- Structural Rewrite 4⁠†‡ MINOR (v1.0.0 4⁠†‡ v1.1.0) or MAJOR if breaking

---

# Integration Points

# # Connector Integration

```python
def check_skill_rewrite_status(skill_name):
    """Called by conductor before skill execution"""
    learnings = load_recent_learnings(skill_name, days=14)
    usage_count = count_successful_uses(skill_name)
    
    if len(learnings) >= 3:
        return "rewrite_priority"
    elif usage_count >= 5:
        return "optimization_ready"
    else:
        return "active"
```

# # Git Integration

```bash
# Auto-commit after self-rewrite
git add .agent/skills/{skill_name}/
git commit -m "refactor({skill_name}): self-rewrite after {usage_count} uses - v{new_version}"
git push origin main
```

# # Memory Integration

- **Episodic.jsonl:** Track all successes/failures for usage count
- **AGENT_LEARNINGS.jsonl:** Source for failure patterns
- **Lessons.md:** Append pattern insights as new sections
- **WORKSPACE.md:** Log rewrite timestamp

---

# Failure Modes

# # 1. False Positive Rewrite

**Error:** Skill rewrites when no pattern exists

**Fix:**
- Don't commit rewrite (rollback Git)
- Add more data before triggering
- Set `evidence_threshold` higher (e.g., 5 failures instead of 3)

# # 2. Missed Rewrite

**Error:** Skill has clear pattern but doesn't rewrite

**Fix:**
- Lower evidence threshold
- Add manual override: user can trigger rewrite
- Log missed trigger to workspace for review

# # 3. Version Confusion

**Error:** Multiple skills rewriting simultaneously, version conflicts

**Fix:**
- Process rewrites sequentially (one at a time)
- Document all changes in commit messages
- Use feature branches for rewrites to avoid merge conflicts

---

# Next Steps

After completing self-rewrite:

1. 👍 Append lessons to KNOWLEDGE.md
2. 👍 Update _manifest.jsonl with new version and constraints
3. 👍 Update _index.md (human-readable registry)
4. 👍 Run tests to confirm fix works
5. 👍 Commit to Git with detailed message
6. 👍 Notify user of successful self-rewrite
7. 👍 Log rewrite event to Episodic.jsonl

EOT
