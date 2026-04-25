# AGENTS.md

## Project-Specific Skills

Before working in this repository, read `CLAUDE.md` and follow its project
guidance alongside this file.

This project keeps project-local skill definitions under `.claude/skills`.

When the user asks to use one of these skills, or when a task clearly matches a
skill description, read the corresponding `SKILL.md` before answering and follow
its workflow:

- `diversity-check`: `.claude/skills/diversity-check/SKILL.md`
  - Use for analyzing the diversity of decomposition axes in a set of Ogiri
    answers.
  - Do not evaluate whether answers are funny.
- `fun-check`: `.claude/skills/fun-check/SKILL.md`
  - Use for identifying risks or caveats in a set of Ogiri answers.
  - Do not judge whether answers are funny; report only risks to know before
    use.
- `cluster-fit-check`: `.claude/skills/cluster-fit-check/SKILL.md`
  - Use for analyzing how Ogiri answers align with literature-derived user
    cluster preference features.
  - Do not judge whether answers are funny; report cluster-fit signals and
    improvement notes.

Skill-related content and Ogiri analysis should be written in Japanese.
