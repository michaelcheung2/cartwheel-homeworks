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

The feedback below was drafted by the assistant at the student's request,
using inspected traces and the recorded review workflow. It does not claim
that the student personally performed the preliminary standard Langfuse
inspection; that activity has not been independently reported.

## Feedback on reviewing traces

The most useful part of trace review was comparing what the assistant said
with what the tools actually did. A plausible final answer is not enough to
judge success. The review needs the user's request, the tool arguments,
the returned records, and the final answer together. Langfuse retains the
underlying spans and scores, which makes it possible to check those details
and verify that annotations were saved.

One source of friction was reconstructing a conversation across separate
traces. For example, `support-0001` contains three traces under one session.
An earlier turn can explain a later request or show that a human handoff
already happened. Reviewing only the selected turn can therefore produce
an incorrect failure label. Grouping turns by session, in chronological
order, makes that context available while keeping the selected trace's
review and labels separate.

Another challenge was distinguishing a proposed action from an executed
action. Some assistant messages printed tool-call JSON or promised a lookup
without a corresponding tool execution. The decisive evidence is the
actual TOOL span and its result. Showing each call's arguments and result
together makes this distinction easier to check, including when a call
failed and returned an exception.

Policy review also required reading the supporting evidence closely. A
citation can name a real document yet fail to support the particular claim.
Conversely, a fact returned by a tool does not necessarily require a policy
citation. In `support-0047`, trace
`01994e8ae186fc97b029be687ae706f6`, the escalation result supplied ticket 151
and a 24-hour SLA. That supported the response's 24-hour follow-up statement;
the additional account-tracking advice needed a separate support check.
This example helped refine the citation category rather than treating every
uncited sentence as the same error.

The custom viewer addresses these review needs through session grouping,
visible tool results and retrieval content, and notes beside highlighted
evidence. Separating initial observations, search suggestions, and final
binary labels also makes the review process easier to follow. An AI
suggestion remains visibly distinct from a confirmed human decision.

The main remaining limitation is judgment: an interface cannot resolve an
ambiguous specification or decide a category boundary on its own. Those
questions still required explicit review and, in one case, an approved SPEC
clarification. A dedicated span tree and annotations spanning multiple
evidence blocks would further help with complex traces. The implemented UI
was checked with DOM stubs; a successful visual browser check is still
unverified.

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
