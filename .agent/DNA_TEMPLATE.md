# Forensic Root Cause Analysis & Process Discovery Protocol

**Document Version:** [VERSION]  
**Last Updated:** [DATE]  
**Author:** [OWNER]

---

## Executive Summary

This document defines the comprehensive forensic root cause analysis and process discovery methodology used throughout the SecondMind framework. It provides systematic approaches to analyzing system behavior, identifying patterns, and generating actionable insights from operational data.

---

## Table of Contents

1. Overview
2. Core Principles
3. Process Discovery Protocol Components
4. Forensic Root Cause Analysis Methodology
5. Memory Integration
6. System Integration Patterns
7. Sanitized Example Workflows
8. Troubleshooting and Diagnostics
9. Revision History

---

## 1. Overview

### 1.1 Purpose

This protocol provides a structured methodology for:
- Discovering and documenting system processes automatically
- Performing forensic analysis of system behavior
- Generating actionable insights from operational data
- Integrating with external knowledge systems

### 1.2 Scope

This protocol covers:
- Automated process discovery from user activity
- Root cause analysis of detected issues
- Pattern identification and correlation
- Knowledge extraction and documentation

### 1.3 Target Audience

This document is intended for:
- System operators
- Sub-agents
- Automation engineers
- Knowledge architects

---

## 2. Core Principles

### 2.1 Systematic Observation

**Purpose:** Ensure comprehensive data collection across all relevant sources without distortion.

- Observe system behavior, user interactions, and operational patterns
- Capture raw data with minimal preprocessing
- Maintain data integrity through collection-to-storage pipeline
- Document observation methodology and scope

### 2.2 Truthful Representation

**Purpose:** Represent collected information faithfully without alteration or bias.

- Preserve original context and meaning of observations
- Avoid interpretive overlay during storage
- Maintain audit trail of data transformations
- Flag assumptions separately from observed facts

### 2.3 Contextual Preservation

**Purpose:** Retain metadata and contextual information essential for meaningful retrieval.

- Store temporal, spatial, and situational metadata
- Link related observations through explicit relationship markers
- Preserve conversation and interaction threads intact
- Maintain provenance chains

### 2.4 Non-Intervention

**Purpose:** Operate as passive observer rather than active participant in system dynamics.

- Do not modify external systems during observation
- Use read-only operations where possible
- Document any necessary interventions separately
- Minimize observation footprint

---

## 3. Process Discovery Protocol Components

### 3.1 Data Collection Layer

The process discovery protocol begins with comprehensive data collection from multiple sources:

#### 3.1.1 Primary Sources

1. **Task Execution Logs**
   - Capture all task start/completion events
   - Record execution timestamps and durations
   - Store input/output parameters
   - Track success/failure states

2. **Memory Access Patterns**
   - Monitor episodic memory queries
   - Log retrieval frequencies and patterns
   - Track memory aging and updates
   - Record deletion operations

3. **System Interactions**
   - Document external system API calls
   - Store response times and status codes
   - Track authentication and authorization events
   - Log error conditions and retries

#### 3.1.2 Collection Frequency

- **Real-time events:** Immediate capture with event IDs
- **Periodic snapshots:** Every 15 minutes for state analysis
- **End-of-session summaries:** Complete execution trail

### 3.2 Analysis Pipeline

#### 3.2.1 Pattern Detection

The protocol identifies recurring patterns through:

1. **Temporal Analysis**
   - Identify time-of-day dependencies
   - Detect periodic execution cycles
   - Correlate with calendar events if available
   - Flag anomalies in expected patterns

2. **Causal Chain Reconstruction**
   - Map trigger → action → outcome sequences
   - Identify branching conditions
   - Document conditional paths taken
   - Record decision points and criteria

3. **Resource Utilization Profiling**
   - Track system resource usage patterns
   - Identify bottlenecks and constraints
   - Correlate with performance metrics
   - Flag resource contention events

#### 3.2.2 Process Classification

