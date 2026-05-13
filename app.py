import streamlit as st
import os
import pathlib
from dotenv import load_dotenv
from utils.llm_handler import LLMHandler
from agents.researcher import ResearchAgent
from agents.virality_analyzer import ViralityAnalyzer
from agents.script_writer import ScriptWriter
from utils.formatter import ScriptFormatter

load_dotenv()

st.set_page_config(page_title="AI History Shorts Generator", page_icon="\U0001f3ac", layout="wide")

st.title("\U0001f3ac AI History Shorts Generator")
st.caption("Turn any historical topic into a viral YouTube Shorts script")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    Generate engaging, viral-optimized scripts for history shorts in seconds.
    Enter a historical topic and our AI agents will research, analyze, and craft a script
    designed to maximize viewer engagement and retention.
    """)
with col2:
    api_provider = st.radio("API Provider", ["OpenAI", "Anthropic"])

st.divider()

col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("Historical Topic", placeholder="e.g., The Dancing Plague of 1518")
with col2:
    duration = st.selectbox("Video Duration", [60, 90])

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox("Storytelling Style", ["cinematic", "dark history", "mysterious", "emotional", "shocking", "myth vs reality"])
with col2:
    tone = st.selectbox("Tone", ["dramatic", "suspenseful", "mysterious", "awe-inspiring", "dark"])

st.divider()

if st.button("\U0001f680 Generate Script", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a historical topic!")
    else:
        provider = "anthropic" if api_provider == "Anthropic" else "openai"
        try:
            with st.spinner("Initializing..."):
                llm = LLMHandler()
                llm.switch_provider(provider)

            with st.spinner(f"\U0001f4da Researching '{topic}'..."):
                research_result = ResearchAgent(llm).research(topic)

            with st.spinner("\U0001f525 Analyzing viral elements..."):
                virality_strategy = ViralityAnalyzer(llm).analyze(
                    topic=topic, viral_elements=research_result["viral_elements"],
                    duration=duration, style=style
                )

            with st.spinner("\u270d\ufe0f Writing script..."):
                script_data = ScriptWriter(llm).write(
                    topic=topic, viral_elements=research_result["viral_elements"],
                    virality_strategy=virality_strategy, duration=duration, style=style, tone=tone
                )

            st.success("\u2705 Script generated!")
            st.divider()
            st.markdown(f"## \U0001f4dd {script_data.get('title', 'Your Script')}")

            tab1, tab2, tab3 = st.tabs(["Script", "Metadata", "Research"])
            with tab1:
                st.markdown("### Hook")
                st.write(script_data.get("hook", ""))
                st.markdown("### Full Script")
                col_script, col_visuals = st.columns([3, 2])
                with col_script:
                    st.caption("Narration")
                    st.code(script_data.get("script", ""), language="text")
                with col_visuals:
                    st.caption("Visual Suggestions")
                    st.write(script_data.get("visual_suggestions", ""))
                st.markdown("### Subtitle Emphasis")
                st.write(script_data.get("subtitle_emphasis", ""))
            with tab2:
                st.json({"topic": topic, "duration": duration, "style": style, "tone": tone, "provider": api_provider})
            with tab3:
                st.json(research_result.get("viral_elements", {}))
                if isinstance(virality_strategy, dict):
                    st.json(virality_strategy)

            save_dir = pathlib.Path("outputs/scripts")
            save_dir.mkdir(parents=True, exist_ok=True)
            safe_topic = topic.replace(" ", "_").replace("/", "-")[:50]
            (save_dir / f"{safe_topic}.md").write_text(
                ScriptFormatter.format_for_markdown(script_data), encoding="utf-8"
            )

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("\U0001f4e5 Download as Text", ScriptFormatter.format_for_download(script_data),
                    file_name=f"script_{topic.replace(' ', '_')}.txt", mime="text/plain")
            with col2:
                st.download_button("\U0001f4e5 Download as Markdown", ScriptFormatter.format_for_markdown(script_data),
                    file_name=f"script_{topic.replace(' ', '_')}.md", mime="text/markdown")

        except Exception as e:
            st.error(f"\u274c Error: {str(e)}")
            st.write("Check that your API keys are set in the .env file")

st.divider()
with st.expander("\u2139\ufe0f How it works"):
    st.markdown("""
    **4-stage pipeline:**
    1. **Research** \u2192 Searches for facts and extracts viral storytelling elements
    2. **Virality Analysis** \u2192 Optimizes emotional arc, pacing, and retention hooks
    3. **Prompt Engineering** \u2192 Dynamically builds the perfect generation prompt
    4. **Script Generation** \u2192 Creates a cinematic, viral-optimized script

    Multi-stage approach = dramatically better quality than direct generation.
    """)
with st.expander("\U0001f511 API Keys"):
    st.markdown("""
    Copy `.env.example` to `.env` and add your keys:
    ```
    OPENAI_API_KEY=your_key
    ANTHROPIC_API_KEY=your_key
    ```
    Get keys: [OpenAI](https://platform.openai.com/api-keys) | [Anthropic](https://console.anthropic.com/)
    """)

