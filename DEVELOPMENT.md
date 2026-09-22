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

## Example Firewall: using human feedback without creating attractors

Human reactions (which answers got laughs, which fell flat) are the highest-quality
signal available, but pasting concrete examples into `SKILL.md` creates new
attractors (see SMC above). The resolution is a zone separation:

- **Evaluation zone** (this file, evaluation skills, iteration logs, commit
  messages): concrete examples are allowed and encouraged. Record the actual
  answer text, the topic, and the observed reaction.
- **Generation zone** (`.claude/skills/ogiri-ai/SKILL.md`): concrete examples,
  materials, scenarios, and punchlines are banned. Only *structural
  abstractions* may cross over from the evaluation zone.

**Abstraction procedure:**
1. Take the example and name the mechanism that made it work or fail
   (e.g., "the dog thought the entire quest was a walk" → the laugh comes from
   a *premise-level* misunderstanding, not a behavior-level one).
2. Strip every content word: no nouns, no settings, no specific punchline.
   State the rule purely as structure or form ("間違いは前提レベルが最も笑える").
3. **Reconstruction test**: could someone reading only the rule reconstruct the
   original example? If yes, the abstraction is too shallow and will become an
   attractor — abstract one level further. If no, it may cross into `SKILL.md`.
4. **Cross-topic regression**: the abstracted rule must improve answers on
   topics *different from* the one the example came from. A rule that only
   helps its source topic is a disguised example.

Worked precedent: 「散歩じゃなかったと今気づいた」(strong human-rated answer) →
rule 「バカの深さ: 前提の勘違いが最も笑える」. The rule contains no dog, no
Momotarō, no walk; reading it cannot reproduce the joke. It passed cross-topic
regression (improved 健診/お菓子 topics too).

The same firewall applies to *negative* examples: a joke that fell flat goes
into the iteration log and may justify a structural prohibition, but the joke
itself never appears in `SKILL.md` as a "don't write this" example — that too
is an attractor (the model anchors on it).

## Skill Development Process

Two tiers: a cheap **light loop** for everyday iteration, and a heavier
**gate check** run only when you want to claim an improvement is validated.

The previous process (5 evaluation skills × 2 runs × 2 topics on *every*
iteration, plus a 3-consecutive-pass streak) cost roughly 250k+ subagent
tokens per iteration and was never completed in practice. This version keeps
the signals that actually drove interventions in past sessions and drops the
rest; the removed requirements are recorded at the bottom so they don't creep
back without new evidence.

**Activation:** any request like "improve the prompt", "make the skill
better", "reduce convergence", or "run the feedback loop" activates this
process. Do not stop after editing text: a development turn includes
generation, evaluation, and a decision about the next intervention. If
tooling or budget prevents even the light loop, record the blocker and run
the largest subset possible.

### Setup: installing the evaluation skills

