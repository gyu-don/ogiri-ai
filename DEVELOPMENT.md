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

### Non-negotiables (both tiers)

- Read `SKILL.md`, this file, and the evaluation skills you will use, before editing.
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

### Light loop (default — ~5-6 subagent calls per iteration)

1. Hypothesis + one targeted edit to `SKILL.md`.
2. Generate: one `/ogiri-ai` run per fixed topic, 2 fixed topics from
   different categories (5 answers each).
3. Evaluate per topic: `diversity-check` and `fun-check`, one subagent each.
   Also count by hand (no subagent needed): 「」 per run, same-mechanism
   repeats, same borrowed metaphor system repeats, material reappearing from
   the previous iteration's outputs.
4. Log, decide the next intervention.

Light-loop reference values — these are *trend signals*, not pass/fail gates:
- ≥4 distinct decomposition axes per 5 answers
- no single risk type dominating the fun-check flags (the raw flag rate runs
  40-60% even on good sets — fun-check flags generously by design)
- 「」 count within `SKILL.md`'s own limit; no repeated material across iterations

### Gate check (only when claiming a validated improvement — ~15-18 calls)

Run once when light-loop trends look good, not on every iteration:

1. Generate: 2 fixed topics × 2 independent runs each, plus **1 unseen-category
   topic** × 2 runs (pool each topic to 10 answers).
2. `diversity-check` on each pooled 10: **≥6 axes, no axis >40%**.
3. `fun-check` on each pooled 10: no near-identical material across the two
   runs (cross-run attractor), no risk type >40% of all flags, no overlap
   warning repeated from the previous gate. Pooled flag rates overstate what
   one user sees in a single 5-answer output — treat the rate as a trend, not
   a gate.
4. `humor-eval` × **2 independent passes** per pooled 10; compare medians.
   Floors: median Relevance ≥2.5 **and** median Empathy ≥2.5.
   Peak: ≥2 answers at Overall 4 per 10 (ogiri is judged by its best answer,
   not its mean). Ignore Overall-average deltas <0.4 — that is the measured
   noise band between identical runs.
5. All three topics pass → the change is validated. Then **stop looping**:
   once structural metrics pass and humor-eval deltas sit inside the noise
   band, further prompt tuning cannot be validated by LLM evaluation alone.
   The next signal is human reactions, fed back through the Example Firewall.
6. Commit with hypothesis, loop count, per-iteration metrics, and what
   changed between iterations. If the gate was not passed this session,
   report the exact loop depth, the failing criteria, and the next concrete
   intervention — the honest final state is "improved but not fully
   validated", not "done".

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
hand counts: 「」 / repeated mechanisms / repeated metaphor systems
humor-eval (gate only): median Relevance / Empathy / Overall-4 count
decision: next intervention, or gate pass/fail
```

### Evaluation skills at a glance

| Skill | What it measures | What it does NOT measure | When |
|---|---|---|---|
| `diversity-check` | Structural variety of decomposition axes | Funniness | Every iteration |
| `fun-check` | Per-answer risks (ベタ・絵・ひねり・共感・認知度・長さ・滑り・被り・相対典型性) | Overall funniness | Every iteration |
| `humor-eval` | Multi-axis scoring (Novelty/Clarity/Relevance/Intelligence/Empathy/Overall) | Ground-truth human verdict | Gate only, 2-pass medians |
| `humor-rank` | Pairwise relative ranking within a topic | Absolute funniness | Finalist ties only |
| `cluster-fit-check` | Alignment with literature-derived user cluster preferences | Funniness or universal appeal | Style/audience tuning only |

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
