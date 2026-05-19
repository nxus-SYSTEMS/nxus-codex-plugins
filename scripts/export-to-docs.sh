#!/usr/bin/env bash
# Export public Codex Plugin documentation for nxus-docs.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export_dir="${1:-}"

if [ -z "$export_dir" ]; then
  echo "usage: scripts/export-to-docs.sh <export-dir>" >&2
  exit 2
fi

rm -rf "$export_dir"
mkdir -p "$export_dir/codex-plugin/examples"

write_page() {
  local title="$1"
  local description="$2"
  local source="$3"
  local dest="$4"

  mkdir -p "$(dirname "$dest")"
  {
    echo "---"
    printf 'title: "%s"\n' "$title"
    printf 'description: "%s"\n' "$description"
    echo "---"
    echo
    sed '/^---$/,/^---$/d' "$source"
  } > "$dest"
}

write_page \
  "Codex Plugin" \
  "Install and use nxusKit Celerat, the nxusKit Codex Plugin." \
  "$repo_root/README.md" \
  "$export_dir/codex-plugin/index.md"

write_page \
  "Codex Task Examples" \
  "Prompt recipes and starter fixtures for using nxusKit Celerat with Codex." \
  "$repo_root/examples/README.md" \
  "$export_dir/codex-plugin/examples/index.md"

if [ -d "$repo_root/examples/codex-task-recipes" ]; then
  mkdir -p "$export_dir/codex-plugin/examples/codex-task-recipes"
  find "$repo_root/examples/codex-task-recipes" -type f -name '*.md' | sort | while IFS= read -r source; do
    rel="${source#$repo_root/examples/codex-task-recipes/}"
    cp "$source" "$export_dir/codex-plugin/examples/codex-task-recipes/$rel"
  done
fi

if [ -d "$repo_root/examples/fixtures" ]; then
  mkdir -p "$export_dir/codex-plugin/examples/fixtures"
  find "$repo_root/examples/fixtures" -type f -name '*.md' | sort | while IFS= read -r source; do
    rel="${source#$repo_root/examples/fixtures/}"
    mkdir -p "$export_dir/codex-plugin/examples/fixtures/$(dirname "$rel")"
    cp "$source" "$export_dir/codex-plugin/examples/fixtures/$rel"
  done
fi

private_suffix="intern""al"
for forbidden in \
  "nxus-codex-plugins-$private_suffix" \
  "nxusKit-$private_suffix" \
  "nxusKit-examples-$private_suffix" \
  "/""Users/" \
  "code""Repos"
do
  if grep -R -n "$forbidden" "$export_dir" >/dev/null 2>&1; then
    echo "ERROR: forbidden docs-export term found: $forbidden" >&2
    exit 6
  fi
done

echo "Docs export staged at $export_dir"
