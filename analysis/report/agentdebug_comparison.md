# Comparison with AgentDebug

Compared after the student confirmed the eight-category taxonomy and the
100th review. Source: Zhu et al., *Where LLM Agents Fail and How They can
Learn From Failures*, arXiv:2509.25370v1 (29 September 2025), section 2.1
and Appendix A.2, Table 2. Retrieved the published HTML on 10 October 2026:
<https://arxiv.org/html/2509.25370#A2>.

AgentErrorTaxonomy groups errors into Memory, Reflection, Planning, Action
and System. Cartwheel's taxonomy instead identifies observable support
requirements and likely product changes. These are analogies; Cartwheel
traces do not establish which internal reasoning module caused an error.

| Cartwheel mode | Nearest AgentDebug pattern | Boundary retained |
| --- | --- | --- |
| refund_approval_not_requested | Planning: Constraint Ignorance; Action: Planning–Action Disconnect | Only actionable eligible requests above $100, with neither queue nor human handoff |
| unsupported_policy_claim | Memory: Hallucination; sometimes Retrieval Failure | False policy/service promises, independently of citation correctness |
| missing_or_invalid_policy_citation | Closest to omission of relevant information; no exact citation category | Correct answers can still fail attribution; bad IDs are not automatically bad policy content |
| invalid_tool_arguments | Action: Parameter Error; sometimes Format Error | Actual schema rejection, not an expected authorization/business result |
| invented_record_values | Memory: Hallucination (False Memory); Reflection: Hallucination | Invented fields/identifiers differ from faithfully copied but inconsistent evidence |
| ignored_record_inconsistency | Reflection: Outcome Misinterpretation | Flag contradictions or required missing fields before relying on the record |
| required_human_handoff_missing | Planning: Constraint Ignorance; Action: Planning–Action Disconnect | Relevant earlier successful tickets count; general policy questions are excluded |
| unexecuted_tool_request | Action: Planning–Action Disconnect | Printed/narrated intended tools differ from actual execution or a concrete blocker |

## Possible omission and name check

The paper's System categories include step-limit exhaustion, external tool
execution errors, model/API limits and environment errors. The reviewed
Cartwheel argument failures are caused by malformed model arguments, so
calling them external tool failures would obscure the corrective action.
Expected permission_denied and not_found results are guards/contracts
working as specified. This review has no set of three human-confirmed
positive system-failure examples; no System mode is added merely to match
the paper. The local reviewer/certificate/browser setup errors are outside
the support-agent trace judgments.

Reflection hallucination suggests checking whether the assistant claims
execution or a result that never occurred. The exploratory search includes
unselected trace 5a1146a607079abb5f11cff898384b92 (support-0132), which appears
to print a product-tool response after a validation failure. The student rejected its next-tool-stall search hypothesis because the
reply instead presents an invented completed result. This is not one of
three confirmed examples for a separate final mode; the boundary and
possible grounding omission are recorded without inventing a ninth category.
The existing unexecuted_tool_request definition concerns a substituted next
tool call, so a fabricated completed result must be considered separately.

The comparison supports retaining distinct categories for source invention,
interpretation of inconsistent records and missing execution. The citation
name explicitly says missing_or_invalid, rather than implying that a
syntactically present but wrong-document identifier passes. No published
category is copied into the taxonomy without Cartwheel observations and
human confirmation.
