# -*- coding: utf-8 -*-
"""
test_latency.py
Goal: Profile the redaction + provenance pipeline and report P50/P95 latencies.
"""

import time
import statistics
import json
import os
from app.pipeline import pipeline

SYNTHETIC_TRANSCRIPT = (
    "I have had a headache for the past three days, and also developed a fever.\n"
    "In the last two days I started coughing with some yellow phlegm, and my throat hurts when I talk a lot.\n"
    "Yesterday I had diarrhea twice and some dull stomach pain.\n"
    "Occasionally I feel palpitations, but they go away quickly."
)

def test_latency_reports_p50_p95(tmp_path):
    times = []
    for _ in range(50):
        t0 = time.perf_counter()
        pipeline(SYNTHETIC_TRANSCRIPT)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)  # milliseconds

    p50 = statistics.median(times)
    p95 = statistics.quantiles(times, n=100)[94]  # approximate 95th percentile

    report = {"p50_ms": p50, "p95_ms": p95, "n": len(times)}
    out = tmp_path / "latency_report.json"
    out.write_text(json.dumps(report, indent=2))

    # Assertions
    assert report["p50_ms"] > 0
    assert report["p95_ms"] >= report["p50_ms"]
    assert os.path.exists(out)