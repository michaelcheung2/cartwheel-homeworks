# HW4 human review

From the repository root:

```bash
env -u OTEL_SDK_DISABLED uv run python -m analysis.review_app.server
```

Open <http://localhost:8020>. Langfuse must be running with its existing
credentials in `.env`. Startup reads the live project, restricts the corpus
to final HW3 support scenarios, and saves a temporary cache locally. No model
calls are needed to review the recorded evidence.

## Review workflow

1. Select a trace in **Review**. Other traces from its session provide context.
2. Read until the first failure. Highlight the relevant text, write your own
   observation, select **First failure observed**, and save. If no failure is
   observed, select that option explicitly and save the note.
3. Review the first 30 traces. **Progress** can then prepare the role batch.
4. Ask the coding agent to organize your notes into candidate definitions.
   Inspect the evidence before confirming a grouping. Search suggestions
   remain separate and require your acceptance or rejection with a reason.
5. Review 25 depth-search traces and the final 15 uniform traces. The agent
   prepares explicit AI drafts and final-example proposals; inspect and
   accept/correct them before they count. Search decisions are separate.
6. After confirming the final taxonomy, use **Final labels** to inspect the
   complete trace for each category and save present/absent decisions.

Saving is explicit. Browser drafts are backed up in local storage; they are
not submitted judgments. Accepted notes are TEXT scores named `hw4_open_code`
in Langfuse. Final binary scores use the failure mode's name, with 1=present
and 0=absent. Stable score IDs make retries update the same judgment.
Synchronization is marked successful only after an API read verifies it.
Corrections preserve prior local records; label files are append-only.

The instructor's demonstration files are preserved under
`analysis/state/starter_demo_backup/`, separate from the student's HW4 state.
The application refuses to replace existing review work on initialization.

## Later batch gates

The first batch has exactly 15 uniform draws and 15 centroid representatives
from eight clusters of standardized structural features. User role was
chosen before reviewing outcomes for batch two (10 traces per role).
Depth-search selection is deferred until human observations support
candidate definitions; the final 15 uniform draws are deferred until there
is a draft taxonomy. No trace may count in more than one batch.

Taxonomy proposals and search retrievals will be added by the coding agent
to `patterns.json` and `suggestions.json` during the human review loop. The
interface polls these files through the local API. Do not initialize modes
from the starter demonstration or HW3 generator expectations.

## Temporary offline recovery

Only when Langfuse is temporarily unavailable:

```bash
uv run python -m analysis.review_app.server --offline-reason "Describe the observed temporary outage"
```

This uses the committed HW3 export, preserves trace IDs, and records the
reason in `corpus_source.json`. Record the same reason in the interface
comparison. Scores remain pending until a live restart and explicit retry.

## Focused verification

```bash
uv run python -m unittest analysis.review_app.test_server
```

These tests use isolated temporary state and a mock Langfuse client. They
do not create reviews or labels in the student's project.

## Complete labeling proposals

`label_proposals.json` contains compact AI drafts for every selected trace
and final mode. Final labels shows the draft beside full trace evidence;
flagged boundary interpretations need particular attention. Saving requires
an explicit inspection checkbox, and retains AI provenance. A complete
reviewed package can be saved through `/api/confirm-label-drafts` only with
explicit IDs and human confirmation. The endpoint prevalidates the entire
package before any write. `/api/verify-label-sync` checks exact score IDs,
trace IDs, values, current definition versions and evidence notes.

Pending label drafts are not label files or accepted judgments. Search
decisions remain separate and never silently expand the selected sample.
