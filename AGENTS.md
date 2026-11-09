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

The evaluation tools live in [gyu-don/humor-skills](https://github.com/gyu-don/humor-skills). The validated checks (`overlap-check`, `trait-check`) are installed into `.claude/skills/` (git-ignored; `skills-lock.json` is the committed pin). The research judges (`funniness-score`, `risk-flags`, `diversity-check`, `cluster-fit-check`) are not installable and run from a humor-skills checkout. `DEVELOPMENT.md` has the install and invocation commands.

## Secrets

Anything calling the TypeSafe AI (Jev) API needs `TYPESAFE_API_KEY`. If it is not already in the environment, run the command under `doppler run --`. See the "Secrets and environment variables" section of `DEVELOPMENT.md`.

## Codex Development Discipline

When Codex is asked to improve the ogiri prompt, `SKILL.md`, or any evaluation skill, it must treat `DEVELOPMENT.md` as the execution contract, not background reading.

Required behavior:
- Read `DEVELOPMENT.md` and the relevant skill files before editing.
- Start with a concrete failure hypothesis, then make a targeted prompt change. Do not reword large sections without naming the failure mode.
- Use the two-tier loop described in `DEVELOPMENT.md`: the **light loop** (`ogiri-ai` generation + `overlap-check` + `trait-check` + hand counts) for everyday iteration, and the **gate check** (pooled 2-run generation with a baseline, an unseen topic, hard mechanical checks, `trait-check` regression checks and similarity warnings against the baseline, and an optional blind human comparison) before claiming an improvement. The research judges are optional diagnostics only and never pass or fail a change.
- Prefer independent runs through subagents or CLI invocations. If those are unavailable, run the same checks locally and clearly mark the verification as limited.
- Keep per-iteration metrics: `overlap-check` near duplicates, `trait-check` `concrete`/`indirect` means, hand counts (「」, form violations, repeated mechanisms/templates/metaphor systems, cross-run material), and — at gates — the mechanical-check results, the baseline comparison (including the `compare.ts` win rate), and the blind human comparison if one was run.
- Do not claim the prompt is "good enough" from self-review alone. Report the gate outcome exactly as `DEVELOPMENT.md` defines it (mechanically passed / validated / not passed). Evaluator scores count as evidence of funniness only if humor-skills' latest validation marks them `gate: yes`.
- Never make the loop wait on a human. Ask for a blind comparison only when a human is present, and record it in humor-skills `data/human-evals/`.
- If the gate check is not passed in the current session, report the exact loop depth reached, the remaining failing criteria, and the next concrete intervention.

Shortcut rules:
- Do not skip raw candidate generation.
- Do not replace the evaluation skills with a generic opinion about whether answers are funny.
- Do not optimize for one metric while ignoring diversity, relevance, empathy, and convergence. Never treat a rise in `trait-check` values as a reason to accept a change; they catch regressions only.
- Do not end with only a proposal when the user asked for an improvement; edit the relevant file and verify as far as the environment allows.

## Sub-Agent Usage for Ogiri

When delegating Ogiri generation to sub-agents, apply the following defaults unless the user specifies otherwise:

**Model and effort defaults:**
- Claude: the latest Opus at high effort or below, **or** Sonnet 4.6 (or later) at high effort or below. (Decision of 2026-11-08: the latest Opus is no longer token-inefficient, so the earlier Opus 4.6 cap was lifted. Record the resolved model id in the iteration log.) Prefer Opus when the change targets answers Sonnet cannot produce (see the generator capability check in `DEVELOPMENT.md`).
- GPT (Codex): the latest Sol at high effort or below (`gpt-6.1-sol` as of 2026-11-09). Older GPT versions have no token-efficiency advantage, so prefer the newest. Run it from an isolated directory holding only the skill, not at the repo root (see "How to invoke" in `DEVELOPMENT.md`).
- Token cost order: Sonnet high < Sol high < Opus high. Larger models tend to be funnier, though not strictly in cost or size order. Claude and GPT are both valid generators; register the family, and never mix families within one pooled set or between baseline and candidate. Details in `DEVELOPMENT.md` ("Generator choice").

**When making many sub-agent calls:**
- Prefer lower effort settings and/or lower-tier models to control costs.
- Reserve higher-effort or higher-tier models for cases where response quality is likely to benefit meaningfully.

## Language Guidelines

When creating or modifying files in this repository:
- **Ogiri-related content** (e.g., `.claude/skills/ogiri-ai/`) should be written in **Japanese**
- General infrastructure should be written in **English**
