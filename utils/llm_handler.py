import os
from typing import Optional
from openai import OpenAI
from anthropic import Anthropic
from pydantic import BaseModel


class LLMConfig(BaseModel):
    provider: str = "openai"
    temperature: float = 0.7
    max_tokens: int = 2000


class LLMHandler:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.provider = os.getenv("DEFAULT_API_PROVIDER", "openai").lower()
        self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def switch_provider(self, provider: str):
        self.provider = provider.lower()
        self._init_client()

    def get_model(self, task_type: str) -> str:
        models = {
            "openai": {
                "research": os.getenv("OPENAI_RESEARCH_MODEL", "gpt-4o-mini"),
                "analysis": os.getenv("OPENAI_ANALYSIS_MODEL", "gpt-4o"),
                "script":   os.getenv("OPENAI_SCRIPT_MODEL", "gpt-4o"),
            },
            "anthropic": {
                "research": os.getenv("ANTHROPIC_RESEARCH_MODEL", "claude-3-5-haiku-20241022"),
                "analysis": os.getenv("ANTHROPIC_ANALYSIS_MODEL", "claude-3-5-sonnet-20241022"),
                "script":   os.getenv("ANTHROPIC_SCRIPT_MODEL", "claude-opus-4-7"),
            }
        }
        return models.get(self.provider, {}).get(task_type, "")

    def generate(self, system_prompt: str, user_prompt: str, task_type: str = "script",
                 temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        model = self.get_model(task_type)
        temp  = temperature or self.config.temperature
        tokens = max_tokens or self.config.max_tokens

        if self.provider == "openai":
            r = self.client.chat.completions.create(
                model=model, temperature=temp, max_tokens=tokens,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user",   "content": user_prompt}]
            )
            return r.choices[0].message.content

        elif self.provider == "anthropic":
            r = self.client.messages.create(
                model=model, temperature=temp, max_tokens=tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return r.content[0].text

        return ""
