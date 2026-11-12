"""Prepared statements can be switched off from the environment (D-219).

The Supabase pooler in transaction mode (port 6543) does not support prepared statements, and
psycopg 3 prepares a query on its own once it has run it `prepare_threshold` times (5 by
default). With DB_PREPARED_STATEMENTS=false the engine passes `prepare_threshold=None` to
`psycopg.connect()`, which disables them on every connection. Without the variable nothing is
passed and psycopg keeps its default.
"""

from typing import Any

import pytest
from sqlalchemy import event

from hi_db.session import make_engine

URL = "postgresql+psycopg://user:secret@localhost:1/nothing"  # never connected in these tests


class _ArgumentsCapturedError(Exception):
    """Stops the connection attempt once the DBAPI arguments are known."""


def _connect_kwargs(monkeypatch: pytest.MonkeyPatch, **env: str) -> dict[str, Any]:
    monkeypatch.delenv("DB_PREPARED_STATEMENTS", raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    engine = make_engine(URL)
    captured: dict[str, Any] = {}

    def capture(_dialect: Any, _record: Any, _cargs: Any, cparams: dict[str, Any]) -> None:
        captured.update(cparams)
        raise _ArgumentsCapturedError

    event.listen(engine, "do_connect", capture)
    with pytest.raises(_ArgumentsCapturedError):
        engine.connect()
    return captured


def test_without_the_variable_psycopg_keeps_its_default(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "prepare_threshold" not in _connect_kwargs(monkeypatch)


def test_the_transaction_pooler_can_turn_prepared_statements_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kwargs = _connect_kwargs(monkeypatch, DB_PREPARED_STATEMENTS="false")
    assert "prepare_threshold" in kwargs
    assert kwargs["prepare_threshold"] is None


def test_turning_them_on_explicitly_changes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "prepare_threshold" not in _connect_kwargs(monkeypatch, DB_PREPARED_STATEMENTS="true")


def test_a_value_that_is_not_a_boolean_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_PREPARED_STATEMENTS", "sometimes")
    with pytest.raises(ValueError, match="db_prepared_statements"):
        make_engine(URL)