Processes are classified into categories:

| Category | Description | Discovery Method |
|----------|-------------|------------------|
| Linear | Sequential, predictable | Direct observation |
| Conditional | Branching based on criteria | Path tracing |
| Iterative | Repetitive with variations | State tracking |
| Event-driven | Triggered by external events | Event correlation |
| Background | Continuous operation | Monitoring |

### 3.3 Output Generation

#### 3.3.1 Process Documentation

Each discovered process generates:

1. **Process Definition**
   - Human-readable description
   - Input/output specifications
   - Expected behaviors
   - Failure modes

2. **Execution Flowchart**
   - Visual representation of process flow
   - Decision points clearly marked
   - Error handling paths included
   - Termination conditions defined

3. **Metadata Package**
   - Discovery timestamp
   - Confidence scores
   - Alternative paths identified
   - Edge cases noted

---

## 4. Forensic Root Cause Analysis Methodology

### 4.1 Analysis Framework

The forensic root cause analysis follows a structured approach:

#### 4.1.1 Initial Assessment

1. **Incident Identification**
   - Document the observed anomaly or failure
   - Capture timestamp and scope
   - Record immediate impact assessment
   - Identify affected components

2. **Data Harvesting**
   - Collect all relevant logs and metrics
   - Preserve system state (where possible)
   - Snapshot active processes and connections
   - Archive memory state indicators

#### 4.1.2 Temporal Reconstruction

1. **Timeline Construction**
   - Build chronological event sequence
   - Include pre-incident baseline
   - Mark incident onset clearly
   - Document recovery actions

2. **Correlation Analysis**
   - Cross-reference with external events
   - Identify concurrent system activities
   - Map dependency relationships
   - Note environmental changes

#### 4.1.3 Cause Identification

1. **Direct Cause Determination**
   - Identify the immediate trigger
   - Document the failure mechanism
   - Establish causation chain
   - Verify with evidence

2. **Root Cause Discovery**
   - Apply "5 Whys" methodology
   - Trace to systemic issues
   - Identify contributing factors
   - Document fundamental cause

3. **Validation**
   - Cross-check findings with data
   - Verify causation vs correlation
   - Test hypothesis if possible
   - Document confidence level

### 4.2 Analysis Artifacts

#### 4.2.1 Root Cause Report Structure

```
ROOT CAUSE ANALYSIS REPORT
==========================

Incident: [INCIDENT_ID]
Date: [DATE]
Analyst: [OWNER]

## Executive Summary
[Brief description of incident and root cause]

## Timeline
[Chronological event sequence]

## Direct Cause
[Immediate cause of failure]

## Root Cause
[Fundamental systemic issue]

## Contributing Factors
[List of secondary factors]

## Impact Assessment
[Scope and severity of impact]

## Corrective Actions
[Steps to prevent recurrence]

## Recommendations
[Broader improvements suggested]

## Appendix
[Raw data, logs, supporting evidence]
```

#### 4.2.2 Evidence Package

For each analysis, maintain:
- Raw log files (unchanged)
- Extracted relevant entries
- Annotated timeline
- System snapshots
- Correlation diagrams

---

## 5. Memory Integration

### 5.1 Storage Architecture

The protocol integrates with the memory system through:

#### 5.1.1 Episodic Memory Integration

Process discovery data is stored in episodic memory structure:

- **Location:** [MEMORY_PATH]
- **Format:** Structured JSON with timestamps
- **Indexing:** By process ID, timestamp, and tags
- **Retention:** Configurable based on policy

#### 5.1.2 Semantic Memory Integration

Discovered patterns are stored in semantic memory:

- **Format:** Conceptual relationships
- **Links:** To episodic instances
- **Inference:** Pattern-based queries
- **Aggregation:** Statistical summaries

#### 5.1.3 Procedural Memory Integration

Learned processes update procedural knowledge:

