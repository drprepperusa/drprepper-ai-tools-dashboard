# DR Prepper AI Tools Ops Dashboard

A living reference dashboard for AI/design/ops tools shared in chat, categorized by business use case and source post.

- Live site: https://drprepperusa.github.io/drprepper-ai-tools-dashboard/
- Source of truth: `data/tools.json`
- Static output: `index.html`

## Local update workflow

```bash
# Add/modify entries in data/tools.json, then render:
scripts/render_dashboard.py
scripts/render_dashboard.py --check

git add data/tools.json index.html templates/index.template.html scripts/*.py README.md
git commit -m "chore: update tools dashboard"
git push
```

## Candidate merge workflow

Create a JSON array of candidate entries using the same fields as `data/tools.json`, then run:

```bash
scripts/add_tools.py /path/to/candidates.json
scripts/render_dashboard.py
```

Required fields:

- `name`
- `category`
- `priority` — `High`, `Medium`, `Watch`, or `Lead`
- `summary`
- `drprepper`
- `aluma`
- `next`
- `toolUrl`
- `postUrl`

## Automation

A Hermes scheduled job searches recent assistant sessions for new tool/resource links, adds only business-relevant candidates, renders the dashboard, commits, pushes, and reports whether anything changed.

Limitation: Hermes can only analyze links that were sent to/handled by the assistant and stored in session history. It cannot read arbitrary Discord channel history unless a Discord-specific history API/tool is later connected.
