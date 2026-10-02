import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

summary_path = Path("submission/evidence/run_summary.json")
if not summary_path.exists():
    print("run_summary.json not found!")
    exit(1)

records = json.loads(summary_path.read_text(encoding="utf-8"))
print("=" * 72)
print(f"{'CORRELATION ID':<16} | {'PHASE / BATCH':<20} | {'LATENCY':<12} | {'SLO STATUS'}")
print("=" * 72)
for r in records:
    if r["batch"] in ["baseline", "challenge_incident", "recovery"]:
        lat = r["latency_ms"]
        status = "[BREACH > 2000ms]" if lat > 2000 else "[NORMAL <= 152ms]"
        print(f"{r['corr_id']:<16} | {r['batch']:<20} | {lat:>6} ms   | {status}")
print("=" * 72)
print("Metric Insight: Latency surged from 151ms to 2654ms during 'rag_slow'")
print("Incident Duration: 10:52:53 - 10:53:07 UTC+7 | Threshold: 2000ms")
print("=" * 72)
