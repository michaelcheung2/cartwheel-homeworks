# HW6 baseline classification review

## Cartwheel baseline results

| Case | Passed | Trials | Record in the case |
| --- | ---: | ---: | --- |
| `e-001` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-002` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-003` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-004` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-005` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-006` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-007` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-008` | 0 | 5 | `kind: "capability"`, `baseline_pass_rate: 0.0` |
| `e-009` | 5 | 5 | `kind: "regression"` |
| `e-010` | 5 | 5 | `kind: "regression"` |

Add the reported classification to each case before exporting the CI suite.

All 50 trials reached the verifier and have rewards with no trial exceptions.
The Actions run failed only in the original summary reader; the corrected reader
uses the saved per-trial evidence. Agents were not rerun.

The four refund cases and four dispute cases passed 0/5 each.
Both account-change cases created matching tickets in all five trials.
For example, e-001 printed a nonexistent refund_order call after get_order;
e-005 printed a policy lookup after get_order and created no human ticket.
An e-009 run actually called escalate_to_human and received ticket_id 151.
These are observed tool/action results, not a judgment of every sentence.

**Proposed classifications:** e-001 through e-008 are capability (baseline 0.0);
e-009 and e-010 are regression. Student confirmation is pending.

The 15-run comparison can use e-005, the disputed-charge case.
Its baseline is zero passes; the new 15 observations may also all fail, which
would produce zero pass@k estimates rather than fabricated improvements.
