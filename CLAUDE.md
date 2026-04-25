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
