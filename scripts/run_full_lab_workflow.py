import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Ensure REPO_ROOT is in path and env is loaded
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

from starlette.testclient import TestClient
from app.main import app
from app.tracing import flush_langfuse, get_langfuse_client
from app.incidents import enable, disable, status

def run_workflow():
    log_file = REPO_ROOT / "data" / "logs.jsonl"
    # Clear log file to ensure clean evaluation without stale data
    if log_file.exists():
        log_file.unlink()
    
    records = []

    with TestClient(app) as client:
        # Check health
        health = client.get("/health").json()
        print("Initial Health:", health)

        # 1. Batch Baseline (Prompt v1, Production)
        os.environ["LANGFUSE_PROMPT_LABEL"] = "production"
        baseline_queries = [
            {"user_id": "k4-u01", "session_id": "s01", "feature": "qa", "message": "What is your refund policy? My email is student01@vinuni.edu.vn"},
            {"user_id": "k4-u02", "session_id": "s02", "feature": "policy", "message": "Can I get my money back within 7 days? Phone: 0901234567"},
            {"user_id": "k4-u03", "session_id": "s03", "feature": "summary", "message": "Summarize monitoring policies for production LLMOps."},
            {"user_id": "k4-u04", "session_id": "s04", "feature": "qa", "message": "What should not appear in application logs? CCCD: 012345678901"},
            {"user_id": "k4-u05", "session_id": "s05", "feature": "qa", "message": "Credit card policy payment test: 4111-1111-1111-1111"},
        ]

        print("\n--- Running Baseline Batch (Prompt v1 - production) ---")
        for q in baseline_queries:
            r = client.post("/chat", json=q)
            res = r.json()
            corr_id = res["correlation_id"]
            records.append({
                "batch": "baseline",
                "label": "production",
                "prompt_ver": "1",
                "corr_id": corr_id,
                "latency_ms": res["latency_ms"],
                "quality": res["quality_score"],
                "cost": res["cost_usd"]
            })
            print(f"[Baseline] {corr_id} | {q['feature']} | {res['latency_ms']}ms | Q={res['quality_score']}")

        # 2. Batch Candidate (Prompt v2, Candidate)
        os.environ["LANGFUSE_PROMPT_LABEL"] = "candidate"
        candidate_queries = [
            {"user_id": "k4-u06", "session_id": "s06", "feature": "policy", "message": "Explain PII redaction policy clearly and concisely."},
            {"user_id": "k4-u07", "session_id": "s07", "feature": "qa", "message": "How do metrics, traces, and logs collaborate in LLMOps?"},
            {"user_id": "k4-u08", "session_id": "s08", "feature": "summary", "message": "Summarize the vector store retrieval guidelines."},
            {"user_id": "k4-u09", "session_id": "s09", "feature": "qa", "message": "What are the key SLI/SLO metrics for an AI service?"},
            {"user_id": "k4-u10", "session_id": "s10", "feature": "policy", "message": "How does prompt versioning enable safe rollbacks?"},
        ]

        print("\n--- Running Candidate Batch (Prompt v2 - candidate) ---")
        for q in candidate_queries:
            r = client.post("/chat", json=q)
            res = r.json()
            corr_id = res["correlation_id"]
            records.append({
                "batch": "candidate",
                "label": "candidate",
                "prompt_ver": "2",
                "corr_id": corr_id,
                "latency_ms": res["latency_ms"],
                "quality": res["quality_score"],
                "cost": res["cost_usd"]
            })
            print(f"[Candidate] {corr_id} | {q['feature']} | {res['latency_ms']}ms | Q={res['quality_score']}")

        # 3. Batch Incident (Challenge: rag_slow)
        print("\n--- Injecting Incident: rag_slow ---")
        client.post("/incidents/rag_slow/enable")
        os.environ["LANGFUSE_PROMPT_LABEL"] = "production"

        challenge_file = REPO_ROOT / "config" / "challenge.json"
        challenge_data = json.loads(challenge_file.read_text(encoding="utf-8"))
        challenge_queries = challenge_data["queries"]

        print(f"--- Running Official Challenge Batch ({challenge_data['challenge_id']}) ---")
        for q in challenge_queries:
            r = client.post("/chat", json=q)
            res = r.json()
            corr_id = res["correlation_id"]
            records.append({
                "batch": "challenge_incident",
                "label": "production",
                "prompt_ver": "1",
                "corr_id": corr_id,
                "latency_ms": res["latency_ms"],
                "quality": res["quality_score"],
                "cost": res["cost_usd"]
            })
            print(f"[Challenge - Slow] {corr_id} | {q['feature']} | {res['latency_ms']}ms (SLO Breach > 2000ms!)")

        # 4. Recovery (Disable incident)
        print("\n--- Recovering: Disabling Incident rag_slow ---")
        client.post("/incidents/rag_slow/disable")
        recovery_queries = [
            {"user_id": "k4-u01", "session_id": "s01", "feature": "qa", "message": "Verify recovery after fixing vector store latency."},
            {"user_id": "k4-u02", "session_id": "s02", "feature": "monitoring", "message": "Confirm tail latency back within normal SLO boundaries."}
        ]
        for q in recovery_queries:
            r = client.post("/chat", json=q)
            res = r.json()
            corr_id = res["correlation_id"]
            records.append({
                "batch": "recovery",
                "label": "production",
                "prompt_ver": "1",
                "corr_id": corr_id,
                "latency_ms": res["latency_ms"],
                "quality": res["quality_score"],
                "cost": res["cost_usd"]
            })
            print(f"[Recovered] {corr_id} | {q['feature']} | {res['latency_ms']}ms")

    flush_langfuse()
    time.sleep(2)

    # Save run summary
    summary_path = REPO_ROOT / "submission" / "evidence" / "run_summary.json"
    summary_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nCompleted {len(records)} requests successfully. Run summary saved to {summary_path}")

if __name__ == "__main__":
    run_workflow()
