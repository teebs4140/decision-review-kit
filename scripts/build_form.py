#!/usr/bin/env python3
"""Turn a decision spec into a self-contained review page.

    python scripts/build_form.py spec.yaml -o review.html

The output is one HTML file with no external requests: a reviewer can open it from
an email attachment on a plane. Answers save to localStorage as they type, and an
Export button downloads a JSON file they mail back.

Why a script rather than writing the markup each time: the browser behaviour here is
small but unforgiving. Radio values need CSS.escape before they can be looked up,
duplicate copies of a question have to stay in step, the blob URL has to be revoked,
and the respondent's name has to be required *before* the download rather than after.
Get one of those wrong and a reviewer loses an afternoon's work without either of you
finding out until they mention it. That is not a good thing to re-derive under time
pressure, so it lives here and is tested.

The interesting judgement -- which decisions are worth a reviewer's attention, and how
to phrase them so they read as decisions rather than as exposition -- is not automated
and should not be. See references/writing-questions.md.

Spec format: see references/schema.md. YAML if PyYAML is installed, otherwise JSON.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_THEME = os.path.join(ROOT, "assets", "theme.css")

# Prefixes that are reserved for the *source* registers a project already keeps
# (decision logs, issue trackers). See check_ids() for why this matters.
DEFAULT_ID_PATTERN = r"^[A-Z][A-Z0-9]*-\d+$"


# --------------------------------------------------------------------------
# spec loading
# --------------------------------------------------------------------------
def load_spec(path: str) -> dict:
    text = open(path, encoding="utf-8").read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError:
            sys.exit("PyYAML not installed — either `pip install pyyaml` or use a .json spec")
        return yaml.safe_load(text)
    return json.loads(text)


# --------------------------------------------------------------------------
# guards
#
# Each of these exists because the failure it prevents actually happened, and each
# was expensive in a way that is invisible until it is far too late to fix.
# --------------------------------------------------------------------------
def check_ids(spec: dict) -> list[str]:
    """IDs must be unique, well-formed, and must not collide with the source register.

    The expensive version of this mistake: a form numbers its items with labels the
    project's own register already uses for different questions. Nothing looks wrong
    until the answers come back, at which point reviewers' judgements are filed
    against the wrong items and the returned file carries no way to tell which
    meaning was intended. It is unrecoverable without going back and asking again,
    which is the one thing the whole exercise is trying to avoid.

    So the form gets its own namespace -- a prefix that cannot appear in the source
    register -- and each item carries `origin` pointing back at the real register
    item. The reviewer never sees `origin`; it is bookkeeping for whoever processes
    the answers.
    """
    problems = []
    items = all_items(spec)
    ids = [i["id"] for i in items]

    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append(f"duplicate ids: {dupes}")

    prefix = spec.get("id_prefix")
    if prefix:
        wrong = [i for i in ids if not i.startswith(prefix)]
        if wrong:
            problems.append(
                f"ids must start with the form's own prefix {prefix!r} so they cannot be "
                f"confused with the source register: {wrong}")

    reserved = spec.get("reserved_prefixes") or []
    for r in reserved:
        clash = [i for i in ids if i.startswith(r)]
        if clash:
            problems.append(
                f"ids collide with reserved register prefix {r!r}: {clash} — "
                f"answers would be filed against the wrong item")
    return problems


def _norm(t: str) -> str:
    """Fold quotes/dashes and strip punctuation so a quote matches its source."""
    t = unicodedata.normalize("NFKC", t)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'),
                 ("”", '"'), ("–", "-"), ("—", "-")):
        t = t.replace(a, b)
    t = re.sub(r"[^a-z0-9]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def check_quotes(spec: dict, sources_dir: str | None) -> tuple[list, list]:
    """Every quoted span attributed to a person must appear in something they sent.

    A quote that is not in any archived source is either a transcription slip or a
    quote from a different channel (someone answered half the questions by email).
    Either way it should be surfaced, because to the person who filled in the form,
    an unlabelled quote from outside it reads as words they never wrote — and they
    will say so, in front of everyone, and be right.

    Returns (unfound, unexplained). Anything in `known_offsource` is expected: give
    a reason there and it moves from unexplained to merely unfound.
    """
    if not sources_dir or not os.path.isdir(sources_dir):
        return [], []

    corpus = ""
    for name in sorted(os.listdir(sources_dir)):
        p = os.path.join(sources_dir, name)
        if not os.path.isfile(p):
            continue
        if name.endswith(".json"):
            try:
                corpus += json.dumps(json.load(open(p, encoding="utf-8")), ensure_ascii=False)
            except Exception:
                corpus += open(p, encoding="utf-8", errors="replace").read()
        elif name.endswith((".txt", ".md")):
            corpus += open(p, encoding="utf-8", errors="replace").read()
    corpus = _norm(corpus)

    known = spec.get("known_offsource") or {}
    unfound = []
    for item in all_items(spec):
        fields = [v for k, v in item.items()
                  if k in ("positions", "background", "context") or k.startswith("said")]
        texts = []
        for f in fields:
            if isinstance(f, dict):
                texts += [str(v) for v in f.values()]
            elif isinstance(f, list):
                texts += [str(v) for v in f]
            elif f:
                texts.append(str(f))
        for text in texts:
            for span in re.findall(r"[“\"](.+?)[”\"]", text, flags=re.S):
                # check the longest ellipsis-free run; short runs match by chance
                for run in re.split(r"…|\.\.\.", span):
                    n = _norm(run)
                    if len(n) > 40 and n[:80] not in corpus:
                        unfound.append((item["id"], n[:70]))
    unexplained = [(i, f) for i, f in unfound if not any(k in f for k in known)]
    return unfound, unexplained


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def all_items(spec: dict) -> list[dict]:
    """Every item that carries an answer widget, in document order."""
    out = []
    for section in spec.get("sections", []):
        if section.get("kind") in ("reference", "settled"):
            continue
        out += section.get("items", [])
    return out


def esc(t) -> str:
    return html.escape(str(t if t is not None else ""))


def rich(t) -> str:
    """Spec text may carry a little inline HTML (<b>, <i>, <code>). Trust it.

    The spec is authored by whoever runs this, not by a reviewer, so this is not an
    injection surface — and forbidding emphasis makes for worse questions.
    """
    return str(t if t is not None else "")


def widget(item: dict) -> str:
    iid = esc(item["id"])
    opts = item.get("options") or []
    chips = "".join(
        f'<label class="chip"><input type="radio" name="v-{iid}" '
        f'value="{html.escape(str(o), quote=True)}"><span>{esc(o)}</span></label>'
        for o in opts)
    chips = f'<div class="chips">{chips}</div>' if chips else ""
    placeholder = esc(item.get("placeholder")
                      or ("Anything to add?" if opts else "Your answer"))
    return (f'<div class="fb" data-id="{iid}" data-kind="{esc(item.get("type","open"))}" '
            f'data-title="{html.escape(str(item.get("title","")), quote=True)}">'
            f'{chips}<textarea rows="2" data-fb="{iid}" placeholder="{placeholder}"></textarea></div>')


def render_item(item: dict) -> str:
    iid = esc(item["id"])
    parts = [f'<div class="entry needs" id="c-{iid}">',
             f'<div class="ehead"><span class="rid">{iid}</span>',
             f'<h4>{esc(item.get("title",""))}</h4>',
             '<span class="tag tag-needs">needs your call</span></div>']

    if item.get("question"):
        parts.append(f'<p class="qline">{rich(item["question"])}</p>')

    # Positions: what each person already said, side by side. Seeing the other view
    # is what lets someone concede in one line instead of restating their own.
    pos = item.get("positions") or {}
    if pos:
        sides = "".join(f'<div class="side"><span>{esc(k)}</span>{rich(v)}</div>'
                        for k, v in pos.items())
        parts.append(f'<div class="two">{sides}</div>')

    if item.get("skip_if"):
        parts.append('<p class="depends"><span>Before you answer</span>'
                     f'{rich(item["skip_if"])}</p>')

    if item.get("recommendation"):
        parts.append('<p class="ask"><span>What we suggest</span>'
                     f'{rich(item["recommendation"])}</p>')

    parts.append(widget(item))

    # Everything that is reasoning rather than decision goes behind a fold. A reviewer
    # who trusts you never opens it; one who does not can audit every number. Both are
    # served, and the page still reads as a short list of questions.
    fold = []
    if item.get("background"):
        fold.append(f'<p class="plain">{rich(item["background"])}</p>')
    if item.get("cost"):
        fold.append(f'<p class="now"><span>What it costs</span>{rich(item["cost"])}</p>')
    if item.get("table"):
        fold.append(render_table(item["table"]))
    if fold:
        parts.append('<details class="more"><summary>Why it matters, and what we measured'
                     f'</summary>{"".join(fold)}</details>')

    parts.append("</div>")
    return "".join(parts)


def render_table(t: dict) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in t.get("columns", []))
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
                   for row in t.get("rows", []))
    return f'<div class="tbl"><table><tr>{head}</tr>{body}</table></div>'


def render_reference(item: dict) -> str:
    """A settled or informational card: on the page for the record, not to be answered."""
    parts = ['<div class="entry settled tight"><div class="ehead">']
    if item.get("id"):
        parts.append(f'<span class="rid">{esc(item["id"])}</span>')
    parts.append(f'<h4>{esc(item.get("title",""))}</h4>'
                 '<span class="tag tag-settled">settled</span></div>')
    detail = []
    if item.get("positions"):
        detail.append("".join(f'<p class="plain"><b>{esc(k)}:</b> {rich(v)}</p>'
                              for k, v in item["positions"].items()))
    if item.get("background"):
        detail.append(f'<p class="plain">{rich(item["background"])}</p>')
    if item.get("effect"):
        detail.append(f'<p class="now"><span>What changes</span>{rich(item["effect"])}</p>')
    if item.get("table"):
        detail.append(render_table(item["table"]))
    if detail:
        parts.append('<details class="more"><summary>What was decided, and what changes'
                     f'</summary>{"".join(detail)}</details>')
    parts.append("</div>")
    return "".join(parts)


JS = r"""
const KEY=%(key)s;
let A={}; try{A=JSON.parse(localStorage.getItem(KEY)||'{}');}catch(e){}
const boxes=[...document.querySelectorAll('.fb[data-id]')];
const ids=[...new Set(boxes.map(b=>b.dataset.id))];
function save(){try{localStorage.setItem(KEY,JSON.stringify(A));}catch(e){}}
function done(id){const a=A[id]||{};return !!(a.choice||(a.comment||'').trim());}
function refresh(){
 boxes.forEach(b=>b.closest('.entry').classList.toggle('answered',done(b.dataset.id)));
 const n=ids.filter(done).length;
 document.getElementById('count').textContent=n;
 const btn=document.getElementById('exportBtn');
 btn.title=n+' of '+ids.length+' answered';
 const bar=document.getElementById('progress');
 if(bar)bar.style.width=(ids.length?100*n/ids.length:0)+'%%';
}
/* paint back whatever was saved earlier, so a reload loses nothing */
boxes.forEach(b=>{const a=A[b.dataset.id]||{};
 const t=b.querySelector('textarea'); if(a.comment)t.value=a.comment;
 if(a.choice){
   /* values are free text, so they must be escaped before use as a selector */
   const sel='input[value="'+(window.CSS&&CSS.escape?CSS.escape(a.choice):a.choice)+'"]';
   const r=b.querySelector(sel); if(r)r.checked=true;}});
