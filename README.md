# Monorepo Consolidator

**B2 Stealthy Solutions**

Turn a pile of related GitHub repositories into one governed monorepo — discover by tag or prefix, absorb with git subtrees, then add lint, SAST, and Dependabot scaffolding.

Not a build-system product (Bazel / Nx / Turborepo). This is **consolidation + governance setup**.

---

## Pricing

| Tier | Price | Status | What you get |
|------|-------|--------|----------------|
| **Free · self-hosted** | $0 | **Live** | This package. You run the aggregator with your own GitHub token. |
| **Hosted** | $9 / month | Coming | We run discovery and consolidation for you. Polar checkout when ready. |
| **Team + API** | $99 / month | Planned | Seats and API after auth and metering are real. No fake SaaS. |

Paid tiers will use **Polar** as merchant of record. The free tier never collects card numbers.

---

## What’s in the box

| Path | Purpose |
|------|---------|
| `github_monorepo_aggregator.py` | Discover repos and consolidate with git subtrees |
| `templates/github-actions/auto-fix.yml` | Lint / format / security-oriented CI template |
| `templates/github-actions/dependabot.yml` | Weekly Dependabot config template |
| `QUICKSTART.md` | Five-minute path |
| `MONOREPO_SETUP_GUIDE.md` | Full setup, tokens, branch protection |

---

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxxx   # scopes: repo, workflow, read:org — rotate every 90 days
python github_monorepo_aggregator.py --help
```

Copy CI templates into your new monorepo:

```bash
mkdir -p .github/workflows
cp templates/github-actions/auto-fix.yml .github/workflows/
cp templates/github-actions/dependabot.yml .github/
```

Details: [QUICKSTART.md](./QUICKSTART.md) · [MONOREPO_SETUP_GUIDE.md](./MONOREPO_SETUP_GUIDE.md)

---

## Honest limits

- Requires a GitHub personal access token with repo access. Treat it like a secret.
- Subtree consolidations can be large and slow — start with a tight tag or prefix filter.
- Hosted and Team + API are **not** checkout-live until Polar products and a real hosted runner exist.
- Does not replace monorepo *build* tools; it consolidates repos and lays down governance scaffolding.

---

## Support

support@b2stealthysolutions.com  

https://www.b2stealthysolutions.com/monorepo-consolidator

© B2 Stealthy Solutions
