import hashlib
from pathlib import Path

import structlog

from .base_llm import BaseLLMService

logger = structlog.get_logger()


class GoldAnalysisService:
    """Gold analysis service that calls LLM with the gold.md prompt."""

    def __init__(self, llm_service: BaseLLMService):
        self.llm_service = llm_service
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "gold.md"

    def _load_prompt(self) -> str:
        return self.prompt_path.read_text(encoding="utf-8")

    def _get_prompt_hash(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]

    async def analyze(self) -> dict:
        logger.info("gold analysis started", model=self.llm_service.get_model_name())

        prompt = self._load_prompt()
        prompt_hash = self._get_prompt_hash(prompt)

        try:
            content = await self.llm_service.generate(prompt)
        except Exception:
            logger.error("gold analysis failed", model=self.llm_service.get_model_name())
            raise

        logger.info("gold analysis completed", model=self.llm_service.get_model_name())

        return {
            "content": content,
            "modelUsed": self.llm_service.get_model_name(),
            "promptHash": prompt_hash,
        }
