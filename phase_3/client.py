import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any

import requests


GROQ_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqClientError(RuntimeError):
  pass


@dataclass
class GroqConfig:
  api_key: str
  base_url: str = GROQ_DEFAULT_BASE_URL
  model: str = GROQ_DEFAULT_MODEL


def load_groq_config() -> GroqConfig:
  """
  Load Groq configuration from environment variables.

  Required:
    - GROQ_API_KEY

  Optional:
    - GROQ_API_BASE (defaults to https://api.groq.com/openai/v1)
    - GROQ_MODEL (defaults to llama-3.3-70b-versatile)
  """
  api_key = os.getenv("GROQ_API_KEY")
  if not api_key:
    raise GroqClientError(
      "GROQ_API_KEY environment variable is not set. "
      "Set it before running Phase 3."
    )

  base_url = os.getenv("GROQ_API_BASE", GROQ_DEFAULT_BASE_URL).rstrip("/")
  model = os.getenv("GROQ_MODEL", GROQ_DEFAULT_MODEL)

  return GroqConfig(api_key=api_key, base_url=base_url, model=model)


class GroqClient:
  """
  Minimal client for Groq chat completions.

  NOTE:
  - This assumes the Groq API is OpenAI-compatible at the /chat/completions
    endpoint. Adjust the URL or payload shape here if the API changes.
  """

  def __init__(self, config: GroqConfig | None = None) -> None:
    self.config = config or load_groq_config()

  def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """
    Send a chat completion request to Groq and return the model's text.
    """
    url = f"{self.config.base_url}/chat/completions"
    headers = {
      "Authorization": f"Bearer {self.config.api_key}",
      "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
      "model": self.config.model,
      "messages": messages,
      "temperature": temperature,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    if response.status_code != 200:
      raise GroqClientError(
        f"Groq API error {response.status_code}: {response.text[:500]}"
      )

    data = response.json()
    try:
      return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
      raise GroqClientError(f"Unexpected Groq response shape: {data}") from exc

