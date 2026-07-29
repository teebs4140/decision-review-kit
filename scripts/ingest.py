#!/usr/bin/env python3
"""Read returned answer files and turn them into saved state.

    python scripts/ingest.py spec.yaml returned/*.json --out-dir registers/

Produces four things:

  report.md        every item, every respondent, side by side
  decisions.md     draft register entries for items everyone agreed on
  open.md          what is still open, and why — conflicts and non-answers
  round2.yaml      a ready-to-build spec for the next round, pre-populated with
                   each conflict and both positions quoted verbatim

The last one is the point. Turning "two people disagreed" into a next-round question
is mechanical work that is easy to do carelessly at the exact moment you are tired of
the project, and carelessness there means asking someone to re-answer something they
already answered — which is how you lose a reviewer's goodwill.

Nothing here writes to your real register. It writes drafts you edit and paste, because
a register entry needs a sentence of reasoning that no script can supply.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_form import load_spec, all_items  # noqa: E402


def load_returns(paths: list[str]) -> list[dict]:
    out = []
    for pattern in paths:
        for p in sorted(glob.glob(pattern)):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception as e:
                print(f"  skipping {p}: {e}", file=sys.stderr)
                continue
            d["_file"] = os.path.basename(p)
            if not d.get("respondent"):
                # The form refuses to export without a name, so this means the file
                # was hand-edited or came from an older build. Say so rather than
                # silently attributing it to nobody.
                print(f"  WARNING {p}: no respondent name — cannot attribute these answers",
                      file=sys.stderr)
            out.append(d)
    return out


def collate(spec: dict, returns: list[dict]) -> dict:
    """item id -> {respondent: {choice, comment}}, in spec order."""
    by_item: dict[str, dict] = defaultdict(dict)
    for r in returns:
        who = r.get("respondent") or f"(unnamed — {r['_file']})"
        for resp in r.get("responses", []):
            by_item[resp["id"]][who] = {
                "choice": resp.get("choice"),
                "comment": resp.get("comment"),
            }
    return by_item


def classify(item: dict, answers: dict) -> tuple[str, str]:
    """Return (state, why). States: agreed, conflict, single, silent.

    'single' is deliberately distinct from 'agreed'. One person answering is not a
    consensus, and treating it as one is how a decision ends up resting on someone
    who never knew they were the only voice on it.
    """
    if not answers:
        return "silent", "nobody answered"

    choices = {w: a["choice"] for w, a in answers.items() if a.get("choice")}
    distinct = set(choices.values())

    if len(answers) == 1:
        who = next(iter(answers))
        return "single", f"only {who} answered"
    if not distinct:
        return "conflict", "answered in prose only — no option chosen, so read the comments"
    if len(distinct) == 1:
        if len(choices) < len(answers):
            silent = [w for w in answers if w not in choices]
            return "agreed", ("everyone who picked an option picked the same one; "
                              f"{', '.join(silent)} commented without picking")
        return "agreed", "everyone picked the same option"
    return "conflict", f"{len(distinct)} different options chosen"


def md_escape(t) -> str:
    return str(t or "").replace("|", "\\|").replace("\n", " ")


def write_report(path: str, spec: dict, items, by_item, states) -> None:
    people = sorted({w for a in by_item.values() for w in a})
    L = [f"# {spec.get('title','Review')} — what came back", ""]
    L.append(f"{len(people)} respondent{'' if len(people)==1 else 's'}: "
             + ", ".join(f"**{p}**" for p in people) if people else "No returns yet.")
    L.append("")

    counts = defaultdict(int)
    for s, _ in states.values():
        counts[s] += 1
    L += ["| state | count | what to do |", "|---|---|---|",
          f"| agreed | {counts['agreed']} | write the decision, close the question |",
          f"| conflict | {counts['conflict']} | goes to the next round as a tie-break |",
          f"| single | {counts['single']} | one voice only — decide if that is enough |",
          f"| silent | {counts['silent']} | nobody answered; carry forward or drop |", ""]

    for item in items:
        iid = item["id"]
        state, why = states[iid]
        L += [f"## {iid} — {item.get('title','')}", "",
              f"**{state}** — {why}", ""]
        if item.get("question"):
            L += [f"> {item['question']}", ""]
        ans = by_item.get(iid, {})
        if ans:
            L += ["| who | chose | said |", "|---|---|---|"]
            for who in sorted(ans):
                a = ans[who]
                L.append(f"| {md_escape(who)} | {md_escape(a['choice']) or '—'} "
                         f"| {md_escape(a['comment']) or '—'} |")
            L.append("")
        if item.get("origin"):
            L += [f"*Register item: `{item['origin']}`*", ""]
    open(path, "w", encoding="utf-8").write("\n".join(L))


def write_decisions(path: str, spec: dict, items, by_item, states) -> None:
    """Draft register entries for the agreed items.

    Deliberately drafts rather than finalises: each stub has a TODO for the effect,
    because 'what changes because of this' is the single most useful line in a
    register and the one a script cannot write. A register full of decisions with no
    stated effect is a list of opinions.
    """
    agreed = [i for i in items if states[i["id"]][0] in ("agreed", "single")]
    L = [f"# Draft decisions — {spec.get('title','Review')}", "",
         "Generated from the returned answers. **Edit before pasting into the register.**",
         "Each entry needs an *Effect* line saying what changes in the work; that is the",
         "part a reviewer will look for in six months and the part no script can supply.", ""]
    if not agreed:
        L.append("_Nothing reached agreement in this round._")
    for item in agreed:
        iid = item["id"]
        state, why = states[iid]
        ans = by_item.get(iid, {})
        chosen = next((a["choice"] for a in ans.values() if a.get("choice")), None)
        L += [f"### {item.get('origin') or iid} — {item.get('title','')}", ""]
        if chosen:
            L.append(f"**Decision:** {chosen}")
        else:
            L.append("**Decision:** _(answered in prose — read the comments and state it)_")
        L.append("")
        for who in sorted(ans):
            a = ans[who]
            bits = []
            if a.get("choice"):
                bits.append(f"chose *{a['choice']}*")
            if a.get("comment"):
                bits.append(f"“{a['comment']}”")
            if bits:
                L.append(f"- **{who}**: " + "; ".join(bits))
        L += ["",
              f"**Effect:** _TODO — what changes in the work because of this._",
              f"**Status:** Confirmed ({why}).",
              f"**Source:** `{spec.get('form_id','review')}` round {spec.get('round',1)}"
              + (f", form item `{iid}`" if item.get("origin") else ""), ""]
    open(path, "w", encoding="utf-8").write("\n".join(L))


def write_open(path: str, spec: dict, items, by_item, states) -> None:
    still = [i for i in items if states[i["id"]][0] in ("conflict", "silent")]
    L = [f"# Still open — {spec.get('title','Review')}", "",
         "Carried out of this round. A conflict is not a failure of the form: it is the",
         "form doing its job, having found a real disagreement early enough to settle.", ""]
    if not still:
        L.append("_Nothing left open._")
    for item in still:
        iid = item["id"]
        state, why = states[iid]
        L += [f"### {item.get('origin') or iid} — {item.get('title','')}", "",
              f"**{state}** — {why}", ""]
        for who, a in sorted(by_item.get(iid, {}).items()):
            frag = a.get("choice") or ""
            if a.get("comment"):
                frag = (frag + ": " if frag else "") + f"“{a['comment']}”"
            L.append(f"- **{who}**: {frag}")
        if state == "silent":
            L.append("- _nobody answered — decide whether to re-ask or drop it_")
        L.append("")
    open(path, "w", encoding="utf-8").write("\n".join(L))


def write_round2(path: str, spec: dict, items, by_item, states) -> None:
    """A next-round spec, pre-populated with the conflicts and both positions.

    Quotes are copied verbatim from the returned files, which is what makes the
    next round honest: each person sees exactly what the other actually wrote,
    not a paraphrase that has drifted toward whoever wrote the summary.
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        print("  (PyYAML not installed — skipping round2.yaml)", file=sys.stderr)
        return

    conflicts = [i for i in items if states[i["id"]][0] == "conflict"]
    if not conflicts:
        print("  no conflicts — no next round needed")
        return

    rnd = int(spec.get("round", 1)) + 1
    prefix = (spec.get("id_prefix") or "Q-").rstrip("-")
    new_prefix = f"{prefix}R{rnd}-"

    out_items = []
    for n, item in enumerate(conflicts, 1):
        positions = {}
        for who, a in sorted(by_item.get(item["id"], {}).items()):
            frag = a.get("comment") or a.get("choice") or ""
            if a.get("choice") and a.get("comment"):
                frag = f"chose <i>{a['choice']}</i> — “{a['comment']}”"
            elif a.get("comment"):
                frag = f"“{a['comment']}”"
            positions[who] = frag
        out_items.append({
            "id": f"{new_prefix}{n:02d}",
            "origin": item.get("origin") or item["id"],
            "type": "tie-break",
            "title": item.get("title", ""),
            "question": item.get("question", ""),
            "positions": positions,
            "recommendation": "TODO — say what you would do and why. A tie-break with no "
                              "recommendation asks two busy people to negotiate; one with a "
                              "recommendation asks them to agree or object, which is faster.",
            "options": item.get("options", []),
            "background": item.get("background", ""),
            "cost": item.get("cost", ""),
        })

    nxt = {
        "title": f"{spec.get('title','Review')} — round {rnd}",
        "form_id": f"{spec.get('form_id','review')}-r{rnd}",
        "round": rnd,
        "storage_key": f"{spec.get('form_id','review')}-r{rnd}",
        "kicker": f"Round {rnd} · {len(out_items)} tie-break"
                  f"{'' if len(out_items)==1 else 's'}",
        "id_prefix": new_prefix,
        "reserved_prefixes": (spec.get("reserved_prefixes") or [])
                             + [spec.get("id_prefix", "")],
        "intro": "TODO — one paragraph. Say that this is short, that it is only the places "
                 "where you answered differently, and that everything else is settled.",
        "sections": [{
            "title": f"1 · Where you landed differently — {len(out_items)} tie-break"
                     f"{'' if len(out_items)==1 else 's'}",
            "note": "Each card quotes both of you verbatim. Pick an option or say you are "
                    "happy to go with the other view.",
            "items": out_items,
        }],
    }
    nxt["reserved_prefixes"] = [p for p in nxt["reserved_prefixes"] if p]
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(nxt, fh, sort_keys=False, allow_unicode=True, width=92)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("returns", nargs="+", help="returned JSON files (globs are fine)")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    items = all_items(spec)
    returns = load_returns(args.returns)
    if not returns:
        sys.exit("no readable answer files")

    by_item = collate(spec, returns)

    unknown = set(by_item) - {i["id"] for i in items}
    if unknown:
        # An answer for an item this spec does not contain means the reviewer filled
        # in a different version of the form. Stop: silently ignoring it loses a real
        # answer, and silently accepting it files it against nothing.
        sys.exit(f"answers reference items not in this spec: {sorted(unknown)}\n"
                 f"the reviewer may have used an older build — check before proceeding")

    states = {i["id"]: classify(i, by_item.get(i["id"], {})) for i in items}

    os.makedirs(args.out_dir, exist_ok=True)
    p = lambda n: os.path.join(args.out_dir, n)  # noqa: E731
    write_report(p("report.md"), spec, items, by_item, states)
    write_decisions(p("decisions.md"), spec, items, by_item, states)
    write_open(p("open.md"), spec, items, by_item, states)
    write_round2(p("round2.yaml"), spec, items, by_item, states)

    counts = defaultdict(int)
    for s, _ in states.values():
        counts[s] += 1
    who = ", ".join(sorted({r.get("respondent") or "(unnamed)" for r in returns}))
    print(f"read {len(returns)} return(s) from {who}")
    print(f"  agreed {counts['agreed']} · conflict {counts['conflict']} · "
          f"single {counts['single']} · silent {counts['silent']}")
    print(f"  wrote report.md, decisions.md, open.md"
          + (", round2.yaml" if counts["conflict"] else "") + f" in {args.out_dir}/")


if __name__ == "__main__":
    main()
