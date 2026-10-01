# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `high_latency_p95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 phải ≤ 3000ms (theo `primary_slo` trong `config/slo.yaml`)
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ quá lâu để nhận câu trả lời, trải nghiệm kém và có thể bỏ cuộc
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Latency** để xác nhận P50/P95/P99 và TTFT; xác định khoảng thời gian latency tăng đột biến.
  2. Lọc `data/logs.jsonl` với `event == "response_sent"` trong khoảng thời gian đó, lấy các `correlation_id` có `latency_ms > 3000`.
  3. Mở trace cùng `correlation_id` trên Langfuse, kiểm tra span `document-retrieval` và `llm-generation` để xác định bước nào gây chậm (ví dụ: `rag_slow` incident có thể làm retrieval mất >2.5s).
- Mitigation tạm thời: nếu do RAG chậm, tắt incident `rag_slow` qua `POST /incidents/rag_slow/disable`; nếu do prompt version mới nặng hơn, rollback label `production` về version cũ trên Langfuse và restart API.
- Owner: `student-2A202602550`

## Alert 2

- Tên: `high_error_rate`
- Severity: `critical`
- Duration: `3m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: error rate ≤ 2% (theo `guardrails.error_rate_pct_max` trong `config/slo.yaml`)
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` liên tục trong 3 phút
- Ảnh hưởng tới người dùng: request bị lỗi hoàn toàn, người dùng không nhận được câu trả lời, nhận HTTP 500
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Errors** để xác nhận error rate và phân loại `error_type` (RuntimeError, TimeoutError, v.v.).
  2. Lọc `data/logs.jsonl` với `event == "request_failed"`, lấy `correlation_id` và `error_type` để xác định loại lỗi phổ biến.
  3. Mở trace cùng `correlation_id` trên Langfuse, kiểm tra span nào bị lỗi — thường là `document-retrieval` nếu `tool_fail` đang active (ví dụ: "Vector store timeout").
- Mitigation tạm thời: tắt incident `tool_fail` qua `POST /incidents/tool_fail/disable`; kiểm tra kết nối vector store; nếu error rate không giảm, chuyển sang fallback retrieval hoặc tạm thời disable RAG.
- Owner: `student-2A202602550`

## Alert 3

- Tên: `low_retrieval_success`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: retrieval success rate ≥ 90% (theo `guardrails.retrieval_success_rate_pct_min` trong `config/slo.yaml`)
- Điều kiện và thời gian duy trì: `retrieval_success_rate_pct < 90%` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: câu trả lời không có context phù hợp, quality giảm, người dùng nhận câu trả lời chung chung và không chính xác
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Errors** để xác nhận `tool_success_rate_pct` giảm; kiểm tra dashboard panel **Quality** để xem quality proxy có đang giảm tương ứng không.
  2. Lọc `data/logs.jsonl` với `tool_success == false` hoặc `tool_name == "retrieval"`, lấy các `correlation_id` để phân tích.
  3. Mở trace cùng `correlation_id` trên Langfuse, kiểm tra span `document-retrieval` — xem `output.documents` có trả về "No domain document matched" hay không, và `input.query` có chứa keyword khớp với corpus hay không.
- Mitigation tạm thời: mở rộng corpus trong `mock_rag.py` để cover thêm keyword; nếu do incident `tool_fail`, tắt nó qua `POST /incidents/tool_fail/disable`; kiểm tra xem prompt có hướng dẫn user đặt câu hỏi cụ thể hơn không.
- Owner: `student-2A202602550`
