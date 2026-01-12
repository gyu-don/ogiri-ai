# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a Claude Code skill for generating Japanese comedy responses (大喜利/Ogiri). Ogiri is a form of Japanese improvisational comedy where participants provide witty, unexpected answers to prompts.

## Repository Structure

- `.claude/skills/ogiri-ai/SKILL.md` - The main skill definition containing comprehensive instructions for generating Ogiri responses
- `oogiri_prompt_techniques.md` - Research-based documentation on prompt engineering techniques for improving humor quality
- `.claude/settings.json` - Claude Code configuration with Jujutsu VCS integration

## Version Control

This project uses **Jujutsu (jj)** as the primary version control system, with Git as the backing store.

### Post-Edit Hook
A hook is configured in `.claude/settings.json` that automatically runs `jj` after any Edit or Write tool usage. This ensures that changes are tracked in Jujutsu automatically.

### Common Commands
- `jj status` - View current working state
- `jj log` - View commit history
- `jj describe` - Edit the description of the current change
- `jj new` - Create a new change
- `jj git push` - Push changes to Git remote

Note: Standard git commands work but `jj` is the preferred interface for this repository.

## Skill Files

The `.claude/skills/ogiri-ai/SKILL.md` file contains the main skill logic. This file is experimental and frequently updated with different approaches to generating humor. Refer to the skill file itself for the current methodology.

The `oogiri_prompt_techniques.md` file contains research-based documentation on prompt engineering techniques, including effect sizes for various humor-generation strategies.

## Language Guidelines

When creating or modifying files in this repository:
- **Ogiri-related content** (e.g., `.claude/skills/ogiri-ai/`, `oogiri_prompt_techniques.md`) should be written in **Japanese**
- **Non-Ogiri skills** (e.g., `.claude/skills/jj/`) and general infrastructure should be written in **English**
