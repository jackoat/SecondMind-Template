# SkillForge: Self-Recursive Execution Engine
# Version 2.0 - Complete Self-rewrite with AuditTrail
# Author: jackoat
# License: MIT

import os
import sys
import json
import hashlib
import time
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple, Literal, Type
from enum import Enum, auto
from abc import ABC, abstractmethod
from contextlib import contextmanager, nullcontext
from itertools import chain
from collections import defaultdict
import re

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# PII Patterns - initialized at runtime
PII_PATTERNS: Dict[str, re.Pattern] = {}

# Mandate Rules (JSON config loaded at runtime)
MANDATE_RULES: Dict[str, Any] = {}

# Global state
SKILLFORGE_STATE: Dict[str, Any] = {
    'running': False,
    'current_skill': None,
    'execution_count': 0,
    'start_time': None,
    'end_time': None,
}

# =============================================================================
# DATA CLASSES FOR AUDITING AND TRACKING
# =============================================================================

@dataclass
class AuditLogEntry:
    """Single audit log entry for SkillForge operations."""
    timestamp: str
    level: str
    skill_name: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level}: {self.skill_name}.{self.action} - {self.status}"


class MandateViolation(Enum):
    """Types of mandate violations that can occur."""
    SELF_MODIFY_PROTECTED_FILES = auto()
    EXCEED_RESOURCE_LIMITS = auto()
    CIRCULAR_DEPENDENCY = auto()
    UNAUTHORIZED_ACCESS = auto()
    DATA_CORRUPTION = auto()
    SECURITY_BREACH = auto()
    DEADLOCK_DETECTED = auto()
    TIMEOUT_EXCEEDED = auto()
    INVALID_EXECUTION_STATE = auto()
    
    @property
    def severity(self) -> str:
        """Return severity level for this violation type."""
        severities = {
            MandateViolation.SELF_MODIFY_PROTECTED_FILES: "critical",
            MandateViolation.EXCEED_RESOURCE_LIMITS: "high",
            MandateViolation.CIRCULAR_DEPENDENCY: "high",
            MandateViolation.UNAUTHORIZED_ACCESS: "high",
            MandateViolation.DATA_CORRUPTION: "critical",
            MandateViolation.SECURITY_BREACH: "critical",
            MandateViolation.DEADLOCK_DETECTED: "high",
            MandateViolation.TIMEOUT_EXCEEDED: "medium",
            MandateViolation.INVALID_EXECUTION_STATE: "medium",
        }
        return severities.get(self, "unknown")


@dataclass
class Mandate:
    """Defines mandate rules for skill execution."""
    name: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'rules': self.rules,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


