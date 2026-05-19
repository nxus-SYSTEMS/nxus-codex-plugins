# PHI Boundary — End-User Reference

This is the plain-language version of the PHI Boundary behavior that
Celerat enforces. The runtime code is in
`plugins/nxuskit/mcp/src/nxuskit_celerat/mcp/phi_boundary.py`.

If you are evaluating Celerat for a healthcare-adjacent workflow, this
page tells you exactly what the plugin will and will not do with content
that may be Protected Health Information (PHI).

---

## 1. We don't accept PHI in chat

If you paste content into Codex chat that looks like it contains PHI
(SSN-shaped numbers, dates of birth, MRNs, "Patient Name:" labels,
phone numbers, addresses, etc.), the skill refuses and asks you to keep
that content in your local files or your authorized workspace (e.g., the
EMR or case-management system you're already permitted to use).

We can still help: we'll point you at a local nxusKit pipeline that
reads those files on your machine. The only thing that comes back to the
assistant is a schema-level summary or a draft you and your reviewer
control.

**Important:** our heuristic is a safety net, not a detector. Some PHI
shapes (free-text personal names, for instance) can't be detected by
regex without unacceptable false positives. We rely on you and the
recipe author to keep PHI on your authorized side of the boundary.

---

## 2. PHI-sensitive recipe outputs are schema-level only

Some recipes are tagged `phi-sensitive` for regulated-data or confidential
local-file workflows. When such a recipe runs:

1. The recipe's output schema declares an **allowlist** of fields that
   are allowed to leave the local pipeline (e.g.,
   `denial_rationale_summary`, `policy_citation_codes`, structural
   counts).
2. Anything not in the allowlist is **stripped** before the response
   reaches the assistant.
3. Each stripped field generates a local audit log line (field NAME
   only — never the field value).

The runtime gate lives in
`phi_boundary.enforce_schema_level()`. The skill is bound by the contract
that comes back; it does not try to fill in stripped fields from
elsewhere.

---

## 3. Correlation handles — explicit declaration only

Some recipes need a stable per-case identifier (a UUID maintained in
**your** case-management system, not derived from PHI) to thread output
back to the right record. Each such field is declared as a
`correlation_handle` in the recipe metadata, and each declaration must
include the recipe author's assertion that the handle is not derived
from PHI:

```yaml
correlation_handles:
  - field_name: case_uuid
    description: Per-case ticket UUID maintained in the auditor's case-management system.
    author_assertion_not_derived_from_phi: true
    workspace_context: Authorized local case-management or records system
```

If a recipe omits the assertion or sets it to `false`, the recipe is
rejected at load time and never enters the snapshot.

If a field looks like a handle (`*_uuid`, `*_id`, `*_number`) but is NOT
declared, it is **stripped**. There is no implicit pattern match.

---

## 4. What Celerat does NOT claim (FR-023b non-claim)

> Celerat does not perform HIPAA Safe Harbor de-identification, does
> not ship a de-identification scrubber, and does not certify any output
> as "de-identified." Schema-level filtering on this recipe's output is
> a safety net, not a compliance guarantee. Responsibility for ensuring
> any declared correlation_handle meets Safe Harbor's "non-identifying
> record code" criterion (45 CFR §164.514(b)(2)(i)(R)) rests with the
> recipe author and the auditor's organization. Installing this plugin
> does not make Codex HIPAA-compliant or constitute a covered-entity /
> business-associate solution.

The assistant surfaces this paragraph verbatim before any
`phi-sensitive` recipe is invoked. We mean it.

---

## 5. Cloud models + remote MCPs

If you ask for "send these records to GPT for analysis" or anything
equivalent, Celerat refuses and points you at a local-provider
alternative through nxusKit (Ollama / LM Studio):

> Real PHI workflows require customer compliance review and appropriate
> agreements (e.g., a Business Associate Agreement) before any
> OpenAI-hosted model or remote MCP receives PHI. Until that's in place,
> here's a local-provider alternative through nxusKit (Ollama / LM
> Studio): use `recommend_recipe_for_task` with
> `workflow_tags=["phi-sensitive", "local-only"]`.

If you enable any non-local / third-party MCP server, Celerat surfaces a
warning before sending data:

> Remote MCP servers are third-party services. Data you send them is
> subject to the third party's retention and residency policies, which
> may differ from Celerat's local-only defaults. For PHI-sensitive
> workflows, prefer a local stdio MCP and a local provider through
> nxusKit.

---

## 6. Heuristic set (what we look for in chat)

| Category | Example shape |
|---|---|
| US SSN | `123-45-6789` |
| US phone | `(415) 555-0142` |
| Email | `name@example.com` |
| ZIP+4 | `94110-1234` |
| Date of birth | `DOB: 12/31/1970` |
| MRN / Patient ID | `MRN: 12345678` |
| Account number | `Account #: 99887766` |
| URL | `https://example.com/...` |
| IP address | `10.0.0.42` |
| Section keyword name | `Patient Name: Jane Doe` |

Free-text personal names are intentionally not regex-matched (false
positives would block legitimate developer chat). The skill relies on
section keywords and on you keeping PHI in authorized files.

---

## 7. Sources

- 45 CFR §164.514(b)(2)(i) — HIPAA Safe Harbor identifier list.
- HHS HIPAA de-identification guidance:
  https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
- OpenAI data-control docs:
  https://platform.openai.com/docs/guides/your-data
- OpenAI Business Associate Agreement (BAA) program:
  https://openai.com/policies/baa (consult OpenAI directly for current terms).

---

**End of phi-boundary.md.**
