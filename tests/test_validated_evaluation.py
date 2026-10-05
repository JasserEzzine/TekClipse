import numpy as np
import pandas as pd

from tekclipse.evaluation.validated import labeled_metrics, evaluate_held_out
from tekclipse.data.generator import generate_synthetic_dataset


def test_known_confusion_matrix_latency_and_duplicates():
    timeline = pd.date_range("2026-01-01", periods=6, freq="s", tz="UTC")
    truth = [False, False, True, True, False, False]
    result = labeled_metrics(
        timeline,
        truth,
        [timeline[0], timeline[3], timeline[3]],
        [(timeline[2], timeline[3])],
    )
    assert (result["tp"], result["fp"], result["tn"], result["fn"]) == (1, 1, 3, 1)
    assert result["precision"] == result["recall"] == result["f1"] == 0.5
    assert result["false_positive_rate"] == 0.25
    assert result["detection_rate"] == 1
    assert result["detection_latency_seconds"] == 1
    assert not labeled_metrics(timeline, None, [], [])["available"]
    assert not labeled_metrics(timeline, [None] * 6, [], [])["available"]
    nominal = labeled_metrics(timeline, np.zeros(6, dtype=bool), [], [])
    assert nominal["recall"] is None and nominal["detection_rate"] is None
    assert nominal["false_positive_rate"] == 0
    missed = labeled_metrics(timeline, truth, [], [(timeline[2], timeline[3])])
    assert missed["detection_rate"] == 0 and missed["detection_latency_seconds"] is None


def test_held_out_real_e4_and_insufficient_data():
    data = generate_synthetic_dataset(13, persist=False)
    result = evaluate_held_out(data, "E4")
    assert result["available"]
    assert pd.Timestamp(result["train_end"]) < pd.Timestamp(result["test_start"])
    assert result["comparisons"]["Hybrid"]["detection_rate"] == 1
    assert result["comparisons"]["Rules only"]["tp"] == 0
    assert not evaluate_held_out(data, "E7", train_hours=0)["available"]
    assert not evaluate_held_out(data, "E4", train_hours=13)["available"]
    assert not evaluate_held_out(data, "UNKNOWN")["available"]
