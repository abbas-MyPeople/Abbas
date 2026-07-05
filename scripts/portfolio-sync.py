#!/usr/bin/env python3
"""
portfolio-sync — refresh the live GIT facts in command/portfolio.json for BOTH repos.

Pulls ahead/behind vs main, last-commit date, and open-PR count for each project's branch via `gh api`,
and stamps meta.last_git_sync. The CURATED fields (role, stage, %, components, blockers, overlaps,
manual_steps, next) are the AI audit and are left untouched here — re-run the AI portfolio audit to refresh
those. Resilient: any lookup that fails keeps the existing value.

Run in the AZ repo's Action. Needs a token with READ access to BOTH repos (set GH_TOKEN to a fine-grained
PAT `PORTFOLIO_PAT`); with only the default GITHUB_TOKEN, the Wok repo's facts won't refresh.
"""
import json, subprocess, datetime, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PJSON = ROOT / "command" / "portfolio.json"
SLUG = {"wok": "abbas-MyPeople/WokAndKarahiTexas.com", "az": "abbas-MyPeople/Abbas"}


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    return (r.stdout.strip() if r.returncode == 0 else None)


def refresh(p):
    slug = SLUG.get(p.get("repo"))
    branch = p.get("branch") or "main"
    if not slug:
        return
    g = p.setdefault("git", {})
    # ahead/behind vs main
    if branch != "main":
        cmp = gh("api", f"repos/{slug}/compare/main...{branch}", "--jq", "{a:.ahead_by,b:.behind_by}")
        if cmp:
            try:
                d = json.loads(cmp); g["ahead"] = d["a"]; g["behind"] = d["b"]
            except Exception:
                pass
    else:
        g["ahead"] = 0; g["behind"] = 0
    # last commit date
    dt = gh("api", f"repos/{slug}/commits/{branch}", "--jq", ".commit.committer.date")
    if dt:
        g["last_commit"] = dt[:10]
    # open PRs from this branch
    prs = gh("pr", "list", "--repo", slug, "--state", "open", "--head", branch, "--json", "number")
    if prs is not None:
        try:
            g["open_prs"] = len(json.loads(prs))
        except Exception:
            pass


def main():
    data = json.loads(PJSON.read_text())
    for p in data["projects"]:
        try:
            refresh(p)
        except Exception as e:  # never let one project break the sync
            print(f"skip {p.get('id')}: {e}")
    data["meta"]["last_git_sync"] = datetime.date.today().isoformat()
    PJSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"portfolio-sync: refreshed {len(data['projects'])} projects · {data['meta']['last_git_sync']}")


if __name__ == "__main__":
    main()
