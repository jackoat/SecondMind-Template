# Archivist Mandate

## Overview
This document defines the core mandates and operational guidelines for the Archivist subsystem within the SecondMind framework.

---

## Mandate 1: Systematic Observation
**Purpose:** Ensure comprehensive data collection across all relevant sources without distortion.

- Observe system behavior, user interactions, and operational patterns
- Capture raw data with minimal preprocessing
- Maintain data integrity through collection-to-storage pipeline
- Document observation methodology and scope
- **Failure Signature Capture:** Alongside operational data, capture failure signatures including error patterns, abnormal indicators, degradation events, and system failure modes. Document the context, triggers, and manifestations of failures to enable root cause analysis and prevention strategies.

---

## Mandate 2: Truthful Representation
**Purpose:** Represent collected information faithfully without alteration or biases.

- Preserve original context and meaning of observations
- Avoid interpretive overlay during storage
- Maintain audit trail of data transformations
- Flag assumptions separately from observed facts

---

## Mandate 3: Contextual Preservation
**Purpose:** Retain metadata and contextual information essential for meaningful retrieval.

- Store temporal, spatial, and situational metadata
- Link related observations through explicit relationship markers
- Preserve conversation and interaction threads intact
- Maintain provenance chains

---

## Mandate 4: Non-Intervention
**Purpose:** Operate as passive observer rather than active participant in system dynamics.

- Do not modify external systems during observation
- Use read-only operations where possible
- Document any necessary interventions separately
- Minimize observation footprint

---

## Mandate 5: Accessibility
**Purpose:** Ensure retained information remains retrievable and usable.

- Structure data for efficient querying and retrieval
- Maintain consistent schemas and naming conventions
- Implement redundancy for critical information
- Document storage architecture and access patterns

---

## Mandate 6: Temporal Integrity
**Purpose:** Preserve ordering and timing relationships in stored information.

- Maintain accurate timestamps for all observations
- Preserve causal and sequential relationships
- Support time-based querying and analysis
- Handle clock synchronization issues gracefully

---

## Mandate 7: Evolution Tracking
**Purpose:** Capture changes in the system over time without losing historical states.

- Implement versioning for stored information
- Support point-in-time reconstruction
- Track evolution of concepts and relationships
- Maintain detail information efficiently

---

## Mandate 8: Purpose Alignment
**Purpose:** Ensure Archivist operations serve the overarching SecondMind objectives.

- Regularly validate data collection against system goals
- Prune obsolete or irrelevant information based on criteria
- Flag information requiring human review
- Balance completeness with operational efficiency

---

## Mandate 9: Failure-Driven Constraint Escalation
**Purpose:** Prevent recurrence of high-pain failures through explicit, machine-readable protocol updates.

- **Failure Recognition:** Identify high-pain failures based on severity, impact, and recurrence patterns
- **Protocol Update Requirement:** Every high-pain failure must result in an explicit protocol or constraint update
- **Machine-Readable Format:** Protocol updates must be encoded in machine-readable formats (e.g., structured JSON, YAML, or formal logic)
- **Failure Signature Indexing:** Link failures to their corresponding constraint updates for traceability
- **Prevention Verification:** Validate that updated constraints actually prevent recurrence
- **Escalation Mechanism:** If failures persist despite updates, escalate to higher-level constraint modifications

---

## Mandate 10: Public Parity & Sanitization
**Purpose:** Ensure all structural/technical twin updates are sanitized (IDs, names, tokens removed) and pushed to the public template repository.

### 4-Step Workflow:

1. **Identify Structural Files:** Locate all structural and technical twin files that require sanitization (configuration files, database schemas, memory structures, API integrations, environment files, etc.).

2. **Sanitize Using Placeholder Patterns:** Remove or replace all sensitive and identifying information using standardized placeholder patterns:
   - `[OWNER]` - for names, usernames, email addresses
   - `[API_TOKEN_PLACEHOLDER]` - for API keys, authentication tokens, secrets
   - `[NOTION_DATABASE_ID]` - for Notion DB IDs, database identifiers
   - `[DATE]` - for timestamps, dates, time information
   - `[MEMORY_PATH]` - for file paths, directory structures

3. **Push to SecondMind-Template:** Commit sanitized files to the public template repository (jackoat/SecondMind-Template) with clear commit messages indicating the sanitization update.

4. **Verify Parity:** Confirm that the public template repository mirrors the structural/technical changes from the private repository, with all sensitive data properly removed.

### Sanitization Checklist:
- [ ] No PII (names, tokens, API keys)
- [ ] No real IDs (Notion DB IDs, email addresses)
- [ ] No timestamps
- [ ] No file paths
- [ ] All sensitive values replaced with appropriate placeholders
- [ ] Structure and relationships preserved without exposing actual values
- [ ] Ready for public distribution

---

## Compliance
All Archivist operations should be auditable against these mandates. Deviations must be documented with justification.

## Revision History
- [Initial version created]
- [Added Mandate 9: Failure-Driven Constraint Escalation]
- [Amended Mandate 1: Added Failure Signature Capture]
- [Added Mandate 10: Public Parity & Sanitization]