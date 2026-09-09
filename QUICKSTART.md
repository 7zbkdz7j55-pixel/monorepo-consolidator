# Monorepo Consolidator — Quick Start

**B2 Stealthy Solutions** · Free self-hosted tier


## 1. Generate GitHub Token

```bash
# Visit: https://github.com/settings/tokens/new
# Scopes: repo, workflow, read:org
# Expiration: 90 days
# Save the token as: $GITHUB_TOKEN
```

## 2. Clone Templates

```bash
git clone https://github.com/7zbkdz7j55-pixel/monorepo-consolidator.git
cd monorepo-consolidator
```

## 3. Set Environment Variable

```bash
# macOS/Linux
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Windows
set GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## 4. Install Dependencies

```bash
pip install PyGithub==2.1.1 requests==2.31.0
```

## 5. Run Aggregator

```bash
# Find repos by tag
python github_monorepo_aggregator.py --tag claude-generated

# Find repos by prefix
python github_monorepo_aggregator.py --prefix "project-"
```

## 6. Setup GitHub Actions

```bash
mkdir -p .github/workflows
cp templates/github-actions/auto-fix.yml .github/workflows/
cp templates/github-actions/dependabot.yml .github/
git add .github/
git commit -m "ci: add workflows"
git push
```

## 7. Enable Branch Protection

- Settings → Branches
- Add rule for `main`
- Require status checks: `lint-and-fix`, `security-sast`, `dependency-check`

## 8. Done! ✓

Your monorepo is now:
- ✓ Consolidated with git subtrees
- ✓ Auto-formatting code on every push
- ✓ Scanning for security vulnerabilities
- ✓ Updating dependencies automatically
- ✓ Zero cost

## Commands Cheat Sheet

```bash
# Check rate limit
GITHUB_TOKEN=$GITHUB_TOKEN python -c "from github import Github; g=Github('$GITHUB_TOKEN'); r=g.get_rate_limit(); print(f'{r.core.remaining}/{r.core.limit}')"

# View logs
tail -f monorepo_aggregator.log

# View report
cat monorepo_consolidation_report.txt

# Manual update of subtree
git subtree pull --prefix projects/repo-name repo/repo-name HEAD --squash

# Rotate token every 90 days
# https://github.com/settings/tokens
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Rate limit exceeded | Wait 1 hour or use fine-grained token |
| Auth failed | Check `echo $GITHUB_TOKEN` is set |
| Workflow not running | Push to main branch, check `.github/workflows/` path |
| Dependabot not working | Enable at Settings → Code & security analysis |

---

**Full Guide**: See `MONOREPO_SETUP_GUIDE.md`  
**Python Script**: `github_monorepo_aggregator.py`  
**CI/CD Workflow**: `auto-fix.yml`  
**Dependency Management**: `dependabot.yml`
