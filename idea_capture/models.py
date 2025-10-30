"""Data models for ideas."""

from datetime import datetime
from typing import Optional
from uuid import uuid4


class JournalIdea:
    """Represents an idea document."""

    def __init__(
        self,
        content: str,
        tags: Optional[list[str]] = None,
        priority: str = "medium",
        status: str = "todo",
        metadata: Optional[dict] = None,
        _id: Optional[str] = None,
        _rev: Optional[str] = None,
        created: Optional[str] = None,
        updated: Optional[str] = None,
    ):
        self._id = _id or str(uuid4())
        self._rev = _rev
        self.type = "idea"
        self.content = content
        self.tags = tags or []
        self.priority = priority
        self.status = status
        self.metadata = metadata or {}
        self.created = created or datetime.utcnow().isoformat()
        self.updated = updated or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for CouchDB."""
        doc = {
            "_id": self._id,
            "type": self.type,
            "content": self.content,
            "tags": self.tags,
            "priority": self.priority,
            "status": self.status,
            "metadata": self.metadata,
            "created": self.created,
            "updated": self.updated,
        }
        if self._rev:
            doc["_rev"] = self._rev
        return doc

    @classmethod
    def from_dict(cls, data: dict) -> "Idea":
        """Create Idea from CouchDB document."""
        return cls(
            content=data["content"],
            tags=data.get("tags", []),
            priority=data.get("priority", "medium"),
            status=data.get("status", "todo"),
            metadata=data.get("metadata", {}),
            _id=data.get("_id"),
            _rev=data.get("_rev"),
            created=data.get("created"),
            updated=data.get("updated"),
        )

    def update_timestamp(self):
        """Update the updated timestamp."""
        self.updated = datetime.now().isoformat()

    def __repr__(self):
        return f"Idea(id={self._id}, status={self.status}, priority={self.priority}, content={self.content[:50]}...)"
