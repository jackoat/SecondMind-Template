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
