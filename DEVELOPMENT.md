# Development Guide

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
3. **Verify with parallel subagents** — run at least 2 agents per topic, 2+ topics. Use one of the following launch methods depending on the agent environment:
   ```
   # Claude Code
   claude -p --model=<model> --effort=<effort> "/ogiri-ai <お題>"

   # Codex CLI
   codex exec -C . -m <model> -c 'model_reasoning_effort="<effort>"' \
     "Read .claude/skills/ogiri-ai/SKILL.md and follow it to answer this topic: <お題>"
   ```
   Or launch subagents that read the skill file and execute it.
4. **Evaluate diversity** using the `/diversity-check` skill:
   - Collect outputs from step 3 and run `/diversity-check` with the topic and all answers
   - Target: **5+ distinct decomposition axes per 10 answers** (2 runs)
   - 3-4 axes = improvement needed, 1-2 = still converging
5. **Evaluate quality risks** using the `/fun-check` skill:
   - Pass the topic and all answers to `/fun-check`
   - It reports *risks* (not verdicts) per answer: ベタ / 絵なし / ひねりなし / 共感 / 認知度 / 長さ / 滑り
   - It also flags relative typicality, structural overlap, and repeated surreal escape patterns
   - Use the output to identify *which answers to replace* and *why*, then re-run `/ogiri-ai`
   - `/fun-check` does **not** judge overall funniness — final quality assessment requires human review (see warning below)
6. **Evaluate preference-cluster fit** using the `/cluster-fit-check` skill when comparing styles or tuning for audience breadth:
   - Pass the topic and all answers to `/cluster-fit-check`
   - It estimates how each answer aligns with literature-derived user cluster preference features
   - Treat its scores as *preference-fit signals*, not funniness scores
   - Use its improvement notes to decide whether to broaden appeal (remove strong negative features) or intentionally sharpen toward a cluster
   - Do not optimize answers by mechanically adding surface features such as parentheses, ellipses, or slang
7. **Test with novel topics** — if a topic has been used repeatedly in testing, the model may overfit to it. Always end a development session by testing with an entirely different topic category.
8. **Commit** with a message explaining the hypothesis and result

**Warning:** Evaluation of "funniness" by the LLM itself is unreliable. The model rates its own outputs as funny because it completed the prescribed process. Use structural checks (diversity, specificity, visual quality) as proxies, and rely on human judgment for final quality assessment.

### Evaluation skills at a glance

| Skill | What it measures | What it does NOT measure |
|---|---|---|
| `diversity-check` | Structural variety of decomposition axes | Funniness |
| `fun-check` | Per-answer risks (ベタ・絵・ひねり・共感・認知度・長さ・滑り・被り・相対典型性) | Overall funniness |
| `cluster-fit-check` | Alignment with literature-derived user cluster preference features | Overall funniness or universal appeal |
| Human review | Overall funniness | — |