- **Automation:** Reusable process templates
- **Optimization:** Refined execution flows
- **Learning:** Success/failure patterns
- **Adaptation:** Context-aware behavior

### 5.2 Memory Management

#### 5.2.1 Update Triggers

Memory updates occur on:
- New process discovery
- Process evolution detected
- Pattern confidence thresholds met
- Root cause analysis completion

#### 5.2.2 Data Lifecycle

1. **Creation:** Initial capture in ephemeral storage
2. **Processing:** Analysis and structuring
3. **Storage:** Commit to permanent memory
4. **Aging:** Gradual priority reduction
5. **Retention:** Policy-based archiving or deletion

---

## 6. System Integration Patterns

### 6.1 External System Integration

The protocol integrates with multiple external systems:

#### 6.1.1 [SYSTEM_A] Integration

**Purpose:** Repository and version control management

- **Operations:**
  - File operations (create, update, delete)
  - Branch and reference management
  - Pull request creation and monitoring
  - Issue tracking and assignment
  - Branch protection and workflow approvals

- **Authentication:** OAuth or personal access tokens
- **Rate Limiting:** Respect API quotas
- **Error Handling:** Retry with backoff strategies

#### 6.1.2 [SYSTEM_B] Integration

**Purpose:** Document storage and collaboration

- **Operations:**
  - File upload and synchronization
  - Folder management
  - Sharing and permission settings
  - Version history tracking
  - Real-time collaboration monitoring

- **Authentication:** OAuth 2.0
- **Sync Strategy:** Change detection and incremental sync
- **Conflict Resolution:** Timestamp-based with manual override option

#### 6.1.3 [SYSTEM_C] Integration

**Purpose:** Knowledge base and task management

- **Operations:**
  - Page creation and updates
  - Database record management
  - Template-based content generation
  - Relation and link management
  - Property and metadata management

- **Authentication:** API keys or OAuth
- **Caching:** Local cache with TTL strategy
- **Sync:** Bidirectional with conflict resolution

### 6.2 Integration Architecture

#### 6.2.1 Adapter Pattern

Each external system has an adapter that:
- Normalizes operations to standard interface
- Handles authentication and headers
- Manages rate limiting and quotas
- Logs all operations for audit

#### 6.2.2 Event-Driven Integration

Systems communicate through:
- Webhooks for real-time updates
- Polling for status checks
- Message queue for async processing
- Event forwarding for correlation

---

## 7. Sanitized Example Workflows

### 7.1 Example: [TASK_NAME]

**Purpose:** Demonstrate process discovery and analysis

#### 7.1.1 Initial State

User initiates request to [TASK_NAME].

#### 7.1.2 Observed Flow

1. **Trigger Detection**
   - Timestamp: [DATE]T[TIME]
   - Source: [SYSTEM_A] webhook
   - Event type: issue_closed

2. **Data Collection**
   - Retrieved issue data from [SYSTEM_A]
   - Queried related PRs and branches
   - Collected commit information

3. **Analysis**
   - Identified completion criteria
   - Mapped to knowledge requirements
   - Generated summary extract

4. **Storage**
   - Created episodic record in [MEMORY_PATH]
   - Updated semantic relationships
   - Indexed for retrieval

5. **Output**
   - Generated summary report
   - Notified user via [SYSTEM_C]
   - Created follow-up tasks as needed

#### 7.1.3 Discovered Patterns

- Common trigger: Issue closure
- Typical duration: 2-5 seconds
- Dependencies: [SYSTEM_A] API access
- Success rate: 98.7%

---

### 7.2 Example: [TASK_NAME]

**Purpose:** Demonstrate root cause analysis

#### 7.2.1 Incident Description

Process failed with error code E-402.

#### 7.2.2 Analysis Process

1. **Evidence Collection**
   - Raw logs preserved
   - System state captured
   - Memory snapshot taken

2. **Timeline Reconstruction**
   - T+0: Request initiated
   - T+1: API call failed
   - T+2: Retry attempt 1
   - T+5: Retry attempt 2 failed
   - T+6: Error raised

