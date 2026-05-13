import json
from typing import Dict, Any
from utils.llm_handler import LLMHandler


class ViralityAnalyzer:
    def __init__(self, llm_handler: LLMHandler):
        self.llm = llm_handler

    def analyze(self, topic: str, viral_elements: Dict[str, Any],
                duration: int = 60, style: str = "cinematic") -> Dict[str, Any]:
        system_prompt = """You are an elite YouTube Shorts strategist who understands retention psychology.
Transform raw historical facts into algorithm-optimized storytelling structure.
Focus on hook strength, retention beats, emotional escalation, and payoff impact."""

        user_prompt = f"""Create an optimized viral storytelling strategy:

TOPIC: {topic}
DURATION: {duration}s
STYLE: {style}
VIRAL ELEMENTS: {json.dumps(viral_elements, indent=2)}

Return as JSON:
{{
  "hook_line": "Opening 3 seconds - must grab immediately",
  "hook_strategy": "Why this hook works",
  "retention_beats": [
    {{"time": "0-3s", "action": "Hook", "purpose": "Grab attention"}},
    {{"time": "3-20s", "action": "Setup", "purpose": "Build context"}},
    {{"time": "20-{duration-10}s", "action": "Escalation", "purpose": "Rising tension"}},
    {{"time": "{duration-10}s-end", "action": "Payoff", "purpose": "Satisfy curiosity"}}
  ],
  "visual_cut_points": ["Where visuals should change"],
  "emotional_arc": "How emotions escalate",
  "pacing_notes": "Sentence length recommendations",
  "strongest_payoff": "Final moment that sticks",
  "rewatch_elements": "What makes people watch twice",
  "share_worthiness": "Why someone would share this"
}}"""

        response = self.llm.generate(system_prompt, user_prompt, task_type="analysis")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_analysis": response}
