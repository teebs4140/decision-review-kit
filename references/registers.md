# Keeping the state: decision log, open questions, registry

The forms are ephemeral. What survives the project is the record of what was decided,
by whom, and whether it was ever actually applied. That record is the deliverable; the
HTML is how you collect it.

- [Three files](#three-files)
- [The decision log](#the-decision-log)
- [Open questions](#open-questions)
- [The registry](#the-registry)
- [Decided is not applied](#decided-is-not-applied)
- [Numbers that appear twice](#numbers-that-appear-twice)
- [Amending rather than rewriting](#amending-rather-than-rewriting)

## Three files

- `decision-log.md` — what has been decided. Append-only in spirit.
- `open-questions.md` — what has not, who owns it, what it blocks.
- `REGISTRY.md` — one page of state across everything, once there is more than one log.

A short project needs the first two. Add the third the first time somebody asks "is
this still open?" and you have to read four files to answer.

## The decision log

One entry per decision. `ingest.py` drafts these for the agreed items; you finish them.

```markdown
### D-104 — Gestational-only coding does not admit to the main list

**Decided:** 2026-07-29 by Dr Okafor (round 1, form item `CLQ-01`).

**Decision:** Exclude from the main list; ship as a switchable sub-list.

**Reasoning:** Gestational diabetes resolves after delivery in most patients, so
including it silently changes what the cohort means. Dr Okafor: “Agreed, but I want
the sub-list to exist — there are perinatal questions that need it.”

**Effect:** 1,240 patients (3.1%) leave the candidate cohort. `build_list.py` gains a
`--include-gestational` flag, off by default. The female median age in the headline
table falls by about 4 years.

**Status:** Applied 2026-07-30 in `build_list.py`.
```

The **Effect** line is the one that earns the file's existence. It is what someone
reads in six months when they are trying to work out why a number moved, and it is the
line the ingest script deliberately leaves as a TODO, because no script can write it.
A log full of decisions with no stated effect is a list of opinions.

**Status** is worth keeping mechanical. Something like: Confirmed → Applied, with the
date and the file. See below for why the gap between those two matters.

If a decision rests on a premise that later turns out to be wrong, do not delete the
entry. Amend it (see below) and check whether anyone else's decision inherited that
premise.

## Open questions

Shorter entries, but each one needs an owner and a blocking relationship, or it is
just a worry list.

```markdown
### Q-207 — Do the three no-ED sites stay in the headline rate?

**Asked:** round 1 (`CLQ-11`). **Waiting on:** Dr Salim.
**Blocks:** every rate in §5.2–5.5; the draft cannot go out without it.
**State:** Dr Okafor answered (exclude, flagged); Dr Salim has not. One voice is not
a consensus on a denominator this load-bearing, so it stays open.
**Next:** carried into round 2 as `CLQR2-03`.
```

Two things make this useful rather than decorative: the **blocks** line, which tells
you whether to chase it, and the **next** line, which stops a question from quietly
falling out of the project between rounds. That is the most common way an open question
dies — not decided, just never carried forward.

## The registry

One page. Not a fourth copy of the reasoning — a state table over everything else.

```markdown
# Registry — state as of 2026-07-29

## Live questions
| id | also called | question | with whom | blocks |
|---|---|---|---|---|
| Q-207 | CLQ-11, CLQR2-03 | no-ED sites in the headline rate | Dr Salim | §5.2–5.5 |

## Decided but not yet applied
| id | decided | what still needs doing |
|---|---|---|
| D-118 | 2026-07-22 | two-code rule not yet in `build_list.py` |

## Out with someone
| what | who | sent | chase after |
|---|---|---|---|
| round 2 form | Dr Salim | 2026-07-26 | 2026-08-02 |

## Numbers that appear in more than one document
| figure | value | as of | appears in |
|---|---|---|---|
| candidate cohort | 39,840 | 2026-07-29 | brief §2, form intro, slide 4 |
```

The **also called** column is what makes it worth maintaining. Once a question has been
through two rounds it has three labels — its register id, its round-1 form id, its
round-2 form id — and somebody will refer to it by whichever one they last saw.

Where the registry and a decision log disagree, the registry is the one being read, so
fix the registry first, then reconcile.

## Decided is not applied

The most dangerous state in a project is a decision everyone believes is done and
nobody implemented. It is more dangerous than an open question, because an open
question is visibly open — this one is invisibly wrong, and everyone downstream is
building on it.

So track it explicitly, and when you hand work back, say out loud which decisions are
recorded but not yet in the code. That sentence is often the most useful thing in the
handover.

The corollary: after applying a decision, check the *outputs*, not just the source.
Presentation-layer artifacts — briefs, slides, generated docs — usually carry their own
copy of the numbers and their own prose about the method, and a change applied in the
pipeline does not reach them until they are rebuilt. Rebuild them, and diff.

## Numbers that appear twice

Half of all review pain is one document quoting a figure another document has since
revised. When a decision moves a number that appears in more than one place, record the
old value, the new value, and the date, then grep for the old one.

Grep for it in every form it might take. A window written `2015-2024` in prose is
`2015:2024` in R and `20152024` in an anchor slug, and a blanket text sweep for the
first form finds neither of the others.

## Amending rather than rewriting

When a decision changes, add a dated amendment under the original rather than editing
it in place:

```markdown
**Amended 2026-08-04:** the window now closes at 2024, not 2025. The 2025 extract
turned out to be partial at every site, so a partial year was entering the denominator
at full weight. Original decision and reasoning preserved above.
```

The record of what was believed in July is what lets you understand a July decision
that now looks strange. Rewriting history makes the log tidier and much less useful,
and it is the difference between a log you trust and one you re-derive.
