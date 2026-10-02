# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Cao Đức Hiệp
- **MSSV:** 2A202602550
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/Hipscarer03/K4-L3-DAY13-CaoDucHiep-2A202602550-Monitoring-LLMOps
- **Commit SHA cuối:** 858ea8fb963b5d80e3ef773b6e09fb1c3f5be479
- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602550`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | [evidence/01-pytest.png](evidence/01-pytest.png) |
| Log validator | [evidence/02-log-validator.png](evidence/02-log-validator.png) |
| Dashboard validator | [evidence/03-dashboard-validator.png](evidence/03-dashboard-validator.png) |
| Structured log | [evidence/04-structured-log.png](evidence/04-structured-log.png) |
| PII redaction | [evidence/05-pii-redaction.png](evidence/05-pii-redaction.png) |
| Trace list | [evidence/06-trace-list.png](evidence/06-trace-list.png) |
| Trace waterfall | [evidence/07-trace-waterfall.png](evidence/07-trace-waterfall.png) |
| Trace metadata | [evidence/08-trace-metadata.png](evidence/08-trace-metadata.png) |
| Prompt versions | [evidence/09-prompt-versions.png](evidence/09-prompt-versions.png) |
| Prompt rollback | [evidence/10-prompt-rollback.png](evidence/10-prompt-rollback.png) |
| Dashboard runtime | [evidence/11-dashboard-overview.png](evidence/11-dashboard-overview.png) |
| Incident metric | [evidence/12-incident-metric.png](evidence/12-incident-metric.png) |
| Incident log | [evidence/13-incident-log.png](evidence/13-incident-log.png) |
| Incident trace | [evidence/14-incident-trace.png](evidence/14-incident-trace.png) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 0/100 (Thiếu enrichment, chưa scrub PII) | 100/100 | Đạt toàn bộ 4 hạng mục kiểm tra, 0 lỗi PII leak, 0 missing context |
| `validate_dashboard.py` | 0/6 panel | 6/6 panel | Đầy đủ 6 panel với threshold, query, unit và aggregations chuẩn |
| `pytest` | Chưa đạt baseline | 24 passed (100%) | Toàn bộ 24 test cases pass trong 2.02s |
| Số traces hợp lệ | 0 | 17 traces | Đầy đủ traces cho baseline, candidate v2, incident và recovery |
| Số PII leak | Chưa kiểm soát | 0 | Không còn PII nguyên văn trong bất kỳ log record nào |
| Latency P95 / TTFT P95 | Chưa đo lường | 152ms / 50ms | Latency bình thường ~152ms, TTFT 50ms; khi test incident đạt 2654ms |
| Retrieval success rate | Chưa đo lường | 100% | 100% các request truy xuất context thành công |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:**
  Triển khai thông qua `CorrelationIdMiddleware` (`app/middleware.py`). Middleware kiểm tra header `x-request-id` gửi từ client; nếu không có sẽ tự động khởi tạo theo format chuẩn `req-<8-hex>` (`req-` kết hợp 8 ký tự hex từ `uuid.uuid4()`). Trước khi xử lý request, gọi `clear_contextvars()` để ngăn rò rỉ context giữa các request concurrent, sau đó gọi `bind_contextvars(correlation_id=correlation_id)`. Khi trả response, gắn `correlation_id` và `x-response-time-ms` vào header HTTP.

- **Các metadata được ghi vào structured log:**
  Các trường chuẩn bao gồm: `ts` (ISO UTC timestamp), `level`, `service`, `event`, `correlation_id`, `env`, `session_id`, `feature`, `user_id_hash` (băm SHA-256 rút gọn 12 ký tự), `model`, `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name`, `tool_success` và `payload` chứa thông tin tóm tắt an toàn (`message_preview`, `answer_preview`).

- **Cách bảo đảm PII được scrub trước khi ghi:**
  Xây dựng hàm `scrub_text` trong `app/pii.py` áp dụng regex patterns để bắt và thay thế Email, Phone VN (`+84` hoặc `09x`), CCCD 12 số, và thẻ tín dụng thành các token `[REDACTED_<TYPE>]`. Đăng ký processor `scrub_event` trong structlog pipeline ngay trước `JsonlFileProcessor()` và `JSONRenderer()`. Do đó, dữ liệu nhạy cảm được làm sạch hoàn toàn trước khi serialize xuống file `data/logs.jsonl` hoặc in ra console.

- **Cách kiểm chứng kết quả:**
  Chạy lệnh `python scripts/validate_logs.py` quét toàn bộ file `data/logs.jsonl` (38 dòng log), xác nhận đạt 100/100 điểm với 0 PII leak. Bộ kiểm thử đơn vị `tests/test_pii.py` kiểm định thành công khả năng scrub đa dạng định dạng email, số điện thoại có dấu cách/dấu chấm, CCCD và số thẻ.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
  Cấu hình biến môi trường `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` trong file `.env` trỏ trực tiếp đến project `day13-k4-l3b-2A202602550` trên Langfuse Cloud. Mọi trace được gán tag `[lab, <feature>, <model>]` và chứa metadata `correlation_id` khớp chính xác với structured log sinh ra trên máy cá nhân.

- **Cấu trúc root/retrieval/generation observations:**
  Mỗi trace là một cây phân cấp rõ ràng:
  - Root observation: `lab-agent-run` (type `agent`), bao bọc toàn bộ chu trình xử lý của agent.
  - Child observation 1: `document-retrieval` (type `span`, type_hint `retriever`), đo lường việc tìm kiếm trong corpus, output chứa danh sách context documents và số lượng doc.
  - Child observation 2: `llm-generation` (type `generation`), ghi nhận model `claude-sonnet-4-5`, input prompt text, token usage (`input` và `output`), TTFT (50ms) và chi phí ước tính.

- **Cách nối trace với log:**
  Correlation ID được bind vào cả structlog context và truyền vào `propagate_attributes(metadata={"correlation_id": correlation_id})` của Langfuse. Nhờ vậy, khi gặp một log bất thường trong `data/logs.jsonl`, có thể copy `correlation_id` và tìm thấy ngay trace tương ứng trên Langfuse.

- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 — labels `['baseline', 'production']`
- **Version/label candidate:** Version 2 — labels `['candidate', 'latest']`
- **Trace ID của mỗi version:**
  - Version 1 (production): Trace ID `3355379f0853665886477f37478de2c3` (correlation ID: `req-7fb5be72`)
  - Version 2 (candidate): Trace ID `e5bf89cbb723ae256e81c2365babb29b` (correlation ID: `req-59a3c1b2`)
- **Cách promote và rollback `production`:**
  Ứng dụng truy xuất prompt động qua `resolve_prompt` bằng nhãn `LANGFUSE_PROMPT_LABEL=production`. Để promote version candidate lên chạy chính thức, chỉ cần chuyển nhãn `production` sang Version 2 trên giao diện Langfuse. Nếu Version 2 phát sinh lỗi hoặc latency cao, thực hiện rollback tức thì bằng cách chuyển nhãn `production` trỏ lại Version 1. Ứng dụng tự động cập nhật mà không cần sửa code, không cần build lại image Docker hay khởi động lại server.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
  Cấu hình tại `config/dashboard.yaml`, bao gồm:
  1. Panel `latency`: P50, P95, P99 và TTFT P95 (đơn vị: ms, threshold P95 <= 3000ms).
  2. Panel `traffic`: Số lượng request và tần suất request mỗi phút (requests_per_minute).
  3. Panel `errors`: Tỷ lệ lỗi %, phân bố `error_type`, và tỷ lệ thành công của retrieval tool (%).
  4. Panel `cost`: Chi phí theo phút và tổng chi phí tích lũy (USD, threshold <= 2.5 USD).
  5. Panel `tokens`: Tổng lượng token in và token out (tokens, threshold <= 50,000 tokens).
  6. Panel `quality`: Điểm chất lượng trung bình theo heuristic proxy (score 0-1, threshold >= 0.75).

- **SLO và lý do chọn:**
  Primary SLO là `fast_successful_requests` với mục tiêu 99.5% request đạt thành công và có `latency_ms <= 3000ms` trong chu kỳ 28 ngày. Chọn ngưỡng 3000ms vì đây là giới hạn trên chấp nhận được cho trải nghiệm người dùng tương tác với RAG Agent trước khi cảm nhận hệ thống bị treo.

- **Cách tính error budget:**
  Với SLO 99.5% trong 28 ngày, error budget là $100\% - 99.5\% = 0.5\%$. Trong kịch bản hệ thống tiếp nhận 10,000 requests trong chu kỳ, error budget cho phép tối đa $10,000 \times 0.5\% = 50$ requests bị lỗi hoặc có độ trễ vượt quá 3000ms.

- **Ba alert và runbook tương ứng:**
  Cấu hình tại `config/alert_rules.yaml` và chi tiết tại `docs/alerts.md`:
  1. `high_latency_p95` (Warning): Kích hoạt khi `p95(latency_ms) > 3000ms` kéo dài 5 phút. Runbook: Kiểm tra panel Latency, lấy `correlation_id` của request chậm, mở trace waterfall để xem span con nào (retrieval hay generation) bị nghẽn.
  2. `high_error_rate` (Critical): Kích hoạt khi `error_rate_pct > 2%` kéo dài 3 phút. Runbook: Kiểm tra panel Errors, trích xuất log `request_failed` để phân loại lỗi (như vector store timeout), xử lý kết nối database hoặc bật fallback.
  3. `low_retrieval_success` (Warning): Kích hoạt khi `retrieval_success_rate_pct < 90%` kéo dài 5 phút. Runbook: Kiểm tra panel Errors và Quality, rà soát keyword truy vấn và bổ sung tài liệu vào corpus.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Khoảng thời gian điều tra:** 10:52:53 – 10:53:07 UTC+7 ngày 02/10/2026.
- **Triệu chứng từ metrics:** Panel Latency phát hiện độ trễ P95 tăng vọt từ 152ms lên 2654ms đối với feature `monitoring`, vượt qua ngưỡng quy định 2000ms trong `config/challenge.json`.
- **Log line và correlation ID liên quan:**
  Trích xuất từ `data/logs.jsonl` các dòng `response_sent` có latency cao:
  - `correlation_id`: `req-db64fd54` (`latency_ms`: 2653, `feature`: `monitoring`, `model`: `claude-sonnet-4-5`)
  - `correlation_id`: `req-199006c9` (`latency_ms`: 2653, `feature`: `monitoring`, `model`: `claude-sonnet-4-5`)
  - `correlation_id`: `req-78eac213` (`latency_ms`: 2652, `feature`: `monitoring`, `model`: `claude-sonnet-4-5`)
- **Trace ID và span gây ảnh hưởng:**
  Trace `a97c321f416a891290ff0e7201bed47a` (gắn liền với `req-db64fd54`) trên Langfuse cho thấy:
  - Span gốc `lab-agent-run`: 2653ms.
  - Span con `document-retrieval`: **2501ms** (chiếm 94.3% tổng thời gian request).
  - Span con `llm-generation`: 148ms (hoàn toàn bình thường).
- **Root cause:**
  Hệ thống gặp sự cố `rag_slow` (mô phỏng vector store bị tắc nghẽn/timeout khi truy xuất tài liệu cho keyword thuộc feature `monitoring`), khiến hàm retrieval mất hơn 2.5s.
- **Fix action:**
  Vô hiệu hóa incident qua endpoint `POST /incidents/rag_slow/disable`. Các request kiểm tra ngay sau đó (`req-8924732d`, `req-f4f94f9a`) có độ trễ giảm ngay về mức chuẩn 152ms.
- **Preventive measure:**
  Thiết lập timeout 1500ms cho tầng retrieval; nếu vector store không phản hồi trong 1.5s, tự động kích hoạt fallback retrieval hoặc trả context rỗng có hướng dẫn để bảo vệ SLO; đồng thời thiết lập alert `high_latency_p95` cảnh báo sớm tới kênh Slack on-call.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
  Quyết định đồng bộ Correlation ID (`x-request-id`) xuyên suốt từ Middleware HTTP qua structlog contextvars đến Langfuse trace metadata. Quyết định này giúp hợp nhất luồng quan sát từ log cục bộ đến trace chi tiết trên cloud, loại bỏ hoàn toàn tình trạng "mù thông tin" khi cần debug giữa log và trace.

- **Một lỗi/blocker đã gặp:**
  Langfuse Python SDK v4 đã vô hiệu hóa endpoint legacy `GET /api/public/traces` và trả về mã lỗi 410. Blocker này được giải quyết bằng cách chuyển đổi phương thức truy xuất sang `GET /api/public/v2/observations` theo đúng khuyến nghị của Langfuse documentation.

- **Cách tìm nguyên nhân và xử lý:**
  Áp dụng mô hình điều tra 3 lớp (Metrics → Logs → Traces):
  1. *Metrics*: Nhận diện triệu chứng bất thường (latency P95 tăng vọt tại một thời điểm).
  2. *Logs*: Lọc các bản ghi lỗi hoặc chậm trong khung giờ đó để trích xuất `correlation_id`.
  3. *Traces*: Dùng `correlation_id` mở trace waterfall trên Langfuse để khoanh vùng chính xác span con bị chậm.

- **Cách hiểu luồng Metrics → Logs → Traces:**
  Metrics cho biết "Có vấn đề gì đang xảy ra và mức độ nghiêm trọng ra sao"; Logs cho biết "Request cụ thể nào, người dùng nào bị ảnh hưởng"; Traces trả lời "Hàm nào, service nào, câu query nào bên trong code là nguyên nhân gốc rễ gây ra lỗi".

- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
  Trong sản phẩm AI, prompt cũng là code và trực tiếp quyết định hành vi, độ dài token và chi phí API. Việc tách prompt thành tài nguyên độc lập có version và label (`production`, `candidate`) cho phép triển khai và rollback an toàn mà không cần build/deploy lại phần mềm.

- **Điều quan trọng nhất đã học:**
  Kỹ năng xây dựng hệ thống quan sát toàn diện cho LLM: từ việc bảo vệ dữ liệu nhạy cảm của người dùng (PII scrubbing ngay trước khi ghi đĩa), kiểm soát ngân sách token, đến khả năng truy vết sự cố theo chuỗi bằng chứng không thể chối cãi.

- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**
  Hệ thống hiện tại sử dụng mock LLM và mock vector store phục vụ môi trường lab. Khi triển khai production thực tế, cần tích hợp semantic caching (như Redis/GPTCache) để giảm thêm chi phí và độ trễ cho các câu hỏi phổ biến.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
