#!/usr/bin/env bash
set -euo pipefail

request_file="${1:-data/request.json}"
jq -c '{provider, prompt}' "$request_file"
