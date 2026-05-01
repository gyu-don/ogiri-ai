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

### Codex autonomous execution prompt

Use this section as the operating prompt for Codex when the task is to improve `ogiri-ai` or its evaluation skills. Its purpose is to prevent shallow prompt editing without evidence.

**Activation:** Any request such as "improve the prompt", "make the skill better", "reduce convergence", "Codex is skipping thinking", or "run the feedback loop" activates this protocol.

**Non-negotiable rule:** Do not stop after editing text. A development turn must include generation, evaluation, and a decision about the next intervention. If tooling, budget, or sandbox limits prevent the full loop, record the blocker explicitly and still run the largest local subset possible.

**Before editing:**
- Read `SKILL.md`, this file, and the evaluation skills that will be used.
- Write one failure hypothesis in concrete terms, for example: "answers pass novelty by escaping into generic eerie imagery, but lose relevance."
- Select at least two fixed topics from different categories for regression. Add one unseen topic before any final gate check.
- Define the metric target before seeing the new outputs.

**One loop iteration means all of the following happened:**
1. Generate candidates with `ogiri-ai`: at least 2 independent runs per fixed topic, producing 10+ answers per topic.
2. Preserve the raw answers. Do not evaluate from memory or from a cleaned-up subset.
3. Run `diversity-check` on each topic and record axis count plus largest-axis share.
4. Run `fun-check` and record total risk rate, risk-type concentration, structural overlap warnings, and surreal-escape warnings.
5. Run `cluster-fit-check` and record any dominant positive or negative feature that appears in more than half of the answers.
6. Use `humor-rank` on plausible finalists or on close pairs where the metrics disagree. Record whether wins concentrate on one brittle pattern.
7. Run `humor-eval` on surviving candidates and record average Relevance, Empathy, and Overall Funniness.
8. Decide one concrete next intervention in `SKILL.md`. The intervention must change behavior, not merely intensify wording.

**Minimum verification before claiming progress:** complete at least one baseline loop and one post-edit loop. If the stricter stop criteria below are not met for three consecutive iterations, say so directly; the correct final state is "improved but not fully validated", not "done".

**What Codex must not do:**
- Do not infer diversity from the apparent variety of nouns; use `diversity-check`.
- Do not treat `fun-check` as a funniness score.
- Do not tune toward cluster-fit by mechanically adding parentheses, ellipses, slang, or other surface features.
- Do not let `humor-eval` Overall Funniness override low Relevance or Empathy.
- Do not discard inconvenient generated answers before scoring.
- Do not change several unrelated prompt mechanisms at once unless the previous loop identified multiple coupled failures.

**Iteration log template:**

```
iteration N
hypothesis:
edit:
topics:
diversity: axes / largest-axis share
fun-check: risk rate / dominant risk / overlap warnings
cluster-fit: dominant signals / lock-in risk
humor-rank: pairwise pattern
humor-eval: avg Relevance / Empathy / Overall
decision: stop / continue, with next intervention
```

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
4. **Evaluate diversity** using `.claude/skills/diversity-check/SKILL.md`:
   - Collect outputs from step 3 and run `diversity-check` with the topic and all answers
   - Target: **5+ distinct decomposition axes per 10 answers** (2 runs)
   - 3-4 axes = improvement needed, 1-2 = still converging
5. **Evaluate quality risks** using `.claude/skills/fun-check/SKILL.md`:
   - Pass the topic and all answers to `fun-check`
   - It reports *risks* (not verdicts) per answer: ベタ / 絵なし / ひねりなし / 共感 / 認知度 / 長さ / 滑り
   - It also flags relative typicality, structural overlap, and repeated surreal escape patterns
   - Use the output to identify *which answers to replace* and *why*, then re-run `/ogiri-ai`
   - `fun-check` does **not** judge overall funniness — final quality assessment requires human review (see warning below)
