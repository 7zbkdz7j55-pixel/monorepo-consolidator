#!/usr/bin/env python3
"""
GitHub Monorepo Aggregator
Consolidates multiple repositories into a single monorepo using git subtrees.
Implements rate-limit handling, error recovery, and comprehensive logging.

Usage:
    python github_monorepo_aggregator.py --token YOUR_TOKEN --org USERNAME --tag claude-generated --monorepo-path ./consolidated-monorepo

Required Environment Variables:
    GITHUB_TOKEN: Personal access token with repo read access
    
Optional Environment Variables:
    MONOREPO_PATH: Path to monorepo (default: ./consolidated-monorepo)
    LOG_LEVEL: DEBUG, INFO, WARNING, ERROR (default: INFO)
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import requests
from github import Github, GithubException, RateLimitExceededException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monorepo_aggregator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GitHubMonorepoAggregator:
    """Manages the consolidation of GitHub repositories into a monorepo."""
    
    def __init__(self, token: str, monorepo_path: str = './consolidated-monorepo'):
        """
        Initialize the aggregator.
        
        Args:
            token: GitHub personal access token
            monorepo_path: Root path for the monorepo
        """
        try:
            self.github = Github(token)
            self.user = self.github.get_user()
            self.monorepo_path = Path(monorepo_path)
            self.rate_limit_buffer = 10  # Keep 10 API calls in reserve
            logger.info(f"Initialized aggregator for user: {self.user.login}")
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e}")
            sys.exit(1)
    
    def check_rate_limit(self) -> Tuple[int, int, datetime]:
        """
        Check remaining API rate limit.
        
        Returns:
            Tuple of (remaining, limit, reset_time)
        """
        try:
            rate_limit = self.github.get_rate_limit()
            remaining = rate_limit.core.remaining
            limit = rate_limit.core.limit
            reset_time = datetime.fromtimestamp(rate_limit.core.reset)
            
            logger.debug(f"Rate limit: {remaining}/{limit}, resets at {reset_time}")
            return remaining, limit, reset_time
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return 0, 0, datetime.now()
    
    def wait_for_rate_limit_reset(self) -> bool:
        """
        Wait for rate limit to reset if approaching threshold.
        
        Returns:
            True if recovered, False if timeout exceeded
        """
        remaining, limit, reset_time = self.check_rate_limit()
        
        if remaining > self.rate_limit_buffer:
            return True
        
        wait_time = (reset_time - datetime.now()).total_seconds()
        if wait_time > 3600:  # Don't wait more than 1 hour
            logger.error(f"Rate limit reset exceeds 1 hour: {wait_time}s")
            return False
        
        if wait_time > 0:
            logger.warning(f"Rate limit approaching. Waiting {wait_time:.0f}s...")
            time.sleep(wait_time + 5)  # Add 5s buffer
        
        return True
    
    def get_repositories_by_tag(self, tag: str) -> List[Dict]:
        """
        Get all repositories matching a specific tag.
        
        Args:
            tag: Topic/tag to search for
            
        Returns:
            List of repository data dictionaries
        """
        repositories = []
        try:
            # Use search to find repos with specific topic
            search_query = f"user:{self.user.login} topic:{tag}"
            results = self.github.search_repositories(query=search_query)
            
            for repo in results:
                repositories.append({
                    'name': repo.name,
                    'url': repo.clone_url,
                    'ssh_url': repo.ssh_url,
                    'description': repo.description,
                    'language': repo.language,
                    'topics': repo.topics
                })
                logger.info(f"Found repository: {repo.name}")
        
        except RateLimitExceededException:
            if not self.wait_for_rate_limit_reset():
                logger.error("Rate limit exceeded and recovery failed")
                return repositories
            return self.get_repositories_by_tag(tag)
        except GithubException as e:
            logger.error(f"GitHub API error fetching repositories: {e}")
        
        return repositories
    
    def get_repositories_by_prefix(self, prefix: str) -> List[Dict]:
        """
        Get all repositories matching a name prefix.
        
        Args:
            prefix: Repository name prefix to match
            
        Returns:
            List of repository data dictionaries
        """
        repositories = []
        try:
            for repo in self.user.get_repos():
                if repo.name.startswith(prefix):
                    repositories.append({
                        'name': repo.name,
                        'url': repo.clone_url,
                        'ssh_url': repo.ssh_url,
                        'description': repo.description,
                        'language': repo.language,
                        'topics': repo.topics
                    })
                    logger.info(f"Found repository: {repo.name}")
        
        except RateLimitExceededException:
            if not self.wait_for_rate_limit_reset():
                logger.error("Rate limit exceeded and recovery failed")
                return repositories
            return self.get_repositories_by_prefix(prefix)
        except GithubException as e:
            logger.error(f"GitHub API error fetching repositories: {e}")
        
        return repositories
    
    def initialize_monorepo(self) -> bool:
        """
        Initialize the monorepo git repository.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.monorepo_path.mkdir(parents=True, exist_ok=True)
            
            # Check if already a git repo
            git_dir = self.monorepo_path / '.git'
            if git_dir.exists():
                logger.info("Monorepo already initialized")
                return True
            
            # Initialize new repo
            result = subprocess.run(
                ['git', 'init'],
                cwd=self.monorepo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Monorepo initialized successfully")
                # Create initial commit
                self._create_initial_commit()
                return True
            else:
                logger.error(f"Failed to initialize monorepo: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error("Git initialization timed out")
            return False
        except Exception as e:
            logger.error(f"Error initializing monorepo: {e}")
            return False
    
    def _create_initial_commit(self) -> bool:
        """Create initial commit if repo is empty."""
        try:
            # Create README
            readme_path = self.monorepo_path / 'README.md'
            readme_path.write_text(
                f"# Consolidated Monorepo\n\n"
                f"Generated: {datetime.now().isoformat()}\n"
                f"User: {self.user.login}\n"
            )
            
            subprocess.run(
                ['git', 'add', 'README.md'],
                cwd=self.monorepo_path,
                capture_output=True,
                timeout=30
            )
            
            subprocess.run(
                ['git', 'config', 'user.email', 'monorepo@example.com'],
                cwd=self.monorepo_path,
                capture_output=True,
                timeout=30
            )
            
            subprocess.run(
                ['git', 'config', 'user.name', 'Monorepo Aggregator'],
                cwd=self.monorepo_path,
                capture_output=True,
                timeout=30
            )
            
            subprocess.run(
                ['git', 'commit', '-m', 'Initial monorepo commit'],
                cwd=self.monorepo_path,
                capture_output=True,
                timeout=30
            )
            
            return True
        except Exception as e:
            logger.warning(f"Could not create initial commit: {e}")
            return False
    
    def add_repository_subtree(self, repo_name: str, repo_url: str, 
                               subdirectory: Optional[str] = None) -> bool:
        """
        Add a repository as a git subtree.
        
        Args:
            repo_name: Name of the repository
            repo_url: Clone URL of the repository
            subdirectory: Custom subdirectory (default: repo_name)
            
        Returns:
            True if successful, False otherwise
        """
        subtree_path = subdirectory or repo_name
        
        try:
            # Add remote
            remote_name = f"repo/{repo_name}"
            
            # Remove remote if it already exists
            subprocess.run(
                ['git', 'remote', 'remove', remote_name],
                cwd=self.monorepo_path,
                capture_output=True,
                timeout=30
            )
            
            result = subprocess.run(
                ['git', 'remote', 'add', remote_name, repo_url],
                cwd=self.monorepo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to add remote for {repo_name}: {result.stderr}")
                return False
            
            # Fetch from remote
            result = subprocess.run(
                ['git', 'fetch', remote_name, 'main', '--depth=1'],
                cwd=self.monorepo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Fallback to master if main doesn't exist
            if result.returncode != 0:
                result = subprocess.run(
                    ['git', 'fetch', remote_name, 'master', '--depth=1'],
                    cwd=self.monorepo_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            if result.returncode != 0:
                logger.error(f"Failed to fetch from {repo_name}: {result.stderr}")
                return False
            
            # Add subtree
            result = subprocess.run(
                ['git', 'subtree', 'add', '--prefix', subtree_path, 
                 f"{remote_name}/HEAD", '--squash'],
                cwd=self.monorepo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully added {repo_name} as subtree at {subtree_path}")
                return True
            else:
                logger.warning(f"Subtree addition had issues for {repo_name}: {result.stderr}")
                # Don't fail completely, subtree might already exist
                return True
        
        except subprocess.TimeoutExpired:
            logger.error(f"Git operation timed out for {repo_name}")
            return False
        except Exception as e:
            logger.error(f"Error adding subtree for {repo_name}: {e}")
            return False
    
    def consolidate_repositories(self, repositories: List[Dict]) -> Dict:
        """
        Consolidate all repositories into the monorepo.
        
        Args:
            repositories: List of repository dictionaries
            
        Returns:
            Dictionary with consolidation results
        """
        results = {
            'total': len(repositories),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        if not self.initialize_monorepo():
            logger.error("Failed to initialize monorepo")
            return results
        
        for i, repo in enumerate(repositories, 1):
            logger.info(f"Processing {i}/{len(repositories)}: {repo['name']}")
            
            # Check rate limit before each operation
            if not self.wait_for_rate_limit_reset():
                logger.error("Rate limit recovery failed, aborting")
                break
            
            success = self.add_repository_subtree(
                repo['name'],
                repo['url']
            )
            
            if success:
                results['successful'] += 1
                results['details'].append({
                    'repo': repo['name'],
                    'status': 'success'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'repo': repo['name'],
                    'status': 'failed'
                })
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a consolidation report."""
        report = f"""
Monorepo Consolidation Report
Generated: {datetime.now().isoformat()}
User: {self.user.login}
Monorepo Path: {self.monorepo_path}

Summary:
  Total Repositories: {results['total']}
  Successful: {results['successful']}
  Failed: {results['failed']}
  Success Rate: {(results['successful']/results['total']*100):.1f}%

Details:
"""
        for detail in results['details']:
            report += f"\n  - {detail['repo']}: {detail['status']}"
        
        return report


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Consolidate GitHub repositories into a monorepo'
    )
    parser.add_argument('--token', default=os.getenv('GITHUB_TOKEN'),
                        help='GitHub personal access token')
    parser.add_argument('--tag', help='Repository tag to search for')
    parser.add_argument('--prefix', help='Repository name prefix to search for')
    parser.add_argument('--monorepo-path', default=os.getenv('MONOREPO_PATH', './consolidated-monorepo'),
                        help='Path to monorepo')
    parser.add_argument('--log-level', default=os.getenv('LOG_LEVEL', 'INFO'),
                        help='Logging level')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.token:
        logger.error("GITHUB_TOKEN not provided")
        sys.exit(1)
    
    if not args.tag and not args.prefix:
        logger.error("Either --tag or --prefix must be specified")
        sys.exit(1)
    
    # Set logging level
    logger.setLevel(getattr(logging, args.log_level))
    
    # Initialize aggregator
    aggregator = GitHubMonorepoAggregator(args.token, args.monorepo_path)
    
    # Fetch repositories
    logger.info("Fetching repositories...")
    if args.tag:
        repositories = aggregator.get_repositories_by_tag(args.tag)
    else:
        repositories = aggregator.get_repositories_by_prefix(args.prefix)
    
    if not repositories:
        logger.warning("No repositories found")
        sys.exit(0)
    
    logger.info(f"Found {len(repositories)} repositories")
    
    # Consolidate
    logger.info("Starting consolidation...")
    results = aggregator.consolidate_repositories(repositories)
    
    # Report
    report = aggregator.generate_report(results)
    logger.info(report)
    
    # Save report
    report_path = Path('monorepo_consolidation_report.txt')
    report_path.write_text(report)
    logger.info(f"Report saved to {report_path}")


if __name__ == '__main__':
    main()
