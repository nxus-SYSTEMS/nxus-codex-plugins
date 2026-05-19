"""``python -m nxuskit_celerat.mcp`` entry point.

Three modes:

- ``--help``         print usage and exit 0
- ``--self-check``   load the snapshot, print one-line diagnostic, exit 0
                     (or non-zero if the snapshot is missing/invalid)
- (no args)          start the stdio MCP server (the path Codex uses)

A ``--snapshot <path>`` flag overrides the bundled snapshot location;
the env var ``NXUSKIT_CELERAT_METADATA`` does the same and is the path
Codex uses when configured externally.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .logging_config import configure as configure_logging
from .server import run as server_run
from .store import MetadataStore, SnapshotMissingError, default_snapshot_path

_USAGE = """\
nxuskit-celerat-mcp — local read-only Model Context Protocol server
                       for the nxusKit Celerat Codex Plugin

Usage:
  python -m nxuskit_celerat.mcp [options]

Options:
  --help                Print this help and exit
  --self-check          Load the bundled snapshot, print a one-line
                        diagnostic, and exit (no MCP server started)
  --snapshot <path>     Override the bundled snapshot path (or set
                        NXUSKIT_CELERAT_METADATA in the environment)
  --version             Print the package version and exit

If invoked with no flags, the server runs over stdio.  Codex (or
mcp-inspector) launches the server this way per the plugin manifest's
mcpServers block.
"""


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nxuskit-celerat-mcp",
        add_help=False,  # we render --help ourselves to keep the contract verbatim
        allow_abbrev=False,
    )
    p.add_argument("--help", action="store_true")
    p.add_argument("--self-check", action="store_true", dest="self_check")
    p.add_argument("--snapshot", type=Path, default=None)
    p.add_argument("--version", action="store_true")
    return p


def _resolve_snapshot_path(arg_path: Path | None) -> Path:
    if arg_path is not None:
        return arg_path.expanduser().resolve()
    env = os.environ.get("NXUSKIT_CELERAT_METADATA")
    if env:
        return Path(env).expanduser().resolve()
    return default_snapshot_path()


def _run_self_check(snapshot_path: Path) -> int:
    """Print the Quickstart §1 diagnostic line and exit.

    Output contract (verbatim):

        nxuskit-celerat-mcp <version>
        snapshot: <identifier>  examples: <N>  recipes: <M>  tiers: 2
        ok
    """
    try:
        store = MetadataStore.load(snapshot_path)
    except SnapshotMissingError as exc:
        sys.stderr.write(f"nxuskit-celerat-mcp {__version__}\n")
        sys.stderr.write(f"snapshot: ERROR — {exc}\n")
        sys.stderr.write("fail\n")
        return 2
    info = store.self_check()
    print(f"nxuskit-celerat-mcp {__version__}")
    print(
        f"snapshot: {info['snapshot_identifier']}  "
        f"examples: {info['examples']}  recipes: {info['recipes']}  "
        f"tiers: {info['tiers']}"
    )
    print("ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _make_parser().parse_args(argv)

    if args.help:
        print(_USAGE)
        return 0
    if args.version:
        print(f"nxuskit-celerat-mcp {__version__}")
        return 0

    snapshot_path = _resolve_snapshot_path(args.snapshot)

    if args.self_check:
        configure_logging()
        return _run_self_check(snapshot_path)

    return server_run(snapshot_path)


if __name__ == "__main__":  # pragma: no cover — module entry
    sys.exit(main())
