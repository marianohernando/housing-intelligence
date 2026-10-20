"""Helpers to turn StrEnums into CHECK constraints (text + CHECK instead of PG ENUM types)."""

from enum import StrEnum

from sqlalchemy import CheckConstraint


def in_enum(
    column: str, enum: type[StrEnum], name: str, *, nullable: bool = False
) -> CheckConstraint:
    values = ", ".join(f"'{member.value}'" for member in enum)
    expr = f"{column} IN ({values})"
    if nullable:
        expr = f"{column} IS NULL OR {expr}"
    return CheckConstraint(expr, name=name)
