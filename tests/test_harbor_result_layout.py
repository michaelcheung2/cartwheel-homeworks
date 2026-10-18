"""The real Harbor 0.23 split-file layout must preserve outcomes and order."""

import json

import pytest

from harbor_adapter.results import load_job_result


def test_split_layout_preserves_raw_summary_order_rewards_and_errors(tmp_path):
    raw = '{"n_total_trials": 2, "stats": {"n_completed_trials": 2}}\n'
    (tmp_path / "result.json").write_text(raw)
    for name, timestamp, reward, error in (
        ("z-first", "2026-10-18T20:00:00Z", 0.0, None),
        ("a-second", "2026-10-18T20:01:00Z", None, {"exception_type": "TransportError"}),
    ):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "result.json").write_text(json.dumps({
            "trial_name": name, "started_at": timestamp,
            "verifier_result": {"rewards": {"reward": reward}}, "exception_info": error,
        }))
    indexed = load_job_result(tmp_path)
    assert (tmp_path / "harbor-result.json").read_text() == raw
    assert [t["trial_name"] for t in indexed["trial_results"]] == ["z-first", "a-second"]
    assert indexed["trial_results"][0]["verifier_result"]["rewards"]["reward"] == 0.0
    assert indexed["trial_results"][1]["exception_info"] == {"exception_type": "TransportError"}
    assert load_job_result(tmp_path) == indexed


def test_split_layout_rejects_missing_trial_files(tmp_path):
    (tmp_path / "result.json").write_text('{"n_total_trials": 5}')
    with pytest.raises(ValueError, match="total trial count"):
        load_job_result(tmp_path)
    assert not (tmp_path / "harbor-result.json").exists()


def test_inline_layout_keeps_original_trial_order(tmp_path):
    result = {"trial_results": [{"trial_name": "second"}, {"trial_name": "first"}]}
    (tmp_path / "result.json").write_text(json.dumps(result))
    assert load_job_result(tmp_path) == result
    assert not (tmp_path / "harbor-result.json").exists()
