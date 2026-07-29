# Running the second round, and closing out

Round one surfaces disagreement. Round two resolves it. They are different documents
and the second one is easy to get wrong in ways that cost you the reviewer.

- [What goes in round two](#what-goes-in-round-two)
- [Show both positions verbatim](#show-both-positions-verbatim)
- [Endorsement inherits reasoning](#endorsement-inherits-reasoning)
- [One voice is not consensus](#one-voice-is-not-consensus)
- [Silence](#silence)
- [When someone answers off-channel](#when-someone-answers-off-channel)
- [Closing out](#closing-out)

## What goes in round two

Only three kinds of thing:

1. **Conflicts.** Where people chose differently. `ingest.py` pre-populates these in
   `round2.yaml`, with both positions quoted.
2. **Genuinely new questions** that round one's answers created. These are common and
   legitimate — a decision to admit lab evidence raises a threshold question that did
   not exist before.
3. **Corrections.** Anything you told them last round that turned out to be wrong.

Everything else goes in a folded "already settled" section so nobody answers the same
thing twice — and so they can check nothing was recorded wrongly, which occasionally
catches a real transcription error.

Round two should be visibly shorter than round one. If it is not, round one asked the
wrong questions and the honest move is to say so in the intro rather than let the
reviewer conclude it themselves.

## Show both positions verbatim

Two columns, equal space, equal tone, each person's words as they wrote them.

This is what lets someone concede in one line. Given "here is what your colleague
actually said, and here is why", people quite often reply "fair enough, go with theirs"
— and that is a resolved decision in ten seconds. Given a summary of the disagreement,
they restate their own position, because a summary gives them nothing new to react to.

Do not editorialise between the columns. If your recommendation sides with one of them,
put that in the recommendation block below, where it is labelled as yours.

## Endorsement inherits reasoning

The trap specific to later rounds:

**When one reviewer defers to another — "I'm happy to go with whatever Dr Okafor says
here" — they inherit that reviewer's reasoning, including any premise that turns out
to be wrong.**

So if you later discover the premise was wrong, both of them need telling, not just the
one who wrote it down. It is easy to miss because the register records the decision
under the person who authored it, and the endorsement looks like a non-event.

Record deferrals explicitly for this reason: "Dr Salim deferred to Dr Okafor's answer
on CLQ-05" belongs in the decision entry, not just in the report. Then when CLQ-05's
premise moves, the grep finds both names.

The same holds for a decision that was right for the wrong reason. If the conclusion
stands but the reasoning was wrong, tell them anyway — they will use that reasoning
again on something where it does not hold.

## One voice is not consensus

`ingest.py` classifies an item answered by exactly one person as `single`, deliberately
distinct from `agreed`. It is a judgement call whether that is enough, and the right
answer depends on how load-bearing the decision is and whether the person who answered
knew they were the only one.

They usually did not. Someone answering a form does not know who else answered it, so
they calibrate as one voice among several — which is a different level of care than
they would bring to a decision they knew rested on them alone. Going back with "you
were the only one on this, are you comfortable owning it" is a small ask and it is the
difference between a decision that holds and one that gets reopened at the worst
possible moment.

## Silence

Nobody answered. Before re-asking, work out which kind of silence it was:

- **The question was unclear.** Rewrite it, do not resend it.
- **It was not theirs to answer.** Decide it yourself and record it.
- **They ran out of time.** Re-ask, and shorten the form so it does not happen again.
- **It was buried.** If it was the eleventh card, that is on the form, not on them.

The one thing not to do is carry it forward unchanged for three rounds. A question
nobody answers twice is telling you something about the question.

## When someone answers off-channel

They will. Half the form comes back as JSON and the rest arrives as a paragraph in an
email reply, and often the email contains the most useful thing anyone said.

Archive the email alongside the returned files and treat it as a source. When you quote
it in the next round, label where it came from — the quote guard exists precisely for
this, because an unlabelled quote from an email reads, to its author looking at a form,
as words they never wrote in it.

Do not ask them to redo it in the form. You are optimising for their attention, not for
your parser.

## Closing out

The loop ends when the open list is empty or everything left on it is explicitly parked
with a reason. At that point hand back:

- the decision log, with an effect line on every entry;
- the open list, with an owner on each remaining item;
- a plain statement of which decisions are recorded but **not yet applied**;
- the rebuilt artifact, if it is downstream of any of this.

Then say what changed since the last version they saw. Reviewers have been carrying
this in their heads across weeks, and the summary of what moved is what lets them let
go of it.
