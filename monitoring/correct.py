"""Bias-corrected failure prevalence for a monitoring period."""

from __future__ import annotations

from typing import Any, Sequence
import numpy as np


def corrected_mode_prevalence(
    sample_preds: Sequence[int],
    test_labels: Sequence[int],
    test_preds: Sequence[int],
    confidence: float = 0.95,
    bootstrap_iterations: int = 20000,
    seed: int | None = 7,
) -> dict[str, Any]:
    """Bias-corrected live prevalence for one mode from sampled verdicts.

    The contract, precisely:

      1. ``raw`` is the uncorrected flag rate: ``mean(sample_preds)``.
      2. Compute the frozen judge's failure sensitivity and pass specificity
         from ``test_labels`` and ``test_preds``. Both use the monitoring
         convention that 1 means a failure is present. Failure sensitivity is
         the flagged fraction of human-labeled failures. Pass specificity is
         the unflagged fraction of human-labeled passes.
      3. Compute the Rogan-Gladen point estimate, then resample the held-out
         records and sampled predictions to obtain a percentile-bootstrap
         interval. Use a seeded NumPy generator so the committed result is
         reproducible.
      4. Resample the monitoring predictions and the paired held-out records
         independently with replacement. Keep their original sample sizes.
         Discard a draw if the correction cannot be computed. Clamp each
         retained estimate to [0, 1], then take the percentile interval.
         Raise ``ValueError`` if no replicate is valid.

    Args:
        sample_preds: the judge's 0/1 verdicts over the UNIFORM BASE sample
            only (never the risk strata; they are biased toward failure by
            design).
        test_labels: human labels for the frozen Homework 5 judge's test
            split.
        test_preds: the frozen judge's predictions on that test split.
        confidence: interval confidence level.
        bootstrap_iterations: number of percentile-bootstrap replicates.
        seed: numpy seed for a reproducible interval; None leaves the RNG
            untouched.

    Returns:
        {"raw", "corrected", "ci_low", "ci_high", "confidence",
         "failure_sensitivity", "pass_specificity", "n_sample"}
        with "corrected" clamped to [0, 1] and rates rounded to 4 places.

    Raises:
        ValueError: if an input is empty, the held-out inputs have different
            lengths, a value is not 0 or 1, a class is absent, the judge is
            missing a usable correction, or no bootstrap replicate is valid.
    """
    def binary(values: Sequence[int]) -> np.ndarray:
        if not len(values) or any(value not in (0, 1) for value in values):
            raise ValueError("inputs must be nonempty binary sequences")
        return np.asarray(values, dtype=int)

    sample, labels, preds = map(binary, (sample_preds, test_labels, test_preds))
    if len(labels) != len(preds):
        raise ValueError("held-out labels and predictions must have equal lengths")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")
    if type(bootstrap_iterations) is not int or bootstrap_iterations < 1:
        raise ValueError("bootstrap_iterations must be a positive integer")

    def rates(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
        if not np.any(y == 1) or not np.any(y == 0):
            raise ValueError("held-out data must contain both classes")
        sensitivity = float(p[y == 1].mean())
        specificity = float((1 - p[y == 0]).mean())
        if sensitivity + specificity <= 1:
            raise ValueError("judge has no usable Rogan-Gladen correction")
        return sensitivity, specificity

    def correct(raw: float, se: float, sp: float) -> float:
        return float(np.clip((raw + sp - 1) / (se + sp - 1), 0, 1))

    sensitivity, specificity = rates(labels, preds)
    raw = float(sample.mean())
    rng = np.random.default_rng(seed)
    retained = []
    for _ in range(bootstrap_iterations):
        sample_draw = rng.choice(sample, size=len(sample), replace=True)
        indices = rng.integers(0, len(labels), size=len(labels))
        try:
            se, sp = rates(labels[indices], preds[indices])
        except ValueError:
            continue
        retained.append(correct(float(sample_draw.mean()), se, sp))
    if not retained:
        raise ValueError("no valid bootstrap replicate")
    tail = (1 - confidence) / 2
    low, high = np.quantile(retained, [tail, 1 - tail])
    return {
        "raw": round(raw, 4),
        "corrected": round(correct(raw, sensitivity, specificity), 4),
        "ci_low": round(float(low), 4), "ci_high": round(float(high), 4),
        "confidence": confidence,
        "failure_sensitivity": round(sensitivity, 4),
        "pass_specificity": round(specificity, 4), "n_sample": len(sample),
    }
