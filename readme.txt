
## The 4-Stage Pipeline
1. ResearchAgent - DuckDuckGo search, extracts hook/twist/visuals/emotion
2. ViralityAnalyzer - retention beats, emotional arc, pacing strategy
3. PromptBuilder - assembles optimized prompt from research + strategy
4. ScriptWriter - calls LLM, parses response into sections

## Script Output Sections
- Title - curiosity-driven
- Hook - first 2 sentences, extreme attention grab
- Script - full narration with timing markers
- Subtitle Emphasis - words to highlight in captions
- Visual Suggestions - shot ideas per line
- ElevenLabs Script - clean plain text, no markers, paste-ready for voiceover

## API Setup
Both OpenAI and Anthropic supported, switchable in the UI.
Configure in .env:
  OPENAI_API_KEY=your_key
  ANTHROPIC_API_KEY=your_key
  DEFAULT_API_PROVIDER=openai

Model tiers:
  Research  - gpt-4o-mini / claude-3-5-haiku (fast, cheap)
  Analysis  - gpt-4o / claude-3-5-sonnet
  Script    - gpt-4o / claude-opus-4-7 (best quality)

Switch providers via LLMHandler.switch_provider("openai" or "anthropic") in utils/llm_handler.py

## Key Design Decisions
- Multi-stage pipeline (not direct topic to script) = dramatically better output
- No educational tone - Netflix documentary energy, not Wikipedia
- ElevenLabs-ready output - clean narration stripped of timing markers
- LLMHandler abstracts both APIs behind one .generate() call

## Known Issues / Notes
- streamlit not on PATH - use full path to launch (see How to Run above)
- GitHub repo trevorMachillen/AI-History-Shorts-Generator exists but not pushed yet
- Script parser in script_writer.py uses regex - may need tuning if LLM output format changes

## Phase 2 Features Planned
- Thumbnail generator
- Visual shot list with timestamps
- ElevenLabs direct API integration
- AI image prompts (Midjourney/Leonardo)
- Retention scoring
- B-roll suggestions
- Auto-save scripts to outputs/scripts/

## Script Style Goals
- Sounds like Netflix documentary compressed into 60 seconds
- NOT educational, NOT Wikipedia-style
- Every sentence builds curiosity or emotional intensity
- Short punchy sentences for narration
- Strong payoff ending
- Every line suggests a visual
'@ | Set-Content C:\Users\maccl\Documents\AI-History-Shorts-Generator\CLAUDE.md

AI-History-Shorts-Generator/
├── app.py # Main Streamlit UI
├── requirements.txt # Dependencies
├── .env # API keys (never commit)
├── .env.example # API key template
├── agents/
│ ├── researcher.py # Stage 1 - web search + viral element extraction
│ ├── virality_analyzer.py # Stage 2 - retention/pacing strategy
│ ├── prompt_builder.py # Stage 3 - dynamic prompt engineering
│ └── script_writer.py # Stage 4 - script generation + parsing
├── utils/
│ ├── llm_handler.py # OpenAI/Anthropic abstraction layer
│ └── formatter.py # text, markdown, ElevenLabs formatters
├── prompts/ # Future prompt templates
├── outputs/scripts/ # Future script saves
└── data/ # Future research cache