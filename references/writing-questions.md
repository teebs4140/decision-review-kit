# Writing questions people can actually answer

The generator handles the browser. This is the part that decides whether the review
works, and it is not automatable, because it rests on knowing what the reviewer knows
and what they care about.

- [Start from what the reviewer owns](#start-from-what-the-reviewer-owns)
- [The four tests](#the-four-tests)
- [Rewriting exposition into a decision](#rewriting-exposition-into-a-decision)
- [Attach the cost](#attach-the-cost)
- [Recommend something](#recommend-something)
- [Options](#options)
- [When the question corrects the asker](#when-the-question-corrects-the-asker)
- [Quoting people](#quoting-people)
- [Length](#length)
- [Before you send](#before-you-send)

## Start from what the reviewer owns

The reviewer is not there to check your work. They are there to make calls that are
theirs to make and yours to implement. Every card should be recognisably one of those.

This distinction does real work when pruning. "Did we index this table correctly" is
not a clinical director's question no matter how much it is bothering you. "Does a
patient whose only coding is gestational count as having diabetes" is nobody else's.
When a card is not clearly the reviewer's, either it belongs to you — decide it, record
it, move on — or it belongs to a different reviewer, which is worth knowing early.

## The four tests

A candidate becomes a card only if all four hold.

1. **A reasonable expert could go either way.** If there is one defensible answer, it
   is not a decision, it is a task. Do it.
2. **The answer changes something you can name.** If you cannot finish "if they say
   yes then ___", it is trivia. Cut it.
3. **This reviewer has standing.** See above.
4. **It is not already settled.** Re-asking a settled question costs you credibility
   on the questions that matter, and reviewers remember it.

Five to ten cards survive a real review. If you have twenty, you have skipped step 2.

## Rewriting exposition into a decision

The most common failure is a card that describes a situation and trails off, leaving
the reviewer to work out what is being asked. They will not; they will write "interesting"
in the box, and you have spent one of your twenty minutes on nothing.

> **Exposition:** Three sites record no emergency department visits at all. This may
> reflect how those sites map their data rather than genuine absence.

> **Decision:** Do those three sites stay in the headline emergency-visit rate, or come
> out of it? Leaving them in reads as a real rate of zero. Taking them out drops the
> denominator by 18% and makes the rate conditional on a site that records the visit
> type at all.

Same facts. The second one can be answered in ten seconds by someone who knows the
domain, and cannot be answered vaguely.

A card that survives this rewrite usually turns out to be either simpler or more
contentious than you thought. Both are useful to find out before the meeting.

## Attach the cost

A decision without a number attached gets answered on instinct and reopened three weeks
later when someone sees the effect. With the number attached, the reviewer is deciding
with their eyes open and it stays decided.

> Excluding these moves 1,240 patients, **3.1%** of the cohort, and raises the median
> age of the female cohort by about 4 years because they cluster at childbearing age.

Two significant figures is plenty. If you genuinely cannot measure it, say so in those
words — "we cannot size this without building both versions" is itself information the
reviewer needs, and it is a fair thing to ask them to decide anyway.

Watch for interactions and say them out loud: "note that if you require two diagnosis
codes in CLQ-05, labs become the main route by which lightly-coded patients get in."
Reviewers answer cards one at a time and will not spot the coupling unless you point
at it.

## Recommend something

A tie-break with no recommendation asks two busy people to negotiate with each other.
One with a recommendation asks them to agree or object, which is faster and, in
practice, produces a better answer, because objecting sharpens what someone thinks
in a way that open-ended asking does not.

Give the reasoning in one or two sentences. Being wrong is fine and costs nothing —
they correct you, which is the point. Being absent costs a round.

The exception is where you genuinely have no view and the choice is one of values
rather than fact. Say that explicitly: "we have no preference here; this is a call
about what the cohort is meant to mean."

## Options

Two to four. They must be genuinely distinct — options that differ only in wording
make the reviewer suspect a leading question, and they are usually right.

The free-text box is always there because the most valuable answer is often "neither,
do this instead", and a form that cannot receive it teaches reviewers to answer by
email, where answers get lost and cannot be collated.

Where a middle option is defensible, offer it. "Exclude from the main list but ship it
as a switchable sub-list" is the answer to a surprising number of inclusion arguments,
and framing it as available prevents an hour of debate about a binary that was never
binary.

## When the question corrects the asker

Sometimes the honest answer is that the question rests on something untrue — a number
that turned out wrong, a mechanism that does not work the way both of you assumed.

Say so plainly, in the card, before answering: *"This one starts from a premise that
does not hold. The rate is 2.8% only because a marker file inflates the denominator;
with it removed it is 0.4%, and the pattern you were asking about is not there."*

This feels risky and is not. Reviewers read an answer that quietly works around a false
premise as either evasion or incompetence. Correcting it directly is the thing that
earns you the right to be believed on the cards where you are asserting rather than
asking.

The same applies to your own errors. A card that says "we told you X last round; X was
wrong, here is why" is worth more than three cards that are merely right.

## Quoting people

Verbatim, always, and attributed. A paraphrase drifts toward whoever wrote the summary
— not dishonestly, just by the ordinary gravity of writing — and the person quoted will
notice and will be right to.

The generator checks this for you if you point `--sources` at the archived replies. If
a quote came from somewhere else — a call, a corridor — label it as such in the card,
because an unlabelled quote from outside the form reads to its author as words they
never wrote.

When you show two people's positions side by side, give both the same amount of room
and the same tone. If one side reads as a summary and the other as a rebuttal, you have
put your thumb on the scale, and the reviewer on the losing end will feel it before
they can articulate it.

## Length

The card should be readable without opening the fold. Question, positions if any,
recommendation, options: that is the card. Everything else — the derivation, the table,
the counts by site — goes behind "Why it matters, and what we measured".

This is not about tidiness. It means the reviewer who trusts you finishes in fifteen
minutes and the one who wants to audit you can do it without a phone call. Both get
served by the same document, which is the only reason it is worth building one.

## Before you send

Open it and read it as the reviewer.

- Is every card answerable without opening a fold?
- Would any of these annoy someone by having been asked already?
- Is there a number on every card where a number exists?
- Does any card ask them to check your work rather than make their call?
- Would you spend twenty minutes on this?

If a card fails the last one, it is not that the card is bad — it is that it is not
theirs. Move it to your own list and decide it.
