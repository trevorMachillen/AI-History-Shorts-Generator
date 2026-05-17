from typing import Dict, Any
import re
from datetime import datetime
import json


class ScriptFormatter:
    @staticmethod
    def format_for_download(script_data: Dict[str, str]) -> str:
        return (
            f"TITLE\n{script_data.get('title', '')}\n\n"
            f"HOOK\n{script_data.get('hook', '')}\n\n"
            f"SCRIPT\n{script_data.get('script', '')}\n\n"
            f"SUBTITLE EMPHASIS\n{script_data.get('subtitle_emphasis', '')}\n\n"
            f"VISUAL SUGGESTIONS\n{script_data.get('visual_suggestions', '')}\n"
        )

    @staticmethod
    def format_for_markdown(script_data: Dict[str, str]) -> str:
        return (
            f"# {script_data.get('title', '')}\n\n"
            f"## Hook\n{script_data.get('hook', '')}\n\n"
            f"## Script\n{script_data.get('script', '')}\n\n"
            f"## Subtitle Emphasis\n{script_data.get('subtitle_emphasis', '')}\n\n"
            f"## Visual Suggestions\n{script_data.get('visual_suggestions', '')}\n"
        )

    @staticmethod
    def format_for_elevenlabs(script_data: Dict[str, str]) -> str:
        hook = script_data.get("hook", "")
        script = script_data.get("script", "")

        # Combine hook + script into one block
        full_text = f"{hook}\n\n{script}" if hook else script

        # Strip timing markers like [0:05] or [0:30]
        full_text = re.sub(r"\[\d+:\d+\]", "", full_text)

        # Strip anything in parentheses (stage directions)
        full_text = re.sub(r"\(.*?\)", "", full_text)

        # Strip markdown bold/italic
        full_text = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", full_text)

        # Collapse multiple blank lines into one
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)

        return full_text.strip()

    @staticmethod
    def format_research(research_data: Dict[str, Any]) -> str:
        output = []
        output.append("AI HISTORY SHORTS GENERATOR - RESEARCH FILE")
        output.append(f"Topic: {research_data.get('topic', 'Unknown')}")
        output.append(f"Generated: {datetime.now().isoformat()}")
        output.append("")

        # Raw search results
        output.append("=" * 50)
        output.append("RAW SEARCH RESULTS")
        output.append("=" * 50)
        output.append("")

        if research_data.get("research_data"):
            output.append(research_data.get("research_data"))
        output.append("")

        # Investigation notes
        if research_data.get("investigation_notes"):
            output.append("=" * 50)
            output.append("INVESTIGATION NOTES")
            output.append("=" * 50)
            output.append("")
            output.append(research_data.get("investigation_notes"))
            output.append("")

        # Extracted viral elements
        output.append("=" * 50)
        output.append("EXTRACTED VIRAL ELEMENTS")
        output.append("=" * 50)
        output.append("")

        viral_elements = research_data.get("viral_elements", {})
        if isinstance(viral_elements, dict):
            for key, value in viral_elements.items():
                output.append(f"{key.upper().replace('_', ' ')}:")
                output.append(str(value))
                output.append("")

        return "\n".join(output)
