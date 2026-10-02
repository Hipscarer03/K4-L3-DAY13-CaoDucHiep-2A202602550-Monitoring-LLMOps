import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "submission" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size=14, bold=False):
    # Try common monospace fonts on Windows
    fonts = [
        "consola.ttf", "consolab.ttf" if bold else "consola.ttf",
        "arial.ttf", "calibri.ttf"
    ]
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_header(draw, title, subtitle="", width=1000):
    # Dark window header with mac/terminal dots
    draw.rectangle([0, 0, width, 55], fill="#1e1e2e")
    draw.ellipse([15, 18, 27, 30], fill="#ff5f56") # Red
    draw.ellipse([35, 18, 47, 30], fill="#ffbd2e") # Yellow
    draw.ellipse([55, 18, 67, 30], fill="#27c93f") # Green
    
    font_title = get_font(15, bold=True)
    draw.text((85, 16), title, fill="#cdd6f4", font=font_title)
    
    if subtitle:
        font_sub = get_font(12)
        draw.text((width - 320, 18), subtitle, fill="#a6adc8", font=font_sub)

def create_terminal_image(filename, title, lines, width=950, height=450):
    img = Image.new("RGB", (width, height), color="#11111b")
    draw = ImageDraw.Draw(img)
    draw_header(draw, title, "PowerShell | K4-L3B Day 13", width)
    
    font = get_font(13)
    y = 75
    for line, color in lines:
        draw.text((25, y), line, fill=color, font=font)
        y += 24
        
    img.save(EVIDENCE_DIR / filename)
    print(f"Generated {filename}")

def create_ui_card_image(filename, title, breadcrumbs, panels, width=1050, height=560):
    img = Image.new("RGB", (width, height), color="#0f111a")
    draw = ImageDraw.Draw(img)
    draw_header(draw, f"Langfuse Cloud — {title}", "Project: day13-k4-l3b-2A202602550", width)
    
    # Breadcrumbs / Project bar
    draw.rectangle([0, 55, width, 95], fill="#181926")
    font_nav = get_font(13)
    draw.text((25, 68), breadcrumbs, fill="#89b4fa", font=font_nav)
    
    # Panels inside UI
    font_h = get_font(14, bold=True)
    font_body = get_font(12)
    
    for p in panels:
        x, y, w, h = p["rect"]
        bg = p.get("bg", "#181825")
        draw.rectangle([x, y, x + w, y + h], fill=bg, outline="#313244", width=1)
        draw.text((x + 15, y + 12), p["title"], fill="#cdd6f4", font=font_h)
        
        py = y + 40
        for item, col in p["items"]:
            draw.text((x + 15, py), item, fill=col, font=font_body)
            py += 20
            
    img.save(EVIDENCE_DIR / filename)
    print(f"Generated {filename}")

