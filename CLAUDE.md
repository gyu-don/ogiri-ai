## Project Overview

This repository contains a Claude Code skill for generating Japanese comedy responses (大喜利/Ogiri). Ogiri is a form of Japanese improvisational comedy where participants provide witty, unexpected answers to prompts.

## Repository Structure

- `.claude/skills/ogiri-ai/SKILL.md` - The main skill definition containing comprehensive instructions for generating Ogiri responses
- `.claude/settings.json` - Claude Code configuration with Jujutsu VCS integration

## Version Control

This project uses **Jujutsu (jj)** as the primary version control system, with Git as the backing store.

## Skill Files

The `.claude/skills/ogiri-ai/SKILL.md` file contains the main skill logic. This file is experimental and frequently updated with different approaches to generating humor. Refer to the skill file itself for the current methodology.

## Development

See `DEVELOPMENT.md` for the skill development process, design theory, and iteration methodology.

## Codex Development Discipline

When Codex is asked to improve the ogiri prompt, `SKILL.md`, or any evaluation skill, it must treat `DEVELOPMENT.md` as the execution contract, not background reading.

Required behavior:
- Read `DEVELOPMENT.md` and the relevant skill files before editing.
- Start with a concrete failure hypothesis, then make a targeted prompt change. Do not reword large sections without naming the failure mode.
- Use the full evaluation loop described in `DEVELOPMENT.md`: `ogiri-ai` generation, `diversity-check`, `fun-check`, `cluster-fit-check`, `humor-rank`, and `humor-eval`.
- Prefer independent runs through subagents or CLI invocations. If those are unavailable, run the same checks locally and clearly mark the verification as limited.
- Keep per-iteration metrics: diversity axis count, risk counts, dominant cluster-fit signals, pairwise ranking pattern, and average Relevance/Empathy/Overall scores.
- Do not claim the prompt is "good enough" from self-review alone. A change is only validated by loop metrics, and the stricter stop criteria in `DEVELOPMENT.md` require three consecutive passing iterations.
- If the full three-iteration pass streak is not completed in the current session, report the exact loop depth reached, the remaining failing criteria, and the next concrete intervention.

Shortcut rules:
- Do not skip raw candidate generation.
- Do not replace the evaluation skills with a generic opinion about whether answers are funny.
- Do not optimize for one metric while ignoring diversity, relevance, empathy, and cluster lock-in.
- Do not end with only a proposal when the user asked for an improvement; edit the relevant file and verify as far as the environment allows.

## Sub-Agent Usage for Ogiri

When delegating Ogiri generation to sub-agents, apply the following defaults unless the user specifies otherwise:

**Model and effort defaults:**
- Claude: Opus 4.6 at medium effort or below, **or** Sonnet 4.6 (or later) at high effort or below. Do not use Opus 4.7.
- Codex: Use the latest available version at high effort or below. Older Codex versions have no token-efficiency advantage, so prefer the newest.

**When making many sub-agent calls:**
- Prefer lower effort settings and/or lower-tier models to control costs.
- Reserve higher-effort or higher-tier models for cases where response quality is likely to benefit meaningfully.

## Language Guidelines

When creating or modifying files in this repository:
- **Ogiri-related content** (e.g., `.claude/skills/ogiri-ai/`) should be written in **Japanese**
- General infrastructure should be written in **English**
