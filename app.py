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

            # Save research to file
            safe_topic = topic.replace(" ", "_").replace("/", "-")[:50]
            research_dir = pathlib.Path("outputs/research")
            research_dir.mkdir(parents=True, exist_ok=True)
            research_file_path = research_dir / f"{safe_topic}_research.txt"
            research_file_path.write_text(
                ScriptFormatter.format_research(research_result), encoding="utf-8"
            )

            # Store in session state for later use
            st.session_state.research_result = research_result
            st.session_state.topic = topic
            st.session_state.duration = duration
            st.session_state.style = style
            st.session_state.tone = tone
            st.session_state.api_provider = api_provider
            st.session_state.research_file_path = str(research_file_path)

            st.success(f"✅ Research completed! File saved to: {research_file_path}")
            st.info("👇 Select the research elements you want emphasized in your script below:")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.write("Check that your API keys are set in the .env file")

# Display research selection UI if research is available
if "research_result" in st.session_state:
    st.divider()
    st.markdown("## \U0001f50d Research Review & Selection")
    st.markdown("Select which viral elements to emphasize in your script:")

    research_result = st.session_state.research_result
    viral_elements = research_result.get("viral_elements", {})

    # Create checkboxes for each viral element
    selected_elements = {}
    if isinstance(viral_elements, dict):
        cols = st.columns(2)
        for idx, (key, value) in enumerate(viral_elements.items()):
            col = cols[idx % 2]
            with col:
                selected_elements[key] = st.checkbox(
                    key.replace("_", " ").title(),
                    value=True,
                    help=f"{key}: {str(value)[:100]}..."
                )

    st.divider()

    # Display research file link
    if "research_file_path" in st.session_state:
        st.markdown(f"📄 **Research file saved:** `{st.session_state.research_file_path}`")
        with open(st.session_state.research_file_path, "r") as f:
            research_text = f.read()
        st.download_button(
            "📥 Download Research File",
            research_text,
            file_name=f"{st.session_state.topic.replace(' ', '_')}_research.txt",
            mime="text/plain"
        )

    # Generate script button
    if st.button("✍️ Generate Script from Selected Research", type="primary", use_container_width=True):
        try:
            topic = st.session_state.topic
            duration = st.session_state.duration
            style = st.session_state.style
            tone = st.session_state.tone
            api_provider = st.session_state.api_provider

            with st.spinner("Initializing..."):
                llm = LLMHandler()
                provider = "anthropic" if api_provider == "Anthropic" else "openai"
                llm.switch_provider(provider)

            with st.spinner("\U0001f525 Analyzing viral elements..."):
                virality_strategy = ViralityAnalyzer(llm).analyze(
                    topic=topic, viral_elements=research_result["viral_elements"],
                    duration=duration, style=style
                )

            # Build selected research dict for prompt injection
            selected_research = {k: v for k, v in viral_elements.items() if selected_elements.get(k, False)}

            with st.spinner("✍️ Writing script..."):
                script_data = ScriptWriter(llm).write(
                    topic=topic,
                    viral_elements=research_result["viral_elements"],
                    virality_strategy=virality_strategy,
                    duration=duration,
                    style=style,
                    tone=tone,
                    selected_research=selected_research
                )

            st.success("✅ Script generated!")
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

            # Clear session state after generating script
            del st.session_state.research_result
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.write("Check that your API keys are set in the .env file")

st.divider()
with st.expander("ℹ️ How it works"):
    st.markdown("""
    **4-stage pipeline:**
    1. **Research** → Searches for facts and extracts viral storytelling elements
    2. **Virality Analysis** → Optimizes emotional arc, pacing, and retention hooks
    3. **Prompt Engineering** → Dynamically builds the perfect generation prompt
    4. **Script Generation** → Creates a cinematic, viral-optimized script

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
