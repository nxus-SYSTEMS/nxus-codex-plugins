# Third-Party Notices — `nxuskit-celerat-mcp`

The `nxuskit-celerat-mcp` Python package is distributed under
`MIT OR Apache-2.0`. It depends on the following third-party libraries.
Each dependency's license terms are reproduced from upstream metadata
and govern that dependency's redistribution; this notice does not
modify them.

## Runtime dependencies

| Package | Version pinned | License |
|---|---|---|
| `mcp` | `>=1,<2` (built against 1.27.0) | MIT |
| `pydantic` | `>=2,<3` (built against 2.13.3) | MIT |
| `rapidfuzz` | `>=3,<4` (built against 3.14.5) | MIT |
| `orjson` | `>=3,<4` (built against 3.11.8) | MPL-2.0 AND (Apache-2.0 OR MIT) |
| `structlog` | `>=25,<26` (built against 25.5.0) | MIT OR Apache-2.0 |
| `pyyaml` | `>=6,<7` (built against 6.0.3) | MIT |

## Development dependencies (not redistributed)

These are used only during development and CI; they are not part of
the runtime distribution. They are listed for transparency.

| Package | Purpose | License |
|---|---|---|
| `pytest` | test runner | MIT |
| `pytest-asyncio` | async test support | Apache-2.0 |
| `pytest-cov` | coverage reporting | MIT |
| `pytest-benchmark` | perf budget assertions | BSD-2-Clause |
| `ruff` | lint + format | MIT |
| `mypy` | strict type-check | MIT |
| `types-PyYAML` | typing stubs | Apache-2.0 |

## Note on `orjson`

`orjson` is dual-licensed: `MPL-2.0 AND (Apache-2.0 OR MIT)`. The
MPL-2.0 clause applies to `orjson` itself and is file-level copyleft
(modifications to `orjson` source files must be made available); we
import `orjson` as a binary wheel without modifications, so the MPL
obligation is satisfied by linking back to the upstream source at
<https://github.com/ijl/orjson>.

## Source bundle attribution

The bundled metadata snapshot at
`plugins/nxuskit/mcp/metadata/snapshot.json` is derived from the
public `nxusKit-examples` repository at the commit pinned in
`snapshot.meta.json`. Each example's authoritative license travels
with the example in that source repository; the snapshot file
embeds only example metadata (names, descriptions, languages, smoke
commands), not example source code.

## Reporting issues

License or attribution issues for any third-party dependency listed
above should be reported via the repository's issue tracker.
