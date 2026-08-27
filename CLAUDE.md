# Releasing this skill to the DCRI marketplace

This directory is the **working copy**: develop, run evals, and commit here.
Nobody installs from it. Users install from the DCRI skills marketplace on the
share, which is published from Sage's Azure DevOps repo:

    https://dev.azure.com/DUKE-DCRI/AI%20Testing/_git/dcri-claude-skills

Local clone of that repo: `~/AI-work/dcri-claude-skills` (branches `dev` and
`main` tracked; `az` CLI is logged in). Marketplace memory and rules:
`~/AI-work/dcri-claude-skills/CONTRIBUTING.md` and `benchmarks/README.md`.

## Workspace

Eval runs, fixtures, review pages and benchmark evidence live in
`~/AI-work/decision-review-kit-workspace/`. That is the skill-creator workspace: nothing in it ships, and nothing
should be parked on the share under `/dcri/shared_code/code_repository/archive/`
— that folder was emptied into these workspaces on 2026-08-26. Copy a
`review.html` to the share only when someone without home-directory access
needs to open it, and treat the copy as disposable.

## Where this repo's files land in the marketplace repo

| Here | Marketplace repo |
|---|---|
| `SKILL.md`, `references/`, `scripts/`, `assets/`, `examples/`, `README.md`, `LICENSE` | `plugins/dcri-global/skills/decision-review-kit/` |
| `evals/` | `benchmarks/dcri-global/decision-review-kit/evals/` |

This skill ships inside the `dcri-global` plugin alongside `task-folders` and `cc-coach`;
there is no plugin.json here — `plugins/dcri-global/.claude-plugin/plugin.json` belongs to the marketplace repo.

Evidence (evals, benchmarks, docs) sits **beside** the plugin under
`benchmarks/`; it is screened and reviewed with the PR but never published to
the share. Never copy workspaces (`*-workspace/`), `.git`, venvs, or anything
listed under "never ships" above.

## The release path — three steps, two of them yours to run

### 1. PR into `dev` (Claude runs this)

```bash
cd ~/AI-work/dcri-claude-skills
git checkout dev && git pull --ff-only origin dev
git checkout -b feature/<skill>-<what-changed>
# copy the files per the table above (cp / rsync; keep the destination layout)
bash scripts/screen-skill.sh plugins/<plugin>      # must PASS; read every warning
bash scripts/screen-skill.sh benchmarks/<plugin>   # same
git add -A && git commit -m "<skill>: <what and why>"
git push -u origin feature/<skill>-<what-changed>
az repos pr create --repository dcri-claude-skills \
  --source-branch feature/<skill>-<what-changed> --target-branch dev \
  --title "<skill>: <what changed>" --description "<what, why, evidence, screen result>"
```

Screen rules that bite: no `version` field in `plugin.json` (the publish step
stamps one); credential-shaped strings hard-fail (`\bPAT\b` is
case-insensitive, so a variable named `pat` fails); absolute paths and the
word "patient" warn — reword or explain the warning in the PR description.
The pipeline also runs an advisory AI review that posts a comment; real
findings get fixed in a follow-up commit on the same branch, false positives
get explained in the PR.

Branch policy on `dev` needs approval from a reviewer who is not the author
(Sage or Dylan). Once approved, Claude completes it:

```bash
az repos pr update --id <PR> --status completed --delete-source-branch true
```

(The `az` output prints the pre-update state; verify with
`git fetch && git log origin/dev -1`, not the table.)

### 2. Promote `dev` → `main` (Claude cuts it, **Dylan completes it**)

```bash
cd ~/AI-work/dcri-claude-skills
bash scripts/promote.sh          # cuts promote/<date-time>, flips marketplace
                                 # names back to dcri-skills / dcri-skills-restricted, pushes
az repos pr create --repository dcri-claude-skills \
  --source-branch promote/<date-time> --target-branch main \
  --title "Promote dev → main: <what>" --description "<PRs included, screen result>"
```

Claude cannot complete a PR into `main` — the auto-mode classifier blocks it.
**Dylan approves and completes the promotion PR in the browser**, then tells
Claude it is merged.

### 3. Publish to the share (Claude runs this after the merge)

```bash
cd ~/AI-work/dcri-claude-skills
git checkout main && git pull --ff-only origin main
DCRI_SHARE_ROOT=/dcri/shared_code/AI bash scripts/publish-to-share.sh
```

This exports only `.claude-plugin/`, `plugins/`, `README.md` to
`/dcri/shared_code/AI/marketplace` (and `restricted/marketplace`), stamping a
version of the form `YYYY.MDD.MINUTE-OF-DAY` (e.g. `2026.826.1255`) into each
exported `plugin.json` and `PUBLISHED.txt`. Every publish bumps the version,
even a docs-only one.

Verify from the install side:

```bash
claude plugin marketplace update dcri-skills
claude plugin update dcri-global@dcri-skills   # should report old → new version
```

Users refresh the same way (`/plugin marketplace update dcri-skills`, then
`/plugin update dcri-global@dcri-skills`).

## Before opening a PR

- Commit here first; the marketplace copy is derived from this repo, never
  the other way round.
- Run the evals (skill-creator loop) when SKILL.md or references changed, and
  put the new iteration's `benchmark.md`/`.json` + analyst notes beside the
  plugin in `benchmarks/`.
- Do not bump a version anywhere; the publish step owns it.
- Do not edit `main` directly; it only moves via promotion PRs.
