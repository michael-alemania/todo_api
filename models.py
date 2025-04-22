# models.py
from sqlalchemy import Table, Column, String, Boolean, Float, Index, text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import metadata

tasks = Table(
    "tasks",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("title", String, nullable=False),
    Column("description", String, nullable=False),
    Column("done", Boolean, nullable=False, server_default=text("FALSE")),
    Column("position", Float, nullable=False, server_default=text("0.0")),
    Index("idx_tasks_position", "position")
)
