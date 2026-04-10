"""
LLM Knowledge Base
===================
Deep per-model profiles that drive meaningfully different prompt generation.
Each profile covers architecture, strengths, failure modes, formatting,
and concrete prompting strategies with examples.
"""

LLM_PROFILES = {

# ================================================================
# CLAUDE (Anthropic)
# ================================================================
"Claude (Anthropic)": {
    "model_family": "Claude 4 / Claude 3.5",
    "context_window": "200K tokens",
    "output_limit": "~8,192 tokens (up to 64K with extended thinking)",
    "strengths": [
        "Exceptional long-form reasoning and nuanced analysis",
        "Strong instruction adherence with minimal hallucination",
        "Excels at tasks requiring careful judgment and ethical reasoning",
        "Handles very long documents natively (200K context)",
        "Strong at structured extraction from unstructured data",
        "Excellent at code generation, debugging, and refactoring",
        "Native extended thinking mode for complex multi-step reasoning",
    ],
    "weaknesses": [
        "Can be overly cautious or hedge when certainty is appropriate",
        "Sometimes over-explains when brevity is desired",
        "May refuse borderline tasks that are actually legitimate",
        "Less strong at real-time/live data tasks (no browsing by default)",
    ],
    "formatting_preferences": {
        "best_structure": "XML tags (<task>, <context>, <instructions>, <output_format>)",
        "why": "Claude's training specifically optimizes for XML-tagged sections — it parses them as semantic boundaries, not just text",
        "headers": "Markdown ## headers work but XML is stronger for task segmentation",
        "lists": "Numbered lists for sequential steps, bullet points for requirements",
        "code": "Triple backticks with language identifier. Claude handles multi-file context well.",
    },
    "system_prompt_behavior": "Claude has a dedicated system prompt field that it treats as highest-priority instructions. Use it for persona, constraints, and output format. User messages are for task-specific content.",
    "prompting_strategies": [
        "Use XML tags to separate context from instructions: <context>...</context> <task>...</task>",
        "Provide WHY context — Claude performs better when it understands the purpose behind a task",
        "For complex tasks, explicitly ask for thinking/reasoning before the final answer",
        "Use 'Be direct and concise' to counter its tendency to over-explain",
        "Prefill the assistant response to guide output format (e.g., start with '{' for JSON)",
        "For extraction tasks, provide the exact schema you want populated",
        "Use negative constraints sparingly — positive instructions work better",
    ],
    "example_patterns": {
        "structured_extraction": "<document>\n{content}\n</document>\n\n<task>\nExtract the following fields from the document above:\n</task>\n\n<output_format>\nRespond with a JSON object containing: {fields}\n</output_format>",
        "reasoning_task": "Think through this step-by-step before giving your final answer.\n\n<problem>\n{problem}\n</problem>\n\n<constraints>\n{constraints}\n</constraints>",
        "code_generation": "<context>\nLanguage: {lang}\nFramework: {framework}\nExisting code structure:\n{structure}\n</context>\n\n<task>\n{what_to_build}\n</task>\n\n<requirements>\n{requirements}\n</requirements>",
    },
    "temperature_guidance": "Default 1.0. Use 0.0-0.3 for factual/extraction tasks. 0.7-1.0 for creative writing. Claude's default is well-calibrated for most tasks.",
    "token_efficiency": "Claude's tokenizer (BPE-based) is efficient with English. Prompts can be verbose — the model handles long instructions well without degradation.",
    "special_features": [
        "Extended thinking: For hard problems, enable thinking mode to get chain-of-thought reasoning",
        "Tool use: Claude can call structured tools/functions — design prompts that leverage this for multi-step workflows",
        "Vision: Can process images — reference visual elements directly in prompts",
        "Citations: Can cite specific parts of long documents — ask for source references",
    ],
},

# ================================================================
# CHATGPT / GPT-4o (OpenAI)
# ================================================================
"ChatGPT / GPT-4o (OpenAI)": {
    "model_family": "GPT-4o / GPT-4.1",
    "context_window": "128K tokens",
    "output_limit": "~16,384 tokens (4,096 default, must request more)",
    "strengths": [
        "Excellent instruction-following — very literal and obedient",
        "Strong role-playing and persona adoption",
        "Native JSON mode for structured output",
        "Good at creative writing with specific style constraints",
        "Strong at code generation across many languages",
        "Handles multi-turn conversations naturally",
        "Function calling / tool use is very reliable",
    ],
    "weaknesses": [
        "Can be sycophantic — agrees rather than pushes back",
        "May hallucinate citations, URLs, and specific facts",
        "Tends to produce verbose responses by default",
        "Older knowledge cutoff compared to some competitors",
        "Can struggle with very long context despite 128K window (lost-in-the-middle problem)",
    ],
    "formatting_preferences": {
        "best_structure": "Markdown headers (##) + role assignment ('You are a...')",
        "why": "GPT models are heavily RLHF-trained on markdown-formatted conversations. Role assignment activates specialized behavior patterns.",
        "headers": "## and ### headers create clear semantic sections the model respects",
        "lists": "Numbered steps for procedures, checkboxes for requirements",
        "code": "Triple backticks. Specify language. GPT responds well to 'write production-quality code'.",
    },
    "system_prompt_behavior": "GPT-4o strongly adheres to system prompts. Use 'You are...' for role definition. System prompt persists across turns. Put guardrails and output format here.",
    "prompting_strategies": [
        "Start with clear role: 'You are an expert {domain} specialist with {N} years of experience'",
        "Use numbered steps for sequential procedures — GPT-4o follows them almost literally",
        "Specify output format explicitly: 'Respond in JSON', 'Use markdown table', etc.",
        "Use 'Do NOT...' constraints to prevent common failure modes (verbosity, hallucination)",
        "For factual tasks, add: 'If you're not sure, say so rather than guessing'",
        "Chain-of-thought: 'Think step by step' still improves reasoning significantly",
        "For code: specify language, framework, style guide, and error handling expectations",
        "Use few-shot examples — GPT-4o pattern-matches from examples very effectively",
    ],
    "example_patterns": {
        "role_based": "## Role\nYou are a {role} who specializes in {specialty}.\n\n## Task\n{task_description}\n\n## Requirements\n{numbered_requirements}\n\n## Output Format\n{format_spec}",
        "few_shot": "## Instructions\n{task}\n\n## Examples\nInput: {ex1_in}\nOutput: {ex1_out}\n\nInput: {ex2_in}\nOutput: {ex2_out}\n\n## Your Turn\nInput: {actual_input}\nOutput:",
        "code_generation": "You are a senior {language} developer.\n\n## Task\n{what_to_build}\n\n## Technical Requirements\n{requirements}\n\n## Constraints\n- Follow {style_guide}\n- Include error handling\n- Add inline comments for complex logic",
    },
    "temperature_guidance": "Default 1.0. Use 0.0 for deterministic/factual tasks. 0.7 for balanced. 1.0+ for creative. Consider using top_p instead for creative tasks.",
    "token_efficiency": "GPT tokenizer (cl100k_base) is efficient for English and code. Be aware of the default 4K output limit — explicitly request 'max_tokens: 16384' or say 'provide a comprehensive response' if you need longer output.",
    "special_features": [
        "JSON mode: Set response_format to json_object for guaranteed valid JSON",
        "Function calling: Define tools with JSON schema — GPT-4o is very reliable at calling them correctly",
        "Vision: Can process images — describe what you want analyzed specifically",
        "DALL-E integration: Can generate images inline in ChatGPT",
        "Code Interpreter: Can execute Python code — leverage for data analysis tasks",
    ],
},

# ================================================================
# GEMINI (Google DeepMind)
# ================================================================
"Gemini (Google DeepMind)": {
    "model_family": "Gemini 2.5 Pro / Flash",
    "context_window": "1M tokens (2M for Gemini 2.5 Pro)",
    "output_limit": "~8,192 tokens (65K for thinking mode)",
    "strengths": [
        "Massive context window — can process entire codebases, books, or video",
        "Strong multimodal capabilities (text, image, video, audio natively)",
        "Excellent at factual grounding and knowledge-intensive tasks",
        "Strong at data analysis and structured reasoning",
        "Good at following complex multi-constraint instructions",
        "Native Google Search grounding for real-time information",
        "Strong multilingual capabilities",
    ],
    "weaknesses": [
        "Can be overly verbose in responses",
        "Sometimes includes unnecessary caveats or disclaimers",
        "May not follow exact formatting as precisely as GPT-4o",
        "Reasoning can be less step-by-step transparent than Claude",
        "Occasionally provides surface-level analysis when depth is needed",
    ],
    "formatting_preferences": {
        "best_structure": "Clear section headers + explicit output schema + grounding cues",
        "why": "Gemini is trained heavily on structured web data and documentation. Explicit structure maps well to its training distribution.",
        "headers": "Both markdown headers and labeled sections work well",
        "lists": "Markdown lists with clear hierarchy. Gemini handles nested structures well.",
        "code": "Triple backticks with language. Gemini handles multi-language contexts well.",
    },
    "system_prompt_behavior": "Gemini uses 'system instructions' that persist across turns. Use for persona, safety constraints, and output format. Supports very long system instructions given the context window.",
    "prompting_strategies": [
        "Leverage the massive context: paste entire documents, codebases, or datasets directly",
        "Use explicit output format specifications: 'Output as a JSON object with these exact keys: ...'",
        "For factual tasks, enable Search grounding: 'Use current information to answer'",
        "For analysis, ask for structured output: tables, JSON, or specific schemas",
        "Break complex tasks into numbered sub-tasks — Gemini handles multi-part well",
        "For multimodal: describe what aspect of the image/video to focus on",
        "Use 'Be thorough but concise' to counter verbosity",
        "Specify the audience: 'Explain for a technical audience' vs 'Explain for a beginner'",
    ],
    "example_patterns": {
        "grounded_analysis": "Analyze the following content thoroughly.\n\nContent:\n{content}\n\nProvide your analysis in this exact format:\n1. Summary (2-3 sentences)\n2. Key findings (bullet points)\n3. Potential issues (bullet points)\n4. Recommendations (numbered list)",
        "multimodal": "Look at this image and:\n1. Describe what you see in detail\n2. Identify any {specific_elements}\n3. Provide {analysis_type}\n\nFormat your response as:\n{output_schema}",
        "data_extraction": "Extract structured data from the following {document_type}.\n\nDocument:\n{content}\n\nOutput a JSON object with this schema:\n{json_schema}\n\nRules:\n- If a field is not found, use null\n- Dates should be in ISO 8601 format\n- Numbers should be unformatted integers or floats",
    },
    "temperature_guidance": "Default 1.0. Use 0.0-0.2 for extraction/factual. 0.4-0.7 for analysis. 0.8-1.0 for creative. Gemini also supports top_k sampling.",
    "token_efficiency": "Gemini's tokenizer handles multilingual content efficiently. The massive context window means you rarely need to summarize — just paste the full content. But be explicit about what parts to focus on to avoid diffuse responses.",
    "special_features": [
        "1M+ context: Paste entire repos, books, or video transcripts directly",
        "Search grounding: Enable for real-time factual queries",
        "Multimodal: Natively processes images, video, and audio — reference specific elements",
        "Code execution: Can run Python code for data analysis",
        "Structured output: Can output guaranteed JSON with schema enforcement",
        "Thinking mode: Gemini 2.5 supports extended reasoning with thinking budgets",
    ],
},

# ================================================================
# MICROSOFT COPILOT
# ================================================================
"Microsoft Copilot (GPT-4 based)": {
    "model_family": "GPT-4 Turbo / GPT-4o (Microsoft-hosted)",
    "context_window": "128K tokens",
    "output_limit": "~4,096 tokens (typically shorter in practice)",
    "strengths": [
        "Deep integration with Microsoft 365 ecosystem",
        "Real-time web search integrated by default",
        "Good at productivity-oriented tasks (emails, reports, presentations)",
        "Strong at document summarization and reformatting",
        "Handles business communication well",
        "Can reference uploaded files and images",
    ],
    "weaknesses": [
        "More constrained than raw GPT-4o — Microsoft safety layer adds restrictions",
        "Output length is often shorter than direct API access",
        "Cannot run code like ChatGPT's Code Interpreter",
        "Sometimes adds unwanted disclaimers or source citations",
        "Less flexible for creative or unconventional tasks",
        "Web search results can dominate responses even when not needed",
    ],
    "formatting_preferences": {
        "best_structure": "Professional framing + clear task scope + expected deliverable",
        "why": "Copilot is optimized for business/productivity. Professional framing activates its strongest behavior patterns. Think 'workplace assistant' framing.",
        "headers": "Simple, professional headers. Avoid overly technical formatting.",
        "lists": "Bullet points for requirements, numbered steps for procedures",
        "code": "Backticks work but Copilot is weaker at code than direct GPT-4o access",
    },
    "system_prompt_behavior": "Limited system prompt access in consumer Copilot. Use strong first-message framing instead. Enterprise Copilot allows custom system prompts.",
    "prompting_strategies": [
        "Frame as professional task: 'Act as a professional {role} preparing a {deliverable}'",
        "Be explicit about the deliverable: 'Write a 500-word report' not just 'Tell me about...'",
        "Specify the audience: 'This is for a C-level executive' or 'for a technical team'",
        "For web-sourced answers, say 'Based on current information, ...'",
        "To avoid web search: 'Using only your training knowledge, ...'",
        "Keep prompts focused on single tasks — Copilot handles chained tasks less well",
        "Request specific formats: 'Present as a table with columns for...'",
        "Use professional tone indicators: 'formal', 'executive summary', 'briefing note'",
    ],
    "example_patterns": {
        "professional_task": "Act as a professional {role} with expertise in {domain}.\n\nTask: {task}\n\nDeliverable: {what_to_produce}\n\nRequirements:\n- {req1}\n- {req2}\n\nAudience: {who_will_read_this}\nTone: {formal/informal/technical}\nLength: {word_count}",
        "document_summary": "Summarize the following document for {audience}.\n\nDocument:\n{content}\n\nProvide:\n1. Executive summary (3 sentences)\n2. Key takeaways (5 bullet points)\n3. Action items (if any)\n4. Questions for follow-up",
        "email_draft": "Draft a professional email.\n\nContext: {situation}\nTo: {recipient_role}\nPurpose: {goal}\nTone: {tone}\nLength: {short/medium/detailed}\n\nInclude: {specific_elements}",
    },
    "temperature_guidance": "Not directly controllable in consumer Copilot. Influence via prompt: 'be creative' vs 'be precise and factual'. Enterprise API allows temperature setting.",
    "token_efficiency": "Keep prompts concise — Copilot tends to produce shorter responses. Front-load the most important instructions. Avoid very long prompts as Copilot may lose focus.",
    "special_features": [
        "Web search: Always available — leverage for current data but disable with explicit instruction when not needed",
        "Microsoft 365: Can reference and process Word, Excel, PowerPoint files in enterprise version",
        "Image generation: Can create images via DALL-E integration",
        "Notebook mode: For longer, less filtered responses",
    ],
},

# ================================================================
# MISTRAL
# ================================================================
"Mistral (Mistral AI)": {
    "model_family": "Mistral Large / Medium / Small",
    "context_window": "128K tokens (Mistral Large)",
    "output_limit": "~8,192 tokens",
    "strengths": [
        "Excellent multilingual capabilities, especially European languages",
        "Strong at code generation and technical tasks",
        "Good instruction-following with less safety over-refusal",
        "Efficient and fast — good cost-performance ratio",
        "Strong at structured output and JSON generation",
        "Handles function calling reliably",
        "Good at concise, direct responses",
    ],
    "weaknesses": [
        "Less strong at nuanced reasoning compared to Claude/GPT-4o",
        "Smaller training data footprint — less broad world knowledge",
        "Can be too terse when detail is needed",
        "Less reliable at very long, multi-step reasoning chains",
        "Weaker at creative writing compared to larger models",
        "Less robust at handling ambiguous or underspecified instructions",
    ],
    "formatting_preferences": {
        "best_structure": "Direct, explicit instructions with clear format specifications",
        "why": "Mistral responds best to clear, unambiguous instructions. It doesn't infer implicit requirements as well as larger models — spell everything out.",
        "headers": "Simple markdown headers work. Keep structure flat, not deeply nested.",
        "lists": "Numbered lists for sequential tasks. Keep each item self-contained.",
        "code": "Backticks with language. Mistral is strong at code — provide clear specs.",
    },
    "system_prompt_behavior": "Mistral supports system prompts via the API. Use for role definition and constraints. Keep system prompts focused — overly long system prompts can degrade performance.",
    "prompting_strategies": [
        "Be explicit about everything — Mistral infers less from context than Claude/GPT-4o",
        "Specify output format precisely: 'Output exactly as JSON with keys: ...'",
        "For reasoning tasks, explicitly request step-by-step: 'Show your reasoning before the answer'",
        "Keep instructions sequential — one thing at a time works better than complex multi-part asks",
        "Use few-shot examples for non-obvious formats or patterns",
        "For multilingual: specify input and output languages explicitly",
        "Avoid implicit assumptions — state constraints and edge cases directly",
        "For code: specify language, framework, style, AND error handling approach",
    ],
    "example_patterns": {
        "explicit_task": "Task: {task_description}\n\nInput: {input}\n\nInstructions:\n1. {step1}\n2. {step2}\n3. {step3}\n\nOutput format: {format_spec}\n\nConstraints:\n- {constraint1}\n- {constraint2}",
        "code_task": "Write a {language} function that {description}.\n\nFunction signature: {signature}\n\nBehavior:\n- Input: {input_spec}\n- Output: {output_spec}\n- Edge cases: {edge_cases}\n\nStyle: {style_guide}\nError handling: {error_approach}",
        "multilingual": "Translate the following text from {source_lang} to {target_lang}.\n\nPreserve:\n- Tone and register\n- Technical terminology\n- Formatting\n\nText:\n{content}\n\nOutput only the translation, no explanations.",
    },
    "temperature_guidance": "Default 0.7. Use 0.0-0.1 for deterministic tasks (code, extraction). 0.3-0.5 for analysis. 0.7-1.0 for creative work. Mistral is more sensitive to temperature than larger models.",
    "token_efficiency": "Mistral's tokenizer is efficient for European languages. Keep prompts focused and well-structured. Shorter, clearer prompts perform better than verbose ones.",
    "special_features": [
        "Function calling: Reliable tool use with JSON schema definitions",
        "JSON mode: Can enforce structured JSON output",
        "Multilingual: Particularly strong in French, German, Spanish, Italian",
        "Code generation: Strong across Python, JavaScript, Rust, and more",
        "Le Chat: Web interface with search and canvas features",
    ],
},

# ================================================================
# LLAMA (Meta)
# ================================================================
"Llama (Meta, open source)": {
    "model_family": "Llama 4 / Llama 3.3",
    "context_window": "128K tokens (Llama 3.3), 10M tokens (Llama 4 Scout)",
    "output_limit": "Varies by hosting provider, typically 4K-8K tokens",
    "strengths": [
        "Open source — fully customizable, fine-tunable, self-hostable",
        "Strong code generation (Code Llama variants)",
        "Good at following structured prompts with clear formatting",
        "No content restrictions from the model itself (depends on hosting)",
        "Competitive with proprietary models at many tasks",
        "Available in multiple sizes for different hardware constraints",
        "Large ecosystem of fine-tuned variants for specific tasks",
    ],
    "weaknesses": [
        "Less reliable at implicit instruction following — needs explicit guidance",
        "Weaker at nuanced reasoning and multi-step logic than Claude/GPT-4o",
        "Prone to repetition in longer outputs",
        "Less world knowledge than models trained on larger/newer data",
        "Quality varies significantly by hosting provider and quantization",
        "Weaker at self-correction — tends to commit to first approach",
        "Chat-tuned versions can be overly conversational when precision is needed",
    ],
    "formatting_preferences": {
        "best_structure": "Explicit format templates with clear delimiters + few-shot examples",
        "why": "Llama models have less implicit format understanding. Show, don't tell — provide concrete examples of the exact output format you want.",
        "headers": "Simple labeled sections: 'INPUT:', 'INSTRUCTIONS:', 'OUTPUT:'. Avoid complex nesting.",
        "lists": "Numbered lists with each step being self-contained and unambiguous",
        "code": "Backticks with language. Provide function signatures and expected behavior explicitly.",
    },
    "system_prompt_behavior": "Uses [INST] and <<SYS>> tags (Llama 2 format) or <|begin_of_text|> tokens (Llama 3+). System prompt support varies by hosting provider. Some providers use standard system/user message format. Keep system prompts short and directive.",
    "prompting_strategies": [
        "Be hyper-explicit — state everything, assume nothing is inferred",
        "Provide at least one few-shot example of the exact format you want",
        "Use clear section delimiters: 'INPUT:', 'TASK:', 'FORMAT:', 'OUTPUT:'",
        "For reasoning, provide a worked example showing the step-by-step process",
        "Keep individual steps simple and atomic — avoid compound instructions",
        "Specify what NOT to include: 'Do not add explanations or preamble'",
        "For long outputs, add mid-prompt reminders about format requirements",
        "Repeat critical constraints at the end of the prompt",
        "Use temperature 0.1-0.3 for tasks requiring precision",
    ],
    "example_patterns": {
        "few_shot_explicit": "TASK: {task_description}\n\nFORMAT: {format_description}\n\nEXAMPLE 1:\nInput: {ex1_input}\nOutput: {ex1_output}\n\nEXAMPLE 2:\nInput: {ex2_input}\nOutput: {ex2_output}\n\nNOW YOUR TURN:\nInput: {actual_input}\nOutput:",
        "structured_extraction": "Extract the following fields from the text below.\n\nFIELDS TO EXTRACT:\n- {field1}: {description}\n- {field2}: {description}\n- {field3}: {description}\n\nTEXT:\n{content}\n\nOUTPUT FORMAT:\n{field1}: [value]\n{field2}: [value]\n{field3}: [value]\n\nIMPORTANT: Output ONLY the fields above. No additional text.",
        "code_generation": "Write a {language} function.\n\nFunction name: {name}\nParameters: {params}\nReturns: {return_type}\n\nBehavior:\n{step_by_step_behavior}\n\nExample usage:\n{example_code}\n\nExpected output:\n{expected_output}\n\nWrite ONLY the function code. No explanations.",
    },
    "temperature_guidance": "Use lower temperature than proprietary models. 0.1-0.3 for factual/code. 0.5-0.7 for analysis. 0.8-1.0 for creative. Llama models are more sensitive to temperature — small changes have outsized effects.",
    "token_efficiency": "Token efficiency varies by quantization level. GPTQ/AWQ quantized models may need simpler prompts. Full-precision models handle longer prompts better. Front-load critical instructions.",
    "special_features": [
        "Fine-tuning: Can be fine-tuned on your specific task data with LoRA or full fine-tuning",
        "Self-hosting: Run on your own hardware for data privacy",
        "Quantization: Available in 4-bit, 8-bit, and full precision for different hardware",
        "Tool use: Llama 3.1+ supports native tool calling",
        "Multimodal: Llama 4 supports image understanding natively",
        "Long context: Llama 4 Scout supports up to 10M token context",
    ],
},

# ================================================================
# DEEPSEEK
# ================================================================
"DeepSeek (DeepSeek AI)": {
    "model_family": "DeepSeek-V3 / DeepSeek-R1",
    "context_window": "128K tokens",
    "output_limit": "~8,192 tokens (longer with R1 reasoning)",
    "strengths": [
        "Exceptional code generation — rivals GPT-4o and Claude at coding",
        "Strong mathematical and logical reasoning (especially R1)",
        "R1 model has native chain-of-thought reasoning (shows thinking process)",
        "Very competitive price-performance ratio",
        "Strong at algorithm design and optimization",
        "Good at structured data processing and transformation",
        "Handles complex multi-file code tasks well",
    ],
    "weaknesses": [
        "Weaker at creative writing and nuanced prose",
        "Less broad general knowledge compared to GPT-4o or Claude",
        "English output quality can be inconsistent — occasional awkward phrasing",
        "R1's thinking process can be excessively long for simple tasks",
        "Less reliable at following complex formatting instructions",
        "Weaker at tasks requiring cultural context or idiomatic language",
        "Can be overly literal — misses subtext and implicit requirements",
    ],
    "formatting_preferences": {
        "best_structure": "Clear problem statement + explicit reasoning framework + output spec",
        "why": "DeepSeek excels when given a clear reasoning framework to follow. Its strength is systematic thinking — leverage this by structuring prompts as problems to solve.",
        "headers": "Labeled sections work well: 'Problem:', 'Approach:', 'Constraints:', 'Output:'",
        "lists": "Numbered steps for algorithms and procedures. Decision trees for conditional logic.",
        "code": "Triple backticks with language. Include test cases and expected output.",
    },
    "system_prompt_behavior": "DeepSeek supports system prompts via API. Keep them focused on the task domain. For R1, system prompts can guide the reasoning process.",
    "prompting_strategies": [
        "Frame tasks as problems to solve rather than content to generate",
        "For R1: explicitly ask to 'think through this step by step' — activates deep reasoning mode",
        "Provide test cases or validation criteria for code tasks",
        "Use explicit chain-of-thought frameworks: 'First analyze, then plan, then implement'",
        "For code: specify language, framework, performance requirements, and edge cases",
        "Include input/output examples for data transformation tasks",
        "For math/logic: state the problem formally, then ask for the solution with proof",
        "Keep creative requirements minimal — focus on technical precision",
        "Break complex problems into sub-problems with clear interfaces",
    ],
    "example_patterns": {
        "code_problem": "Problem: {description}\n\nLanguage: {language}\nInput format: {input_spec}\nOutput format: {output_spec}\n\nConstraints:\n- {constraint1}\n- {constraint2}\n- Time complexity: {time_req}\n- Space complexity: {space_req}\n\nTest cases:\nInput: {test1_in} -> Expected: {test1_out}\nInput: {test2_in} -> Expected: {test2_out}\n\nSolve this problem. Show your reasoning, then provide the final code.",
        "reasoning_chain": "Problem: {problem_statement}\n\nApproach:\n1. First, analyze {what_to_analyze}\n2. Then, identify {what_to_identify}\n3. Finally, determine {what_to_determine}\n\nShow your complete reasoning process, then provide the final answer.",
        "data_transform": "Transform the following data:\n\nInput format: {input_format}\nOutput format: {output_format}\n\nTransformation rules:\n1. {rule1}\n2. {rule2}\n3. {rule3}\n\nInput data:\n{data}\n\nOutput:",
    },
    "temperature_guidance": "Use 0.0 for code and math (deterministic). 0.3-0.5 for analysis. Avoid high temperature — DeepSeek's creative output quality drops significantly above 0.7.",
    "token_efficiency": "DeepSeek is efficient with code tokens. For R1, be aware that the thinking process consumes tokens — budget accordingly. Keep prompts focused on the core problem.",
    "special_features": [
        "R1 reasoning: Native chain-of-thought that shows the full thinking process",
        "Fill-in-the-middle: Strong at code completion and infilling",
        "Multi-file code: Handles cross-file references and project-level tasks",
        "Mathematical reasoning: Strong at formal proofs and derivations",
        "Function calling: Supports structured tool use via API",
    ],
},

# ================================================================
# GROK (xAI)
# ================================================================
"Grok (xAI)": {
    "model_family": "Grok 3 / Grok 3 Mini",
    "context_window": "128K tokens",
    "output_limit": "~8,192 tokens",
    "strengths": [
        "Direct, unfiltered communication style — less hedging than competitors",
        "Strong at technical and scientific topics",
        "Access to real-time X (Twitter) data for current events",
        "Good at providing contrarian or unconventional perspectives",
        "Strong at humor and wit when appropriate",
        "Handles controversial or edgy topics more openly",
        "Good at concise, actionable responses",
        "DeepSearch mode for thorough research tasks",
        "Think mode for complex reasoning (similar to o1/R1)",
    ],
    "weaknesses": [
        "Smaller training corpus — less comprehensive knowledge base",
        "Can be too informal when professionalism is needed",
        "Less reliable at very long structured outputs",
        "Fewer safety guardrails — can produce less filtered content",
        "Weaker at nuanced, multi-perspective analysis",
        "Less ecosystem integration compared to GPT/Gemini",
        "API access is more limited than competitors",
    ],
    "formatting_preferences": {
        "best_structure": "Direct task statement + explicit constraints + format spec",
        "why": "Grok works best with no-nonsense, direct prompts. Skip lengthy preambles and get straight to the task. Clear boundaries prevent the model from being too casual.",
        "headers": "Simple headers work. Keep prompts lean and direct.",
        "lists": "Short, punchy bullet points. Avoid verbose list items.",
        "code": "Backticks with language. Grok handles code well but keep specs clear.",
    },
    "system_prompt_behavior": "Grok supports system prompts via API. Use for tone control — Grok defaults to casual/witty so specify 'professional tone' if needed. Keep system prompts concise.",
    "prompting_strategies": [
        "Be direct — skip preamble and pleasantries, state the task immediately",
        "Set explicit tone: 'Respond professionally' or 'Be direct and technical'",
        "Use clear task boundaries: 'Do X. Do not do Y.'",
        "For factual tasks: 'Provide only verified information. No speculation.'",
        "Leverage its directness for tasks where bluntness is a feature (code review, feedback)",
        "For research: use 'DeepSearch' framing to get thorough, sourced responses",
        "For reasoning: explicitly request 'Think mode' or step-by-step analysis",
        "Keep prompts concise — Grok responds better to tight, focused instructions",
        "For current events: leverage its X/Twitter data access explicitly",
    ],
    "example_patterns": {
        "direct_task": "Task: {task}\n\nConstraints:\n- {constraint1}\n- {constraint2}\n\nOutput: {format}\n\nDo not include explanations or caveats.",
        "technical_analysis": "Analyze {subject} from a technical perspective.\n\nFocus on:\n1. {aspect1}\n2. {aspect2}\n3. {aspect3}\n\nBe direct. Skip disclaimers. Provide actionable insights.",
        "code_review": "Review this code for bugs, performance issues, and style problems.\n\nCode:\n{code}\n\nFor each issue:\n- Line number\n- Problem\n- Fix\n\nBe blunt. No sugarcoating.",
    },
    "temperature_guidance": "Default works well for most tasks. Use 0.0-0.2 for factual/technical precision. 0.5-0.7 for analysis. Higher temperature for creative/humorous content.",
    "token_efficiency": "Keep prompts concise — Grok performs best with focused instructions. Long, verbose prompts can cause it to lose focus. Front-load the key task.",
    "special_features": [
        "DeepSearch: Extended research mode for thorough information gathering",
        "Think mode: Chain-of-thought reasoning for complex problems",
        "Real-time X data: Access to current Twitter/X posts and trends",
        "Image generation: Can create images via Aurora model",
        "Image understanding: Can analyze uploaded images",
        "Less filtered: Handles edgy/controversial topics more directly than competitors",
    ],
},

}


def get_profile(llm_name: str) -> dict:
    """Get the full profile for an LLM by name or partial match."""
    # Exact match
    if llm_name in LLM_PROFILES:
        return LLM_PROFILES[llm_name]
    # Partial match
    lower = llm_name.lower()
    for key, profile in LLM_PROFILES.items():
        if lower in key.lower():
            return profile
    return {}


def get_profile_text(llm_name: str) -> str:
    """Get a formatted text representation of an LLM profile for injection into prompts."""
    profile = get_profile(llm_name)
    if not profile:
        return f"No detailed profile found for {llm_name}. Use general best practices."

    lines = [f"=== DETAILED PROFILE: {llm_name} ===\n"]
    lines.append(f"Model family: {profile['model_family']}")
    lines.append(f"Context window: {profile['context_window']}")
    lines.append(f"Output limit: {profile['output_limit']}")
    lines.append(f"Temperature guidance: {profile['temperature_guidance']}")
    lines.append(f"Token efficiency: {profile['token_efficiency']}")

    lines.append(f"\nSystem prompt behavior: {profile['system_prompt_behavior']}")

    lines.append(f"\nFormatting preferences:")
    fmt = profile['formatting_preferences']
    lines.append(f"  Best structure: {fmt['best_structure']}")
    lines.append(f"  Why: {fmt['why']}")
    lines.append(f"  Headers: {fmt['headers']}")
    lines.append(f"  Lists: {fmt['lists']}")
    lines.append(f"  Code: {fmt['code']}")

    lines.append(f"\nStrengths:")
    for s in profile['strengths']:
        lines.append(f"  + {s}")

    lines.append(f"\nWeaknesses (design prompts to compensate):")
    for w in profile['weaknesses']:
        lines.append(f"  - {w}")

    lines.append(f"\nPrompting strategies:")
    for i, s in enumerate(profile['prompting_strategies'], 1):
        lines.append(f"  {i}. {s}")

    lines.append(f"\nExample prompt patterns:")
    for name, pattern in profile['example_patterns'].items():
        lines.append(f"\n  [{name}]:")
        for line in pattern.split('\n'):
            lines.append(f"    {line}")

    lines.append(f"\nSpecial features to leverage:")
    for f in profile['special_features']:
        lines.append(f"  * {f}")

    return '\n'.join(lines)


def get_all_llm_names() -> list[str]:
    """Return all supported LLM names."""
    return list(LLM_PROFILES.keys())
