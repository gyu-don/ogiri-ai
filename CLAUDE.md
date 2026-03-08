# CLAUDE.md

## Project Overview

This repository contains a Claude Code skill for generating Japanese comedy responses (大喜利/Ogiri). Ogiri is a form of Japanese improvisational comedy where participants provide witty, unexpected answers to prompts.

## Repository Structure

- `.claude/skills/ogiri-ai/SKILL.md` - The main skill definition containing comprehensive instructions for generating Ogiri responses
- `.claude/settings.json` - Claude Code configuration with Jujutsu VCS integration

## Version Control

This project uses **Jujutsu (jj)** as the primary version control system, with Git as the backing store.

## Skill Files

The `.claude/skills/ogiri-ai/SKILL.md` file contains the main skill logic. This file is experimental and frequently updated with different approaches to generating humor. Refer to the skill file itself for the current methodology.

## Key Concept: Semantic Mode Collapse (SMC)

SMC is the core problem this skill tries to solve. When an LLM receives the same type of prompt repeatedly, it converges on the same structural decomposition — not the same words, but the same *skeleton*. For ogiri, this means the model always attacks the same elements of the topic (e.g., for wedding prompts: always BGM, vows, bouquet). Surface variation in word choice masks structural convergence.

**Causes:**
- Training data contains dense cultural templates for common scenarios
- RLHF typicality bias amplifies the most frequent patterns
- The smarter the model, the more precisely it finds the "optimal" decomposition — and converges faster

**Key insight on instructions:**
- Positive instructions (examples, types, tags) create new attractors → avoid
- Negative instructions (what NOT to do) are limited by self-policing: the model that generates defaults is the same model that's supposed to avoid them
- *Form-level* hints (style, format) do NOT cause SMC — they constrain HOW, not WHAT
- Process inversion (逆走: start from punchline, connect to topic) is the only intervention that changes the generation pathway itself

## Skill Development Process

When iterating on `SKILL.md`, follow this cycle:

1. **Hypothesize** — identify the specific failure mode (SMC? not funny? verbose?)
2. **Edit** `SKILL.md` with a targeted change
3. **Verify with parallel subagents** — run at least 2 agents per topic, 2+ topics:
   ```
   claude -p --model=opus "/ogiri-ai <お題>"
   ```
   Or launch subagents that read the skill file and execute it.
4. **Evaluate** across two dimensions:
   - **Diversity**: do runs on the same topic produce different outputs? Are the 5 answers structurally distinct?
   - **Quality**: are the outputs actually funny, or just structurally diverse?
5. **Test with novel topics** — if a topic has been used repeatedly in testing, the model may overfit to it. Always end a development session by testing with an entirely different topic category.
6. **Commit** with a message explaining the hypothesis and result

**Warning:** Evaluation of "funniness" by the LLM itself is unreliable. The model rates its own outputs as funny because it completed the prescribed process. Use structural checks (diversity, specificity, visual quality) as proxies, and rely on human judgment for final quality assessment.

## Language Guidelines

When creating or modifying files in this repository:
- **Ogiri-related content** (e.g., `.claude/skills/ogiri-ai/`) should be written in **Japanese**
- General infrastructure should be written in **English**
