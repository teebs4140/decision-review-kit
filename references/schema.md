# Spec format, export format, and the behaviours that must not be dropped

Read this when writing a spec, or when hand-rolling a page instead of using the
generator.

- [The spec](#the-spec)
- [Item fields](#item-fields)
- [Section kinds](#section-kinds)
- [The guards](#the-guards)
- [The returned file](#the-returned-file)
- [Non-negotiable behaviours](#non-negotiable-behaviours)

## The spec

YAML if PyYAML is installed, JSON otherwise. Top level:

```yaml
title: "Diabetes code list — eight decisions before we build it"
form_id: dm-codelist-r1        # goes in the export; keep it unique per round
round: 1
storage_key: dm-codelist-r1    # localStorage key — change it per round or round 2
                               # will show round 1's answers back at the reviewer
kicker: "Code list review · round 1 · 8 decisions"
minutes: 20                    # honest estimate; omit and it guesses 3/question

id_prefix: "CLQ-"              # the form's own namespace
reserved_prefixes: ["CL-", "TKT-"]   # namespaces it must not collide with
sources_dir: replies/          # optional; enables the quote check
known_offsource:               # quote fragment -> why it is not in sources_dir
  "we should probably drop": "said on the 14 May call, minuted not transcribed"

intro: >
  One paragraph. What you are asking for and why it is short.
footer: >
  Provenance: where the numbers came from, as of when.

sections: [...]
```

`intro`, `footer`, and every item text field may carry inline `<b>`, `<i>`, `<code>`.
The spec is authored by you, not by a reviewer, so this is not an injection surface,
and forbidding emphasis makes for worse questions.

## Item fields

Every field is optional except `id`. Order on the page is fixed by the renderer, not
by the order you write them.

| Field | What it does |
|---|---|
| `id` | required; must start with `id_prefix` |
| `origin` | the real register item this maps back to; never shown to the reviewer |
| `type` | free text, carried into the export (`boundary`, `tie-break`, `scope`…) |
| `title` | the card heading |
| `question` | **the fork.** Rendered large with a rule down the left. If this does not end in something answerable, the card does not belong on the form |
| `positions` | `{name: what they said}` — rendered two-up. Quote verbatim |
| `skip_if` | a "before you answer" note: conditions under which the question is moot |
| `recommendation` | what you would do and why. Give one |
| `options` | radio chips. 2–4 is right; more and it becomes a survey |
| `placeholder` | textarea prompt; defaults to "Anything to add?" |
| `background` | folded — the reasoning |
| `cost` | folded — what the answer moves, with a number |
| `table` | folded — `{columns: [...], rows: [[...]]}` |

The textarea is always rendered, options or not, because the useful answer is often
"neither — do this instead" and a form that cannot receive that answer trains
reviewers to reply by email, which is where answers go to die.

Settled items (in a `settled` section) use a different set: `id`, `title`,
`background`, `positions`, `effect` — `effect` being what changed as a result.

## Section kinds

```yaml
sections:
  - title: "1 · Where the boundaries sit"
    note: "Pick an option or write your own."
    items: [...]

  - title: "2 · Already settled"
    kind: settled                # or `reference` — same rendering
    summary: "3 items settled earlier — open only to check nothing was recorded wrongly"
    items: [...]
```

`settled` and `reference` sections are collapsed behind a fold, carry no answer
widget, and are excluded from the question count. A visible divider is inserted
before the first one — "That is everything we need. The rest is reference." — so a
reviewer knows when they can stop.

## The guards

Both run by default; `--no-guards` skips them for drafting only.

**IDs.** Duplicates, items that do not start with `id_prefix`, and items that collide
with any `reserved_prefixes` entry all fail the build. This is the guard worth
understanding: if a form numbers its items with labels the project's register already
uses for different questions, nothing looks wrong until the answers come back, and
then the reviewers' judgements are filed against the wrong items with no way to tell
from the returned file which meaning was intended. Unrecoverable without asking again.

**Quotes.** With `--sources <dir>` (or `sources_dir:` in the spec), every quoted span
in `positions`/`background`/`context` is checked against the archived replies —
NFKC-folded, punctuation-stripped, longest ellipsis-free run over 40 characters. An
unfound quote fails the build unless a fragment of it appears as a key in
`known_offsource` with a reason. A quote from another channel is fine; a quote from
another channel that looks like it came from the form is not, and the person quoted
will notice.

## The returned file

What the Export button downloads, named
`<form_id>-<name-slug>-<YYYY-MM-DD>.json`:

```json
{
  "form": "dm-codelist-r1",
  "round": 1,
  "respondent": "Dr Okafor",
  "exported": "2026-07-29T14:02:11.884Z",
  "answered": 6,
  "total": 8,
  "responses": [
    {"id": "CLQ-01", "type": "boundary", "title": "Gestational diabetes",
     "choice": "Exclude — gestational is a different condition",
     "comment": "Agreed, but keep the sub-list."}
  ]
}
```

Only answered items appear in `responses`; `choice` and `comment` are independently
nullable. `ingest.py` reads any number of these against the spec.

## Non-negotiable behaviours

If you hand-roll a page instead of using the generator, keep these. Each one, when
absent, loses a reviewer's work without either of you finding out until they mention
it — which is both the worst kind of bug and the kind that never shows up in testing,
because you test with an empty form and they use it with an afternoon's work in it.

1. **Save on every keystroke, to `localStorage`, under a per-round key.** No save
   button. A reviewer who closes the tab must lose nothing.
2. **Escape radio values before using them as selectors.** Option text is free text
   with quotes and brackets in it; `CSS.escape` or the restore silently fails and
   the reviewer sees their choices come back blank.
3. **Keep duplicate copies of the same item in step.** If an item appears twice on
   the page, answering one must update the other, or the export takes whichever the
   DOM found first.
4. **Require the name before the download, not after.** An anonymous file arriving in
   a thread with three reviewers cannot be attributed afterwards.
5. **Refuse an empty export** with a message, rather than downloading an empty file
   that looks like a completed review.
6. **Revoke the blob URL** after the click.
7. **No external requests at all.** It has to work from an email attachment with no
   network. One `<script src>` and it does not.
