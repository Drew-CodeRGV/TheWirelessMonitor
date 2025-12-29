#!/usr/bin/env python3
"""
GitHub Integration for The Wireless Monitor
Handles repository creation, file management, and publishing
"""

import requests
import json
import base64
import os
import logging
from datetime import datetime
from models import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubManager:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = None
        self.username = None
        self.repo_name = None
        self.load_config()
    
    def load_config(self):
        """Load GitHub configuration from database"""
        try:
            conn = get_db_connection()
            config = conn.execute('''
                SELECT github_token, github_username, github_repo 
                FROM github_config 
                WHERE id = 1
            ''').fetchone()
            conn.close()
            
            if config:
                self.token = config['github_token']
                self.username = config['github_username']
                self.repo_name = config['github_repo']
        except Exception as e:
            logger.warning(f"GitHub config not found: {e}")
    
    def save_config(self, token, username, repo_name):
        """Save GitHub configuration to database"""
        try:
            conn = get_db_connection()
            
            # Create table if it doesn't exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS github_config (
                    id INTEGER PRIMARY KEY,
                    github_token TEXT,
                    github_username TEXT,
                    github_repo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert or update config
            conn.execute('''
                INSERT OR REPLACE INTO github_config (id, github_token, github_username, github_repo, updated_at)
                VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (token, username, repo_name or 'TheWirelessMonitor'))
            
            conn.commit()
            conn.close()
            
            self.token = token
            self.username = username
            self.repo_name = repo_name
            
            return True
        except Exception as e:
            logger.error(f"Error saving GitHub config: {e}")
            return False
    
    def get_headers(self):
        """Get authentication headers for GitHub API"""
        if not self.token:
            raise Exception("GitHub token not configured")
        
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Wireless-Monitor-Kiro'
        }
    
    def test_connection(self):
        """Test GitHub API connection and permissions"""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'username': user_data.get('login'),
                    'name': user_data.get('name'),
                    'public_repos': user_data.get('public_repos'),
                    'private_repos': user_data.get('total_private_repos', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f"GitHub API error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_repository(self, repo_name, description="The Wireless Monitor - RSS News Aggregator", private=False):
        """Create a new GitHub repository"""
        try:
            data = {
                'name': repo_name,
                'description': description,
                'private': private,
                'auto_init': True,
                'gitignore_template': 'Python',
                'license_template': 'mit'
            }
            
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.get_headers(),
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                self.repo_name = repo_name
                return {
                    'success': True,
                    'repo_url': repo_data.get('html_url'),
                    'clone_url': repo_data.get('clone_url'),
                    'ssh_url': repo_data.get('ssh_url')
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to create repository: {response.json().get('message', 'Unknown error')}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_repository_info(self):
        """Get information about the configured repository"""
        if not self.username or not self.repo_name:
            return {'success': False, 'error': 'Repository not configured'}
        
        try:
            response = requests.get(
                f"{self.base_url}/repos/{self.username}/{self.repo_name}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'success': True,
                    'name': repo_data.get('name'),
                    'description': repo_data.get('description'),
                    'url': repo_data.get('html_url'),
                    'private': repo_data.get('private'),
                    'created_at': repo_data.get('created_at'),
                    'updated_at': repo_data.get('updated_at'),
                    'size': repo_data.get('size'),
                    'language': repo_data.get('language'),
                    'default_branch': repo_data.get('default_branch', 'main')
                }
            else:
                return {
                    'success': False,
                    'error': f"Repository not found or access denied: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_file(self, file_path, content, commit_message=None, branch='main'):
        """Upload or update a file in the repository"""
        if not self.username or not self.repo_name:
            raise Exception("Repository not configured")
        
        if commit_message is None:
            commit_message = f"Update {file_path} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            # Check if file exists to get SHA for update
            existing_file_url = f"{self.base_url}/repos/{self.username}/{self.repo_name}/contents/{file_path}"
            existing_response = requests.get(existing_file_url, headers=self.get_headers())
            
            # Encode content to base64
            content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                'message': commit_message,
                'content': content_encoded,
                'branch': branch
            }
            
            # If file exists, include SHA for update
            if existing_response.status_code == 200:
                existing_data = existing_response.json()
                data['sha'] = existing_data['sha']
            
            # Upload/update file
            response = requests.put(
                existing_file_url,
                headers=self.get_headers(),
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                return {
                    'success': True,
                    'commit_url': result_data.get('commit', {}).get('html_url'),
                    'file_url': result_data.get('content', {}).get('html_url')
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to upload file: {response.json().get('message', 'Unknown error')}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def publish_project(self):
        """Publish the entire Wireless Monitor project to GitHub"""
        if not self.username or not self.repo_name:
            return {'success': False, 'error': 'Repository not configured'}
        
        try:
            project_root = '/home/wifi/rss_aggregator'
            results = []
            
            # Files to publish
            files_to_publish = [
                ('README.md', 'README.md'),
                ('requirements.txt', 'requirements.txt'),
                ('version.json', 'version.json'),
                ('DEPLOYMENT.md', 'DEPLOYMENT.md'),
                ('app/main.py', 'app/main.py'),
                ('app/models.py', 'app/models.py'),
                ('app/rss_fetcher.py', 'app/rss_fetcher.py'),
                ('app/ai_analyzer.py', 'app/ai_analyzer.py'),
                ('app/updater.py', 'app/updater.py'),
                ('app/github_manager.py', 'app/github_manager.py'),
                ('static/style.css', 'static/style.css'),
                ('static/app.js', 'static/app.js'),
                ('config/settings.py', 'config/settings.py'),
                ('scripts/install.sh', 'scripts/install.sh'),
                ('scripts/auto_update.py', 'scripts/auto_update.py'),
                ('scripts/monitor.sh', 'scripts/monitor.sh'),
                ('app/templates/base.html', 'app/templates/base.html'),
                ('app/templates/index.html', 'app/templates/index.html'),
                ('app/templates/article.html', 'app/templates/article.html'),
                ('app/templates/admin.html', 'app/templates/admin.html'),
                ('app/templates/entertainment.html', 'app/templates/entertainment.html'),
                ('app/templates/social_config.html', 'app/templates/social_config.html'),
                ('app/templates/feeds.html', 'app/templates/feeds.html'),
                ('app/templates/weekly.html', 'app/templates/weekly.html'),
                ('app/templates/podcast.html', 'app/templates/podcast.html')
            ]
            
            for local_path, github_path in files_to_publish:
                full_path = os.path.join(project_root, local_path)
                
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    result = self.upload_file(
                        github_path, 
                        content, 
                        f"Update {github_path} via Kiro"
                    )
                    
                    results.append({
                        'file': github_path,
                        'success': result['success'],
                        'error': result.get('error')
                    })
                    
                    if result['success']:
                        logger.info(f"Published {github_path}")
                    else:
                        logger.error(f"Failed to publish {github_path}: {result.get('error')}")
                else:
                    results.append({
                        'file': github_path,
                        'success': False,
                        'error': 'File not found locally'
                    })
            
            successful_uploads = sum(1 for r in results if r['success'])
            total_files = len(results)
            
            return {
                'success': successful_uploads > 0,
                'uploaded': successful_uploads,
                'total': total_files,
                'results': results,
                'repo_url': f"https://github.com/{self.username}/{self.repo_name}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_commit_history(self, limit=10):
        """Get recent commit history"""
        if not self.username or not self.repo_name:
            return {'success': False, 'error': 'Repository not configured'}
        
        try:
            response = requests.get(
                f"{self.base_url}/repos/{self.username}/{self.repo_name}/commits",
                headers=self.get_headers(),
                params={'per_page': limit},
                timeout=10
            )
            
            if response.status_code == 200:
                commits = response.json()
                return {
                    'success': True,
                    'commits': [{
                        'sha': commit['sha'][:8],
                        'message': commit['commit']['message'],
                        'author': commit['commit']['author']['name'],
                        'date': commit['commit']['author']['date'],
                        'url': commit['html_url']
                    } for commit in commits]
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to get commits: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }