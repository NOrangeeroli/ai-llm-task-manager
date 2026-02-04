from typing import Any

import httpx


class LLMClient:
    """
    Thin abstraction over an LLM provider.

    - For provider == 'openai' and an API key is set, uses the OpenAI chat
      completions endpoint.
    - Otherwise falls back to a local stub for easy testing.
    """

    def __init__(self, provider: str, api_key: str | None = None) -> None:
        self.provider = provider
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        """
        Generate a completion for the given prompt.
        """
        if self.provider == "openai" and self.api_key:
            try:
                resp = httpx.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as exc:  # noqa: BLE001
                # Fall back to a stubbed response but include error info.
                return f"[openai error] {exc}"

        if self.provider == "qwen" and self.api_key:
            try:
                resp = httpx.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "qwen-plus",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as exc:  # noqa: BLE001
                return f"[qwen error] {exc}"

        # Default stub behaviour (for 'stub' or missing key)
        return f"[{self.provider} stub] {prompt}"

    def embed(self, text: str) -> list[float]:
        """
        Return an embedding vector for the given text.

        - For provider == 'openai' and an API key is set, uses the OpenAI
          embeddings endpoint.
        - For provider == 'qwen' and an API key is set, calls the Qwen
          embeddings endpoint (DashScope-compatible).
        - Otherwise falls back to a simple deterministic stub.
        """
        if self.provider == "openai" and self.api_key:
            try:
                resp = httpx.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "text-embedding-3-small",
                        "input": text,
                    },
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["data"][0]["embedding"]
            except Exception as exc:  # noqa: BLE001
                # Fall back to stubbed embedding but include error info in length.
                return [float(len(text)), 1.0, 0.0]

        if self.provider == "qwen" and self.api_key:
            try:
                resp = httpx.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "text-embedding-v1",
                        "input": text,
                    },
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["data"][0]["embedding"]
            except Exception:  # noqa: BLE001
                return [float(len(text)), 1.0, 0.0]

        # Default stub behaviour
        return [float(len(text)), 1.0, 0.0]

    def info(self) -> dict[str, Any]:
        return {"provider": self.provider, "has_api_key": bool(self.api_key)}


if __name__ == "__main__":
    # Simple CLI-style test for the LLM client:
    #   python -m src.utils.llm_client
    from src.config import settings

    client = LLMClient(provider=settings.llm_provider, api_key=settings.llm_api_key)
    print(f"Provider: {client.provider}, has_api_key={bool(client.api_key)}")
    print("Response:", client.generate("Say hello in one short sentence."))