3. **Root Cause**
   - **Direct:** API rate limit exceeded
   - **Root:** Insufficient token scope for operations
   - **Contributing:** Caching layer not utilized

4. **Corrective Action**
   - Update token permissions
   - Implement caching for repeated queries
   - Add rate limit awareness

#### 7.2.3 Lessons Learned

- Always validate token scope before operations
- Implement caching for read-heavy tasks
- Add exponential backoff for retries
- Document failure modes for each integration

---

## 8. Troubleshooting and Diagnostics

### 8.1 Common Issues

#### 8.1.1 Discovery Not Triggering

**Symptoms:** Process logs empty, no data captured

**Troubleshooting:**
1. Verify webhook endpoints are active
2. Check authentication tokens
3. Confirm API permissions
4. Review event subscription settings

#### 8.1.2 Analysis Latency

**Symptoms:** Delayed processing, timeout errors

**Troubleshooting:**
1. Check system resource utilization
2. Verify queue depth
3. Review batch size configurations
4. Analyze data volume patterns

#### 8.1.3 Data Inconsistency

**Symptoms:** Conflicting information, missing records

**Troubleshooting:**
1. Verify data pipeline integrity
2. Check for concurrent modifications
3. Review locking mechanisms
4. Validate checksums and hashes

### 8.2 Diagnostic Commands

```bash
# Check discovery status
/agent status discovery

# View recent process discoveries
/memory list recent --type=process

# Analyze specific incident
/followup incident [INCIDENT_ID]

# Generate analysis report
/report root-cause [INCIDENT_ID]
```

---

## 9. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| v920 | [DATE] | [OWNER] | Initial creation of Process Discovery Protocol |
| v921 | [DATE] | [OWNER] | Added Forensic Root Cause Analysis section |

---

## Appendix A: API Reference

### A.1 Collection Endpoints

- `POST /collect/task` - Capture task execution
- `POST /collect/memory` - Log memory operations
- `POST /collect/system` - Record system events

### A.2 Analysis Endpoints

- `GET /analysis/patterns` - Retrieve discovered patterns
- `POST /analysis/root-cause` - Submit for analysis
- `GET /analysis/report/[ID]` - Retrieve analysis results

### A.3 Storage Endpoints

- `POST /memory/episodic` - Store episodic data
- `POST /memory/semantic` - Update semantic relations
- `POST /memory/procedural` - Update procedural knowledge

---

## Appendix B: Data Schema

### B.1 Process Record Schema

```json
{
  "_schema_version": "921",
  "process_id": "proc-uuid",
  "name": "human-readable-name",
  "triggers": ["event-1", "event-2"],
  "steps": ["step-1", "step-2"],
  "outputs": {"type": "schema-reference"},
  "created_at": "ISO-8601-timestamp",
  "updated_at": "ISO-8601-timestamp",
  "confidence": 0.95,
  "source_data": ["data-reference"]
}
```

### B.2 Incident Record Schema

```json
{
  "_schema_version": "921",
  "incident_id": "inc-uuid",
  "timestamp": "ISO-8601-timestamp",
  "severity": "low|medium|high|critical",
  "description": "incident-description",
  "root_cause": "root-cause-description",
  "corrective_actions": ["action-1"],
  "status": "open|investigating|resolved|closed",
  "analyst": "analyzer-identifier"
}
```

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| Process Discovery | Automatic identification and documentation of system processes |
| Root Cause Analysis | Systematic investigation to identify fundamental causes of issues |
| Episodic Memory | Time-stamped event records with contextual data |
| Semantic Memory | Conceptual knowledge and relationships |
| Procedural Memory | Learned actions and automation patterns |
| Adapter | Abstraction layer for external system integration |

---

## Document Control

**Classification:** Internal  
**Distribution:** Authorized personnel  
**Retention:** 7 years  
**Review Cycle:** Quarterly

**End of Document**