The evaluation skills no longer live in this repo. They moved to
[gyu-don/humor-skills](https://github.com/gyu-don/humor-skills), which keeps
each original prompt-based `SKILL.md` **and** adds a Jev port
(`scripts/evaluate.ts`) that returns numbers instead of an LLM's prose verdict.
Install them before running any loop:

```bash
npx skills add ../humor-skills -s '*' -y        # local checkout next to this repo
npx skills add gyu-don/humor-skills -s '*' -y   # or straight from GitHub
```

or, inside Claude Code:

```
/plugin marketplace add https://github.com/gyu-don/humor-skills
/plugin install humor-skills
```

The installed copies land in `.claude/skills/<name>/` (`.agents/skills/` is a
symlink to the same directory, so Codex sees them too) and are **git-ignored**.
Only `skills-lock.json` is committed, so `npx skills experimental_install`
restores the pinned set on a fresh checkout. Never edit an installed copy — fix
it in `humor-skills` and reinstall.

For the numeric (Jev) version, run `npm install` once at this repo's root
(Node.js >= 22.6). The root `package.json` exists only to provide
`@typesafe-ai/sdk`, the scripts' single dependency; Node finds it by walking up
from `.claude/skills/<name>/scripts/`, so reinstalling or updating the skills
does not require another install. Using the ogiri-ai skill itself needs no
Node at all.

```bash
npm install                                  # once per clone
doppler run -- node .claude/skills/<name>/scripts/evaluate.ts <input.json> [output.json]
```

Input is `{"topic": "...", "answers": ["...", ...]}` — see each skill's
`assets/samples.json` for the shape, including the multi-sample form used to
compare two candidate sets in one run. `TYPESAFE_API_KEY` is required; run under
`doppler run --` when it is not already in the environment (see `AGENTS.md`).
`diversity-check` is prompt-only: it ships no `evaluate.ts` and is always run by
subagent.

### Non-negotiables (both tiers)

- Read `SKILL.md`, this file, and the evaluation skills you will use
  (installed under `.claude/skills/`), before editing.
- Write one concrete failure hypothesis before editing, then make **one**
  targeted change (two only if the previous loop showed coupled failures).
  Do not reword large sections without naming the failure mode.
- Generate real candidates by skill invocation. Never evaluate from memory or
  from a cleaned-up subset; preserve the raw outputs.
- **One subagent, one skill.** Agents asked to run several evaluation skills
  in one prompt return partial reports.
- Funniness self-review is not evidence. Structural metrics and human
  reactions (fed back through the Example Firewall) are.
- Log every iteration (template below); put the hypothesis and metrics in the
  commit message.

### How to invoke

Prefer subagents with native skill invocation (Sonnet-class at moderate
effort is sufficient; see model defaults in `CLAUDE.md`):

```
# Claude-family subagent prompt
/ogiri-ai <お題>

# Codex-family subagent prompt
$ogiri-ai <お題>
```

CLI fallback when subagents are unavailable:

```
claude -p --model=<model> --effort=<effort> '/ogiri-ai <お題>'
codex exec -C . -m <model> -c 'model_reasoning_effort="<effort>"' '$ogiri-ai <お題>'
```
(Single-quote the Codex prompt so the shell does not expand `$ogiri-ai`.)

Evaluation skills have two invocation modes, and they answer different
questions:

- **Prompt mode** (subagent, `/humor-eval` etc.): returns the full report with
  per-answer reasoning and rewrite notes. Use it when you need to know *why* a
  set failed.
- **Jev mode** (`doppler run -- node .claude/skills/<name>/scripts/evaluate.ts`):
  returns the same axes as numbers, cheaply and reproducibly. Use it for the
  per-iteration metrics, for comparing two iterations, and wherever this file
  asks for a median or a share. It has no subagent budget cost, so prefer it
  when the question is "did the number move?".

Numbers from Jev mode and scores from prompt mode are on the same 0-4 axes but
are not interchangeable across a comparison — pick one mode per comparison and
stay in it.

Reproducible is not the same as valid. As of 2026-09-23, no funniness score
from either mode agrees with human judgment better than chance (see
"How far to trust the evaluators" below), so a number that moved is not
evidence that the answers got funnier.

### Light loop (default — ~5-6 subagent calls per iteration)

1. Hypothesis + one targeted edit to `SKILL.md`.
2. Generate: one `/ogiri-ai` run per fixed topic, 2 fixed topics from
   different categories (5 answers each).
3. Evaluate per topic: `diversity-check` and `fun-check`, one subagent each.
   Also count by hand (no subagent needed): 「」 per run, answers that break
   the form the お題 asks for (e.g. a 「一言」 お題 answered with a situation
   description instead of an utterance), same-mechanism repeats, same
   sentence-template repeats, same borrowed metaphor system repeats, material
   reappearing from the previous iteration's outputs.
4. Log, decide the next intervention.

Light-loop reference values — these are *trend signals*, not pass/fail gates;
read them against the previous iteration, not as absolute bars:
- ≥4 distinct decomposition axes per 5 answers
- no single risk type dominating the fun-check flags (the raw flag rate runs
  40-60% even on good sets — fun-check flags generously by design)
- 「」 count within `SKILL.md`'s own limit; no repeated material across iterations

### Gate check (only when claiming a validated improvement — ~15-18 calls)

Run once when light-loop trends look good, not on every iteration:

The gate never waits for a human. Mechanical checks decide pass/fail; the
funniness signal and the optional blind human comparison decide how strongly
the result can be claimed.

1. Generate: 2 fixed topics × 2 independent runs each, plus **1 unseen-category
   topic** × 2 runs (pool each topic to 10 answers). Also generate the same
   topics with the pre-change `SKILL.md` (the baseline) — the funniness
   signal and the human comparison compare the two.
2. **Checks on each pooled 10.** Only unambiguous checks are pass/fail.
   Fuzzy similarity is judged *relative to the baseline*, because a strict
   absolute similarity bar gets optimized against: it rejects answers that
   merely share the お題's own premise, and the judge invents similarity when
   there is none (see "How far to trust the evaluators"). The human's
   favorite set on record (2026-07-11 FIRST TAKE, skill off) would have failed
   an absolute version of these checks.
   - **Pass/fail (hard):**
     - every answer takes the form the お題 asks for (utterance for 「一言」,
       a description of the thing for 「どんな〇〇？」, a title for 「タイトル」…)
     - 「」 count and length within `SKILL.md`'s own limits
     - no near-duplicate pair: Jev `fun-check` `nearDuplicates` (exact match,
       or same core material ≥0.7) is empty — unless the baseline pooled on
       the same topic has as many, which means the お題 forces a shared form
   - **Relative to the baseline (warning, not a failure by itself):**
     - `fun-check` Jev `sameMaterial` distribution and prompt-mode 被りチェック
       flag count: warn if clearly higher than the baseline's
     - `diversity-check` axis count and largest-axis share: warn if clearly
       worse than the baseline's
     - material or mechanism reappearing across the two runs (cross-run
       attractor) or repeated from the previous gate
     Two or more warnings on the same topic count as a failure for that topic.
   - **Diagnostic only (log, never gate):** set-wide convergence in one
     direction (every answer reinterpreting the お題 the same way, the same
     シュール手癖, the same sentence template). No judge detects this
     reliably yet; read the prompt-mode reports and count by hand, and
     discount any "shared structure" that is just a restatement of the お題.
3. **Funniness signal (always run, never blocking)**: check the latest
   `reports/validation/<date>/summary.md` in humor-skills.
   - If a metric is marked `gate: yes`, it is trusted: the candidate must not
     lose to the baseline on it.
   - Otherwise (the state as of 2026-09-23), run `humor-eval` × 2 passes on
     candidate and baseline anyway and log the medians and the Overall-4
     count, labeled **provisional**. They can neither validate nor veto the
     change. Watch for the known failure: it rates safe, explanatory sets
     above bold ones.
4. **Blind human comparison (optional, asynchronous)**: if a human is
   present in the session and willing, show candidate and baseline side by
   side per topic with sources hidden and order randomized (AskUserQuestion
   works; ask "which set is funnier", allow a tie, and let them mark
   standout answers). Record the result as a new session in humor-skills
   `data/human-evals/ogiri-ai/` (`.md` + `.json`, schema in its README)
   — this is what grows the ground truth used to improve the evaluators. If
   no human is available, skip it; do not block, poll, or ask repeatedly.
5. Outcome, stated exactly in the final report and commit message:
   - **mechanically passed** — step 2 has no hard failure and no topic with
     two or more warnings, on all three topics. The change
     may be committed. Then **stop looping**: further prompt tuning cannot
     be validated by LLM evaluation alone.
   - **validated** — mechanically passed, *and* either the blind human
     comparison preferred the candidate (or tied) on the topics shown, or a
     `gate: yes` evaluator did.
   - **not passed** — report the exact loop depth, the failing criteria, and
     the next concrete intervention. The honest final state is "improved but
     not fully validated", not "done".
6. Commit with hypothesis, loop count, per-iteration metrics, and what
   changed between iterations.

### Optional tools (run only when they answer a specific question)

- `humor-rank`: breaking ties between finalists, or when other metrics
  disagree about a pair. Re-run close pairs with A/B order swapped; a flipped
  winner or confidence ≤0.55 is a draw. Pairwise wins concentrating on one
  brittle pattern (e.g., novelty-only) is a warning sign.
- `cluster-fit-check`: only when deliberately tuning style or audience
  breadth. Treat scores as preference-fit signals, not funniness. Never
  optimize by mechanically adding parentheses, ellipses, or slang.

### Iteration log template (both tiers; leave blank what wasn't run)

```
iteration N (light|gate)
hypothesis:
edit:
topics:
diversity: axes / largest-axis share
fun-check: dominant risk type / overlap warnings / flag-rate trend
hand counts: 「」 / form violations / repeated mechanisms / repeated templates / repeated metaphor systems
funniness (gate only, provisional unless gate-eligible): humor-eval median Relevance / Empathy / Overall-4, candidate vs baseline
human blind comparison (gate only, optional): not run | candidate / baseline / tie per topic
decision: next intervention, or gate outcome (mechanically passed / validated / not passed)
```

### Evaluation skills at a glance

| Skill | What it measures | What it does NOT measure | When |
|---|---|---|---|
| `diversity-check` | Structural variety of decomposition axes | Funniness; style/template convergence (count those by hand) | Every iteration, read against the baseline |
| `fun-check` | Per-answer risks (ベタ・絵・ひねり・共感・認知度・長さ・滑り・被り・相対典型性) | Overall funniness | Every iteration; Jev `nearDuplicates` is a hard gate check, the rest is read against the baseline |
| `humor-eval` | Multi-axis scoring (Novelty/Clarity/Relevance/Intelligence/Empathy/Overall) | Ground-truth human verdict | Gate only, 2-pass, provisional |
| `humor-rank` | Pairwise relative ranking within a topic | Absolute funniness | Finalist ties only |
| `cluster-fit-check` | Alignment with literature-derived user cluster preferences | Funniness or universal appeal | Style/audience tuning only |

All five come from [gyu-don/humor-skills](https://github.com/gyu-don/humor-skills).
Every row except `diversity-check` also has a Jev port (`scripts/evaluate.ts`).

### How far to trust the evaluators

humor-skills validates every judge against recorded human judgments
(`data/human-evals/`) and writes the result to
`reports/validation/<date>/summary.md` (procedure: humor-skills `AGENTS.md`,
"Validation"). Check the latest one before relying on a score.

As of the 2026-09-23 run (75 labeled answers, 7 human set preferences, 13
answer pairs, 11 of them blind):

- Funniness judgments from `humor-eval`, `fun-check`, and a no-rubric
  baseline are all at chance (AUC 0.37-0.61, every 95% interval spans 0.5),
  and none beats "shorter is better".
- Prompt-mode `humor-eval` agreed with the human on 2 of 7 set preferences
  and rated both recorded regressions (07-11 attractor set, 09-15 節分)
  above the sets the human preferred. The old gate would have validated them.
- `fun-check`'s ベタ/相対ベタ flags land more often on the answers humans
  liked; `diversity-check` did not detect the convergences humans pointed out.
- What did work: prose reports spotting near-duplicate answers within a set.

Overlap (被り) detection, checked against 16 blind human similarity
judgments (`reports/validation/2026-09-23-overlap/`):

- The old prompt-mode 被りチェック flagged 4 of 10 pairs the human called
  different — pairs that merely shared the お題's premise or an opening
  phrase. After adding explicit "not 被り" criteria: 0 of 10, same recall
  (4 of 5). Jev `sameMaterial` at 0.7 (the `nearDuplicates` threshold): 3 of 5
  caught, 0 of 10 false, r=0.99 between runs. Both were tuned on these same
  16 pairs — confirm on new topics before tightening anything.
- Neither detects same-direction reinterpretation with different material,
  nor set-wide convergence. That stays a diagnostic.

Improving the funniness judges continues in humor-skills; a judge graduates
to gating use only when its validation row is marked `gate: yes`.

### Dropped requirements, and why (do not reinstate without new evidence)

Measured in the 2026-06 sessions:

- **3-consecutive-pass streak**: humor-eval swings ±0.4 between identical
  back-to-back runs, so a streak across full loops measures evaluator luck,
  not prompt quality. One gate pass including an unseen topic gives the same
  confidence at a third of the cost.
- **Mandatory `cluster-fit-check` + `humor-rank` every iteration**: their
  conclusions duplicated what `diversity-check`/`fun-check` plus simple hand
  counting already showed (e.g., quote-form lock-in is visible by counting
  「」). They earn their cost only on the specific questions listed above.
- **≤30% fun-check risk ceiling**: never met in any session, including by the
  sets that scored best on humor-eval — the flag rate did not correlate with
  quality. Risk-type concentration and repeated cross-run overlap are the
  real failure signals and are kept as gates.
- **`humor-eval` on every iteration**: the noisiest and most expensive
  signal; single-pass averages cannot support claims about edits with effect
  size <0.4. Reserved for gates, as 2-pass medians and peak counts.

Measured on 2026-09-23 (humor-skills `reports/validation/2026-09-23/`):

- **`humor-eval` median floors (Relevance/Empathy ≥2.5) and the Overall-4
  peak as validating gate criteria**: checked blind against human labels,
  they were at chance and preferred the human-rejected set in both recorded
  regressions. Kept only as a provisional signal (gate step 3) until a
  humor-skills validation run marks a judge `gate: yes`.
- **A human in every loop**: the blind human comparison is optional and
  asynchronous; mechanical checks alone decide "mechanically passed".
- **Absolute similarity/diversity bars as hard gates** (a sentence template
  shared by >40%, "no overlap" by prompt-mode judgment, `diversity-check`
  ≥6 axes): the human's favorite recorded set would have failed them, and
  prompt-mode overlap judgments invented similarity. Only near-duplicates
  are a hard check; the rest is compared against the baseline.

## Secrets and environment variables

The evaluation skills installed from
[humor-skills](https://github.com/gyu-don/humor-skills) call the TypeSafe AI
(Jev) API and need `TYPESAFE_API_KEY`. This repo's Doppler scope is already
configured, so:

- If the variable is **already in the environment**, run the command directly:
  `node .claude/skills/<name>/scripts/evaluate.ts <input.json>`
- If it is **not set**, prefix the command with `doppler run --`:
  `doppler run -- node .claude/skills/<name>/scripts/evaluate.ts <input.json>`

Check with `[ -n "$TYPESAFE_API_KEY" ]` rather than guessing; the scripts also
fail loudly with the fix (`TYPESAFE_API_KEY is missing. Run through Doppler: ...`).
When in doubt, `doppler run --` is safe — it is a no-op for commands that do not
read the variable.

Never print, log, or commit the key, and do not write it into a `.env` file.
