import json
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from utils.llm_handler import LLMHandler

_SCRAPE_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class ResearchAgent:
    def __init__(self, llm_handler: LLMHandler):
        self.llm = llm_handler

    # ------------------------------------------------------------------ #
    # Phase 1 helpers                                                      #
    # ------------------------------------------------------------------ #

    def generate_queries(self, topic: str) -> list:
        return [
            topic,
            f"{topic} shocking forgotten history",
            f"{topic} eyewitness accounts diary letters",
            f"{topic} conspiracy mysteries unexplained",
        ]

    def search_topic(self, query: str, num_results: int = 8) -> list:
        try:
            return list(DDGS().text(query, max_results=num_results))
        except Exception:
            return []

    def scrape_url(self, url: str) -> str:
        try:
            resp = requests.get(url, timeout=4, headers=_SCRAPE_HEADERS)
            soup = BeautifulSoup(resp.content, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            root = soup.find("article") or soup.find("main") or soup.find("body")
            text = root.get_text(" ", strip=True) if root else ""
            return text[:2000]
        except Exception:
            return ""

    def _gather_web_data(self, topic: str) -> str:
        chunks = []
        for query in self.generate_queries(topic):
            results = self.search_topic(query)
            for idx, r in enumerate(results):
                snippet = f"[{r.get('title', '')}] {r.get('body', '')}"
                if idx < 3 and r.get("href"):
                    full = self.scrape_url(r["href"])
                    if full:
                        snippet += f"\n  FULL TEXT: {full}"
                chunks.append(snippet)

        seen, unique = set(), []
        for c in chunks:
            key = c[:60]
            if key not in seen:
                seen.add(key)
                unique.append(c)

        return "\n\n".join(unique)[:24000]

    # ------------------------------------------------------------------ #
    # Phase 2 — investigative analysis                                     #
    # ------------------------------------------------------------------ #

    def _investigate(self, topic: str, research_data: str) -> str:
        system_prompt = """You are an elite research team for "Historical Oddities Daily" — a YouTube Shorts channel
focused on dark, strange, forgotten, and emotionally shocking history.

Your team works together simultaneously:
- Historian: uncovers obscure, forgotten, counter-narrative details
- Investigative journalist: finds contradictions, cover-ups, disputed facts, and what was hidden
- Documentary writer: identifies cinematic moments, emotional arcs, tension and release
- Viral Shorts editor: hunts for shocking hooks, curiosity gaps, and retention beats
- Conspiracy researcher: surfaces unexplained elements, unresolved questions, alternative theories
- Storyteller: finds first-person accounts, diary entries, witness testimony, human drama

ANTI-WIKIPEDIA RULES — non-negotiable:
- Ignore textbook summaries and dates-and-names overviews
- Only surface: shocking, ironic, cinematic, mysterious, emotionally intense, hard-to-believe details
- Prioritize things audiences have NEVER heard before
- Ask yourself: "What would Netflix focus on? What would make someone say 'I can't believe this is real'?"
- Think visual — describe scenes that could be shown on screen"""

        user_prompt = f"""Deeply investigate this historical topic using all six research roles above.

TOPIC: {topic}

RAW RESEARCH DATA:
{research_data}

Write 600–800 words of investigative notes. Cover:
1. The most shocking or obscure angle that most people don't know
2. First-person accounts, quotes, diary entries, or witness descriptions (real ones if present in the data)
3. Contradictions, disputes, mysteries, or unexplained elements
4. Cinematic visual moments — specific scenes that could be shown on screen
5. The emotional core — what human feeling drives this story (betrayal, obsession, madness, survival?)
6. At least 2 rabbit holes — related stories that branch off this topic
7. What a conspiracy researcher or investigative journalist would highlight

Write as flowing investigation notes, not bullet points. Be specific. Be visceral."""

        return self.llm.generate(system_prompt, user_prompt, task_type="analysis", max_tokens=1500)

    # ------------------------------------------------------------------ #
    # Phase 3 — structured extraction                                      #
    # ------------------------------------------------------------------ #

    def extract_viral_elements(self, topic: str, research_data: str, investigation: str = "") -> Dict[str, Any]:
        system_prompt = """You are a viral content strategist and documentary producer specializing in YouTube Shorts.
Extract structured story elements that maximize emotional impact, viewer retention, and shareability.
Anti-Wikipedia mode: never summarize. Only extract what is shocking, cinematic, mysterious, or hard to believe."""

        user_prompt = f"""Extract the most powerful viral storytelling elements for this historical topic.

TOPIC: {topic}

RAW RESEARCH:
{research_data[:8000]}

INVESTIGATION NOTES:
{investigation}

Return ONLY valid JSON with these exact keys:
{{
  "hook": "Most shocking 1-sentence opening hook",
  "twist": "Most unexpected or counterintuitive revelation",
  "emotional_core": "Primary emotion — fear / awe / mystery / shock / betrayal / obsession / madness",
  "visuals": ["Specific cinematic visual moment 1", "moment 2", "moment 3"],
  "shocking_details": ["Bizarre or hard-to-believe fact 1", "fact 2", "fact 3", "fact 4"],
  "strongest_payoff": "Most disturbing or satisfying conclusion",
  "curiosity_loops": ["Unresolved question that keeps viewer watching 1", "question 2"],
  "social_angle": "Why someone would share this — the 'you won't believe this' angle",
  "mysteries": ["Unexplained or disputed element 1", "mystery 2"],
  "first_person_moments": ["Real witness quote, diary entry, or personal account 1", "account 2"],
  "emotional_themes": ["betrayal", "paranoia", "obsession"],
  "rabbit_holes": ["Related story that could become its own Short 1", "angle 2"]
}}"""

        response = self.llm.generate(system_prompt, user_prompt, task_type="research", max_tokens=3000)
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except json.JSONDecodeError:
            return {"raw_analysis": response}

    # ------------------------------------------------------------------ #
    # Phase 4 — viral highlight curation                                   #
    # ------------------------------------------------------------------ #

    def select_key_highlights(self, topic: str, research_data: str,
                              investigation: str, viral_elements: Dict[str, Any]) -> list:
        system_prompt = """You are the senior content curator for "Historical Oddities Daily."
Your job is to shortlist the most powerful story beats for a 60-second YouTube Short.
You think like a Netflix executive picking scenes — every line must earn its place.
No textbook facts. No safe choices. No Wikipedia summaries.
If a highlight could appear on a Wikipedia summary page, reject it."""

        user_prompt = f"""Pick exactly 8–12 of the highest viral-potential highlights from all research below.

TOPIC: {topic}

INVESTIGATION NOTES:
{investigation}

VIRAL ELEMENTS:
{json.dumps(viral_elements, indent=2)}

RAW RESEARCH (excerpt):
{research_data[:6000]}

SELECTION CRITERIA — each highlight must satisfy at least one:
- Shock/irony: something that makes viewers say "wait, what?"
- Emotional intensity: betrayal, obsession, madness, survival, horror
- Visual cinematic potential: a scene that can be shown on screen
- Mystery/unresolved tension: something unexplained or disputed
- Originality: something audiences have almost certainly never heard
- Shareability: the "you won't believe this" angle

Return ONLY a valid JSON array of 8–12 strings. Each string is one punchy, specific highlight.
No preamble. No explanation. Just the JSON array.
Example format: ["Highlight one.", "Highlight two.", ...]"""

        response = self.llm.generate(system_prompt, user_prompt, task_type="analysis", max_tokens=1000)
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            result = json.loads(clean.strip())
            if isinstance(result, list):
                return [str(h) for h in result if str(h).strip()]
            return []
        except (json.JSONDecodeError, Exception):
            return []

    # ------------------------------------------------------------------ #
    # Main entry point                                                     #
    # ------------------------------------------------------------------ #

    def research(self, topic: str) -> Dict[str, Any]:
        research_data = self._gather_web_data(topic)
        investigation = self._investigate(topic, research_data)
        viral_elements = self.extract_viral_elements(topic, research_data, investigation)
        key_highlights = self.select_key_highlights(topic, research_data, investigation, viral_elements)
        return {
            "topic": topic,
            "research_data": research_data,
            "investigation_notes": investigation,
            "viral_elements": viral_elements,
            "key_highlights": key_highlights,
        }