refresh();
document.addEventListener('input',e=>{const t=e.target.closest('textarea[data-fb]');if(!t)return;
 const id=t.dataset.fb;
 A[id]=Object.assign({},A[id],{comment:t.value});
 /* the same item can appear in more than one place; keep every copy in step */
 document.querySelectorAll('textarea[data-fb="'+id+'"]').forEach(o=>{if(o!==t)o.value=t.value;});
 save();refresh();});
document.addEventListener('change',e=>{const r=e.target.closest('.chip input');if(!r)return;
 const id=r.name.slice(2);
 A[id]=Object.assign({},A[id],{choice:r.value});
 document.querySelectorAll('input[name="'+r.name+'"]').forEach(o=>{o.checked=(o.value===r.value);});
 save();refresh();});
const who=document.getElementById('who');
who.value=A.__who||''; who.addEventListener('input',()=>{A.__who=who.value;save();});
function toast(m){let t=document.querySelector('.toast');
 if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t);}
 t.textContent=m;requestAnimationFrame(()=>t.classList.add('on'));
 clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('on'),3600);}
document.getElementById('exportBtn').onclick=()=>{
 const out=[];
 ids.forEach(id=>{if(!done(id))return;
  const b=document.querySelector('.fb[data-id="'+id+'"]');const a=A[id];
  out.push({id:id,type:b.dataset.kind,title:b.dataset.title,
            choice:a.choice||null,comment:(a.comment||'').trim()||null});});
 if(!out.length){toast('Nothing to export yet — answer something first.');return;}
 const name=(who.value||'').trim();
 /* Ask for the name BEFORE the download, not after. An anonymous file that arrives
    in a thread with three reviewers cannot be attributed after the fact. */
 if(!name){toast('Add your name at the top first — we need to know whose answers these are.');
  who.focus();who.scrollIntoView({behavior:'smooth',block:'center'});return;}
 const payload={form:%(form)s,round:%(round)s,respondent:name,
   exported:new Date().toISOString(),answered:out.length,total:ids.length,responses:out};
 const slug=name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40);
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);
 a.download=%(form)s+'-'+slug+'-'+new Date().toISOString().slice(0,10)+'.json';
 document.body.appendChild(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(a.href),1000);
 toast('Downloaded '+out.length+' answer'+(out.length===1?'':'s')+' — email the file back.');};
