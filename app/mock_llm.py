from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE
from .tracing import get_langfuse_client, tracing_enabled


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str
    ttft_ms: int


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    def generate(self, prompt: str) -> FakeResponse:
        """Generate a response from the mock LLM.

        Instrumented as a Langfuse 'generation' observation, capturing:
        - Model name for model comparison / filtering
        - Input prompt and output text
        - Token usage (input_tokens, output_tokens) for cost calculation
        - Time-to-first-token (TTFT) as metadata
        """
        langfuse = get_langfuse_client()

        if tracing_enabled():
            with langfuse.start_as_current_observation(
                as_type="generation",
                name="llm-generation",
                model=self.model,
                input={"prompt": prompt},
            ) as generation:
                response = self._do_generate(prompt)
                generation.update(
                    output=response.text,
                    usage_details={
                        "input": response.usage.input_tokens,
                        "output": response.usage.output_tokens,
                    },
                    metadata={
                        "ttft_ms": response.ttft_ms,
                        "model": self.model,
                    },
                )
                return response
        else:
            return self._do_generate(prompt)

    def _do_generate(self, prompt: str) -> FakeResponse:
        """Core generation logic, separated for clean instrumentation."""
        started = time.perf_counter()
        time.sleep(0.05)  # mô phỏng thời điểm token đầu tiên sẵn sàng
        ttft_ms = int((time.perf_counter() - started) * 1000)
        time.sleep(0.10)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
        answer = (
            "Starter answer. You should improve this output logic and add better quality checks. "
            "Use retrieved context and keep responses concise."
        )
        return FakeResponse(
            text=answer,
            usage=FakeUsage(input_tokens, output_tokens),
            model=self.model,
            ttft_ms=ttft_ms,
        )
