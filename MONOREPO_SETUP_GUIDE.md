# GitHub Monorepo Consolidation System - Complete Setup Guide

A production-ready, zero-cost solution for consolidating dispersed GitHub repositories into a secure, governed monorepo with automated code quality and security scanning.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Installation & Setup](#installation--setup)
5. [Workflow Configuration](#workflow-configuration)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   Monorepo Aggregator                    │
│  (Python script with GitHub API integration)             │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌───────▼──────┐
│ Repositories │  │   Git CLI    │
│  (by tag/    │  │  (Subtrees)  │
│   prefix)    │  └──────────────┘
└──────────────┘

        ↓ (Push to monorepo)

┌──────────────────────────────────────────────────────────┐
│              GitHub Actions CI/CD Pipeline                │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐    │
│  │Linting/Fmt   │ │CodeQL SAST   │ │ Dependency    │    │
│  │(Black, ESL)  │ │ (Security)   │ │ Audit         │    │
│  └──────────────┘ └──────────────┘ └───────────────┘    │
└──────────────────────────────────────────────────────────┘

        ↓ (Auto-commit safe fixes)

┌──────────────────────────────────────────────────────────┐
│           Dependabot Vulnerability Management             │
│  Monitors dependencies → Creates PRs for patches          │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Aggregation Phase**: Python script discovers repositories via GitHub API
2. **Consolidation Phase**: Git subtrees integrate repositories into monorepo
3. **Validation Phase**: GitHub Actions validates code quality on every push
4. **Remediation Phase**: Automated linters fix safe issues, create PRs for complex ones
5. **Security Phase**: CodeQL scans for vulnerabilities, Dependabot updates dependencies

---

## Prerequisites

### Required

- GitHub account with repository access
- Git installed locally (v2.15+)
- Python 3.9+ 
- Access to create GitHub Actions workflows
- GitHub Personal Access Token (PAT) with appropriate permissions

### Recommended

- pip (Python package manager)
- Node.js 16+ (for JavaScript linting)
- 2GB+ free disk space for initial consolidation
- Familiarity with Git workflows

---

## Environment Configuration

### Step 1: Create a GitHub Personal Access Token

#### For Classic Token (Simpler, Less Secure)
1. Navigate to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Configure scopes:
   ```
   ✓ repo (full control of private repositories)
   ✓ workflow (update GitHub Action workflows)
   ✓ read:org (read org data)
   ✓ admin:public_key (manage public keys)
   ```
4. Set expiration to 90 days (automatic refresh cycle)
5. Copy the token immediately (cannot be viewed again)

#### For Fine-Grained Token (Recommended for Security)
1. Navigate to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Click "Generate new token"
3. Configure:
   - **Token name**: "Monorepo Aggregator"
   - **Expiration**: 90 days
   - **Repository access**: Select specific repositories or "All repositories"
   - **Permissions**:
     - Repository: `contents` (read/write), `actions` (read/write)
     - Organization: `members` (read), `administration` (read)
4. Copy the token immediately

### Step 2: Securely Store the Token

#### Option A: GitHub Secrets (Recommended for Automated Workflows)

1. In your monorepo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `GITHUB_TOKEN`
4. Value: Paste your PAT
5. Click **Add secret**

⚠️ **Note**: GitHub automatically provides a default `GITHUB_TOKEN` for Actions, but you may want to use your personal token for cross-repository access.

#### Option B: Local Environment Variable (For Local Script Execution)

```bash
# On macOS/Linux, add to ~/.bashrc or ~/.zshrc:
export GITHUB_TOKEN="your_token_here"

# On Windows PowerShell:
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "your_token_here", "User")

# Verify it's set:
echo $GITHUB_TOKEN
```

#### Option C: .env File (Development Only - Never Commit)

```bash
# Create .env file in project root
echo "GITHUB_TOKEN=your_token_here" > .env

# Add to .gitignore
echo ".env" >> .gitignore

# Load in scripts with python-dotenv:
pip install python-dotenv
# Then in Python:
from dotenv import load_dotenv
load_dotenv()
```

### Step 3: Install Dependencies

```bash
# Clone the setup files
git clone <monorepo-url>
cd consolidated-monorepo

# Install Python dependencies
pip install PyGithub==2.1.1 requests==2.31.0

# For local linting (optional, but recommended)
pip install black==23.12.0 flake8==6.1.0 isort==5.13.2

# For Node.js (if you have JavaScript code)
npm install -g eslint prettier
```

---

## Installation & Setup

### Step 1: Prepare Your Monorepo

```bash
# Create monorepo directory
mkdir consolidated-monorepo
cd consolidated-monorepo

# Initialize Git
git init
git config user.name "Monorepo Bot"
git config user.email "bot@example.com"

# Create initial structure
mkdir -p .github/workflows
mkdir -p docs

# Create README
cat > README.md << 'EOF'
# Consolidated Monorepo

This repository consolidates multiple GitHub repositories into a single monorepo.

## Structure

- `projects/` - Individual project subtrees
- `.github/workflows/` - CI/CD automation
- `docs/` - Documentation

## Security

- CodeQL: Continuous security scanning
- Dependabot: Automated dependency updates
- Branch protection: Enforce security checks
EOF

# Initial commit
git add .
git commit -m "Initial monorepo structure"
```

### Step 2: Configure GitHub Repository

```bash
# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/consolidated-monorepo.git
git branch -M main
git push -u origin main
```

### Step 3: Run the Aggregator Script

```bash
# Basic usage - find repos by tag
GITHUB_TOKEN=your_token python github_monorepo_aggregator.py \
  --tag claude-generated \
  --monorepo-path ./consolidated-monorepo

# Alternative - find repos by prefix
GITHUB_TOKEN=your_token python github_monorepo_aggregator.py \
  --prefix "project-" \
  --monorepo-path ./consolidated-monorepo

# With custom logging
GITHUB_TOKEN=your_token python github_monorepo_aggregator.py \
  --tag claude-generated \
  --monorepo-path ./consolidated-monorepo \
  --log-level DEBUG
```

### Step 4: Monitor the Consolidation

The script creates a detailed log file and report:

```bash
# View real-time logs
tail -f monorepo_aggregator.log

# View final report
cat monorepo_consolidation_report.txt
```

---

## Workflow Configuration

### Step 1: Add GitHub Actions Workflows

```bash
# Copy workflow file
cp auto-fix.yml .github/workflows/auto-fix.yml

# Commit
git add .github/workflows/auto-fix.yml
git commit -m "ci: add automated code quality workflow"
git push
```

### Step 2: Add Dependabot Configuration

```bash
# Create Dependabot config
mkdir -p .github
cp dependabot.yml .github/dependabot.yml

# Commit
git add .github/dependabot.yml
git commit -m "ci: add dependabot configuration"
git push
```

### Step 3: Enable Branch Protection

1. Go to **Settings → Branches**
2. Click **Add rule**
3. Configure:
   - **Branch name pattern**: `main`
   - **Require a pull request before merging**: ✓
   - **Require approvals**: ✓ (set to 1)
   - **Require status checks to pass**: ✓
     - Select: `lint-and-fix`, `security-sast`, `dependency-check`
   - **Include administrators**: ✓

### Step 4: Test the Workflow

```bash
# Create a test file with formatting issues
cat > test_file.py << 'EOF'
def poorly_formatted_function( x,y ):
    result=x+y
    return result
EOF

# Push and watch GitHub Actions execute
git add test_file.py
git commit -m "test: trigger workflow"
git push

# The workflow should:
# 1. Format the code with Black
# 2. Fix imports with isort
# 3. Auto-commit the fixes
# 4. Run CodeQL scan
# 5. Check dependencies
```

---

## Security Best Practices

### 1. Token Management

```bash
# ✓ DO: Use fine-grained tokens
# ✓ DO: Set 90-day expiration
# ✓ DO: Rotate tokens regularly
# ✓ DO: Scope to specific repositories

# ✗ DON'T: Commit tokens to git
# ✗ DON'T: Use classic tokens in production
# ✗ DON'T: Share tokens via email/Slack
# ✗ DON'T: Set expiration to "Never"
```

### 2. Secret Rotation Checklist

Every 90 days:
```bash
# 1. Generate new token in GitHub
# 2. Update GitHub Secrets
# 3. Update .env files (if used locally)
# 4. Revoke old token
# 5. Verify workflows still pass
```

### 3. Monitor Security Alerts

```bash
# GitHub automatically notifies you of:
# - Exposed tokens (even in commit history)
# - Vulnerable dependencies
# - Code vulnerabilities (via CodeQL)

# Check alerts at: Settings → Code & security analysis
```

### 4. Code Scanning Configuration

The auto-fix workflow includes:

- **CodeQL**: Detects security vulnerabilities in Python/JavaScript
- **pip-audit**: Finds vulnerable Python packages
- **npm audit**: Identifies JavaScript vulnerabilities
- **ESLint**: Catches potential security issues

### 5. Audit Log Review

```bash
# Review all GitHub Actions executions
# Go to: Actions → All workflows → View run

# Check for:
# - Unexpected auto-commits
# - Failed security checks
# - Unusual dependency updates
```

---

## Troubleshooting

### Issue: Rate Limit Exceeded

**Error**: `GithubException: 403 API rate limit exceeded`

**Solution**:
```bash
# Check current rate limit
GITHUB_TOKEN=your_token python -c "
from github import Github
g = Github('$GITHUB_TOKEN')
rate_limit = g.get_rate_limit()
print(f'Remaining: {rate_limit.core.remaining}/{rate_limit.core.limit}')
print(f'Resets at: {rate_limit.core.reset}')
"

# The aggregator script handles this automatically with backoff
# But if running multiple scripts, wait 1 hour before retrying
```

### Issue: Git Subtree Already Exists

**Error**: `Working tree has uncommitted changes`

**Solution**:
```bash
# Clean up uncommitted changes
cd consolidated-monorepo
git reset --hard HEAD
git clean -fd

# Then re-run the aggregator
```

### Issue: Authentication Failed

**Error**: `GithubException: 401 Bad credentials`

**Solution**:
```bash
# Verify token is set correctly
echo $GITHUB_TOKEN

# If empty, set it:
export GITHUB_TOKEN="your_token_here"

# Verify token permissions
GITHUB_TOKEN=$GITHUB_TOKEN python -c "
from github import Github
g = Github('$GITHUB_TOKEN')
user = g.get_user()
print(f'Authenticated as: {user.login}')
"
```

### Issue: Workflow Not Triggering

**Solution**:
1. Check if workflow file is in `.github/workflows/`
2. Verify branch is in `on.push.branches`
3. Check file is valid YAML (use online validator)
4. Push to trigger manually: `git commit --allow-empty -m "trigger"`

### Issue: Dependabot Not Creating PRs

**Solution**:
1. Go to **Settings → Code & security analysis**
2. Ensure **Dependabot alerts** is enabled
3. Ensure **Dependabot security updates** is enabled
4. Check `.github/dependabot.yml` for syntax errors

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check for failed workflows
# Go to: Actions → All workflows

# Review any Dependabot PRs
# Go to: Pull requests → Filter by "author:dependabot"

# Monitor security alerts
# Go to: Security → Code scanning alerts
```

### Weekly Maintenance

```bash
# Review and merge Dependabot PRs
# - All "patch" updates: Auto-merge recommended
# - "minor" updates: Review before merging
# - "major" updates: Thorough testing required

# Check rate limit usage
GITHUB_TOKEN=$GITHUB_TOKEN python github_monorepo_aggregator.py --help

# Review logs for anomalies
grep "ERROR\|WARNING" monorepo_aggregator.log
```

### Monthly Tasks

```bash
# 1. Update linting tool versions in auto-fix.yml
#    - Check for new Black releases
#    - Update ESLint/Prettier versions

# 2. Review failed security checks
#    - Triage CodeQL findings
#    - Prioritize critical vulnerabilities

# 3. Audit team access
#    - Review who has push access
#    - Ensure branch protection is enforced

# 4. Performance review
#    - Monitor GitHub Actions usage
#    - Optimize workflow run times
```

### Quarterly Review

```bash
# 1. Rotate GITHUB_TOKEN (90-day cycle)
# 2. Review and update branch protection rules
# 3. Assess monorepo structure
#    - Are subtrees still organized logically?
#    - Should any repos be separated?
# 4. Security audit
#    - Review all CodeQL findings
#    - Assess vulnerability remediation progress
```

---

## Advanced Configuration

### Custom Linting Rules

Edit `.eslintrc.json` in monorepo root to customize rules:

```json
{
  "rules": {
    "no-console": "error",
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "prefer-const": "error"
  }
}
```

### Conditional Auto-Commit

Modify the `auto-fix.yml` workflow to only auto-commit for specific paths:

```yaml
- name: Auto-fix with Black
  if: |
    steps.black.outputs.exit_code != '0' &&
    contains(github.event.head_commit.modified, 'src/')
  run: black --line-length 100 src/ --exclude venv
```

### Custom Commit Messages

Modify the commit message in auto-fix.yml:

```yaml
git commit -m "chore: auto-format code

Triggered by: ${{ github.event_name }}
Commit: ${{ github.sha }}
Branch: ${{ github.ref }}"
```

---

## Cost Analysis

### Free Tier Coverage

| Component | Cost | Notes |
|-----------|------|-------|
| GitHub Actions | Free | 2,000 minutes/month for private repos |
| CodeQL | Free | Unlimited scans on public repos |
| Dependabot | Free | All repositories |
| Git Subtrees | Free | Part of git |
| PyGithub Library | Free | Open source |

**Total Monthly Cost: $0**

---

## Support & Resources

- **GitHub Documentation**: https://docs.github.com
- **PyGithub Docs**: https://pygithub.readthedocs.io/
- **CodeQL Documentation**: https://codeql.github.com/docs/
- **Dependabot Docs**: https://docs.github.com/en/code-security/dependabot

---

## License

This setup guide and scripts are provided as-is for educational and commercial use.

---

**Last Updated**: January 2025  
**Maintainer**: DevOps & Security Team