addEventListener('beforeunload',save);
"""


def render(spec: dict, theme: str) -> str:
    n_ask = len(all_items(spec))
    body = []

    for section in spec.get("sections", []):
        kind = section.get("kind", "questions")
        title = esc(section.get("title", ""))
        note = rich(section.get("note", ""))
        items = section.get("items", [])

        if kind in ("reference", "settled"):
            cards = "".join(render_reference(i) for i in items)
            summary = esc(section.get("summary")
                          or f"{len(items)} items — open only if you want to check "
                             f"nothing was recorded wrongly")
            body.append(
                f'<section class="part ref"><h2>{title}</h2>'
                f'<details class="fold"><summary>{summary}</summary>'
                + (f'<p class="note">{note}</p>' if note else "")
                + f'{cards}</details></section>')
        else:
            cards = "".join(render_item(i) for i in items)
            body.append(
                f'<section class="part"><h2>{title}</h2>'
                + (f'<p class="note">{note}</p>' if note else "")
                + f'{cards}</section>')

    if any(s.get("kind") in ("reference", "settled") for s in spec.get("sections", [])):
        # a visible line between "your homework" and "the record"
        marker = '<p class="divider">That is everything we need. The rest is reference.</p>'
        first_ref = next(i for i, b in enumerate(body) if 'class="part ref"' in b)
        body.insert(first_ref, marker)

    js = JS % dict(key=json.dumps(spec.get("storage_key", "drk-answers")),
                   form=json.dumps(spec.get("form_id", "review")),
                   round=json.dumps(spec.get("round", 1)))

    minutes = spec.get("minutes") or max(5, 3 * n_ask)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(spec.get('title','Review'))}</title>
<style>{theme}</style></head>
<body><div id="progresswrap"><div id="progress"></div></div>
<main>
<header class="mast">
  <p class="kicker">{esc(spec.get('kicker',''))}</p>
  <h1>{n_ask} question{"" if n_ask == 1 else "s"},<br>about {minutes} minutes</h1>
  {f'<p>{rich(spec["intro"])}</p>' if spec.get("intro") else ""}
  <p class="hint">Answers save as you type, so closing the tab loses nothing.
  <b>Export answers</b> downloads one file to email back. If you are happy to go with
  someone else's view on something, say so and we will close it.</p>
  <label class="who">Your name
    <input id="who" type="text" placeholder="so we know whose answers these are" autocomplete="name">
  </label>
</header>
<div class="tools">
  <button id="exportBtn" class="primary">Export answers <span id="count">0</span></button>
</div>
{''.join(body)}
{f'<footer>{rich(spec["footer"])}</footer>' if spec.get("footer") else ""}
</main>
<script>{js}</script></body></html>"""


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", default="review.html")
    ap.add_argument("--theme", default=DEFAULT_THEME,
                    help="CSS file to inline (swap this to rebrand)")
    ap.add_argument("--sources", default=None,
                    help="directory of archived reviewer replies; quotes are checked against it")
    ap.add_argument("--no-guards", action="store_true",
                    help="skip the id/quote checks (for drafting only — never for a form you send)")
    args = ap.parse_args()

    spec = load_spec(args.spec)

    if not args.no_guards:
        problems = check_ids(spec)
        if problems:
            sys.exit("ID problems — answers would be filed wrongly:\n  "
                     + "\n  ".join(problems))
        sources = args.sources or spec.get("sources_dir")
        if sources and not os.path.isabs(sources):
            sources = os.path.join(os.path.dirname(os.path.abspath(args.spec)), sources)
        unfound, unexplained = check_quotes(spec, sources)
        if unexplained:
            sys.exit(
                "UNSOURCED QUOTE — appears in no archived reply and is not listed under\n"
                "known_offsource. Label its source or fix the wording:\n  "
                + "\n  ".join(f"{i}: “{f}…”" for i, f in unexplained))
        if unfound:
            print(f"quote provenance: {len(unfound)} off-source quote(s), all accounted for")

    theme = open(args.theme, encoding="utf-8").read() if os.path.exists(args.theme) else ""
    page = render(spec, theme)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(page)

    n = len(all_items(spec))
    ref = sum(len(s.get("items", [])) for s in spec.get("sections", [])
              if s.get("kind") in ("reference", "settled"))
    print(f"wrote {args.out}  ({len(page)/1024:.0f} KB)")
    print(f"  {n} question{'' if n == 1 else 's'} to answer · {ref} for the record")


if __name__ == "__main__":
    main()
