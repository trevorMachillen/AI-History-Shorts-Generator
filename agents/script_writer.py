from typing import Dict, Any
from utils.llm_handler import LLMHandler
from agents.prompt_builder import PromptBuilder
import re


class ScriptWriter:
    def __init__(self, llm_handler: LLMHandler):
        self.llm = llm_handler
        self.prompt_builder = PromptBuilder()

    def write(self, topic: str, viral_elements: Dict[str, Any], virality_strategy: Dict[str, Any],
              duration: int = 60, style: str = "cinematic", tone: str = "dramatic") -> Dict[str, str]:
        response = self.llm.generate(
            system_prompt=self.prompt_builder.build_system_prompt(),
            user_prompt=self.prompt_builder.build(topic, viral_elements, virality_strategy, duration, style, tone),
            task_type="script",
            max_tokens=3000
        )
        return self._parse_response(response)

    def _parse_response(self, response: str) -> Dict[str, str]:
        sections = {"title": "", "hook": "", "script": "", "subtitle_emphasis": "", "visual_suggestions": ""}

        patterns = {
            "title":              r"(?:^|\n)\s*(?:\d+\.\s*)?(?:\*{1,2})?title(?:\*{1,2})?:?\**\s*(.+?)(?=\n\s*(?:\d+\.\s*)?(?:\*{1,2})?(?:hook|script|subtitle|visual)|\Z)",
            "hook":               r"(?:^|\n)\s*(?:\d+\.\s*)?(?:\*{1,2})?hook(?:\*{1,2})?:?\**\s*(.+?)(?=\n\s*(?:\d+\.\s*)?(?:\*{1,2})?(?:title|script|subtitle|visual)|\Z)",
            "script":             r"(?:^|\n)\s*(?:\d+\.\s*)?(?:\*{1,2})?script(?:\*{1,2})?:?\**\s*(.+?)(?=\n\s*(?:\d+\.\s*)?(?:\*{1,2})?(?:title|hook|subtitle|visual)|\Z)",
            "subtitle_emphasis":  r"(?:^|\n)\s*(?:\d+\.\s*)?(?:\*{1,2})?subtitle[_ ]?emphasis(?:\*{1,2})?:?\**\s*(.+?)(?=\n\s*(?:\d+\.\s*)?(?:\*{1,2})?(?:title|hook|script|visual)|\Z)",
            "visual_suggestions": r"(?:^|\n)\s*(?:\d+\.\s*)?(?:\*{1,2})?visual[_ ]?suggestions(?:\*{1,2})?:?\**\s*(.+?)(?=\n\s*(?:\d+\.\s*)?(?:\*{1,2})?(?:title|hook|script|subtitle)|\Z)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()

        # Fallback: if nothing parsed, dump full response into script
        if not any(sections.values()):
            sections["script"] = response.strip()

        return sections
