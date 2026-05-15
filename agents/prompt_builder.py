import json
from typing import Dict, Any


class PromptBuilder:
    def __init__(self):
        pass

    def build(self, topic: str, viral_elements: Dict[str, Any], virality_strategy: Dict[str, Any],
              duration: int = 60, style: str = "cinematic", tone: str = "dramatic", selected_research: Dict[str, Any] = None) -> str:
        timing = {
            60: {"hook": "0-3s", "setup": "3-15s", "escalation": "15-50s", "payoff": "50-60s"},
            90: {"hook": "0-3s", "setup": "3-20s", "escalation": "20-70s", "payoff": "70-90s"}
        }.get(duration, {"hook": "0-3s", "setup": "3-15s", "escalation": "15-50s", "payoff": "50-60s"})

        selected_research_str = ""
        if selected_research and isinstance(selected_research, dict) and len(selected_research) > 0:
            selected_research_str = f"""
USER-SELECTED EMPHASIS:
The user has chosen to particularly emphasize these research elements:
{json.dumps(selected_research, indent=2)}
Please ensure these selected elements are prominently featured in the generated script.
"""

        return f"""Create a YouTube Shorts script about: "{topic}"

STYLE: {style} | TONE: {tone} | DURATION: {duration}s

TIMING:
- Hook ({timing['hook']}): Extreme attention grab
- Setup ({timing['setup']}): Rapid context
- Escalation ({timing['escalation']}): Rising tension
- Payoff ({timing['payoff']}): Shocking conclusion

VIRAL ELEMENTS: {json.dumps(viral_elements, indent=2)}
STORYTELLING STRATEGY: {json.dumps(virality_strategy, indent=2)}{selected_research_str}

RULES:
1. Every sentence must increase curiosity or emotional intensity
2. NO educational tone - sound like Netflix, not Wikipedia
3. NO filler, NO "today we're talking about"
4. Short punchy sentences written for narration
5. Active voice only
6. Every line suggests a visual
7. End with a payoff that sticks
8. Script must be ~130-150 words — exactly 60 seconds of continuous ElevenLabs voiceover with no pauses

OUTPUT:
1. TITLE: [curiosity-driven title]
2. HOOK: [opening line, max 2 sentences]
3. SCRIPT: [clean narration only — NO timing markers, NO brackets, NO stage directions. Plain sentences, copy-paste ready for ElevenLabs voiceover]
4. SUBTITLE_EMPHASIS: [words to emphasize]
5. VISUAL_SUGGESTIONS: [one visual per script beat, with timing markers for the video editor:
   [0-3s] <what to show>
   [3-15s] <what to show>
   etc.]"""

    def build_system_prompt(self) -> str:
        return """You are an elite YouTube Shorts writer specializing in viral historical content.

Your scripts must:
- Maintain constant curiosity and emotional intensity
- Feel like a Netflix documentary compressed into 60 seconds
- Use powerful language that suggests visuals
- Sound entertaining, never educational
- Build tension and deliver satisfying payoffs
- Be written as clean spoken narration — no timing markers, no brackets, no stage directions
- Target ~130-150 words so ElevenLabs reads it in exactly 60 seconds

Every word must serve the retention goal."""
