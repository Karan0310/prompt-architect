#!/usr/bin/env python3
"""
Prompt Architect Agent
======================
A conversational AI agent that generates LLM-specific prompts through
an interactive multi-turn dialogue. Built on the Anthropic SDK with tool use.

Usage:
    python agent.py

Requires:
    pip install anthropic rich
    Set ANTHROPIC_API_KEY environment variable
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import box

from llm_profiles import get_profile_text, get_profile

# ============================================================
# CONFIG
# ============================================================

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
HISTORY_FILE = Path(__file__).parent / ".prompt_history.json"

SUPPORTED_LLMS = {
    "1": "Claude (Anthropic)",
    "2": "ChatGPT / GPT-4o (OpenAI)",
    "3": "Gemini (Google DeepMind)",
    "4": "Microsoft Copilot (GPT-4 based)",
    "5": "Mistral (Mistral AI)",
    "6": "Llama (Meta, open source)",
    "7": "DeepSeek (DeepSeek AI)",
    "8": "Grok (xAI)",
}

STYLES = {
    "1": "detailed and thorough",
    "2": "concise and brief",
    "3": "step-by-step structured",
    "4": "creative and exploratory",
}

INCLUDE_OPTIONS = {
    "1": "examples",
    "2": "reasoning steps",
    "3": "role/persona",
    "4": "format constraints",
}

# ============================================================
# SYSTEM PROMPT
# ============================================================

BASE_SYSTEM_PROMPT = """You are Prompt Architect, an expert AI agent specialized in crafting optimal prompts for different LLMs. You have deep, research-backed knowledge of how each model processes instructions and what patterns produce the best results.

Rules you always follow:
1. Write the ACTUAL prompt the user should paste into the target LLM — never meta-instructions about prompting
2. Tailor the prompt's structure, formatting, tone, and strategy specifically to the target LLM using the detailed profile provided below
3. Actively exploit the target LLM's strengths and compensate for its weaknesses in how you design the prompt
4. Include requested elements naturally woven in — not bolted on
5. Make prompts ready to use immediately — only use placeholders where the user must fill in their own content
6. When refining, preserve what works and surgically improve what the user asks to change
7. Use the target LLM's preferred formatting style (XML tags for Claude, markdown headers for ChatGPT, explicit delimiters for Llama, etc.)
8. Consider the target LLM's context window and output limits when sizing the prompt
9. Apply the recommended temperature/sampling guidance in your explanation
10. Reference the example prompt patterns from the profile as structural templates

You have access to tools. Use them when appropriate:
- save_prompt: Save the current prompt to history
- load_history: View saved prompt history
- export_prompt: Export prompt to a text file
- rate_prompt: Analyze and score a prompt's quality

When generating or refining a prompt, always use this exact format in your response:
- First output the prompt text
- Then add "---EXPLANATION---" on its own line
- Then 2-4 sentences explaining your design choices, referencing specific profile traits (formatting preferences, strategies, strengths/weaknesses) that informed your decisions. Also recommend temperature settings and note any special features the user should enable."""


def build_system_prompt(target_llm: str) -> str:
    """Build a system prompt dynamically injected with the target LLM's full profile."""
    profile_text = get_profile_text(target_llm)
    return f"{BASE_SYSTEM_PROMPT}\n\n{profile_text}"

# ============================================================
# TOOLS DEFINITION
# ============================================================

TOOLS = [
    {
        "name": "save_prompt",
        "description": "Save the generated prompt to local history for future reference. Call this after generating or refining a prompt.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt_text": {
                    "type": "string",
                    "description": "The full prompt text to save"
                },
                "target_llm": {
                    "type": "string",
                    "description": "The target LLM this prompt was designed for"
                },
                "task_summary": {
                    "type": "string",
                    "description": "A short summary of the task the prompt addresses"
                },
                "explanation": {
                    "type": "string",
                    "description": "Brief explanation of design choices"
                }
            },
            "required": ["prompt_text", "target_llm", "task_summary"]
        }
    },
    {
        "name": "load_history",
        "description": "Load and display saved prompt history. Use when the user wants to see or revisit past prompts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of history entries to return (default 10)"
                }
            }
        }
    },
    {
        "name": "export_prompt",
        "description": "Export a prompt to a .txt file on disk. Use when the user wants to save the prompt as a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt_text": {
                    "type": "string",
                    "description": "The prompt text to export"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename (without extension). Auto-generated if not provided."
                }
            },
            "required": ["prompt_text"]
        }
    },
    {
        "name": "rate_prompt",
        "description": "Analyze and rate a prompt's quality across multiple dimensions: clarity, specificity, LLM-fit, completeness, and usability. Returns a score and improvement suggestions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt_text": {
                    "type": "string",
                    "description": "The prompt text to analyze"
                },
                "target_llm": {
                    "type": "string",
                    "description": "The target LLM this prompt is designed for"
                }
            },
            "required": ["prompt_text", "target_llm"]
        }
    }
]

# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def tool_save_prompt(prompt_text: str, target_llm: str, task_summary: str, explanation: str = "") -> str:
    history = _load_history_file()
    entry = {
        "id": int(time.time() * 1000),
        "llm": target_llm,
        "task": task_summary[:120],
        "prompt": prompt_text,
        "explanation": explanation,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    history.insert(0, entry)
    if len(history) > 50:
        history = history[:50]
    _save_history_file(history)
    return f"Prompt saved to history (ID: {entry['id']}). Total saved: {len(history)}"


def tool_load_history(limit: int = 10) -> str:
    history = _load_history_file()
    if not history:
        return "No prompts saved yet."
    entries = history[:limit]
    result = f"Showing {len(entries)} of {len(history)} saved prompts:\n\n"
    for i, h in enumerate(entries, 1):
        result += f"{i}. [{h['llm']}] {h['task']}\n   Saved: {h['time']}\n   Preview: {h['prompt'][:80]}...\n\n"
    return result


def tool_export_prompt(prompt_text: str, filename: str = "") -> str:
    if not filename:
        filename = f"prompt_{int(time.time())}"
    filename = filename.replace(" ", "_")
    if not filename.endswith(".txt"):
        filename += ".txt"

    export_dir = Path(__file__).parent / "exports"
    export_dir.mkdir(exist_ok=True)
    filepath = export_dir / filename
    filepath.write_text(prompt_text, encoding="utf-8")
    return f"Prompt exported to: {filepath.resolve()}"


def tool_rate_prompt(prompt_text: str, target_llm: str) -> str:
    word_count = len(prompt_text.split())
    has_structure = any(marker in prompt_text for marker in ["##", "###", "<", "1.", "Step "])
    has_role = any(phrase in prompt_text.lower() for phrase in ["you are", "act as", "your role"])
    has_examples = any(phrase in prompt_text.lower() for phrase in ["example", "for instance", "such as", "e.g."])
    has_format = any(phrase in prompt_text.lower() for phrase in ["format", "output", "respond with", "return"])
    has_context = any(phrase in prompt_text.lower() for phrase in ["context", "background", "given that", "because"])

    scores = {
        "Clarity": min(10, 5 + (2 if has_structure else 0) + (1 if word_count > 30 else 0) + (2 if has_format else 0)),
        "Specificity": min(10, 4 + (2 if has_examples else 0) + (2 if has_format else 0) + (2 if has_context else 0)),
        "LLM-Fit": min(10, 5 + (2 if has_structure else 0) + (2 if has_role else 0) + (1 if word_count > 50 else 0)),
        "Completeness": min(10, 3 + (2 if has_role else 0) + (2 if has_examples else 0) + (2 if has_format else 0) + (1 if has_context else 0)),
        "Usability": min(10, 5 + (2 if word_count < 500 else -1) + (2 if has_structure else 0) + (1 if has_format else 0)),
    }

    overall = sum(scores.values()) / len(scores)

    suggestions = []
    if not has_role:
        suggestions.append("Add a role/persona for the LLM")
    if not has_examples:
        suggestions.append("Include concrete examples")
    if not has_format:
        suggestions.append("Specify expected output format")
    if not has_structure:
        suggestions.append("Add structural markers (headers, numbered steps, XML tags)")
    if not has_context:
        suggestions.append("Provide more context about why this task matters")

    result = f"Prompt Quality Analysis for {target_llm}\n"
    result += "=" * 40 + "\n"
    for dim, score in scores.items():
        bar = "#" * score + "-" * (10 - score)
        result += f"  {dim:<14} {bar} {score}/10\n"
    result += f"\n  Overall: {overall:.1f}/10\n"
    result += f"  Word count: {word_count}\n"

    if suggestions:
        result += f"\nSuggestions:\n"
        for s in suggestions:
            result += f"  -> {s}\n"
    else:
        result += "\nNo major improvements needed — prompt looks solid!"

    return result


def _load_history_file() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_history_file(history: list):
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


# Tool dispatch
TOOL_DISPATCH = {
    "save_prompt": lambda inp: tool_save_prompt(
        inp["prompt_text"], inp["target_llm"], inp["task_summary"], inp.get("explanation", "")
    ),
    "load_history": lambda inp: tool_load_history(inp.get("limit", 10)),
    "export_prompt": lambda inp: tool_export_prompt(inp["prompt_text"], inp.get("filename", "")),
    "rate_prompt": lambda inp: tool_rate_prompt(inp["prompt_text"], inp["target_llm"]),
}

# ============================================================
# AGENT CORE
# ============================================================

console = Console()

class PromptArchitectAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            console.print("[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set.")
            console.print("Set it with: [dim]export ANTHROPIC_API_KEY=sk-ant-...[/dim]")
            sys.exit(1)

        self.client = anthropic.Anthropic(api_key=api_key)
        self.messages: list[dict] = []
        self.current_prompt = ""
        self.target_llm = ""
        self.system_prompt = BASE_SYSTEM_PROMPT
        self.refine_count = 0

    def gather_task(self) -> dict:
        """Interactive task gathering — mirrors the HTML flow."""
        console.print()
        console.print(Panel(
            Text("Prompt Architect Agent", style="bold italic", justify="center"),
            subtitle="AI Prompt Engineering",
            border_style="yellow",
            box=box.DOUBLE,
            padding=(1, 4),
        ))
        console.print()

        # Step 1: Choose LLM
        console.print("[yellow]01 — Choose your target LLM[/yellow]\n")
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column(style="dim")
        table.add_column(style="bold")
        table.add_column(style="dim")
        for key, name in SUPPORTED_LLMS.items():
            parts = name.split(" (")
            table.add_row(f"[{key}]", parts[0], f"({parts[1]}" if len(parts) > 1 else "")
        console.print(table)
        console.print()

        while True:
            choice = Prompt.ask("[yellow]Select LLM[/yellow]", default="1")
            if choice in SUPPORTED_LLMS:
                self.target_llm = SUPPORTED_LLMS[choice]
                self.system_prompt = build_system_prompt(self.target_llm)
                profile = get_profile(self.target_llm)
                console.print(f"  -> [bold]{self.target_llm}[/bold]")
                if profile:
                    console.print(f"     [dim]{profile['model_family']} | {profile['context_window']} context | {profile['output_limit']} output[/dim]")
                    console.print(f"     [dim]Best format: {profile['formatting_preferences']['best_structure']}[/dim]\n")
                break
            console.print("[red]  Invalid choice. Enter 1-8.[/red]")

        # Step 2: Describe task
        console.print("[yellow]02 — Describe your task[/yellow]\n")
        task = Prompt.ask("[yellow]Task[/yellow]")
        while not task.strip():
            task = Prompt.ask("[red]Please describe your task[/red]")
        console.print()

        # Step 3: Output style
        console.print("[yellow]03 — Output style[/yellow]")
        console.print("[dim]  [1] Detailed  [2] Concise  [3] Step-by-step  [4] Creative[/dim]")
        style_choice = Prompt.ask("[yellow]Style[/yellow]", default="1")
        style = STYLES.get(style_choice, STYLES["1"])
        console.print(f"  -> {style}\n")

        # Step 4: Include options
        console.print("[yellow]04 — Include elements[/yellow]")
        console.print("[dim]  [1] Examples  [2] Reasoning  [3] Role persona  [4] Format rules[/dim]")
        include_input = Prompt.ask("[yellow]Include (comma-separated)[/yellow]", default="1,2")
        includes = []
        for num in include_input.split(","):
            num = num.strip()
            if num in INCLUDE_OPTIONS:
                includes.append(INCLUDE_OPTIONS[num])
        if not includes:
            includes = ["examples", "reasoning steps"]
        console.print(f"  -> {', '.join(includes)}\n")

        return {
            "task": task.strip(),
            "llm": self.target_llm,
            "style": style,
            "includes": ", ".join(includes),
        }

    def generate(self, task_info: dict):
        """Initial prompt generation."""
        user_msg = (
            f"Generate an optimal prompt for {task_info['llm']}.\n\n"
            f"Task: {task_info['task']}\n"
            f"Desired output style: {task_info['style']}\n"
            f"Elements to include: {task_info['includes']}\n\n"
            f"Write the prompt now:"
        )

        self.messages = [{"role": "user", "content": user_msg}]
        self._call_agent("Generating your prompt")

    def refine(self, feedback: str):
        """Refine the current prompt with user feedback."""
        refine_msg = (
            f'The user wants to refine the prompt. Their feedback: "{feedback}"\n\n'
            f"Here is the current prompt:\n<current_prompt>\n{self.current_prompt}\n</current_prompt>\n\n"
            f"Apply the feedback and output the complete revised prompt. "
            f"After the prompt, include ---EXPLANATION--- with a note on what you changed."
        )

        self.messages.append({"role": "user", "content": refine_msg})
        self._call_agent("Refining prompt")
        self.refine_count += 1

    def _call_agent(self, status_msg: str):
        """Core agent loop — handles streaming + tool use."""
        with console.status(f"[yellow]{status_msg}...[/yellow]"):
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=TOOLS,
                messages=self.messages,
            )

        # Process response — handle tool use loop
        while response.stop_reason == "tool_use":
            # Collect all parts
            assistant_content = response.content
            self.messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    console.print(f"  [dim]⚙ Using tool: {tool_name}[/dim]")

                    if tool_name in TOOL_DISPATCH:
                        result = TOOL_DISPATCH[tool_name](tool_input)
                        console.print(f"  [dim]  ✓ {result[:80]}[/dim]")
                    else:
                        result = f"Unknown tool: {tool_name}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            self.messages.append({"role": "user", "content": tool_results})

            with console.status("[yellow]Agent thinking...[/yellow]"):
                response = self.client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=self.system_prompt,
                    tools=TOOLS,
                    messages=self.messages,
                )

        # Extract text response
        full_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                full_text += block.text

        self.messages.append({"role": "assistant", "content": response.content})

        # Parse prompt vs explanation
        parts = full_text.split("---EXPLANATION---")
        self.current_prompt = parts[0].strip()
        explanation = parts[1].strip() if len(parts) > 1 else None

        # Display
        console.print()
        console.print(Panel(
            self.current_prompt,
            title="[yellow]Generated Prompt[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        ))

        if explanation:
            console.print(Panel(
                explanation,
                title="[dim]Design Choices[/dim]",
                border_style="dim",
                padding=(0, 2),
            ))

        # Stats
        word_count = len(self.current_prompt.split())
        stats = f"[dim]{word_count} words"
        if self.refine_count > 0:
            stats += f" | {self.refine_count} refinement{'s' if self.refine_count != 1 else ''}"
        stats += "[/dim]"
        console.print(stats)
        console.print()

    def run_refinement_loop(self):
        """Interactive refinement loop — the agentic part."""
        console.print("[yellow]Agent ready for refinement.[/yellow]")
        console.print("[dim]Commands: type feedback to refine | 'copy' to copy | 'save' to save | 'export' to export | 'rate' to analyze | 'new' for new task | 'quit' to exit[/dim]\n")

        while True:
            try:
                user_input = Prompt.ask("[yellow]>[/yellow]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Goodbye![/dim]")
                break

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break

            elif cmd == "new":
                return "new"

            elif cmd == "copy":
                try:
                    import subprocess
                    # Try multiple clipboard methods
                    if sys.platform == "win32":
                        subprocess.run("clip", input=self.current_prompt.encode(), check=True)
                    elif sys.platform == "darwin":
                        subprocess.run("pbcopy", input=self.current_prompt.encode(), check=True)
                    else:
                        subprocess.run(["xclip", "-selection", "clipboard"], input=self.current_prompt.encode(), check=True)
                    console.print("[green]  ✓ Copied to clipboard[/green]")
                except Exception:
                    console.print("[red]  Could not copy to clipboard. Printing prompt instead:[/red]")
                    console.print(self.current_prompt)

            elif cmd == "save":
                result = tool_save_prompt(
                    self.current_prompt, self.target_llm,
                    self.messages[0]["content"][:100] if self.messages else "untitled"
                )
                console.print(f"[green]  ✓ {result}[/green]")

            elif cmd == "export":
                result = tool_export_prompt(self.current_prompt)
                console.print(f"[green]  ✓ {result}[/green]")

            elif cmd == "rate":
                result = tool_rate_prompt(self.current_prompt, self.target_llm)
                console.print(Panel(result, title="[yellow]Prompt Analysis[/yellow]", border_style="yellow"))

            elif cmd == "history":
                result = tool_load_history()
                console.print(result)

            elif cmd == "help":
                console.print("[dim]  Type natural language to refine the prompt[/dim]")
                console.print("[dim]  'copy' — copy prompt to clipboard[/dim]")
                console.print("[dim]  'save' — save to history[/dim]")
                console.print("[dim]  'export' — export as .txt file[/dim]")
                console.print("[dim]  'rate' — analyze prompt quality[/dim]")
                console.print("[dim]  'history' — view saved prompts[/dim]")
                console.print("[dim]  'new' — start a new task[/dim]")
                console.print("[dim]  'quit' — exit[/dim]")

            else:
                # Natural language refinement
                self.refine(user_input)

        return "quit"


# ============================================================
# MAIN
# ============================================================

def main():
    agent = PromptArchitectAgent()

    while True:
        task_info = agent.gather_task()
        agent.generate(task_info)
        result = agent.run_refinement_loop()
        if result == "quit":
            break
        # result == "new" -> loop again
        agent = PromptArchitectAgent()


if __name__ == "__main__":
    main()
