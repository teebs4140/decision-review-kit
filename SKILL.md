---
name: decision-review-kit
description: >
  Run a decision review — surface the judgement calls behind a piece of work, put them
  to the people who should own them as a short self-contained HTML form, collect their
  answers as JSON, reconcile disagreements, and keep a durable register of what was
  decided and what is still open. Use this whenever someone needs sign-off, review, or
  a decision from named people: getting a code list or spec approved, resolving reviewer
  or stakeholder feedback, running an expert panel or advisory board, chasing scattered
  email opinions into one place, or turning "this is wrong" into answerable questions.
  Also use it when a decision log, open-questions list, or design doc needs to go in
  front of humans, when review feedback has come back and needs processing, when two
  reviewers disagree and someone must break the tie, or when a project keeps relitigating
  the same choices because nobody recorded who decided what. Reach for it even if the
  user only says "I need X to review this" or "how do I get sign-off on this" — the
  interview at the start will work out whether it fits.
---

# Decision review kit

## The idea worth holding onto

Most review goes badly because the wrong thing is put in front of the reviewer.

Somebody sends a four-thousand-row code list, a two-hundred-page spec, or a rendered
analysis and asks "does this look right?" The reviewer cannot audit it, so they either
rubber-stamp it or say "this is wrong" without being able to say why. The team then
takes a defensive posture against every conceivable future objection, which is
exhausting and never finishes, because the objection is never really about the artifact.

**The artifact is downstream of a handful of judgement calls.** A code list rests on
maybe eight boundary decisions. An analysis rests on a dozen definitional ones. Surface
those, attach what each one costs, and put *them* in front of the person whose call it
is. Now they can decide, in twenty minutes, and they own the result — because they
defined what acceptable means rather than being asked to bless a list.

That reframes the deliverable. You are not building a feedback form. You are
transferring ownership of a judgement, and leaving a record of who took it.

Everything below serves that. The HTML is the least interesting part.

## Do not start by building anything

Start by interviewing. You cannot write good questions about work you do not
understand, and the failure mode — generating twenty plausible-looking questions that
miss the two things actually in dispute — wastes the reviewer's goodwill, which is the
scarcest thing in the whole exercise.

Ask, conversationally, and adapt as you learn:

1. **What is the artifact, and what would "wrong" mean?** The thing people complain
   about. Chase the complaint: "they say the list is too broad" is a boundary decision
   in disguise.
2. **Who decides?** Names, and how many. One decider and three is a different document.
3. **What is already settled?** Anything re-asked will annoy them and cost you
   credibility on the questions that matter.
4. **How much of their attention do you have?** Twenty minutes is typical. This is a
   budget, and it sets how many questions survive.
5. **Where is the material?** Code, specs, prior threads, existing decision logs,
   returned reviews. You will read it next.
6. **Is there an existing register or ticket scheme?** You need its ID format so the
   form does not collide with it. This matters more than it sounds — see below.

If the user is vague, propose a reading and let them correct it. That is faster than
twenty questions and it shows them what you understood.

## Then find the decisions — do not invent them

Read the material before drafting. For anything non-trivial, dispatch subagents in
parallel, each over a different slice, each answering the same question:

> Where does this work make a choice that a reasonable expert could make differently?
> For each: what is the choice, what are the live options, roughly how much does it
> move, and where in the material is it made?

Good slices: the code that implements it; the docs that describe it; prior review
threads and email; the existing decision log; adjacent or competing implementations.
Ask them to return candidates with file and line references so you can verify rather
than trust.

Then, and this is the part that takes judgement, **prune hard**. Candidates that
survive are the ones where:

- a reasonable expert could genuinely go either way, *and*
- the answer changes something downstream, *and*
- the decider has standing to answer it.

Anything failing the third test is a question for you or the team, not for them. Do not
launder your own uncertainty into a reviewer's inbox — deciding it yourself and
recording the decision is usually the better service.

Anything that fails the second test is trivia. If you cannot say what changes, cut it.

A useful sanity check: if you have more than a dozen questions, you have not finished
pruning. Real reviews land between five and ten.

## Write questions that read as decisions

This is where reviews are won and lost, and it is worth reading
`references/writing-questions.md` before drafting. The short version:

- **A question is a fork, not a fact.** "Three sites record no emergency visits" is
  exposition. "Do those three sites stay in the headline rate, or come out of it?" is a
  question. If the card does not end in something answerable, it does not belong.
- **Attach the cost.** "Excluding these moves 1,240 patients, 3.1%" turns an
  aesthetic preference into an informed call. A decision with no number attached gets
  answered on vibes and reopened later.
- **Recommend something.** A tie-break with no recommendation asks two busy people to
  negotiate. One with a recommendation asks them to agree or object, which is much
  faster and gets a better answer. Being wrong is fine; being absent is not.
