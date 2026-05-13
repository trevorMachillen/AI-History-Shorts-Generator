import json
from typing import Dict, Any
from duckduckgo_search import DDGS
from utils.llm_handler import LLMHandler


class ResearchAgent:
    def __init__(self, llm_handler: LLMHandler):
        self.llm = llm_handler

    def search_topic(self, topic: str, num_results: int = 5) -> str:
        try:
            results = DDGS().text(topic, max_results=num_results)
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        except Exception as e:
            return f"Search error: {str(e)}"

    def extract_viral_elements(self, topic: str, research_data: str) -> Dict[str, Any]:
        system_prompt = """You are a viral content strategist specializing in YouTube Shorts.
Analyze historical events and extract elements that maximize viewer engagement and retention.
Focus on what captivates modern audiences, not educational content."""

        user_prompt = f"""Extract ONLY the most viral storytelling elements from this historical event:

TOPIC: {topic}
RESEARCH DATA:
{research_data}

Return as JSON:
{{
  "hook": "Most shocking opening hook (one sentence)",
  "twist": "Most unexpected revelation",
  "emotional_core": "Primary emotion (fear/awe/mystery/shock)",
  "visuals": ["Visually interesting moments"],
  "shocking_details": ["Bizarre or counter-intuitive facts"],
  "strongest_payoff": "Most satisfying conclusion",
  "curiosity_loops": ["What keeps viewers asking what happens next"],
  "social_angle": "Why people would share this"
}}"""

        response = self.llm.generate(system_prompt, user_prompt, task_type="research")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_analysis": response}

    def research(self, topic: str) -> Dict[str, Any]:
        research_data = self.search_topic(topic)
        viral_elements = self.extract_viral_elements(topic, research_data)
        return {"topic": topic, "research_data": research_data, "viral_elements": viral_elements}
