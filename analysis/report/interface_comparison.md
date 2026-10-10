# HW4 interface comparison

## Inspection and approval

The student approved the proposed interface before implementation. Ten
actual traces were read from the live `cartwheel-dev` Langfuse project,
including shopper, merchant and support roles, retrievals, escalation,
single-turn conversations and followups. Inspected trace IDs:

- `9027cc4e0fc61543b0503fc723b1b0ca`
- `e5f4a553ba49d62f04976bab1e9efc6b`
- `fa6f48bf8e7f43bfcac8cf64cdae50eb`
- `1e79fb44ed721a3f30934500464e10ee`
- `24addea55d7b9707be68aa4908bd9600`
- `ecc32ba020398fbe6dbb8b22fa3bf2cf`
- `8aa7ab5dd576a91445abbef931dc0a05`
- `6cf8c1332cd18bfbc5c5ac2bdc2d6963`
- `ee864393192e7122500d8771446cd19b`
- `bc39eb34abf1dee8fbb368a38658ec1f`

Student feedback about their preliminary standard Langfuse reviews is
**pending**. The observations below describe inspected data and interface
behavior, rather than attributing unreported experiences to the student.

## Retained design

Highlighted evidence and adjacent human notes were retained from the
reference viewer. Selecting text preserves the highlight before the note
editor receives focus. Call arguments and results share one container.
Role colors identify user, assistant and tool content. Browser draft backup
and state polling support interrupted review sessions.

## Changed after inspecting real traces

`support-0001` has three separate trace IDs with one session ID; therefore
the custom viewer groups by `cartwheel.session_id`, orders turns by
timestamp, and distinguishes the selected trace from context turns.
Context turns do not automatically count as reviewed. Complete tool
results remain visible beside replies. Exception status is preserved even
when a tool has no ordinary output. Complete model inputs, outputs and raw
span records remain expandable. Repeated model history is collapsed, while
tool evidence is readable without expansion.

Initial free form observations and final category labels have separate
screens. Suggestions use a dashed container and explicit decisions, rather
than being presented as human labels. A structural coverage map uses
position for token/tool counts and hue for role; it does not claim that
position predicts failure.

## Remaining limitations

The reviewer still makes at least 100 trace reviews and every final binary
judgment. The interface cannot determine intended behavior where the
specification is ambiguous. Taxonomy proposals and later depth-search
batches require the coding agent's review loop. Drafts use browser local
storage and are not portable until submitted. Text selection currently
anchors one passage within one evidence block. The full span JSON is
available, but there is no dedicated tree explorer.

## Sources and optional work

Normal startup fetches the live Langfuse project. No offline fallback was
used in preparing the first batch. Startup records its source timestamp
under `analysis/state/corpus_source.json`; the committed HW3 export is used
only with an explicit temporary-outage reason. Workshop Part C is skipped.

## Verification

Focused offline and local browser checks are recorded in `hw4-progress.md`.
Live trace reads were verified. All 100 explicitly confirmed open-code TEXT scores were read back from
Langfuse with exact IDs and text. All 800 binary judgments are explicitly confirmed and verified in
Langfuse, with matching current local JSONL records. No test judgments
were inserted in the live project.
The Final labels screen now shows AI proposals separately, flags boundary
interpretations and requires explicit inspection before saving. Fourteen
offline tests pass, including bulk-confirmation and synchronization gates.
Complete source/evidence references and AI acceptance history are preserved.
