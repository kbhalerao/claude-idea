"""MCP server for idea capture integration with Claude Code."""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json
from .db import db
from .models import Idea


# Create MCP server instance
app = Server("idea-capture")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for idea capture."""
    return [
        Tool(
            name="idea_add",
            description="Add a new idea to capture system",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the idea"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorizing the idea",
                        "default": []
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level",
                        "default": "medium"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in-progress", "done", "archived"],
                        "description": "Current status",
                        "default": "todo"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata",
                        "default": {}
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="idea_list",
            description="List ideas with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in-progress", "done", "archived"],
                        "description": "Filter by status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filter by priority"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by tag"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of ideas to return",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="idea_get",
            description="Get a specific idea by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "idea_id": {
                        "type": "string",
                        "description": "The ID of the idea to retrieve"
                    }
                },
                "required": ["idea_id"]
            }
        ),
        Tool(
            name="idea_update",
            description="Update an existing idea",
            inputSchema={
                "type": "object",
                "properties": {
                    "idea_id": {
                        "type": "string",
                        "description": "The ID of the idea to update"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags (replaces existing)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in-progress", "done", "archived"],
                        "description": "New status"
                    }
                },
                "required": ["idea_id"]
            }
        ),
        Tool(
            name="idea_delete",
            description="Delete an idea",
            inputSchema={
                "type": "object",
                "properties": {
                    "idea_id": {
                        "type": "string",
                        "description": "The ID of the idea to delete"
                    }
                },
                "required": ["idea_id"]
            }
        ),
        Tool(
            name="idea_next_actions",
            description="Get next actions (todo items sorted by priority)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of actions to return",
                        "default": 5
                    }
                }
            }
        ),
        Tool(
            name="idea_search_by_tags",
            description="Search ideas by tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Tag to search for"
                    }
                },
                "required": ["tag"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "idea_add":
            return await _handle_add(arguments)
        elif name == "idea_list":
            return await _handle_list(arguments)
        elif name == "idea_get":
            return await _handle_get(arguments)
        elif name == "idea_update":
            return await _handle_update(arguments)
        elif name == "idea_delete":
            return await _handle_delete(arguments)
        elif name == "idea_next_actions":
            return await _handle_next_actions(arguments)
        elif name == "idea_search_by_tags":
            return await _handle_search_by_tags(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _handle_add(args: dict) -> list[TextContent]:
    """Handle idea_add tool call."""
    idea = Idea(
        content=args["content"],
        tags=args.get("tags", []),
        priority=args.get("priority", "medium"),
        status=args.get("status", "todo"),
        metadata=args.get("metadata", {})
    )
    created = db.create_idea(idea)
    return [TextContent(
        type="text",
        text=f"Created idea {created._id}\n{_format_idea(created)}"
    )]


async def _handle_list(args: dict) -> list[TextContent]:
    """Handle idea_list tool call."""
    status = args.get("status")
    priority = args.get("priority")
    tag = args.get("tag")
    limit = args.get("limit", 20)

    if status:
        ideas = db.get_by_status(status)
    elif priority:
        ideas = db.get_by_priority(priority)
    elif tag:
        ideas = db.search_by_tags(tag)
    else:
        ideas = db.list_ideas(limit=limit)

    if not ideas:
        return [TextContent(type="text", text="No ideas found")]

    text = f"Found {len(ideas)} idea(s):\n\n"
    for idea in ideas:
        text += _format_idea(idea) + "\n\n"

    return [TextContent(type="text", text=text)]


async def _handle_get(args: dict) -> list[TextContent]:
    """Handle idea_get tool call."""
    idea = db.get_idea(args["idea_id"])
    if not idea:
        return [TextContent(type="text", text=f"Idea not found: {args['idea_id']}")]

    return [TextContent(type="text", text=_format_idea(idea, detailed=True))]


async def _handle_update(args: dict) -> list[TextContent]:
    """Handle idea_update tool call."""
    idea = db.get_idea(args["idea_id"])
    if not idea:
        return [TextContent(type="text", text=f"Idea not found: {args['idea_id']}")]

    if "content" in args:
        idea.content = args["content"]
    if "tags" in args:
        idea.tags = args["tags"]
    if "priority" in args:
        idea.priority = args["priority"]
    if "status" in args:
        idea.status = args["status"]

    updated = db.update_idea(idea)
    return [TextContent(
        type="text",
        text=f"Updated idea {updated._id}\n{_format_idea(updated)}"
    )]


async def _handle_delete(args: dict) -> list[TextContent]:
    """Handle idea_delete tool call."""
    idea = db.get_idea(args["idea_id"])
    if not idea:
        return [TextContent(type="text", text=f"Idea not found: {args['idea_id']}")]

    if db.delete_idea(idea._id, idea._rev):
        return [TextContent(type="text", text=f"Deleted idea: {args['idea_id']}")]
    else:
        return [TextContent(type="text", text=f"Failed to delete idea: {args['idea_id']}")]


async def _handle_next_actions(args: dict) -> list[TextContent]:
    """Handle idea_next_actions tool call."""
    limit = args.get("limit", 5)
    ideas = db.get_next_actions()

    if not ideas:
        return [TextContent(type="text", text="No pending actions found")]

    text = f"Next {min(limit, len(ideas))} action(s):\n\n"
    for idea in ideas[:limit]:
        text += _format_idea(idea) + "\n\n"

    return [TextContent(type="text", text=text)]


async def _handle_search_by_tags(args: dict) -> list[TextContent]:
    """Handle idea_search_by_tags tool call."""
    ideas = db.search_by_tags(args["tag"])

    if not ideas:
        return [TextContent(type="text", text=f"No ideas found with tag: {args['tag']}")]

    text = f"Found {len(ideas)} idea(s) with tag '{args['tag']}':\n\n"
    for idea in ideas:
        text += _format_idea(idea) + "\n\n"

    return [TextContent(type="text", text=text)]


def _format_idea(idea: Idea, detailed: bool = False) -> str:
    """Format an idea for display."""
    status_emoji = {
        'todo': '☐',
        'in-progress': '⏳',
        'done': '✓',
        'archived': '📦'
    }
    priority_emoji = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }

    lines = [
        f"{status_emoji.get(idea.status, '?')} {priority_emoji.get(idea.priority, '')} {idea.content}",
        f"ID: {idea._id}"
    ]

    if idea.tags:
        tags_str = ', '.join(f"#{tag}" for tag in idea.tags)
        lines.append(f"Tags: {tags_str}")

    if detailed:
        lines.extend([
            f"Status: {idea.status}",
            f"Priority: {idea.priority}",
            f"Created: {idea.created}",
            f"Updated: {idea.updated}"
        ])
        if idea.metadata:
            lines.append(f"Metadata: {json.dumps(idea.metadata, indent=2)}")

    return "\n".join(lines)


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