@dataclass
class SkillState:
    """Tracks the state of a skill during execution."""
    skill_id: str
    status: str = "idle"  # idle, queued, running, paused, completed, failed, blocked
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    parent_skill: Optional[str] = None
    child_skills: List[str] = field(default_factory=list)
    resources_used: Dict[str, Any] = field(default_factory=dict)
    execution_count: int = 0
    last_run_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionResult:
    """Result of skill execution."""
    skill_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: Optional[float] = None
    output_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PiiSanitizer:
    """Sanitize and mask PII data in strings and dictionaries."""
    
    def __init__(self):
        self.patterns = initialize_pii_patterns()
        self.replacements = {
            'email': '[EMAIL_PLACEHOLDER]',
            'phone': '[PHONE_PLACEHOLDER]',
            'credit_card': '[CREDIT_CARD_PLACEHOLDER]',
            'ssn': '[SSN_PLACEHOLDER]',
            'api_key': '[API_KEY_PLACEHOLDER]',
            'password': '[PASSWORD_PLACEHOLDER]',
            'jwt': '[JWT_PLACEHOLDER]',
        }
    
    def sanitize(self, data: Union[str, Dict[str, Any], List], recursive: bool = True) -> Union[str, Dict, List]:
        """Sanitize PII from data structure."""
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return self._sanitize_dict(data, recursive)
        elif isinstance(data, list):
            return self._sanitize_list(data, recursive)
        else:
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize PII patterns from a string."""
        result = text
        for pii_type, pattern in self.patterns.items():
            if pii_type in self.replacements:
                result = pattern.sub(self.replacements[pii_type], result)
        return result
    
    def _sanitize_dict(self, data: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
        """Sanitize PII from a dictionary."""
        result = {}
        for key, value in data.items():
            if recursive and isinstance(value, (str, dict, list)):
                result[key] = self.sanitize(value, recursive)
            elif isinstance(value, str):
                result[key] = self._sanitize_string(value)
            else:
                result[key] = value
        return result
    
    def _sanitize_list(self, data: List, recursive: bool = True) -> List:
        """Sanitize PII from a list."""
        return [self.sanitize(item, recursive) for item in data]


class AuditTrail:
    """Centralized audit logging system."""
    
    def __init__(self, log_file: Optional[str] = None, level: str = "INFO"):
        self.log_file = log_file or ".agent/skills/skillforge/audit.log"
        self.level = level
        self.logger = logging.getLogger('SkillForge.AuditTrail')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.entries: List[AuditLogEntry] = []
        self.max_entries = 10000
    
    def log(self, skill_name: str, action: str, details: Dict[str, Any], 
            status: str = "pending", error: Optional[str] = None,
            user_id: Optional[str] = None, request_id: Optional[str] = None) -> AuditLogEntry:
        """Create and store an audit log entry."""
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            level=self.level,
            skill_name=skill_name,
            action=action,
            details=details,
            status=status,
            error=error,
            user_id=user_id,
            request_id=request_id,
        )
        
        self._log_to_file(entry)
        self._store_entry(entry)
        return entry
    
    def _log_to_file(self, entry: AuditLogEntry):
        """Log entry to file using logger."""
        log_msg = f"{entry.skill_name}.{entry.action} - {entry.status}"
        if entry.error:
            log_msg += f" [ERROR]: {entry.error}"
        
        if entry.level == "DEBUG":
            self.logger.debug(log_msg)
        elif entry.level == "INFO":
            self.logger.info(log_msg)
        elif entry.level == "WARNING":
            self.logger.warning(log_msg)
        elif entry.level == "ERROR":
            self.logger.error(log_msg)
        elif entry.level == "CRITICAL":
            self.logger.critical(log_msg)
    
    def _store_entry(self, entry: AuditLogEntry):
        """Store entry in memory and trim if needed."""
        self.entries.append(entry)
        while len(self.entries) > self.max_entries:
            self.entries.pop(0)
    
    def get_entries(self, skill_name: Optional[str] = None, 
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   levels: Optional[List[str]] = None) -> List[AuditLogEntry]:
        """Filter and retrieve audit log entries."""
        filtered = self.entries
        
        if skill_name:
            filtered = [e for e in filtered if e.skill_name == skill_name]
        
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
        
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
        
        if levels:
            filtered = [e for e in filtered if e.level in levels]
        
        return filtered
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of audit log."""
        if not self.entries:
            return {
                'total_entries': 0,
                'by_level': {},
                'by_skill': {},
                'by_status': {},
            }
        
        by_level = defaultdict(int)
        by_skill = defaultdict(int)
        by_status = defaultdict(int)
        
        for entry in self.entries:
            by_level[entry.level] += 1
            by_skill[entry.skill_name] += 1
            by_status[entry.status] += 1
        
        return {
            'total_entries': len(self.entries),
            'by_level': dict(by_level),
            'by_skill': dict(by_skill),
            'by_status': dict(by_status),
        }
    
    def clear(self):
        """Clear all stored entries."""
        self.entries.clear()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def initialize_pii_patterns() -> Dict[str, re.Pattern]:
    """Initialize regex patterns for detecting PII."""
    patterns = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'),
        'credit_card': re.compile(r'\b(?:\d{4}[- ]?){4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'api_key': re.compile(r'(?i)(api[_-]?key|apikey|access[_-]?key)\s*[=:]\s*["\']?[A-Za-z0-9]{16,}["\']?'),
        'password': re.compile(r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?.*["\']?'),
        'jwt': re.compile(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
        'private_key': re.compile(r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----.*?-----END (?:RSA |DSA |EC )?PRIVATE KEY-----', re.DOTALL),
        'github_token': re.compile(r'gh[pousr]_[A-Za-z0-9_]{36,}'),
        'slack_token': re.compile(r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*'),
    }
    return patterns


def sanitize_content(content: str, pii_patterns: Optional[Dict[str, re.Pattern]] = None) -> str:
    """Sanitize content by replacing PII patterns with placeholders."""
    if not content or not isinstance(content, str):
        return content
    
    patterns = pii_patterns or initialize_pii_patterns()
    result = content
    
    # Define replacements
    replacements = {
        'email': '[EMAIL_PLACEHOLDER]',
        'phone': '[PHONE_PLACEHOLDER]',
        'credit_card': '[CREDIT_CARD_PLACEHOLDER]',
        'ssn': '[SSN_PLACEHOLDER]',
        'api_key': '[API_KEY_PLACEHOLDER]',
        'password': '[PASSWORD_PLACEHOLDER]',
        'jwt': '[JWT_PLACEHOLDER]',
        'private_key': '[PRIVATE_KEY_PLACEHOLDER]',
        'github_token': '[GITHUB_TOKEN_PLACEHOLDER]',
        'slack_token': '[SLACK_TOKEN_PLACEHOLDER]',
    }
    
    for pii_type, pattern in patterns.items():
        if pii_type in replacements:
            result = pattern.sub(replacements[pii_type], result)
    
    return result


def validate_skill_before_activation(skill_id: str, skill_config: Dict[str, Any], 
                                    audit_trail: AuditTrail) -> Tuple[bool, Optional[str]]:
    """Validate a skill before activation to ensure it meets safety requirements."""
    # Check for protected file modifications
    protected_paths = ['.agent/skills/skillforge/execute.py', '.agent/config/mandates.json']
    
    modifications = skill_config.get('modifications', [])
    for mod in modifications:
        path = mod.get('path', '')
        if any(path.startswith(p) for p in protected_paths):
            error_msg = f"Attempt to modify protected file: {path}"
            audit_trail.log(
                skill_name=skill_id,
                action='validation',
                details={'path': path, 'modifications': modifications},
                status='failed',
                error=error_msg
            )
            return False, error_msg
    
    # Check for circular dependencies
    dependencies = skill_config.get('dependencies', [])
    if skill_id in dependencies:
        error_msg = f"Circular dependency detected for {skill_id}"
        audit_trail.log(
            skill_name=skill_id,
            action='validation',
            details={'dependencies': dependencies},
            status='failed',
            error=error_msg
        )
        return False, error_msg
    
    # Check resource limits
    max_memory_mb = skill_config.get('max_memory_mb', 1024)
    max_duration_minutes = skill_config.get('max_duration_minutes', 60)
    
    if max_memory_mb > 4096:
        error_msg = f"Memory limit {max_memory_mb}MB exceeds maximum 4096MB"
        audit_trail.log(
            skill_name=skill_id,
            action='validation',
            details={'max_memory_mb': max_memory_mb},
            status='failed',
            error=error_msg
        )
        return False, error_msg
    
    if max_duration_minutes > 120:
        error_msg = f"Duration limit {max_duration_minutes}min exceeds maximum 120min"
        audit_trail.log(
            skill_name=skill_id,
            action='validation',
            details={'max_duration_minutes': max_duration_minutes},
            status='failed',
            error=error_msg
        )
        return False, error_msg
    
    # Log successful validation
    audit_trail.log(
        skill_name=skill_id,
        action='validation',
        details={'validated': True, 'dependencies': dependencies},
        status='passed'
    )
    
    return True, None


async def commit_with_message(owner: str, repo: str, branch: str, message: str,
                              files: List[Dict[str, Any]], commit_author: Optional[Dict[str, str]] = None) -> str:
    """Commit files to a repository with a message."""
    # This function would use GitHub API to commit files
    # Placeholder for actual implementation
    commit_sha = hashlib.sha256(f"{message}{time.time()}".encode()).hexdigest()[:40]
    
    return commit_sha


# =============================================================================
# CORE CLASSES
# =============================================================================

class MandateManager:
    """Manages mandate rules and violations."""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.mandates: Dict[str, Mandate] = {}
        self.enabled_mandates: Set[str] = set()
        self.violation_callbacks: List[Callable[[MandateViolation, Dict], None]] = []
    
    def add_mandate(self, mandate: Mandate) -> None:
        """Add a mandate rule."""
        self.mandates[mandate.name] = mandate
        if mandate.enabled:
            self.enabled_mandates.add(mandate.name)
        
        self.audit_trail.log(
            skill_name='MandateManager',
            action='add_mandate',
            details={'mandate_name': mandate.name, 'enabled': mandate.enabled},
            status='success'
        )
    
    def remove_mandate(self, mandate_name: str) -> bool:
        """Remove a mandate rule."""
        if mandate_name in self.mandates:
            del self.mandates[mandate_name]
            self.enabled_mandates.discard(mandate_name)
            
            self.audit_trail.log(
                skill_name='MandateManager',
                action='remove_mandate',
                details={'mandate_name': mandate_name},
                status='success'
            )
            return True
        return False
    
    def enable_mandate(self, mandate_name: str) -> bool:
        """Enable a mandate."""
        if mandate_name in self.mandates:
            self.mandates[mandate_name].enabled = True
            self.enabled_mandates.add(mandate_name)
            return True
        return False
    
    def disable_mandate(self, mandate_name: str) -> bool:
        """Disable a mandate."""
        if mandate_name in self.mandates:
            self.mandates[mandate_name].enabled = False
            self.enabled_mandates.discard(mandate_name)
            return True
        return False
    
    def check_mandates(self, skill_id: str, action: str, context: Dict[str, Any]) -> List[MandateViolation]:
        """Check if an action violates any enabled mandates."""
        violations = []
        
        for mandate_name in self.enabled_mandates:
            mandate = self.mandates[mandate_name]
            for rule in mandate.rules:
                if self._evaluate_rule(rule, action, context):
                    violations.append(MandateViolation(rule['violation_type']))
                    
                    self.audit_trail.log(
                        skill_name=skill_id,
                        action='mandate_check',
                        details={
                            'mandate': mandate_name,
                            'rule': rule['name'],
                            'violation_type': rule['violation_type']
                        },
                        status='violation',
                        error=f"Mandate violation: {rule['name']}"
                    )
        
        return violations
    
    def _evaluate_rule(self, rule: Dict[str, Any], action: str, context: Dict[str, Any]) -> bool:
        """Evaluate a single rule against an action and context."""
        condition = rule.get('condition', '')
        
        # Simple condition evaluation (would be more sophisticated in production)
        if condition == 'modify_protected_file':
            path = context.get('file_path', '')
            protected_paths = ['.agent/skills/skillforge/', '.agent/config/']
            return any(path.startswith(p) for p in protected_paths)
        
        elif condition == 'exceed_memory_limit':
            memory_mb = context.get('memory_mb', 0)
            return memory_mb > rule.get('threshold', 4096)
        
        elif condition == 'exceed_duration_limit':
            duration_minutes = context.get('duration_minutes', 0)
            return duration_minutes > rule.get('threshold', 120)
        
        elif condition == 'circular_dependency':
            skill_id = context.get('skill_id', '')
            dependencies = context.get('dependencies', [])
            return skill_id in dependencies
        
        return False
    
    def register_violation_callback(self, callback: Callable[[MandateViolation, Dict], None]) -> None:
        """Register a callback for mandate violations."""
        self.violation_callbacks.append(callback)
    
    def _trigger_violation_callbacks(self, violation: MandateViolation, context: Dict[str, Any]) -> None:
        """Trigger all registered violation callbacks."""
        for callback in self.violation_callbacks:
            try:
                callback(violation, context)
            except Exception as e:
                self.audit_trail.log(
                    skill_name='MandateManager',
                    action='violation_callback',
                    details={'error': str(e)},
                    status='error',
                    error=str(e)
                )


class ResourceTracker:
    """Tracks resource usage during skill execution."""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.usage: Dict[str, Dict[str, Any]] = {}
        self.limits: Dict[str, Any] = {
            'max_memory_mb': 4096,
            'max_cpu_percent': 100,
            'max_file_operations': 10000,
            'max_api_calls': 1000,
        }
    
    def track_memory(self, skill_id: str, memory_mb: float) -> bool:
        """Track memory usage and check limits."""
        if skill_id not in self.usage:
            self.usage[skill_id] = {'total_memory_mb': 0, 'peak_memory_mb': 0}
        
        self.usage[skill_id]['total_memory_mb'] += memory_mb
        self.usage[skill_id]['peak_memory_mb'] = max(
            self.usage[skill_id]['peak_memory_mb'],
            memory_mb
        )
        
        if memory_mb > self.limits['max_memory_mb']:
            self.audit_trail.log(
                skill_name=skill_id,
                action='resource_check',
                details={'memory_mb': memory_mb, 'limit': self.limits['max_memory_mb']},
                status='warning',
                error='Memory limit exceeded'
            )
            return False
        
        return True
    
    def track_cpu(self, skill_id: str, cpu_percent: float) -> bool:
        """Track CPU usage and check limits."""
        if skill_id not in self.usage:
            self.usage[skill_id] = {'total_cpu_percent': 0, 'peak_cpu_percent': 0}
        
        self.usage[skill_id]['total_cpu_percent'] += cpu_percent
        self.usage[skill_id]['peak_cpu_percent'] = max(
            self.usage[skill_id]['peak_cpu_percent'],
            cpu_percent
        )
        
        if cpu_percent > self.limits['max_cpu_percent']:
            self.audit_trail.log(
                skill_name=skill_id,
                action='resource_check',
                details={'cpu_percent': cpu_percent, 'limit': self.limits['max_cpu_percent']},
                status='warning',
                error='CPU limit exceeded'
            )
            return False
        
        return True
    
    def track_file_operations(self, skill_id: str, operations: int = 1) -> bool:
        """Track file operation count."""
        if skill_id not in self.usage:
            self.usage[skill_id] = {'file_operations': 0}
        
        self.usage[skill_id]['file_operations'] += operations
        
        if self.usage[skill_id]['file_operations'] > self.limits['max_file_operations']:
            self.audit_trail.log(
                skill_name=skill_id,
                action='resource_check',
                details={'file_operations': self.usage[skill_id]['file_operations']},
                status='warning',
                error='File operation limit exceeded'
            )
            return False
        
        return True
    
    def get_usage(self, skill_id: str) -> Dict[str, Any]:
        """Get resource usage for a skill."""
        return self.usage.get(skill_id, {})
    
    def reset(self, skill_id: Optional[str] = None) -> None:
        """Reset resource tracking."""
        if skill_id:
            self.usage.pop(skill_id, None)
        else:
            self.usage.clear()


class DependencyResolver:
    """Resolves and validates skill dependencies."""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.dependencies: Dict[str, Set[str]] = {}
        self.dependents: Dict[str, Set[str]] = defaultdict(set)
    
    def add_dependencies(self, skill_id: str, dependencies: List[str]) -> None:
        """Add dependencies for a skill."""
        self.dependencies[skill_id] = set(dependencies)
        for dep in dependencies:
            self.dependents[dep].add(skill_id)
        
        self.audit_trail.log(
            skill_name=skill_id,
            action='add_dependencies',
            details={'dependencies': dependencies},
            status='success'
        )
    
    def resolve_order(self, skill_id: str) -> List[str]:
        """Resolve execution order for a skill and its dependencies."""
        visited = set()
        execution_order = []
        
        def visit(sid: str):
            if sid in visited:
                return
            visited.add(sid)
            for dep in self.dependencies.get(sid, []):
                visit(dep)
            execution_order.append(sid)
        
        visit(skill_id)
        return execution_order
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return False
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in self.dependencies:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def get_dependents(self, skill_id: str) -> Set[str]:
        """Get all skills that depend on a given skill."""
        return self.dependents.get(skill_id, set())


class StateManager:
    """Manages skill execution state."""
    
    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail
        self.states: Dict[str, SkillState] = {}
        self.skill_definitions: Dict[str, Dict[str, Any]] = {}
    
    def create_skill(self, skill_id: str, definition: Dict[str, Any]) -> None:
        """Create a new skill."""
        self.skill_definitions[skill_id] = definition
        self.states[skill_id] = SkillState(
            skill_id=skill_id,
            status='idle',
            dependencies=definition.get('dependencies', []),
            metadata=definition.get('metadata', {}),
        )
        
        self.audit_trail.log(
            skill_name=skill_id,
            action='create',
            details={'definition': definition},
            status='created'
        )
    
    def update_state(self, skill_id: str, status: str, error: Optional[str] = None) -> None:
        """Update skill state."""
        if skill_id not in self.states:
            raise ValueError(f"Skill {skill_id} not found")
        
        old_status = self.states[skill_id].status
        self.states[skill_id].status = status
        
        if status == 'running':
            self.states[skill_id].started_at = datetime.now().isoformat()
        elif status in ['completed', 'failed']:
            self.states[skill_id].completed_at = datetime.now().isoformat()
            self.states[skill_id].execution_count += 1
            self.states[skill_id].last_run_at = datetime.now().isoformat()
        
        if error:
            self.states[skill_id].error = error
        
        self.audit_trail.log(
            skill_name=skill_id,
            action='state_update',
            details={'old_status': old_status, 'new_status': status},
            status=status,
            error=error
        )
    
    def get_state(self, skill_id: str) -> Optional[SkillState]:
        """Get current state of a skill."""
        return self.states.get(skill_id)
    
    def get_all_states(self) -> Dict[str, SkillState]:
        """Get all skill states."""
        return self.states.copy()
    
    def cleanup(self, skill_id: str) -> None:
        """Clean up skill state after execution."""
        if skill_id in self.states:
            state = self.states[skill_id]
            state.resources_used.clear()
            state.child_skills.clear()
            self.states[skill_id].status = 'idle'


class SkillExecutor:
    """Executes skills with safety checks and resource management."""
    
    def __init__(self, mandate_manager: MandateManager, resource_tracker: ResourceTracker,
                 state_manager: StateManager, audit_trail: AuditTrail):
        self.mandate_manager = mandate_manager
        self.resource_tracker = resource_tracker
        self.state_manager = state_manager
        self.audit_trail = audit_trail
        self.running_skills: Set[str] = set()
    
    async def execute(self, skill_id: str, context: Dict[str, Any] = None) -> ExecutionResult:
        """Execute a skill with full safety checks."""
        context = context or {}
        start_time = time.time()
        
        # Check if skill exists
        if skill_id not in self.state_manager.skill_definitions:
            self.audit_trail.log(
                skill_name='SkillExecutor',
                action='execute',
                details={'skill_id': skill_id},
                status='error',
                error=f"Skill {skill_id} not found"
            )
            return ExecutionResult(
                skill_id=skill_id,
                success=False,
                error=f"Skill {skill_id} not found"
            )
        
        # Update state to running
        self.state_manager.update_state(skill_id, 'running')
        self.running_skills.add(skill_id)
        
        # Check mandates
        violations = self.mandate_manager.check_mandates(
            skill_id, 'execute', {'context': context}
        )
        
        if violations:
            error_msg = f"Mandate violations: {[v.name for v in violations]}"
            self.state_manager.update_state(skill_id, 'failed', error_msg)
            self.running_skills.discard(skill_id)
            
            return ExecutionResult(
                skill_id=skill_id,
                success=False,
                error=error_msg
            )
        
        try:
            # Get skill definition
            skill_def = self.state_manager.skill_definitions[skill_id]
            
            # Simulate execution (would be actual skill code in production)
            await self._execute_skill_def(skill_def, context)
            
            # Success
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            self.state_manager.update_state(skill_id, 'completed')
            self.running_skills.discard(skill_id)
            
            return ExecutionResult(
                skill_id=skill_id,
                success=True,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            error_trace = traceback.format_exc()
            self.state_manager.update_state(skill_id, 'failed', str(e))
            self.running_skills.discard(skill_id)
            
            return ExecutionResult(
                skill_id=skill_id,
                success=False,
                error=str(e),
                error_traceback=error_trace,
                duration_ms=duration_ms
            )
    
    async def _execute_skill_def(self, skill_def: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a skill definition."""
        # Extract function or code to execute
        if 'execute' in skill_def:
            # Execute a callable
            execute_func = skill_def['execute']
            if callable(execute_func):
                if asyncio.iscoroutinefunction(execute_func):
                    return await execute_func(context)
                else:
                    return execute_func(context)
        
        elif 'code' in skill_def:
            # Execute code string (unsafe in production, use exec with caution)
            code = skill_def['code']
            # Sanitize PII first
            code = sanitize_content(code)
            # Execute (placeholder)
            return None
        
        return None


class SkillForge:
    """Main SkillForge execution engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.audit_trail = AuditTrail(
            log_file=self.config.get('audit_log_file'),
            level=self.config.get('log_level', 'INFO')
        )
        self.mandate_manager = MandateManager(self.audit_trail)
        self.resource_tracker = ResourceTracker(self.audit_trail)
        self.dependency_resolver = DependencyResolver(self.audit_trail)
        self.state_manager = StateManager(self.audit_trail)
        self.skill_executor = SkillExecutor(
            self.mandate_manager,
            self.resource_tracker,
            self.state_manager,
            self.audit_trail
        )
        self.pii_sanitizer = PiiSanitizer()
        
        # Initialize mandates from config or defaults
        self._initialize_mandates()
        
        self.audit_trail.log(
            skill_name='SkillForge',
            action='initialized',
            details={'config': self.config},
            status='initialized'
        )
    
    def _initialize_mandates(self) -> None:
        """Initialize default mandates."""
        self.mandate_manager.add_mandate(Mandate(
            name='protect_skillforge',
            rules=[
                {
                    'name': 'no_modify_execute_py',
                    'condition': 'modify_protected_file',
                    'violation_type': 'SELF_MODIFY_PROTECTED_FILES',
                },
            ],
            enabled=True
        ))
        
        self.mandate_manager.add_mandate(Mandate(
            name='resource_limits',
            rules=[
                {
                    'name': 'memory_limit',
                    'condition': 'exceed_memory_limit',
                    'threshold': 4096,
                    'violation_type': 'EXCEED_RESOURCE_LIMITS',
                },
                {
                    'name': 'duration_limit',
                    'condition': 'exceed_duration_limit',
                    'threshold': 120,
                    'violation_type': 'EXCEED_RESOURCE_LIMITS',
                },
            ],
            enabled=True
        ))
    
    def add_skill(self, skill_id: str, definition: Dict[str, Any]) -> None:
        """Add a skill to SkillForge."""
        # Validate before activation
        validated, error = validate_skill_before_activation(
            skill_id, definition, self.audit_trail
        )
        
        if not validated:
            raise ValueError(error)
        
        self.state_manager.create_skill(skill_id, definition)
        
        # Add dependencies
        dependencies = definition.get('dependencies', [])
        if dependencies:
            self.dependency_resolver.add_dependencies(skill_id, dependencies)
            self.state_manager.update_state(
                skill_id, 
                'queued',
                error=None
            )
    
    async def run_skill(self, skill_id: str, context: Dict[str, Any] = None) -> ExecutionResult:
        """Run a single skill."""
        SKILLFORGE_STATE['running'] = True
        SKILLFORGE_STATE['current_skill'] = skill_id
        SKILLFORGE_STATE['execution_count'] += 1
        
        self.audit_trail.log(
            skill_name='SkillForge',
            action='run_skill',
            details={'skill_id': skill_id, 'context': context},
            status='running'
        )
        
        result = await self.skill_executor.execute(skill_id, context)
        
        self.audit_trail.log(
            skill_name='SkillForge',
            action='run_skill_complete',
            details={'skill_id': skill_id, 'success': result.success},
            status='completed' if result.success else 'failed'
        )
        
        return result
    
    async def run_skills_in_order(self, skill_ids: List[str], 
                                  context: Dict[str, Any] = None) -> List[ExecutionResult]:
        """Run multiple skills in dependency order."""
        # Resolve execution order
        if skill_ids:
            # Use the first skill as the entry point
            execution_order = self.dependency_resolver.resolve_order(skill_ids[0])
            # Filter to only include requested skills
            execution_order = [s for s in execution_order if s in skill_ids]
        else:
            execution_order = skill_ids
        
        # Check for circular dependencies
        cycles = self.dependency_resolver.detect_circular_dependencies()
        if cycles:
            error_msg = f"Circular dependencies detected: {cycles}"
            self.audit_trail.log(
                skill_name='SkillForge',
                action='run_skills',
                details={'skill_ids': skill_ids, 'cycles': cycles},
                status='error',
                error=error_msg
            )
            return [
                ExecutionResult(
                    skill_id=sid,
                    success=False,
                    error=error_msg
                ) for sid in skill_ids
            ]
        
        # Execute in order
        results = []
        for skill_id in execution_order:
            result = await self.run_skill(skill_id, context)
            results.append(result)
            
            # If a skill fails, continue anyway (collect all results)
            # Or could break early: if not result.success: break
        
        return results
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit log summary."""
        return self.audit_trail.get_summary()
    
    def get_skill_state(self, skill_id: str) -> Optional[SkillState]:
        """Get state of a skill."""
        return self.state_manager.get_state(skill_id)
    
    def get_all_skill_states(self) -> Dict[str, SkillState]:
        """Get all skill states."""
        return self.state_manager.get_all_states()
    
    def sanitize(self, data: Union[str, Dict, List], recursive: bool = True) -> Union[str, Dict, List]:
        """Sanitize PII from data."""
        return self.pii_sanitizer.sanitize(data, recursive)
    
    def shutdown(self) -> None:
        """Shutdown SkillForge and cleanup resources."""
        self.audit_trail.log(
            skill_name='SkillForge',
            action='shutdown',
            details={},
            status='shutting_down'
        )
        
        SKILLFORGE_STATE['running'] = False
        SKILLFORGE_STATE['end_time'] = datetime.now().isoformat()
        self.state_manager.cleanup('SkillForge')


# =============================================================================
# MAIN EXECUTION FUNCTION
# =============================================================================

async def run_skillforge(config: Optional[Dict[str, Any]] = None, 
                        skills: Optional[List[Dict[str, Any]]] = None,
                        run_skills: Optional[List[str]] = None) -> Dict[str, Any]:
    """Main entry point for SkillForge execution."""
    
    # Initialize SkillForge
    forge = SkillForge(config)
    
    try:
        # Add skills if provided
        if skills:
            for skill in skills:
                skill_id = skill.get('id', skill.get('name', 'unnamed'))
                forge.add_skill(skill_id, skill)
        
        # Run specific skills if provided
        if run_skills:
            results = await forge.run_skills_in_order(run_skills)
            return {
                'success': True,
                'results': [r.to_dict() for r in results],
                'audit_summary': forge.get_audit_summary(),
            }
        
        # If no specific skills to run, just return initialization info
        return {
            'success': True,
            'message': 'SkillForge initialized successfully',
            'skills_loaded': len(forge.state_manager.skill_definitions),
            'audit_summary': forge.get_audit_summary(),
        }
        
    finally:
        forge.shutdown()


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == '__main__':
    # Example: Create and run a simple skill
    async def main():
        # Define a sample skill
        sample_skill = {
            'id': 'test_skill',
            'name': 'Test Skill',
            'description': 'A sample skill for testing',
            'dependencies': [],
            'execute': lambda ctx: {"result": "success", "context": ctx},
            'max_memory_mb': 1024,
            'max_duration_minutes': 30,
        }
        
        # Create SkillForge instance
        forge = SkillForge({
            'log_level': 'DEBUG',
            'audit_log_file': '.agent/skills/skillforge/audit.log',
        })
        
        # Add and run skill
        forge.add_skill('test_skill', sample_skill)
        result = await forge.run_skill('test_skill', {'test': 'data'})
        
        print(f"Result: {result.to_dict()}")
        print(f"Audit Summary: {forge.get_audit_summary()}")
        
        forge.shutdown()
    
    import asyncio
    asyncio.run(main())
