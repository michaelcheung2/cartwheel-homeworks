# HW9 continuous video guide — pending completion of Part C

Record one continuous video, at most five minutes. The student's recording
and final assessment remain pending. Do not present Part C as measured yet.

1. **0:00–0:45:** Show `profile/results/costs.csv`. Explain the customer/judge
   distinction, zero local API fees, and labeled historical judge estimates.
2. **0:45–1:30:** Show the concise reply experiment and summary table.
   Output tokens and latency fell, input tokens rose, and score dropped,
   so the change was reverted.
3. **1:30–2:15:** After Part C is complete, show actual cached fractions,
   prompt order and prices. Explain zero cache hits if that is observed.
4. **2:15–3:15:** Show `cascade/results/thresholds.csv`, the frozen 0.9
   threshold and `check.json`. No threshold met 95% on development; test
   agreement was 19/38 = 50%, so the cascade is rejected.
5. **3:15–4:15:** Show the updated `profile/results/frontier.csv`. State
   which configuration you would use and explain your own assessment.
6. **4:15–5:00:** Recalculate a committed score offline:

   ```bash
   uv run python profile/scripts/reproduce.py
   ```

This reads saved counts and checks the protected input hashes. It makes
no model requests and does not repeat either assignment's test evaluations.