6. **Evaluate preference-cluster fit** using `.claude/skills/cluster-fit-check/SKILL.md` when comparing styles or tuning for audience breadth:
   - Pass the topic and all answers to `cluster-fit-check`
   - It estimates how each answer aligns with literature-derived user cluster preference features
   - Treat its scores as *preference-fit signals*, not funniness scores
   - Use its improvement notes to decide whether to broaden appeal (remove strong negative features) or intentionally sharpen toward a cluster
   - Do not optimize answers by mechanically adding surface features such as parentheses, ellipses, or slang
7. **Rank candidates pairwise** using `.claude/skills/humor-rank/SKILL.md`:
   - Compare candidates within the same topic (A/B) and keep winners
   - Use this as a *relative ranking* signal, not a universal funniness score
   - Require clear relevance + empathy before novelty can win
8. **Run multi-axis scoring** using `.claude/skills/humor-eval/SKILL.md`:
   - Score each surviving candidate on 6 axes: Novelty / Clarity / Relevance / Intelligence / Empathy / Overall Funniness
   - Apply a gate: if Relevance or Empathy is too low, cap overall score and regenerate
9. **Run an explicit feedback loop until quality is sufficient**:
   - Treat steps 3-8 as one loop iteration
   - After each iteration, edit `SKILL.md` based on the evaluation reports and run the same topics again
   - Keep a per-iteration log (`iteration N`) with: diversity axis count, fun-check risk counts, top cluster-fit signals, pairwise wins/losses, and average 6-axis scores
   - Continue until all stop criteria are met in **three consecutive iterations** (not two)
10. **Stricter stop criteria (“sufficiently good”)**:
   - **Diversity floor**: at least **6 decomposition axes per 10 answers**, and no single axis may contain >40% of answers
   - **Diversity stability**: worst iteration in the 3-iteration pass streak must still be ≥6 axes
   - **Risk ceiling** (`fun-check`): at most 30% of answers may have any risk flag, and no single risk type may account for >30% of all flagged risks
   - **No repeated overlap warnings**: if structural-overlap or surreal-escape warnings appear in two consecutive iterations, loop must continue
   - **Cluster anti-lock-in**: no single positive or negative cluster-fit feature may appear as the dominant signal in >50% of answers
   - **Pairwise robustness** (`humor-rank`): pairwise wins should not concentrate on one brittle pattern (e.g., novelty-only wins)
   - **Empathy/Relevance floor** (`humor-eval`): average Empathy and Relevance should both be ≥2.5 for finalists
   - **Cross-topic robustness**: all above conditions must hold for at least 2 topic categories in the same development session
11. **If criteria are not met, force another improvement cycle**:
   - Add or revise one concrete intervention in `SKILL.md` (do not only reword)
   - Re-run the same topic set, then one additional unseen topic before the next gate check
12. **Test with novel topics** — always end a development session by testing with an entirely different topic category.
13. **Commit** with a message explaining the hypothesis, loop count, metrics per iteration, and what intervention changed between iterations

**Warning:** Evaluation of "funniness" by the LLM itself is unreliable. The model rates its own outputs as funny because it completed the prescribed process. Use structural checks (diversity, specificity, visual quality) as proxies, and rely on human judgment for final quality assessment.

### Evaluation skills at a glance

| Skill | What it measures | What it does NOT measure |
|---|---|---|
| `diversity-check` | Structural variety of decomposition axes | Funniness |
| `fun-check` | Per-answer risks (ベタ・絵・ひねり・共感・認知度・長さ・滑り・被り・相対典型性) | Overall funniness |
| `cluster-fit-check` | Alignment with literature-derived user cluster preference features | Overall funniness or universal appeal |
| `humor-rank` | Pairwise relative ranking within the same topic | Absolute/universal funniness |
| `humor-eval` | Multi-axis scoring (Novelty/Clarity/Relevance/Intelligence/Empathy/Overall) | Ground-truth human final verdict |