- **Reasoning goes behind a fold.** The reviewer who trusts you never opens it; the one
  who does not can audit every number. Both are served and the page stays short.
- **Quote people verbatim.** If you are relaying what someone said, use their words.
  A paraphrase drifts toward whoever wrote the summary, and the person quoted will
  notice.

## Build the form

Write a spec (`references/schema.md`) and run:

```bash
python scripts/build_form.py spec.yaml -o review.html
```

One self-contained HTML file: no external requests, opens from an email attachment,
answers save to `localStorage` as they type, and an Export button downloads JSON to
mail back. No server, no accounts, no link that expires — which is what makes it
actually get filled in.

**Give the form its own ID namespace, and mean it.** If the project uses `D-nnn` in a
decision log, the form uses something that cannot collide — `R2-nn`, `CLQ-nn` — and each
item carries `origin` pointing back at the real register item. The reviewer never sees
`origin`. This is not fussiness: reusing register labels means returned answers get
filed against the wrong decisions, and you cannot tell from the returned file which
meaning was intended. The build refuses to proceed if IDs collide, which is the only
reason it gets caught.

**Point `--sources` at archived replies** when you are quoting people. Every quoted span
is checked against what they actually sent; anything unfound fails the build unless you
list it under `known_offsource` with a reason. An unlabelled quote from another channel
reads, to the person who filled in the form, as words they never wrote.

Before sending, open it and check: is every card answerable without opening a fold? Is
anything already settled? Would you spend twenty minutes on this?

## Collect and reconcile

```bash
python scripts/ingest.py spec.yaml returned/*.json --out-dir registers/
```

Sorts every item into **agreed**, **conflict**, **single** (only one person answered —
not the same as consensus, and treating it as consensus rests a decision on someone who
never knew they were the only voice), or **silent**. Writes:

- `report.md` — everyone's answers side by side
- `decisions.md` — draft register entries for the agreed items
- `open.md` — what is still open and why
- `round2.yaml` — a ready-to-build spec for the next round, with each conflict
  pre-populated and both positions quoted verbatim

Edit the drafts before they become real. Each decision needs an **Effect** line saying
what changes in the work — that is the line someone reads in six months, and the script
deliberately leaves it as a TODO because no script can write it. A register full of
decisions with no stated effect is a list of opinions.

## Keep the state — this is what makes it durable

The forms are ephemeral. The register is the product. Keep three things
(`references/registers.md` has the formats):

- **A decision log.** One entry per decision: what was decided, who decided it, what
  changes, status. Append; amend in place with a dated note rather than rewriting,
  so the record of what was believed in March survives.
- **An open-questions list.** What is unresolved, who it is waiting on, and what it
  blocks.
- **A one-page registry** if the project runs long enough to grow more than one log:
  live questions with their aliases, decisions logged but *not yet applied in code*,
  what is out with whom, and the numbers that appear in more than one document.

That third one earns its keep the moment somebody asks "is this still open?" and the
answer lives in four files. The gap it is really tracking is between *decided* and
*applied* — a decision marked Confirmed that nobody implemented is the most dangerous
state in a project, because everyone believes it is done.

**Numbers move.** When a decision changes a figure that appears in several documents,
record both values and the date. Half of all review pain is one document quoting a
number another document has since revised.

## Later rounds

Round two is short: only where people disagreed, plus anything genuinely new. Show both
positions verbatim side by side — seeing the other view is what lets someone concede in
one line instead of restating their own. Carry a folded "already settled" section so
nobody answers the same thing twice.

Watch for the round-two-specific traps in `references/rounds.md`. The main one:
**a reviewer endorsing another reviewer's answers inherits their reasoning, including
any premise that turns out to be wrong.** If you later find the premise was wrong,
both of them need telling, even when the decision itself stands.

## What to hand back

When the loop closes, the user should have: a register that says what was decided and
by whom, a short list of what is still open and who owns it, and — if the work is
downstream of the decisions — the rebuilt artifact. Say plainly which decisions are
recorded but not yet applied. That gap is where projects rot.

## Files

| Path | What it is |
|---|---|
| `scripts/build_form.py` | spec → self-contained HTML, with the ID and quote guards |
| `scripts/ingest.py` | returned JSON → report, draft decisions, open list, next-round spec |
| `assets/theme.css` | the look; swap this file to rebrand |
| `references/writing-questions.md` | how to phrase a card so it reads as a decision |
| `references/registers.md` | decision log, open questions, registry formats |
| `references/rounds.md` | running round two and closing out |
| `references/schema.md` | spec and export JSON formats |
| `examples/` | worked specs — a code list and a technical migration |

Hand-rolling the HTML is fine when a project needs something the spec cannot express.
If you do, keep the behaviours in `references/schema.md` under "non-negotiable" — they
are the ones whose absence loses a reviewer's work without either of you noticing.
