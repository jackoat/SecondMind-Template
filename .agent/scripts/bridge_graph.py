"""Neo4j schema constants, connection bridge, and utility helpers."""

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Neo4j schema constants
# ---------------------------------------------------------------------------

NODE_LABELS = {
    "NOTE": "Note",
    "TAG": "Tag",
    "PROJECT": "Project",
    "SOURCE": "Source",
    "TOPIC": "Topic",
    "REFERENCE": "Reference",
    "DAILY_NOTE": "DailyNote",
}

REL_TYPES = {
    "TAGGED_WITH": "TAGGED_WITH",
    "PART_OF": "PART_OF",
    "REFERENCES": "REFERENCES",
    "LINKS_TO": "LINKS_TO",
    "DERIVED_FROM": "DERIVED_FROM",
    "MENTIONS": "MENTIONS",
    "CREATED_ON": "CREATED_ON",
}


# ---------------------------------------------------------------------------
# NotePack – structured container for note data going in/out of Neo4j
# ---------------------------------------------------------------------------

class NotePack:
    """A lightweight container holding all fields of a note to be persisted."""

    __slots__ = (
        "id",
        "title",
        "body",
        "tags",
        "source",
        "project",
        "created_at",
        "updated_at",
        "metadata",
    )

    def __init__(
        self,
        id: str,
        title: str = "",
        body: str = "",
        tags: Optional[list[str]] = None,
        source: str = "",
        project: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.id = id
        self.title = title
        self.body = body
        self.tags = tags or []
        self.source = source
        self.project = project
        self.created_at = created_at or now_iso()
        self.updated_at = updated_at or now_iso()
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        return {slot: getattr(self, slot) for slot in self.__slots__}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NotePack":
        return cls(**{k: v for k, v in data.items() if k in cls.__slots__})


# ---------------------------------------------------------------------------
# Neo4j bridge
# ---------------------------------------------------------------------------

class Neo4jBridge:
    """Thin wrapper around a Neo4j driver that reads credentials from
    environment variables and exposes ``merge_node`` and ``run`` helpers.
    """

    def __init__(self, uri: str = "", user: str = "", password: str = "") -> None:
        self.uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "")
        self._driver: Any = None

    @property
    def driver(self) -> Any:
        if self._driver is None:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
            )
        return self._driver

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def merge_node(
        self,
        label: str,
        key_property: str,
        key_value: Any,
        properties: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """MERGE a node by ``key_property`` and SET additional properties.

        Returns the created / matched node as a plain dict.
        """
        props = dict(properties or {})
        props[key_property] = key_value

        set_clause = ", ".join(
            f"n.{k} = ${k}" for k in props if k != key_property
        )
        query = (
            f"MERGE (n:{label} {{{key_property}: ${key_property}}}) "
            f"SET {set_clause} "
            "RETURN n"
        )

        result = self.run(query, **props)
        record = result.single()
        if record is None:
            return {"_id": None}
        node = record["n"]
        return dict(node)

    def run(self, query: str, **parameters: Any) -> Any:
        """Execute a Cypher query and return the result."""
        with self.driver.session() as session:
            return session.run(query, **parameters)

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "Neo4jBridge":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def read_json(path: str) -> Any:
    """Read a JSON file from disk."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: str, data: Any, indent: int = 2) -> None:
    """Write *data* as pretty-printed JSON to *path*."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)
