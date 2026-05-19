"""nxuskit-celerat-mcp — local read-only Model Context Protocol server.

Reads a bundled metadata snapshot of nxusKit examples + CLI/Bash and
knowledge-work recipes; exposes 10 typed read-only tools to Codex over stdio.

This package is part of the nxusKit Celerat Codex Plugin (manifest name
``nxuskit``, display name ``nxusKit Celerat``).
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__: str = _pkg_version("nxuskit-celerat-mcp")
except PackageNotFoundError:  # pragma: no cover — only hit when running from source without install
    __version__ = "0.9.4+local"

__all__ = ["__version__"]
