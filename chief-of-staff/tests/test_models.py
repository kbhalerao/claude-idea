"""Tests for Pydantic models"""

import pytest
from pydantic import ValidationError

from cos.models import (
    CreateDocRequest,
    DocType,
    Priority,
    SourceInfo,
    Status,
    UpdateDocRequest,
)


class TestCreateDocRequest:
    def test_minimal_valid_request(self):
        """Test creating a doc with minimal required fields"""
        req = CreateDocRequest(
            doc_type=DocType.idea,
            content="Test idea content",
        )
        assert req.doc_type == DocType.idea
        assert req.content == "Test idea content"
        assert req.status == Status.inbox  # default
        assert req.tags == []

    def test_full_request(self):
        """Test creating a doc with all fields"""
        req = CreateDocRequest(
            doc_type=DocType.task,
            content="Review the PRs",
            title="PR Review",
            tags=["work", "urgent"],
            priority=Priority.high,
            status=Status.todo,
            due_date="2025-11-28",
            source=SourceInfo(
                client="claude-code",
                project="labcore",
                branch="main",
            ),
        )
        assert req.doc_type == DocType.task
        assert req.priority == Priority.high
        assert req.source.project == "labcore"

    def test_empty_content_fails(self):
        """Test that empty content is rejected"""
        with pytest.raises(ValidationError):
            CreateDocRequest(
                doc_type=DocType.idea,
                content="",
            )

    def test_content_too_long_fails(self):
        """Test that content over 10000 chars is rejected"""
        with pytest.raises(ValidationError):
            CreateDocRequest(
                doc_type=DocType.idea,
                content="x" * 10001,
            )


class TestUpdateDocRequest:
    def test_empty_update(self):
        """Test that empty update is valid (no fields to update)"""
        req = UpdateDocRequest()
        assert req.content is None
        assert req.status is None

    def test_partial_update(self):
        """Test updating specific fields"""
        req = UpdateDocRequest(
            status=Status.done,
            priority=Priority.low,
        )
        assert req.status == Status.done
        assert req.priority == Priority.low
        assert req.content is None


class TestSourceInfo:
    def test_minimal_source(self):
        """Test source with just client"""
        source = SourceInfo(client="cli")
        assert source.client == "cli"
        assert source.project is None

    def test_full_source(self):
        """Test source with all fields"""
        source = SourceInfo(
            client="claude-code",
            project="chief-of-staff",
            branch="feature/api",
            files=["cos/router.py", "cos/models.py"],
            session_id="abc123",
        )
        assert source.project == "chief-of-staff"
        assert len(source.files) == 2
