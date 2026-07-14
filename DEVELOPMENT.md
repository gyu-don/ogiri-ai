# Development Guide

## Tuning Targets

The skill is tuned to be maximally funny on **each vendor's latest frontier model** (as of 2026-07: Claude Fable 5, GPT-5.6-sol). Improvements made at the frontier are expected to transfer reasonably well to other models; the reverse is not assumed.

Implications:
- Keep `SKILL.md` model-agnostic. No model-specific tricks, vocabulary, or workarounds.
- A failure mode observed on one frontier model but not another (e.g., GPT-5.6-sol collapsing into pure exaggeration while Fable 5 doesn't) is still a skill bug. Fix it with stronger form-level constraints; don't dismiss it as "that model's problem."
- Generation quality only counts when measured on a tuning target. Cheaper models are for mechanical checks (see division of labor below).

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

SMC also occurs *within a single answer set*: five individually fine answers that all use the same decomposition axis get flagged by human evaluators (see 2026-07-10 findings). Diversity must be checked per-set, not just across runs.

## Model Tiers

Roles are tier-based, not model-based — the concrete names WILL change; update the "as of" line when they do.

- **Lightweight tier** (as of 2026-07: Claude Sonnet 5, GPT-5.6-luna) — runs the workflow: candidate generation during fast iteration, format smoke tests, output collection, `/diversity-check`, `/funniness-check` screening, statistics.
- **Heavyweight tier** (as of 2026-07: Claude Fable 5, GPT-5.6-sol) — the tuning targets AND the skill engineers. Reserve heavyweight runs for: diagnosing failure modes, editing `SKILL.md`, and pre-commit verification generation. Never spend a heavyweight run on workflow mechanics the lightweight tier could do.
- **Human** — ground truth for funniness. Every AI funniness judgment is a screening proxy, nothing more.

Caveat: lightweight-tier generation is *directional only* — it tells you whether an edit changed the output shape, not whether the tuning target got funnier. Any `SKILL.md` change must pass heavyweight verification before commit.

## Skill Development Process

**Cost note:** one skill run on a heavyweight model takes minutes. Run heavyweight jobs in parallel, and never spend one on something the lightweight tier could have caught first.

The cycle:

1. **Hypothesize** — identify the specific failure mode (SMC? pure exaggeration? not funny? verbose?)
2. **Edit** `SKILL.md` with a targeted change
3. **Lightweight checks first** — a lightweight-tier subagent runs the skill on any topic to verify format compliance (output starts with 【, exact format, no preamble) and catches gross regressions. Don't proceed to heavyweight runs until this passes.
4. **Heavyweight verification** — run the skill on a tuning-target model, 2+ topics, launched **in parallel**:
   ```
   claude -p --model=<heavyweight> "/ogiri-ai <お題>"
   ```
   Or launch subagents that read the skill file and execute it (generator invocations must follow the contamination rules in `CLAUDE.md`: they read only the ogiri-ai `SKILL.md`, never `evaluations/` or `DEVELOPMENT.md`).
   **Include a skill-off baseline** for at least one topic: run the same topic on the bare tuning-target model with no skill. If skill-off wins in human evaluation, a recently added instruction is acting as an attractor — diff recent `SKILL.md` changes against the style of the skill-on failures to find it.
5. **Screen on the lightweight tier** — feed collected outputs (topic + answers only, no generation context) to:
   - `/diversity-check` — across runs: **5+ distinct decomposition axes per 10 answers** (2 runs). 3-4 axes = improvement needed, 1-2 = still converging. Within one set of 5: no axis should appear more than twice.
   - `/funniness-check` — pairwise ranking + loss-pattern flags. This is a screening proxy, not a verdict; see "Funniness Evaluation" below.
6. **Evaluate quality with a human** — log the feedback in `evaluations/` (one dated file per session, in Japanese) so learnings accumulate. Distill recurring patterns into the findings section below.
7. **Test with novel topics** — if a topic has been used repeatedly in testing, the model may overfit to it. Always end a development session by testing with an entirely different topic category.
8. **Commit** with a message explaining the hypothesis and result

**Warning:** Evaluation of "funniness" by the LLM itself is unreliable. The model rates its own outputs as funny because it completed the prescribed process. Use structural checks (diversity, specificity, visual quality) as proxies, and rely on human judgment for final quality assessment.

## Funniness Evaluation (`/funniness-check`)

The `/funniness-check` skill makes AI funniness judgment *usable as a screening proxy* by restricting it to what LLM judges are least bad at:

- **No absolute scores.** Pairwise ranking only ("which one gets a laugh out loud, not a smirk").
- **Deduction filters, not taste.** The flags are the loss patterns repeatedly confirmed by human evaluation (exaggeration-only, concept-only, word-swap parody, needs-explanation, verbose).
- **Judge ≠ generator.** Generation and judging are always separate invocations; a judge never evaluates answers it produced.
- **Blind judging.** The judge sees only topic + answers — never `evaluations/`, the generator's reasoning, or which condition (skill on/off, which model) produced which set.

**Calibration:** before trusting a judge model (or after editing the funniness-check skill), run it blind on 2–3 logged answer sets from `evaluations/` and compare its ranking against the recorded human ranking. If it misses the human top pick on most sets, fix the funniness-check criteria — never conclude the human was wrong. Re-distill new loss patterns from `evaluations/` into the filter list as feedback accumulates.

## AI-Assisted Improvement Loop

Human feedback stays the ground truth, but it's scarce. Between human rounds, run this loop to pre-filter candidate skill changes so human attention is spent only on edits that survived screening:

1. **Generate** (lightweight tier): current skill vs. baseline (skill-off), 2+ topics, fresh generator invocations under the contamination rules.
2. **Screen** (lightweight tier): `/diversity-check` + `/funniness-check` on topic+answers only.
3. **Diagnose & edit** (heavyweight tier): read the screening reports *and* the `evaluations/` history, identify the failure mode, and make one targeted `SKILL.md` edit obeying the SMC rules — negative or conditional form, form-level, never an unconditional positive style target.
4. **Re-screen** (lightweight tier): repeat 1–2 with the edited skill. Keep the edit only if screening improves or holds while the targeted failure disappears.
5. **Verify** (heavyweight tier): tuning-target generation on a novel topic + skill-off baseline, per the main process.
6. **Human round**: present the surviving before/after sets for judgment; log to `evaluations/`; recalibrate `/funniness-check` against the new data if its ranking disagreed.

Never let the loop self-approve: an edit that only ever passed AI screening is a hypothesis, not an improvement. One human round can reject what ten screening rounds approved.

## Findings from Human Evaluation

Distilled from `evaluations/`. When a finding is safely encodable as a form-level rule, move it into `SKILL.md`; findings that would act as positive attractors stay here as hypotheses.

### 2026-07-10 — 4 topics, Fable 5 high vs GPT-5.6-sol high

- **Pure exaggeration fails.** Answers that only escalate degree (「余命より長いイントロ」「全ファンの実家へ挨拶済み」) were uniformly rated not funny. The winners convert greatness into concrete *evidence left in the world*, anchored by one specific number/duration/place (「文春の張り込み三日目で記者が沼落ち」「デビューから12年トイレの目撃情報なし」「震度5の中ひとりだけ振付を続行」). → Encoded in SKILL.md (痕跡を見せろ / 数字を刺せ / 誇張を捨てろ).
- **Single-word-swap parody fails unless the swapped word imports a second coherent context.** 「丸ノ内ぎっくり腰」 works because the word carries an aging/physical theme that meshes with the artist-parody frame; 「丸ノ内サイゼリヤ」 is just a cheap-brand substitution and fails. → Encoded (入れ替えた語が別の文脈を丸ごと連れてくること).
- **Set-level axis collapse gets flagged even when individual answers pass.** GPT-5.6-sol's 前前前世 set was rated a hit overall, yet the evaluator still noted all five shared one direction (modern-bureaucracy-in-prehistory). → Encoded as a set-level check (5つ揃えてから読み返す).
- **Hypothesis (NOT encoded — attractor risk):** the highest-rated answers tend to show *the world reacting* to the subject (記者が沼落ち, 目撃情報なし) rather than the subject asserting its own quality. Encoding this as a positive instruction would likely collapse all five answers into evidence-format. Revisit only if exaggeration-collapse persists after the current negative rules.
- **Referential answers need a one-glance trigger.** 「君を探し始めた初日、雨で中止」 (君の名は×天気の子) was liked but flagged as hard to parse. If an answer leans on an external work, the reference must land in one read.

### 2026-07-11 — 3 topics, Fable 5 skill-on vs skill-off (bare model)

- **Skill-on lost on 2 of 3 topics** (THE FIRST TAKE, ヤバい新入社員), tied on 1 (ASKUL対義語). The evaluator still believes skill-on is better on average, but suspected "unnecessary instructions" hurting.
- **The 2026-07-10 attractor hypothesis is confirmed — by our own edit.** The rules added on 07-10 (「痕跡を見せろ」「数字・日数・場所をひとつ刺せ」), though derived from winning answers and phrased as advice, acted as positive attractors: skill-on sets collapsed into subtle-detail evidence humor (「概要欄の端に小さくテイク38」「コメント欄が全員同じ苗字」 — trace + small number + place, exactly the encoded shape). Every answer landed in smirk register; no bold laugh. Skill-off winners were often only 1-step but bold and instantly visible (「入社代行の業者が来た」「ラジオ体操第一」).
- **Lesson: even "show, don't tell" style advice becomes the house style.** Any unconditional positive rule — including ones extracted from human-validated winners — gets applied to all five answers. Positive rules must be scoped as *conditional repair tools* ("when you're about to exaggerate, do Y"; "when the picture is vague, add a number"), never as unconditional targets.
- **Changes made:** demoted the 数字/痕跡 rules to conditional repair tools; qualified 「2段階飛べ」 (association distance, not reader decoding effort); added negative self-check 「うまいこと言ってるだけで笑えない」→捨てろ; added set-level register check (all-smirk sets must be redone); added the skill-off baseline comparison to the process (step 4).

### 2026-07-11 (round 2) — 1 topic, after the attractor demotion; Fable 5 on/off + GPT-5.6-sol

- **The demotion worked on Fable.** Skill-on became competitive again (2 answers rated funny vs 1 for the bare-model baseline), and the "subtle-trace + small-number" shape disappeared from the set.
- **GPT-5.6-sol failed with a consistent shape: concept-only jokes.** All five answers were absurd rules/demands stated in the abstract — logic inversion (米の持ち込みはご遠慮ください), meme-template insertion (「炊けた」は本人の感想です), a pun — with no object and no event. Across both models, answers that got picked always contain a *happening phenomenon* (まれに米粒の数が増えます) or a *tactile object*; pure logic inversions were never picked, including Fable's own (本製品は炊飯にも使えます). → Encoded as negatives: 概念は絵じゃない (質感のある物か起きてる現象を連れてこい) and self-check 「理屈は通ってるが、物も現象も出てこない」→捨てろ.
- **Caveat:** negative instructions rely on self-policing, which looks weaker on GPT-5.6-sol (its sets also keep collapsing to one register despite the set-check). If concept-collapse persists there, the next lever is process-level (e.g., forcing the 絵 test as an explicit step), not more adjectives.
- **Ablation candidate:** the BTL cluster table in SKILL.md is long, generic, and has no observed effect in any evaluation so far. Worth a with/without comparison in a future session before deciding to keep it.
