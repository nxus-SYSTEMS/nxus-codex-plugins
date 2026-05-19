"""Structured logging configured for stdio safety + on-disk boundary.

FR-003: the MCP server MUST NOT write outside its own cache/log directory.
This module is the chokepoint for *all* writes: configure structlog to emit
JSONL to ``~/.nxuskit-celerat/logs/<date>.jsonl`` and refuse any write
outside the root via :class:`LogDirBoundaryError`.

Logs go to file, never to stdout: stdout is reserved for MCP JSON-RPC
framing.  stderr is allowed for hard fatal errors only (e.g., snapshot
missing on startup).
"""

from __future__ import annotations

import logging
import os
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import structlog


class LogDirBoundaryError(RuntimeError):
    """Raised when a caller attempts to write outside the per-user root dir.

    The root is ``~/.nxuskit-celerat/`` (or ``$XDG_CACHE_HOME/nxuskit-celerat/``
    if set).  Sub-directories: ``logs/``, ``cache/``, ``audit/``.
    """


_DEFAULT_ROOT_NAME: Final[str] = "nxuskit-celerat"

# Module-level state, set once by :func:`configure`.
_root_dir: Path | None = None
_configured = False
_configure_lock = threading.Lock()


def _resolve_root() -> Path:
    """Choose the per-user root directory.

    Priority:
    1. ``NXUSKIT_CELERAT_ROOT`` env var (test override)
    2. ``$XDG_CACHE_HOME/nxuskit-celerat/``
    3. ``~/.nxuskit-celerat/``
    """
    if (env := os.environ.get("NXUSKIT_CELERAT_ROOT")):
        return Path(env).expanduser().resolve()

    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return (Path(xdg).expanduser().resolve() / _DEFAULT_ROOT_NAME)

    home = Path.home()
    return (home / f".{_DEFAULT_ROOT_NAME}").resolve()


def get_root_dir() -> Path:
    """Return the configured per-user root.  Lazily configures if needed."""
    if _root_dir is None:
        configure()
    assert _root_dir is not None
    return _root_dir


def get_log_dir() -> Path:
    return get_root_dir() / "logs"


def get_cache_dir() -> Path:
    return get_root_dir() / "cache"


def get_audit_dir() -> Path:
    return get_root_dir() / "audit"


def assert_within_root(path: Path) -> Path:
    """Raise :class:`LogDirBoundaryError` if ``path`` is not under the root.

    Returns the resolved absolute path on success.
    """
    root = get_root_dir()
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:  # not within root
        raise LogDirBoundaryError(
            f"Refusing to write to {resolved!s}: outside per-user root {root!s} "
            "(FR-003)."
        ) from exc
    return resolved


def safe_open_for_write(path: Path, *, mode: str = "a") -> Any:
    """Open ``path`` for writing only after the boundary check passes.

    Use this for any file write inside the package.  Modes are restricted
    to write/append text or binary; read-only modes are rejected (call
    :func:`open` directly for those — reads are unconstrained).
    """
    if not any(c in mode for c in ("w", "a", "x")):
        raise LogDirBoundaryError(
            f"safe_open_for_write only permits write/append/exclusive modes, got {mode!r}"
        )
    target = assert_within_root(path)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return target.open(mode)


def _ensure_dirs(root: Path) -> None:
    """Create root + subdirs with mode 0700 (best-effort on POSIX)."""
    import contextlib

    for sub in (root, root / "logs", root / "cache", root / "audit"):
        sub.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(OSError, NotImplementedError):  # pragma: no cover -- Windows / restricted FS
            sub.chmod(0o700)


def configure(
    *,
    log_level: str = "INFO",
    root_dir_override: Path | None = None,
) -> Path:
    """Configure structlog and ensure the per-user root exists.

    Idempotent: safe to call multiple times.  Returns the resolved root
    directory.
    """
    global _root_dir, _configured

    with _configure_lock:
        root = root_dir_override.expanduser().resolve() if root_dir_override else _resolve_root()
        _ensure_dirs(root)
        _root_dir = root

        if _configured:
            return root

        # Today's log file, JSONL.
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        log_path = root / "logs" / f"{today}.jsonl"

        # Guard rails: confirm log_path is within root before we open it.
        assert_within_root(log_path)

        # File handler — append-only, line-buffered.
        fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(message)s"))

        root_logger = logging.getLogger()
        root_logger.handlers = [fh]  # replace any default handlers (no stderr/stdout)
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Belt and suspenders: ensure no logger writes to stdout (which is the
        # MCP framing channel).  We do not touch sys.stderr — it's available
        # for fatal startup errors before this configure() runs.
        for name in ("", "nxuskit_celerat"):
            lg = logging.getLogger(name)
            for handler in list(lg.handlers):
                if isinstance(handler, logging.StreamHandler) and handler.stream is sys.stdout:
                    lg.removeHandler(handler)

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, log_level.upper(), logging.INFO)
            ),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        _configured = True
        return root


def get_logger(name: str = "nxuskit_celerat.mcp") -> Any:
    """Return a structlog logger.  Configures on first use."""
    if not _configured:
        configure()
    return structlog.get_logger(name)


def redaction_event(
    *,
    event: str,
    recipe_id: str,
    field_name: str,
    snapshot_identifier: str,
    extra: dict[str, Any] | None = None,
) -> None:
    """Emit a single ``phi_redaction_strip`` log line per stripped field.

    Per ``contracts/phi-boundary.md`` §2 last bullet: the field NAME is
    logged but never the field VALUE.
    """
    logger = get_logger()
    payload: dict[str, Any] = {
        "event": event,
        "recipe_id": recipe_id,
        "field_name": field_name,
        "snapshot_identifier": snapshot_identifier,
    }
    if extra:
        # Defense in depth: never let callers slip a field value into the log.
        for key in ("value", "field_value", "raw_value"):
            extra.pop(key, None)
        payload.update(extra)
    logger.info(**payload)


def reset_for_tests() -> None:
    """Reset module-level state.  ONLY for use in test fixtures."""
    global _root_dir, _configured
    with _configure_lock:
        _root_dir = None
        _configured = False
        # Drop file handlers so the next configure() opens a fresh path.
        root_logger = logging.getLogger()
        import contextlib

        for handler in list(root_logger.handlers):
            with contextlib.suppress(Exception):  # pragma: no cover
                handler.close()
            root_logger.removeHandler(handler)
        structlog.reset_defaults()


__all__ = [
    "LogDirBoundaryError",
    "assert_within_root",
    "configure",
    "get_audit_dir",
    "get_cache_dir",
    "get_log_dir",
    "get_logger",
    "get_root_dir",
    "redaction_event",
    "reset_for_tests",
    "safe_open_for_write",
]
