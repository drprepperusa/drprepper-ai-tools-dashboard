# Hermes cron prompt: DR Prepper AI Tools Dashboard Auto-Update

You are maintaining the public dashboard at:
https://drprepperusa.github.io/drprepper-ai-tools-dashboard/

Repo/workdir:
/Users/djmac/projects/drprepper-ai-tools-dashboard

Goal:
Find new AI/design/ops/business-tool links that DJ sent to or discussed with the assistant since the last dashboard update, decide whether they belong in the dashboard, update `data/tools.json`, render `index.html`, commit, push, and report concisely.

Rules:
1. Do not ask questions. This job runs unattended.
2. Use LA time in the final report.
3. Only add concrete tools, source posts, repos, workflows, or lead-source signals with business relevance to DR Prepper, PrepShip/client portal, KF Goodies, Aluma, sales/outreach, fulfillment, dashboards, or internal automation.
4. Do NOT add generic commentary, duplicate links, one-off jokes, or links without a usable business takeaway.
5. Every new entry must include a source link in `postUrl` and the actual tool/site/repo link in `toolUrl` when different. If only the post is known, use the post URL for both fields.
6. Keep summaries practical and non-hypey. Tie `drprepper`, `aluma`, and `next` to operations.
7. If a link cannot be verified, either skip it or mark the next action as verification needed. Do not invent details.
8. Never include credentials, tokens, private customer info, or secrets.

Discovery approach:
- Search recent sessions with session_search for likely tool/link terms, sorted newest. Use multiple focused queries if needed:
  - `x.com OR twitter.com OR threads.com OR reddit.com OR github.com OR producthunt.com OR "AI tool" OR "MCP" OR "Claude" OR "dashboard"`
  - `MotionSites OR Higgsfield OR "ui-skills" OR "claude-directory" OR "Claude Mythos" OR "landing page"`
  - `DR Prepper operations tool OR Aluma lead gen OR 3PL tool OR fulfillment automation`
- Compare candidates against existing `data/tools.json` before adding.
- Prefer links from DJ/user messages and assistant-analyzed links over broad web discovery.

Update workflow:
1. `cd /Users/djmac/projects/drprepper-ai-tools-dashboard`
2. `git pull --ff-only origin main`
3. Read `data/tools.json`.
4. Create `/tmp/drprepper-tools-candidates.json` containing only new/updated entries that meet the rules.
5. If candidates exist:
   - `scripts/add_tools.py /tmp/drprepper-tools-candidates.json`
   - `scripts/render_dashboard.py`
   - `python3 -m json.tool data/tools.json >/dev/null`
   - `python3 -m py_compile scripts/render_dashboard.py scripts/add_tools.py`
   - `scripts/render_dashboard.py --check`
   - `git add data/tools.json index.html README.md scripts templates`
   - `git commit -m "chore: update AI tools dashboard"`
   - `git push`
6. If no candidates exist, do not commit.
7. Verify the public URL with curl if a commit was pushed.

Final report format:
- `Updated: <yes/no>`
- `Entries added/updated: <number>`
- `Live dashboard: https://drprepperusa.github.io/drprepper-ai-tools-dashboard/`
- Bullets for new items, if any.
- If no changes: one sentence saying no new qualifying tool links were found in recent assistant-handled sessions.
