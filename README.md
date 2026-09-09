# Monorepo Consolidator

**B2 Stealthy Solutions** — consolidate scattered GitHub repos into one governed monorepo with git subtrees, then layer lint/SAST/Dependabot via GitHub Actions.

## Pricing

| Tier | Price | What you get |
|------|-------|----------------|
| **Free (self-hosted)** | $0 | This repo: aggregator script + Actions templates + docs. You run it with your own GitHub token. |
| **Hosted** | $9/mo | We run discovery + consolidation for you (coming next — Polar checkout). |
| **Team + API** | $99/mo | Seats, API, team workflows (only after auth/metering are real — not fake SaaS). |

Polar is the intended merchant of record for paid tiers. Free tier never collects cards.

## Quick start (Free)

See [QUICKSTART.md](./QUICKSTART.md) and [MONOREPO_SETUP_GUIDE.md](./MONOREPO_SETUP_GUIDE.md).

```bash
export GITHUB_TOKEN=ghp_xxxx   # repo, workflow, read:org
pip install PyGithub==2.1.1 requests==2.31.0
python github_monorepo_aggregator.py --tag claude-generated
```

## What’s included

- `github_monorepo_aggregator.py` — discover repos by tag/prefix, subtree into a monorepo
- `.github/workflows/auto-fix.yml` — lint/format + security-oriented CI
- Docs for branch protection and Dependabot

## Honest limits

- Needs a GitHub PAT with repo access — treat tokens like secrets; rotate every 90 days
- Git subtree consolidation can be slow/large; start with a small tag/prefix filter
- Hosted/$99 tiers are **not** live until Polar products + a real hosted runner exist
- Not a Bazel/Nx replacement — this is **repo consolidation + governance scaffolding**

## Support

support@b2stealthysolutions.com

© B2 Stealthy Solutions
