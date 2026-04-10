# Prompt Architect

An AI agent that generates LLM-specific prompts. Describe your task, pick your target model, and get a prompt engineered specifically for how that model thinks — then refine it through conversation.

**[Try it live](https://karan0310.github.io/prompt-architect/)**

## What it does

Most people write the same prompt regardless of which LLM they're using. But each model has different strengths, formatting preferences, and failure modes. Prompt Architect knows these differences and exploits them.

For example, the same task produces:
- **Claude** prompts with XML tags (`<task>`, `<context>`) and reasoning-first structure
- **ChatGPT** prompts with role assignment (`You are a...`) and markdown headers
- **Llama** prompts with explicit delimiters (`INPUT:`, `OUTPUT:`) and few-shot examples
- **DeepSeek** prompts framed as problems with test cases and reasoning chains

## Supported models

| Model | Key prompting strategy |
|-------|----------------------|
| Claude (Anthropic) | XML tags, WHY context, extended thinking |
| ChatGPT / GPT-4o (OpenAI) | Role assignment, numbered steps, markdown |
| Gemini (Google) | Grounding cues, structured output, massive context |
| Microsoft Copilot | Professional framing, deliverable-focused |
| Mistral (Mistral AI) | Explicit instructions, flat structure |
| Llama (Meta) | Few-shot examples, clear delimiters, repetition of constraints |
| DeepSeek (DeepSeek AI) | Problem framing, chain-of-thought, test cases |
| Grok (xAI) | Direct tone, tight constraints, no preamble |

Each model has a deep knowledge profile covering context windows, output limits, formatting preferences, strengths, weaknesses, 7-9 prompting strategies, example patterns, temperature guidance, and special features.

## Features

- **Deep LLM knowledge base** — not just "use markdown for ChatGPT" but detailed profiles with formatting preferences, failure modes, and concrete strategies
- **Agent refinement** — after generating, refine the prompt through conversation ("make it shorter", "add examples", "more professional tone")
- **Real-time streaming** — see the prompt generated token by token
- **Quick-refine chips** — one-click refinements: Shorter, More detail, Add examples, Professional tone, Format rules, Simplify
- **Prompt history** — saved locally, click to reload and continue refining
- **Copy & download** — grab the prompt for immediate use
- **Word/token count** — know how large your prompt is
- **Works on mobile** — responsive design, use from your phone
- **Privacy-first** — your API key stays in your browser, sent only to Anthropic's API

## Quick start

### Web (no install)

1. Open **[karan0310.github.io/prompt-architect](https://karan0310.github.io/prompt-architect/)**
2. Enter your [Anthropic API key](https://console.anthropic.com/settings/keys)
3. Pick an LLM, describe your task, generate

### CLI agent (Python)

```bash
git clone https://github.com/Karan0310/prompt-architect.git
cd prompt-architect
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python agent.py
```

The CLI agent has the same features plus:
- **Tool use** — the agent can save, export, rate, and manage prompt history autonomously
- **Prompt quality scoring** — rates prompts across clarity, specificity, LLM-fit, completeness, and usability
- **File export** — save prompts as `.txt` files

## How the knowledge base works

Each LLM has a comprehensive profile in `llm_profiles.py` covering:

```
Context window     — 200K (Claude) vs 1M (Gemini) vs 128K (others)
Output limits      — affects how ambitious the generated prompt can be
Formatting         — XML tags vs markdown headers vs explicit delimiters
System prompt      — how each model treats system vs user messages
Strengths          — 5-8 capabilities to exploit
Weaknesses         — 4-6 failure modes to compensate for
Strategies         — 7-9 tested prompting techniques
Example patterns   — 2-3 structural templates
Temperature        — specific ranges for factual/analysis/creative
Special features   — model-unique capabilities (thinking mode, JSON mode, etc.)
```

When you select an LLM, its full profile (~4,000-6,500 chars) is injected into the system prompt, giving the generation model deep context about how to structure the output prompt.

## Project structure

```
index.html         — Web agent (single file, no build step)
agent.py           — Python CLI agent
llm_profiles.py    — LLM knowledge base (8 model profiles)
requirements.txt   — Python dependencies
```

## Privacy

- Your API key is stored in `localStorage` (browser) or as an environment variable (CLI)
- It is only sent to `api.anthropic.com` — never to any other server
- No analytics, tracking, or telemetry
- The web app is a static HTML file with zero backend

## License

MIT
