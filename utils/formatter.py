from typing import Dict, Any
import re


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
