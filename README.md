# decision-review-kit

A Claude Code skill for getting decisions out of busy people.

Most review goes badly because the wrong thing gets put in front of the reviewer.
Somebody sends a four-thousand-row code list, a long spec, or a finished analysis and
asks "does this look right?" The reviewer can't audit it, so they either rubber-stamp
it or say "this is wrong" without being able to say why. The team then defends the
artifact against every conceivable objection, forever, because the objection was never
really about the artifact.

The artifact is downstream of a handful of judgement calls. A code list rests on maybe
eight boundary decisions. An analysis rests on a dozen definitional ones. Surface
those, attach what each one costs, and put *them* in front of the person whose call it
is. They can decide in twenty minutes — and they own the result, because they defined
what acceptable means rather than being asked to bless a list.

This kit runs that loop: interview, surface the decisions, build a form, collect the
answers, reconcile them, keep the register.

## What you get

A self-contained HTML page — no server, no accounts, no link that expires. It opens
from an email attachment on a plane, saves answers to `localStorage` as the reviewer
types, and exports one JSON file to mail back. Then a script that reads those files,
sorts them into agreed / conflict / single-voice / silent, drafts your decision-log
entries, and writes the next round's spec with both sides quoted verbatim.

```bash
python scripts/build_form.py examples/codelist-review.yaml -o review.html
# ... reviewers fill it in and email back the JSON ...
python scripts/ingest.py examples/codelist-review.yaml returned/*.json --out-dir registers/
```

## Install

Drop the directory into your skills folder:

```bash
git clone https://github.com/<you>/decision-review-kit.git ~/.claude/skills/decision-review-kit
pip install pyyaml   # optional — JSON specs work without it
```

Then just describe what you need: *"I need the clinical lead to sign off on this code
list"*, *"two reviewers disagreed about the exclusion criteria"*, *"turn this feedback
into something I can act on"*. The skill starts by interviewing you about what you're
trying to document, then reads the project to work out what the decisions actually are.

The scripts work standalone if you'd rather write the specs yourself.

## Layout

```
SKILL.md                          the workflow
scripts/build_form.py             spec → self-contained HTML
scripts/ingest.py                 returned JSON → registers + next round
assets/theme.css                  the look; swap this file to rebrand
references/writing-questions.md   how to phrase a card so it reads as a decision
references/registers.md           decision log, open questions, registry
references/rounds.md              running round two and closing out
references/schema.md              spec format, export format, non-negotiables
examples/codelist-review.yaml     eight boundary decisions behind a code list
examples/migration-review.yaml    a round-two tie-break on an API cutover
```

Both examples are invented — the people, numbers, and projects in them are not real.

## The parts that matter

**The questions.** Not automated, and shouldn't be. A card that describes a situation
and trails off gets "interesting" written in the box. A card that ends in a fork, with
a number attached to each side, gets answered in ten seconds and stays answered.
`references/writing-questions.md` is the longest reference file for a reason.

**The ID namespace.** The form gets its own prefix, and the build fails if it collides
with the register the project already keeps. Without this, returned answers get filed
against the wrong decisions and the returned file carries no way to tell which meaning
was intended — unrecoverable without going back and asking again, which is the one
thing the exercise is trying to avoid.

**The register.** The forms are ephemeral; the record of what was decided, by whom, and
whether it was ever actually applied is the deliverable. The gap between *decided* and
*applied* is the most dangerous state in a project, because everyone believes it's done.

**The browser behaviour.** Small, unforgiving, and bundled rather than re-derived:
escaping radio values before using them as selectors, keeping duplicate copies of a
question in step, requiring the respondent's name *before* the download, refusing an
empty export. Get one wrong and a reviewer loses an afternoon's work without either of
you finding out until they mention it.

## Licence

MIT.
