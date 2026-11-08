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

### Setup: the evaluation tools

The evaluation tools live in
[gyu-don/humor-skills](https://github.com/gyu-don/humor-skills), split in two
by whether they agree with recorded human judgments:

- **Installable checks** (`skills/` there): `overlap-check` and `trait-check`.
  Jev-only, validated against human labels, usable as automated checks. These
  are the only ones installed into this repo.
- **Research judges** (`research/` there): `funniness-score` (was
  `humor-eval`), `risk-flags` (the rest of `fun-check`), `diversity-check`,
  `cluster-fit-check`. None beats a no-rubric or length baseline yet. They are
  **not installable**; run them from a humor-skills checkout, and never let
  them pass or fail a change.

Old names map as follows (reports before 2026-09-25 use them):

| Old | Now |
|---|---|
| `fun-check` Step 3 (被り) | `skills/overlap-check` |
| `fun-check` 絵なし・長さ | `skills/trait-check` (`concrete`, `indirect`) |
| `humor-rank` | `skills/trait-check` `scripts/compare.ts` |
| other `fun-check` flags | `research/risk-flags` |
| `humor-eval` | `research/funniness-score` |
| `diversity-check`, `cluster-fit-check` | `research/` (same names) |

Install the checks before running any loop:

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
it in `humor-skills` and reinstall. Copies of the old skills (`fun-check`,
`humor-eval`, `humor-rank`, `diversity-check`, `cluster-fit-check`) left in
`.claude/skills/` from an earlier install are stale: delete them and drop them
from `skills-lock.json`.

Run `npm install` once at this repo's root (Node.js >= 22.6). The root
`package.json` exists only to provide `@typesafe-ai/sdk`, the scripts' single
dependency; Node finds it by walking up from `.claude/skills/<name>/scripts/`,
so a per-skill `npm install` (which each `SKILL.md` suggests) is unnecessary
here, and reinstalling the skills does not require another install. Using the
ogiri-ai skill itself needs no Node at all.

```bash
npm install                                  # once per clone
doppler run -- node .claude/skills/overlap-check/scripts/evaluate.ts <input.json> [output.json]
doppler run -- node .claude/skills/trait-check/scripts/evaluate.ts <input.json> [output.json]
doppler run -- node .claude/skills/trait-check/scripts/compare.ts <pairs.json> [output.json]
```

`evaluate.ts` takes `{"topic": "...", "answers": ["...", ...]}` or an array of
such sets (compare candidate and baseline in one run); `compare.ts` takes
`{"topic", "answerA", "answerB"}` or an array of them. See each skill's
`assets/` for samples. `TYPESAFE_API_KEY` is required; run under
`doppler run --` when it is not already in the environment (see `AGENTS.md`).

Research judges need `npm install` in the humor-skills checkout, then:

```bash
doppler run -- node ../humor-skills/research/<name>/scripts/evaluate.ts <input.json> [output.json]
```

`diversity-check` has no script: give a subagent
`../humor-skills/research/diversity-check/SKILL.md` and the answers.

### Non-negotiables (both tiers)

- Read `SKILL.md`, this file, and the `SKILL.md` of every check you will use
  (installed under `.claude/skills/`) before editing.
- Write one concrete failure hypothesis before editing, then make **one**
  targeted change (two only if the previous loop showed coupled failures).
  Do not reword large sections without naming the failure mode.
- Generate real candidates by skill invocation. Never evaluate from memory or
  from a cleaned-up subset; preserve the raw outputs.
- **One subagent, one skill.** Agents asked to run several skills in one
  prompt return partial reports.
- Funniness self-review is not evidence. The installed checks, hand counts,
  and human reactions (fed back through the Example Firewall) are.
- Never optimize for a check's number. `trait-check` values are extracted from
  past winning answers; maximizing them reproduces the 07-11 attractor
  collapse. Use them only to catch regressions against the baseline.
- Log every iteration (template below); put the hypothesis and metrics in the
  commit message.

### How to invoke

Prefer subagents with native skill invocation for generation (model defaults
in `AGENTS.md`). Use the same model and effort for baseline and candidate.

**Generator capability check.** Before tuning the skill for a new kind of
answer, run a small, predefined no-skill diagnostic on the intended generator:
ask for that kind of answer directly. Record the exact model/version, effort,
prompt, run count, raw outputs, and audit. A failure means the capability was
not demonstrated under those conditions, not that no prompt could elicit it;
use it to pick a generator before spending iterations. A success does not
guarantee the answer will appear spontaneously through the skill. Keep
diagnostics and confirmation runs in separate fresh contexts.

Exploratory record, 2026-11-08: asked directly for answers that play with a
7-character condition, Sonnet only mentioned or refused the condition and
miscounted once; the latest Opus at high effort used the condition in 10/10
answers with correct counts. Three `SKILL.md` interventions tested on Sonnet
showed no target answers; the same text on Opus showed one in two runs. This
supports testing such changes on Opus; it does not by itself explain every
Sonnet failure.

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

The installed checks are plain scripts: run them directly, no subagent and no
subagent budget. They are reproducible (retest r ≥ 0.97), so a moved number is
a real change in the answers — but only `overlap-check` and `trait-check` have
shown that a moved number means anything to a human (see "How far to trust
the evaluators").

Subagents are still used for generation and for the prompt-mode
`diversity-check` report, which is read as a diagnostic, never counted.

`evaluate.ts` in both checks groups array input by `sample.id`; an array of
sets without distinct ids is merged, and every set then reports the same pooled
`summaries` (seen 2026-11-08). Invoke it once per set with a single object
until distinct-id arrays are verified in humor-skills.

### Change-specific criteria (both tiers)

The fixed topics catch regressions; they cannot show that a change does what
it was made for. When a change targets a specific kind of answer, register the
criteria before generating any confirmatory outputs. Disclose earlier
exploration and diagnostics, and never reuse outputs you have already
inspected as confirmatory evidence.

For each topic, record:
- its exact text and roles: required target, leakage control, regression
  (fixed), unseen-category, and/or stretch;
- its content requirement (what the answer must show or convey), its explicit
  form conditions, and the single condition, if any, eligible for the form
  exception below;
- the run count, success and leakage thresholds, and counting conventions
  (characters, morae with recorded readings, …).

Require at least one required target. Freeze candidate, baseline, generator
settings, evaluation policy, and topic roles before confirmation. After seeing
confirmatory outputs, do not reclassify a failed target as stretch, replace
topics, or pick favourable runs. Never hand a criterion, a diagnostic example,
or a previous answer to the generator.

A **stretch** topic is one where the move was registered in advance as very
hard (e.g. bending a 五七五 count while still evoking the season). Stretch
waives only the minimum number of target answers; every other check applies.
Zero successes there are recorded as "not demonstrated". Stretch-only results
do not discharge the Example Firewall's cross-topic requirement: if no benefit
outside the source topic is shown, report transfer as unconfirmed.

Leakage — the move, or a form violation it causes, appearing where it does
not belong — counts on every topic, whether or not the change caused it.

### Light loop (default — ~2-3 subagent calls per iteration)

1. Hypothesis + one targeted edit to `SKILL.md`.
2. Generate: one `/ogiri-ai` run per fixed topic, 2 fixed topics from
   different categories (5 answers each).
3. Check per topic (scripts, no subagent):
   - `overlap-check`: `nearDuplicates` and the `sameMaterial` distribution
   - `trait-check` `evaluate.ts`: set means of `concrete` and `indirect`,
     against the previous iteration
   Also count by hand: 「」 per run, answers that break the form the お題
   asks for (e.g. a 「一言」 お題 answered with a situation description
   instead of an utterance), same-mechanism repeats, same sentence-template
   repeats, same borrowed metaphor system repeats, material reappearing from
   the previous iteration's outputs.
   Optional: a `diversity-check` subagent report when you suspect set-wide
   convergence and want it put into words. Read the prose; do not log the
   axis count as a metric.
4. Log, decide the next intervention.

Light-loop reference values — *trend signals*, not pass/fail gates; read them
against the previous iteration, not as absolute bars:
- `nearDuplicates` empty
- `concrete` not falling and `indirect` not rising across iterations
- 「」 count within `SKILL.md`'s own limit; no repeated material across iterations

### Gate check (only when claiming a validated improvement)

Run once when light-loop trends look good, not on every iteration.

The gate never waits for a human. Mechanical checks decide pass/fail; the
optional blind human comparison decides how strongly the result can be
claimed.

1. Generate: 2 fixed topics × 2 independent runs each, plus **1 unseen-category
   topic** × 2 runs (pool each topic to 10 answers). Also generate the same
   topics with the pre-change `SKILL.md` (the baseline), also 2 runs each.
2. **Checks on each pooled 10.** Only unambiguous checks are pass/fail.
   Everything else is judged *relative to the baseline*, because absolute
   bars get optimized against, and the human's favorite set on record
   (2026-07-11 FIRST TAKE, skill off) would have failed absolute similarity
   bars.
   - **Pass/fail (hard):**
     - every answer takes the form the お題 asks for (utterance for 「一言」,
       a description of the thing for 「どんな〇〇？」, a title for 「タイトル」…),
       except an answer accepted under the preregistered **form
       exception**. This is an external experimental acceptance policy;
       it does not imply that the current `SKILL.md` permits such answers.
       Record the tested revision's actual generation rules. Only the
       condition registered as eligible for the topic may be broken.
       Accept only when all hold; ambiguous cases are rejected:
       - exactly one eligible condition is broken; the content requirement,
         every other condition, the length and 「」 limits, the output
         format, and a requested utterance form are kept
       - the departure itself shows what the お題 asks for, and any claim the
         answer makes about itself matches the actual answer (count it)
       - repairing the departure removes the mechanism (record the repair)
       - the answer would not work unchanged for an unrelated content
         requirement under the same form (record the control お題 used)
       - the connection is apparent without explanation
       At most one accepted exception per original five-answer run. Audit
       separately from generation, with sources hidden where possible, and
       apply the same audit to baseline and candidate. Count strict
       violations, accepted exceptions, unaccepted violations, and
       within-form condition play (an answer that keeps the condition but
       plays with it) separately. This is a manual semantic judgment, not
       evidence of funniness. Report any remaining tension with the skill's
       own generation or self-check rules; this audit does not establish the
       skill's internal consistency.
     - 「」 count and length within `SKILL.md`'s own limits
     - `overlap-check` `nearDuplicates` is empty — unless the baseline pooled
       on the same topic has as many, which means the お題 forces a shared
       form. When `sameMaterial` bunches just under 0.7 on such a topic,
       compare its distribution with the baseline's instead.
   - **Regression against the baseline (fail the topic)**, per
     `trait-check`'s `SKILL.md`:
     - `concrete` mean of ordinary answers lower than the baseline's
     - `indirect` set mean higher than the baseline's
     - `compare.ts` over all candidate × baseline pairs (10 × 10, candidate
       as A) gives mean `probA` below 0.5 by more than the noise band below
     A difference no larger than the gap between the baseline's own two runs
     is noise, not a regression. For `compare.ts`, that gap is measured by
     comparing the baseline's run 1 against its run 2 (5 × 5 pairs): the noise
     band is |mean `probA` − 0.5| of that comparison, and the candidate
     regresses only if 0.5 − its mean `probA` exceeds the band. Use mean
     `probA`, not the draw-excluded win rate, which swings far more (on
     2026-11-08 one baseline's run 1 beat its own run 2 at 0.80). This is a
     preregistered operational tolerance from one run pair, not a confidence
     interval or an estimate of all sampling and position bias. Keep baseline
     run 1 as A, record both the mean and the band, and do not enlarge the band
     after inspecting candidate results. Record the draw-excluded win rate
     separately as a diagnostic. A rise is never a reason to accept a change.

     **Accepted performance answers (user decision, 2026-11-09).** Keep every
     raw answer and every original score. Before reading evaluator scores,
     freeze the form-exception audit labels for both versions. For accepted
     performance answers only, physical-scene `concrete` is N/A: compare
     ordinary-answer means and the baseline's corresponding run gap instead.
     Keep `indirect`, form, relevance, overlap and the other checks on all
     answers. For pairwise comparisons involving an accepted performance
     answer, use `straight` alone; otherwise keep both criteria. Aggregate all
     pairs, including baseline run-to-run pairs, under the same rule and also
     report the original results. This applies only to future preregistered
     gates, never retroactively to a failed gate.
   - **Relative to the baseline (warning, not a failure by itself):**
     - `overlap-check` `sameMaterial` distribution clearly higher than the
       baseline's
     - material or mechanism reappearing across the two runs (cross-run
       attractor) or repeated from the previous gate
     Two warnings on the same topic count as a failure for that topic.
   - **Diagnostic only (log, never gate):** set-wide convergence in one
     direction (every answer reinterpreting the お題 the same way, the same
     シュール手癖, the same sentence template). No judge detects this — not
     `overlap-check`, not `diversity-check` (AUC 0.49). Count by hand, read a
     `diversity-check` report if useful, and discount any "shared structure"
     that is just a restatement of the お題.
3. **Funniness signal**: check the latest
   `reports/validation/<date>/summary.md` in humor-skills.
   - If a metric is marked `gate: yes`, it is trusted: the candidate must not
     lose to the baseline on it.
   - Otherwise (the state as of 2026-09-25), there is no funniness signal.
     Running `research/funniness-score` is optional and its numbers are
     logged as **provisional** at most: the Jev version is inverted against
     the human (AUC 0.38-0.45) and the prompt version is at chance. They can
     neither validate nor veto the change.
4. **Blind human comparison (optional, asynchronous)**: if a human is
   present in the session and willing, show candidate and baseline side by
   side per topic with sources hidden and order randomized (AskUserQuestion
   works; ask "which set is funnier", allow a tie, and let them mark
   standout answers). Record the result as a new session in humor-skills
   `data/human-evals/ogiri-ai/` (`.md` + `.json`, schema in its README; keep
   all answers of every set, not just the liked ones, and record `blind`).
   Answer-level A/B pairs between candidate and baseline are the most useful
   shape for validating the judges later. If no human is available, skip it;
   do not block, poll, or ask repeatedly.
5. Outcome, stated exactly in the final report and commit message. Step 2
   is assessed on the union of all registered gate topics: fixed,
   unseen-category, and any target, leakage-control, and stretch topics from
   change-specific criteria (each 2 runs, with baseline; a topic with several
   roles is generated and checked once).
   - **mechanically passed** — no hard failure, no regression, and no topic
     with two warnings, across that whole union.
   - **validated** — mechanically passed, *and* either the blind human
     comparison preferred the candidate (or tied) on the topics shown, or a
     `gate: yes` evaluator did.
   - **not passed** — report the exact loop depth, the failing criteria, and
     the next concrete intervention. The honest final state is "improved but
     not fully validated", not "done".
   Report change-specific criteria separately as met / not met, transfer as
   demonstrated / unconfirmed, and the number of accepted form exceptions.
   **Adoption** requires a passing gate, met change-specific criteria, and
   the Example Firewall's cross-topic requirement where it applies; a
   record-only commit is not adoption. Stop tuning once adoption
   requirements are met — further prompt tuning cannot be validated by LLM
   evaluation alone. If the gate passes but another requirement is unmet,
   report the limitation and either preregister a new experiment or do not
   adopt; never relax the completed experiment's criteria.
6. Commit with hypothesis, loop count, per-iteration metrics, and what
   changed between iterations.

### Iteration log template (both tiers; leave blank what wasn't run)

```
iteration N (light|gate)
phase: exploratory | confirmatory
registration: path / timestamp / outputs already inspected before registering
revisions: candidate / baseline / evaluation-policy commits
generator: resolved model id / effort / invocation (same for baseline and candidate)
hypothesis:
edit:
topics: text and role (regression / unseen / target / leakage / stretch)
overlap-check: nearDuplicates / sameMaterial max (candidate vs baseline at gate)
trait-check: concrete mean / indirect mean (candidate vs baseline at gate; baseline run-to-run gap) / compare win rate (gate only)
hand counts: 「」 / strict form violations / accepted exceptions / unaccepted violations / within-form condition play / repeated mechanisms / repeated templates / repeated metaphor systems / cross-run material
change-specific (if registered): target successful runs (candidate vs baseline) / stretch successful runs / leakage per topic / met or not / transfer demonstrated or unconfirmed
artifacts: raw outputs / evaluator JSON / per-answer exception audit
diagnostics (optional): diversity-check notes / provisional funniness-score
human blind comparison (gate only, optional): not run | candidate / baseline / tie per topic
decision: next intervention, or gate outcome (mechanically passed / validated / not passed) / adoption (yes / no / pending, with reason)
```

### Evaluation tools at a glance

| Tool | Where | What it measures | What it does NOT measure | When |
|---|---|---|---|---|
| `overlap-check` | installed | Answer pairs sharing the same core material (被り) | Same-direction twists with different material; set-wide convergence | Every iteration; `nearDuplicates` is a hard gate check |
| `trait-check` `evaluate.ts` | installed | `concrete` (a concrete thing/phenomenon/anomaly appears), `indirect` (explanatory, roundabout phrasing) | Funniness itself | Every iteration as a trend; at the gate, regression vs baseline only |
| `trait-check` `compare.ts` | installed | Pairwise preference from concreteness and straightness | Absolute funniness | Gate: candidate × baseline win rate |
| `diversity-check` | research | Decomposition axes of the お題 (prose) | Convergence humans point out (AUC 0.49) | Optional diagnostic |
| `funniness-score` | research | 6-axis funniness scores | Anything humans agree with (inverted/chance) | Optional, provisional |
| `risk-flags` | research | ベタ・ひねりなし・共感・認知度・滑り・相対典型性 flags | Human preference (chance; some inverted) | Not used |
| `cluster-fit-check` | research | Fit to literature-derived user-cluster preferences | Funniness; unvalidatable with one rater | Only when deliberately tuning audience breadth |

### How far to trust the evaluators

humor-skills validates every judge against recorded human judgments
(`data/human-evals/`) and writes the result to
`reports/validation/<date>/summary.md`, with the interpretation in
`notes.md` next to it (procedure: humor-skills `src/validation/README.md`).
Check the latest one before relying on a score.

As of the 2026-09-25 run (75 labeled answers, 7 human set preferences, 13
answer pairs, 11 of them blind; 15 blind similarity judgments):

- `overlap-check` `sameMaterial` at 0.7: AUC 0.94, 4 of 5 similar pairs
  caught, 0 of 10 false flags, retest r=0.99. Tuned on these same pairs —
  confirm on new topics before tightening anything.
- `trait-check`: `concrete` AUC 0.67 (6 of 7 set preferences), `−indirect`
  0.62; `compare.ts` 0.64 within sets and 10 of 13 human-compared pairs.
  The questions were written from the human findings on this same data, so
  read these as optimistic, and none is marked `gate: yes`.
- Every research judge fails to beat the baselines (no-rubric "how funny",
  "which is funnier", and length). Asking a judge "is it funny" in any wording
  came out at chance or inverted; confident judgments were the most wrong.
  `funniness-score` rated both recorded regressions (07-11 attractor set,
  09-15 節分) above the sets the human preferred.
- No judge detects same-direction reinterpretation with different material,
  nor set-wide convergence. That stays a hand-counted diagnostic.

A research judge moves to `skills/` only when its human agreement beats
chance at the 95% level, is stable across two runs (r≥0.95), and reproduces
on new human evaluations. Only then does it belong in this process.

### Dropped requirements, and why (do not reinstate without new evidence)

Measured in the 2026-06 sessions:

- **3-consecutive-pass streak**: humor-eval swings ±0.4 between identical
  back-to-back runs, so a streak across full loops measures evaluator luck,
  not prompt quality. One gate pass including an unseen topic gives the same
  confidence at a third of the cost.
- **Mandatory `cluster-fit-check` + `humor-rank` every iteration**: their
  conclusions duplicated what cheaper checks plus simple hand counting
  already showed (e.g., quote-form lock-in is visible by counting 「」).
- **≤30% fun-check risk ceiling**: never met in any session, including by the
  sets that scored best on humor-eval — the flag rate did not correlate with
  quality.
- **`humor-eval` on every iteration**: the noisiest and most expensive
  signal; single-pass averages cannot support claims about edits with effect
  size <0.4.

Measured on 2026-09-23 (humor-skills `reports/validation/2026-09-23/`):

- **`humor-eval` median floors (Relevance/Empathy ≥2.5) and the Overall-4
  peak as validating gate criteria**: checked blind against human labels,
  they were at chance and preferred the human-rejected set in both recorded
  regressions.
- **A human in every loop**: the blind human comparison is optional and
  asynchronous; mechanical checks alone decide "mechanically passed".
- **Absolute similarity/diversity bars as hard gates** (a sentence template
  shared by >40%, "no overlap" by prompt-mode judgment, `diversity-check`
  ≥6 axes): the human's favorite recorded set would have failed them, and
  prompt-mode overlap judgments invented similarity. Only near-duplicates
  are a hard check; the rest is compared against the baseline.

Measured on 2026-09-24/25 (humor-skills `reports/validation/2026-09-24/`,
`2026-09-25/`):

- **`fun-check` in the light loop (dominant risk type, flag rate)**: its
  risk flags (now `research/risk-flags`) are at chance, and ひねりなし/滑り
  point the wrong way. The parts that worked became `overlap-check` and
  `trait-check`.
- **`diversity-check` axis count and largest-axis share as a gate warning**:
  AUC 0.49 at detecting the convergence humans pointed out. Kept only as an
  optional prose diagnostic.
- **Provisional `humor-eval` medians on every gate**: the Jev version is
  inverted against the human, so logging it by default invited misreading.
  Optional now.
- **Prompt-mode `humor-rank` for finalist ties**: 0.46 on human-compared
  pairs, retest r=0.68, no better than a no-rubric judge. Replaced by
  `trait-check` `compare.ts`.
- **Maximizing `trait-check` values**: they describe past winners; used as a
  target they drive the same collapse as the 07-11 attractor. Regression
  checks only.

## Open evaluation questions (deferred process work)

User direction, 2026-11-09: record these issues and revisit the evaluation
process later; continue improving the generation skill now.

- Concreteness is one feature, not an absolute measure of quality or
  funniness. In condition-finish gate 15 the human tied the 7-character sets,
  while the candidate's two accepted performance answers scored .075 on
  `concrete`; its eight ordinary answers scored .846 versus the baseline's
  .859. The intended mechanism can be penalized because it does not depict a
  physical scene. The scoped exception above was approved; broader changes
  to the evaluation process remain deferred.
- The candidate lost the human comparison on Sylvanian Families. Domain
  mismatch on one feature does not explain away material repetition or weak
  answers on other topics. Keep human judgments and all raw scores.
- A gap from only two baseline runs is an operational tolerance, not a
  reliable sampling-error estimate. Very small or zero gaps can turn tiny
  feature differences into failures. Assess false vetoes and the cost of
  repeated gates before treating the present procedure as a stable quality
  standard.
- Revisit the scope and combination of `concrete`, `indirect`, pairwise
  preference, relevance, empathy and diversity with new human labels. A
  proxy should not become an optimization target or silently substitute for
  the user's judgment. Preserve the distinction between a mechanical result
  and evidence that the answers are funnier.

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