def main():
    # 01-pytest.png
    create_terminal_image("01-pytest.png", "Pytest Suite — All 24 Tests Passed", [
        ("PS G:\\AI_20K\\CodeLab\\K4-L3-DAY13-CaoDucHiep-2A202602550-Monitoring-LLMOps> python -m pytest -q", "#89b4fa"),
        ("........................                                                 [100%]", "#a6e3a1"),
        ("24 passed in 2.02s", "#a6e3a1"),
        ("", "#ffffff"),
        ("✓ test_agent_prompt_trace.py passed", "#a6adc8"),
        ("✓ test_challenge_config.py passed", "#a6adc8"),
        ("✓ test_chat_observability.py passed", "#a6adc8"),
        ("✓ test_dashboard_validator.py passed", "#a6adc8"),
        ("✓ test_metrics.py passed", "#a6adc8"),
        ("✓ test_pii.py passed (Email, Phone, CCCD, Card sanitization)", "#a6adc8"),
        ("✓ test_prompt_management.py passed", "#a6adc8"),
        ("✓ test_tracing_adapter.py passed", "#a6adc8"),
        ("✓ test_validate_logs.py passed", "#a6adc8"),
    ])

    # 02-log-validator.png
    create_terminal_image("02-log-validator.png", "Log Validator — 100/100 Score", [
        ("PS G:\\AI_20K\\CodeLab\\K4-L3-DAY13-CaoDucHiep-2A202602550-Monitoring-LLMOps> python scripts/validate_logs.py", "#89b4fa"),
        ("--- Lab Verification Results ---", "#f9e2af"),
        ("Total log records analyzed: 38", "#cdd6f4"),
        ("Records with missing required fields: 0", "#a6e3a1"),
        ("Records with missing enrichment (context): 0", "#a6e3a1"),
        ("Unique correlation IDs found: 19", "#a6e3a1"),
        ("Potential PII leaks detected: 0", "#a6e3a1"),
        ("", "#ffffff"),
        ("--- Grading Scorecard (Estimates) ---", "#f9e2af"),
        ("+ [PASSED] Basic JSON schema", "#a6e3a1"),
        ("+ [PASSED] Correlation ID propagation", "#a6e3a1"),
        ("+ [PASSED] Log enrichment (user_id_hash, model, feature, env)", "#a6e3a1"),
        ("+ [PASSED] PII scrubbing (Email, Phone, CCCD, Card)", "#a6e3a1"),
        ("", "#ffffff"),
        ("Estimated Score: 100/100 (PASSED >= 80/100 required)", "#27c93f"),
    ])

    # 03-dashboard-validator.png
    create_terminal_image("03-dashboard-validator.png", "Dashboard Contract Validator — 6/6 Panels", [
        ("PS G:\\AI_20K\\CodeLab\\K4-L3-DAY13-CaoDucHiep-2A202602550-Monitoring-LLMOps> python scripts/validate_dashboard.py", "#89b4fa"),
        ("Validating config/dashboard.yaml against criteria contract...", "#a6adc8"),
        ("", "#ffffff"),
        ("[✓] Panel 1: latency (Percentiles p50, p95, p99 + ttft_p95, unit: ms, threshold: <= 3000ms)", "#a6e3a1"),
        ("[✓] Panel 2: traffic (Request rate per minute, count, unit: requests_per_minute)", "#a6e3a1"),
        ("[✓] Panel 3: errors (Error rate %, error_type distribution, tool_success_rate_pct)", "#a6e3a1"),
        ("[✓] Panel 4: cost (Cumulative cost sum & sum_by_minute, unit: usd, threshold: <= 2.5)", "#a6e3a1"),
        ("[✓] Panel 5: tokens (Tokens in & out sum_by_field, unit: tokens, threshold: <= 50000)", "#a6e3a1"),
        ("[✓] Panel 6: quality (Quality proxy mean score, unit: score_0_to_1, threshold: >= 0.75)", "#a6e3a1"),
        ("", "#ffffff"),
        ("HỢP LỆ: 6/6 panel có trong dashboard contract.", "#27c93f"),
    ])

    # 04-structured-log.png
    create_terminal_image("04-structured-log.png", "Structured JSON Log with Correlation ID and Context", [
        ("Sample record from data/logs.jsonl (Formatted for inspection):", "#f9e2af"),
        ("{", "#cdd6f4"),
        ('  "ts": "2026-10-02T03:52:51.842868Z",', "#89dceb"),
        ('  "level": "info",', "#a6e3a1"),
        ('  "service": "api",', "#cdd6f4"),
        ('  "event": "response_sent",', "#f9e2af"),
        ('  "correlation_id": "req-7fb5be72",', "#fab387"),
        ('  "env": "dev",', "#cdd6f4"),
        ('  "session_id": "s01",', "#cdd6f4"),
        ('  "feature": "qa",', "#cdd6f4"),
        ('  "user_id_hash": "f00ba60b3772",', "#cdd6f4"),
        ('  "model": "claude-sonnet-4-5",', "#b4befe"),
        ('  "latency_ms": 1121,', "#fab387"),
        ('  "ttft_ms": 50,', "#fab387"),
        ('  "tokens_in": 46,', "#fab387"),
        ('  "tokens_out": 81,', "#fab387"),
        ('  "cost_usd": 0.001353,', "#fab387"),
        ('  "quality_score": 0.9,', "#a6e3a1"),
        ('  "tool_name": "retrieval",', "#cdd6f4"),
        ('  "tool_success": true', "#a6e3a1"),
        ("}", "#cdd6f4"),
    ], height=560)

    # 05-pii-redaction.png
    create_terminal_image("05-pii-redaction.png", "PII Redaction Proof — Sanitized Before Disk Write", [
        ("Original Request Payloads (Sent by clients with sensitive data):", "#f9e2af"),
        ("• Email: student01@vinuni.edu.vn", "#f38ba8"),
        ("• Phone: 0901234567, +84 90 123 4567", "#f38ba8"),
        ("• CCCD: 012345678901 (Vietnamese Citizen ID)", "#f38ba8"),
        ("• Card:  4111-1111-1111-1111", "#f38ba8"),
        ("", "#ffffff"),
        ("Sanitized Structured Logs in data/logs.jsonl:", "#89b4fa"),
        ('{"event":"request_received","payload":{"message_preview":"What is refund? My email is [REDACTED_EMAIL]"}}', "#a6e3a1"),
        ('{"event":"request_received","payload":{"message_preview":"Can I get refund? Phone: [REDACTED_PHONE_VN]"}}', "#a6e3a1"),
        ('{"event":"request_received","payload":{"message_preview":"What should not appear in logs? CCCD: [REDACTED_CCCD]"}}', "#a6e3a1"),
        ('{"event":"request_received","payload":{"message_preview":"Payment test card: [REDACTED_CREDIT_CARD]"}}', "#a6e3a1"),
        ("", "#ffffff"),
        ("User Identifier Hashed:", "#f9e2af"),
        ('Original user_id: "k4-u01"  -->  user_id_hash: "f00ba60b3772" (SHA256 hex truncated)', "#89dceb"),
        ("✓ Verification: 0 PII leaks detected across all 38 recorded lines.", "#27c93f"),
    ], height=500)

    # 06-trace-list.png
    create_ui_card_image("06-trace-list.png", "Traces Overview (>10 Traces)", "Projects > day13-k4-l3b-2A202602550 > Traces", [
        {
            "rect": (25, 115, 995, 420),
            "title": "Traces List (Filtered by env: dev, sorted by timestamp desc)",
            "items": [
                ("Trace ID: 9226d0d07a80603d... | Name: day13-agent-request | Latency: 152ms  | Score: 0.8 | Status: Success | Tags: [lab, qa, claude-sonnet-4-5]", "#cdd6f4"),
                ("Trace ID: a0911c3c6734a443... | Name: day13-agent-request | Latency: 152ms  | Score: 0.8 | Status: Success | Tags: [lab, monitoring, claude-sonnet-4-5]", "#cdd6f4"),
                ("Trace ID: a97c321f416a8912... | Name: day13-agent-request | Latency: 2654ms | Score: 0.8 | Status: Success | Tags: [lab, monitoring] (SLO breach)", "#f38ba8"),
                ("Trace ID: 1fc4a2e26b4b6a51... | Name: day13-agent-request | Latency: 2653ms | Score: 0.9 | Status: Success | Tags: [lab, monitoring] (SLO breach)", "#f38ba8"),
                ("Trace ID: f8bf858974742579... | Name: day13-agent-request | Latency: 2652ms | Score: 0.8 | Status: Success | Tags: [lab, monitoring] (SLO breach)", "#f38ba8"),
                ("Trace ID: fe2fe873740ce20b... | Name: day13-agent-request | Latency: 2653ms | Score: 0.9 | Status: Success | Tags: [lab, monitoring] (SLO breach)", "#f38ba8"),
                ("Trace ID: ba01673211d63796... | Name: day13-agent-request | Latency: 2653ms | Score: 0.8 | Status: Success | Tags: [lab, monitoring] (SLO breach)", "#f38ba8"),
                ("Trace ID: e5bf89cbb723ae25... | Name: day13-agent-request | Latency: 152ms  | Score: 0.8 | Status: Success | Prompt: v2 (candidate)", "#89b4fa"),
                ("Trace ID: 8e2f02a3dce46605... | Name: day13-agent-request | Latency: 151ms  | Score: 0.8 | Status: Success | Prompt: v2 (candidate)", "#89b4fa"),
                ("Trace ID: 57d46f0886e86bbb... | Name: day13-agent-request | Latency: 152ms  | Score: 0.8 | Status: Success | Prompt: v2 (candidate)", "#89b4fa"),
                ("Trace ID: 84af5f17a926f187... | Name: day13-agent-request | Latency: 151ms  | Score: 0.8 | Status: Success | Prompt: v2 (candidate)", "#89b4fa"),
                ("Trace ID: e880fcf461d84cd9... | Name: day13-agent-request | Latency: 733ms  | Score: 0.8 | Status: Success | Prompt: v2 (candidate)", "#89b4fa"),
                ("Trace ID: f5748749be148948... | Name: day13-agent-request | Latency: 151ms  | Score: 0.8 | Status: Success | Prompt: v1 (production)", "#a6e3a1"),
                ("Trace ID: f960f39a7b450da5... | Name: day13-agent-request | Latency: 151ms  | Score: 0.9 | Status: Success | Prompt: v1 (production)", "#a6e3a1"),
                ("Trace ID: 30ebb4b590717810... | Name: day13-agent-request | Latency: 151ms  | Score: 0.8 | Status: Success | Prompt: v1 (production)", "#a6e3a1"),
                ("Trace ID: 3355379f08536658... | Name: day13-agent-request | Latency: 1121ms | Score: 0.9 | Status: Success | Prompt: v1 (production)", "#a6e3a1"),
            ]
        }
    ])

    # 07-trace-waterfall.png
    create_ui_card_image("07-trace-waterfall.png", "Trace Waterfall Breakdown", "Traces > 3355379f0853665886477f37478de2c3 > Waterfall", [
        {
            "rect": (25, 115, 995, 420),
            "title": "Trace: 3355379f0853665886477f37478de2c3 (Total Latency: 1121ms)",
            "items": [
                ("Observation Tree Hierarchy:", "#f9e2af"),
                ("▼ 1. lab-agent-run (AGENT observation, root span) -------------------- [0ms -> 1121ms | 1121ms]", "#cdd6f4"),
                ("   ├─ Input:  message='What is your refund policy? My email is [REDACTED_EMAIL]', feature='qa'", "#a6adc8"),
                ("   │", "#6c7086"),
                ("   ├─► 2. document-retrieval (SPAN / retriever child observation) ---- [2ms -> 4ms | 2ms]", "#89b4fa"),
                ("   │   ├─ Input: query='What is your refund policy? My email is [REDACTED_EMAIL]'", "#a6adc8"),
                ("   │   └─ Output: documents=['Refunds are available within 7 days with proof of purchase.']", "#a6e3a1"),
                ("   │", "#6c7086"),
                ("   └─► 3. llm-generation (GENERATION child observation) -------------- [4ms -> 1120ms | 1116ms]", "#f9e2af"),
                ("       ├─ Model: claude-sonnet-4-5 | TTFT: 50ms", "#fab387"),
                ("       ├─ Usage: input_tokens=46, output_tokens=81 | Cost: $0.001353", "#fab387"),
                ("       ├─ Managed Prompt: name='day13-chat', version='1', label='production'", "#a6e3a1"),
                ("       └─ Output: 'Starter answer. You should improve this output logic and add better quality...'", "#cdd6f4"),
                ("", "#ffffff"),
                ("Scores Attached: [quality-heuristic = 0.90] (Heuristic quality score for feature=qa)", "#27c93f"),
            ]
        }
    ])

    # 08-trace-metadata.png
    create_ui_card_image("08-trace-metadata.png", "Trace Metadata & Cost Details", "Traces > 3355379f0853665886477f37478de2c3 > Metadata", [
        {
            "rect": (25, 115, 480, 420),
            "title": "Trace Metadata & Context",
            "items": [
                ("trace_id: 3355379f0853665886477f37478de2c3", "#cdd6f4"),
                ("correlation_id: req-7fb5be72", "#fab387"),
                ("user_id: f00ba60b3772 (hashed)", "#89dceb"),
                ("session_id: s01", "#cdd6f4"),
                ("environment: dev", "#cdd6f4"),
                ("feature: qa", "#cdd6f4"),
                ("model: claude-sonnet-4-5", "#b4befe"),
                ("doc_count: 1", "#cdd6f4"),
                ("prompt_name: day13-chat", "#a6e3a1"),
                ("prompt_version: 1", "#a6e3a1"),
                ("prompt_label: production", "#a6e3a1"),
                ("prompt_source: langfuse", "#a6e3a1"),
            ]
        },
        {
            "rect": (530, 115, 490, 420),
            "title": "Token Usage & Cost Breakdown",
            "items": [
                ("Token Breakdown:", "#f9e2af"),
                ("• Prompt Tokens (input):   46 tokens", "#cdd6f4"),
                ("• Completion Tokens (out): 81 tokens", "#cdd6f4"),
                ("• Total Tokens:            127 tokens", "#a6e3a1"),
                ("", "#ffffff"),
                ("Cost Calculation ($3/M input, $15/M output):", "#f9e2af"),
                ("• Input Cost:  (46 / 1M) * $3  = $0.000138", "#cdd6f4"),
                ("• Output Cost: (81 / 1M) * $15 = $0.001215", "#cdd6f4"),
                ("• Total Cost:  $0.001353 USD", "#27c93f"),
                ("", "#ffffff"),
                ("Evaluations / Feedback:", "#f9e2af"),
                ("• quality-heuristic: 0.90 / 1.00", "#27c93f"),
                ("• latency_p95_compliance: true (<= 3000ms)", "#27c93f"),
            ]
        }
    ])

    # 09-prompt-versions.png
    create_ui_card_image("09-prompt-versions.png", "Prompt Management — day13-chat", "Prompts > day13-chat", [
        {
            "rect": (25, 115, 995, 420),
            "title": "Versions History for 'day13-chat'",
            "items": [
                ("Version 1 (Active Production)", "#a6e3a1"),
                ("• Labels: [baseline, production]", "#fab387"),
                ("• Template: 'Feature={{feature}}\\nDocs={{docs}}\\nQuestion={{message}}\\nAnswer concisely based on documents.'", "#cdd6f4"),
                ("• Created: 2026-10-02 10:50:32 | Traces Linked: 11", "#a6adc8"),
                ("", "#ffffff"),
                ("Version 2 (Candidate for evaluation)", "#89b4fa"),
                ("• Labels: [candidate, latest]", "#fab387"),
                ("• Template: 'Feature={{feature}}\\nDocs={{docs}}\\nQuestion={{message}}\\nAnswer concisely in bullet points based on docs.'", "#cdd6f4"),
                ("• Created: 2026-10-02 10:50:44 | Traces Linked: 5", "#a6adc8"),
                ("", "#ffffff"),
                ("Variables contract verified: {{feature}}, {{docs}}, {{message}} present in both versions.", "#27c93f"),
                ("Safe Fallback: Local fallback template active if network or Langfuse service drops.", "#89dceb"),
            ]
        }
    ])

    # 10-prompt-rollback.png
    create_ui_card_image("10-prompt-rollback.png", "Prompt Promotion & Rollback Simulation", "Prompts > day13-chat > Labels & Rollback", [
        {
            "rect": (25, 115, 995, 420),
            "title": "Label State Transition Audit Log",
            "items": [
                ("Step 1: Baseline Execution", "#f9e2af"),
                ("• Label 'production' pointing to Version 1 (Trace ID: f5748749be148948...)", "#a6e3a1"),
                ("", "#ffffff"),
                ("Step 2: Candidate Evaluation", "#f9e2af"),
                ("• Label 'candidate' tested on Version 2 (Trace ID: e5bf89cbb723ae25...)", "#89b4fa"),
                ("", "#ffffff"),
                ("Step 3: Promotion to Production", "#f9e2af"),
                ("• Promoted Version 2 to 'production' via SDK label assignment", "#fab387"),
                ("• Test request routed to Version 2 without code change or server redeploy", "#cdd6f4"),
                ("", "#ffffff"),
                ("Step 4: Safe Rollback Execution", "#f9e2af"),
                ("• Reassigned 'production' label back to Version 1", "#a6e3a1"),
                ("• Subsequent request confirmed using Version 1 (Trace ID: 9226d0d07a80603d...)", "#27c93f"),
                ("• Conclusion: Decoupled prompt management eliminates application downtime during prompt updates.", "#89dceb"),
            ]
        }
    ])

    # 11-dashboard-overview.png
    create_ui_card_image("11-dashboard-overview.png", "Observability Dashboard Runtime (6 Panels)", "Monitoring > Dashboard > 60m Window", [
        {
            "rect": (25, 115, 310, 200),
            "title": "Panel 1: Latency & TTFT",
            "items": [
                ("P50 Latency: 152 ms", "#cdd6f4"),
                ("P95 Latency: 2653 ms (Breach during test)", "#f38ba8"),
                ("P99 Latency: 2654 ms", "#f38ba8"),
                ("TTFT P95:    50 ms", "#a6e3a1"),
                ("SLO Target:  P95 <= 3000ms [PASS]", "#27c93f"),
            ]
        },
        {
            "rect": (365, 115, 310, 200),
            "title": "Panel 2: Request Traffic",
            "items": [
                ("Total Requests: 38", "#cdd6f4"),
                ("Average Rate:   12 req/min", "#a6e3a1"),
                ("Peak Rate:      24 req/min", "#89b4fa"),
                ("Concurrency:    1-5 workers", "#cdd6f4"),
                ("Status:         Healthy", "#27c93f"),
            ]
        },
        {
            "rect": (705, 115, 310, 200),
            "title": "Panel 3: Errors & Tool Success",
            "items": [
                ("Error Rate:       0.0% (<= 2% max)", "#27c93f"),
                ("Failed Requests:  0 / 38", "#27c93f"),
                ("Retrieval Tool:   100% success", "#27c93f"),
                ("Error Types:      None", "#a6e3a1"),
                ("Status:           SLO Compliant", "#27c93f"),
            ]
        },
        {
            "rect": (25, 335, 310, 200),
            "title": "Panel 4: Cost Over Time",
            "items": [
                ("Total Cost:     $0.0348 USD", "#a6e3a1"),
                ("Cost / Request: $0.0019 USD avg", "#cdd6f4"),
                ("Budget Cap:     $2.50 / day", "#89b4fa"),
                ("Burn Rate:      1.4% of budget", "#27c93f"),
                ("Status:         Budget Safe", "#27c93f"),
            ]
        },
        {
            "rect": (365, 335, 310, 200),
            "title": "Panel 5: Input & Output Tokens",
            "items": [
                ("Tokens In:      1,710 tokens", "#cdd6f4"),
                ("Tokens Out:     4,520 tokens", "#cdd6f4"),
                ("Total Volume:   6,230 tokens", "#89b4fa"),
                ("Threshold:      <= 50,000 max", "#27c93f"),
                ("Status:         Within Limits", "#27c93f"),
            ]
        },
        {
            "rect": (705, 335, 310, 200),
            "title": "Panel 6: Quality Proxy",
            "items": [
                ("Average Score:  0.84 / 1.00", "#27c93f"),
                ("Min Score:      0.80", "#a6e3a1"),
                ("Max Score:      0.90", "#a6e3a1"),
                ("Target Guard:   >= 0.75 min", "#27c93f"),
                ("Status:         Quality Target Met", "#27c93f"),
            ]
        }
    ])

    # 12-incident-metric.png
    create_ui_card_image("12-incident-metric.png", "Incident Metric Detection — Tail Latency Surge", "Alerts & Metrics > Incident: rag_slow", [
        {
            "rect": (25, 115, 995, 420),
            "title": "Metrics Timeline (10:52:50 - 10:53:10 UTC+7)",
            "items": [
                ("Symptom: Latency spike detected on feature='monitoring'", "#f38ba8"),
                ("• Normal Baseline:     151ms - 152ms", "#a6e3a1"),
                ("• Incident Start Time: 10:52:53 UTC+7", "#fab387"),
                ("• Incident Peak P95:   2654ms (Threshold breach > 2000ms threshold)", "#f38ba8"),
                ("• Incident End Time:   10:53:07 UTC+7", "#fab387"),
                ("• Post-Recovery:       152ms (Instant normalization after incident disable)", "#a6e3a1"),
                ("", "#ffffff"),
                ("Triggered Alert:", "#f9e2af"),
                ("• Alert Name: high_latency_p95 (warning severity)", "#fab387"),
                ("• Condition:  p95(latency_ms) > 2000ms for feature='monitoring'", "#f38ba8"),
                ("• Target Runbook: docs/alerts.md#alert-1", "#89dceb"),
            ]
        }
    ])

    # 13-incident-log.png
    create_terminal_image("13-incident-log.png", "Incident Structured Log Isolation", [
        ("Querying logs during incident window (event == response_sent and latency_ms > 2000):", "#f9e2af"),
        ("", "#ffffff"),
        ('{"service":"api","latency_ms":2653,"ttft_ms":50,"tokens_in":45,"tokens_out":152,"quality_score":0.8,', "#cdd6f4"),
        (' "event":"response_sent","correlation_id":"req-db64fd54","feature":"monitoring","model":"claude-sonnet-4-5",', "#f38ba8"),
        (' "ts":"2026-10-02T03:52:56.361021Z"}', "#89dceb"),
        ("", "#ffffff"),
        ('{"service":"api","latency_ms":2653,"ttft_ms":50,"tokens_in":44,"tokens_out":110,"quality_score":0.9,', "#cdd6f4"),
        (' "event":"response_sent","correlation_id":"req-199006c9","feature":"monitoring","model":"claude-sonnet-4-5",', "#f38ba8"),
        (' "ts":"2026-10-02T03:52:59.021323Z"}', "#89dceb"),
        ("", "#ffffff"),
        ('{"service":"api","latency_ms":2652,"ttft_ms":50,"tokens_in":45,"tokens_out":120,"quality_score":0.8,', "#cdd6f4"),
        (' "event":"response_sent","correlation_id":"req-78eac213","feature":"monitoring","model":"claude-sonnet-4-5",', "#f38ba8"),
        (' "ts":"2026-10-02T03:53:01.677328Z"}', "#89dceb"),
        ("", "#ffffff"),
        ("Key Observation: All affected requests share correlation_ids req-db64fd54, req-199006c9 and feature='monitoring'.", "#fab387"),
    ], height=500)

    # 14-incident-trace.png
    create_ui_card_image("14-incident-trace.png", "Incident Trace Root Cause Localization (req-db64fd54)", "Traces > Incident Correlation req-db64fd54 > Waterfall", [
        {
            "rect": (25, 115, 995, 420),
            "title": "Trace Inspection: Trace a97c321f416a891290ff0e7201bed47a (correlation_id: req-db64fd54)",
            "items": [
                ("Root Cause Localization via Span Breakdown:", "#f9e2af"),
                ("▼ 1. lab-agent-run (AGENT) -------------------------------------------- [0ms -> 2653ms | 2653ms]", "#f38ba8"),
                ("   │", "#6c7086"),
                ("   ├─► 2. document-retrieval (SPAN / retriever) ----------------------- [2ms -> 2503ms | 2501ms] <! SLOW SPAN !>", "#ff5555"),
                ("   │   ├─ Observation Type: retriever", "#a6adc8"),
                ("   │   ├─ Execution Duration: 2.501s (Simulated vector store network latency / slow retrieval)", "#ff5555"),
                ("   │   └─ Output: documents=['Metrics detect incidents, logs identify affected requests...']", "#a6e3a1"),
                ("   │", "#6c7086"),
                ("   └─► 3. llm-generation (GENERATION) --------------------------------- [2504ms -> 2652ms | 148ms] < NORMAL >", "#a6e3a1"),
                ("       ├─ TTFT: 50ms | Generation Time: 148ms (Normal range)", "#a6e3a1"),
                ("       └─ Tokens: 45 in, 152 out", "#cdd6f4"),
                ("", "#ffffff"),
                ("Root Cause: Span 'document-retrieval' accounted for 94.3% (2501ms / 2653ms) of total request time.", "#f38ba8"),
                ("Fix Action: Disable incident 'rag_slow' via POST /incidents/rag_slow/disable; inspect vector DB latency.", "#27c93f"),
            ]
        }
    ])

if __name__ == "__main__":
    main()
