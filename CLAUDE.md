# CLAUDE.md

## Project Overview

This repository contains a Claude Code skill for generating Japanese comedy responses (大喜利/Ogiri). Ogiri is a form of Japanese improvisational comedy where participants provide witty, unexpected answers to prompts.

## Repository Structure

- `.claude/skills/ogiri-ai/SKILL.md` - The main skill definition containing comprehensive instructions for generating Ogiri responses
- `.claude/skills/diversity-check/SKILL.md` - Dev tool: classifies decomposition axes of answer sets (structure only, no funniness judgment)
- `.claude/skills/funniness-check/SKILL.md` - Dev tool: pairwise funniness screening of answer sets (proxy only; humans are ground truth)
- `evaluations/` - Dated logs of human feedback on generated answers
- `.claude/settings.json` - Claude Code configuration with Jujutsu VCS integration

## Version Control

This project uses **Jujutsu (jj)** as the primary version control system, with Git as the backing store.

## Skill Files

The `.claude/skills/ogiri-ai/SKILL.md` file contains the main skill logic. This file is experimental and frequently updated with different approaches to generating humor. Refer to the skill file itself for the current methodology.

## Development

See `DEVELOPMENT.md` for the skill development process, design theory, and iteration methodology.

## Contamination Prevention (IMPORTANT)

When the `ogiri-ai` skill is invoked to generate answers — whether by an end user or as an evaluation/test run during development — the invocation must read **only** `.claude/skills/ogiri-ai/SKILL.md`. Do NOT read `DEVELOPMENT.md`, `evaluations/`, `.claude/skills/diversity-check/`, `.claude/skills/funniness-check/`, or any other repository file in that invocation. Knowledge of evaluation criteria, judge heuristics, or previously logged answers contaminates the output: the generator starts optimizing for the judge or echoing logged jokes, which invalidates both the answers and any evaluation of them.

The same isolation applies in reverse to `/funniness-check` and `/diversity-check`: a judge invocation sees only the topic and the answers, never the generator's reasoning or `evaluations/`.

Development sessions (diagnosing failures, editing skills, calibrating judges) may read everything — but must delegate generation and judging to separate, isolated invocations rather than doing them inline.

## Language Guidelines

When creating or modifying files in this repository:
- **Ogiri-related content** (e.g., `.claude/skills/ogiri-ai/`) should be written in **Japanese**
- General infrastructure should be written in **English**
