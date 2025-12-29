#!/usr/bin/env python3
"""
Auto-update system for RSS News Aggregator
"""

import requests
import json
import subprocess
import os
import logging
from datetime import datetime
from models import get_db_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemUpdater:
    def __init__(self):
        self.install_dir = "/home/pi/rss_aggregator"
        self.repo_url = "https://api.github.com/repos/Drew-CodeRGV/TheWirelessMonitor"
        self.current_version = self.get_current_version()
        
    def get_current_version(self):
        """Get current system version"""
        try:
            with open(f"{self.install_dir}/version.json", 'r') as f:
                version_data = json.load(f)
                return version_data.get('version', '0.0.0')
        except Exception as e:
            logger.error(f"Error reading version: {e}")
            return "0.0.0"
    
    def check_for_updates(self):
        """Check GitHub for newer version"""
        try:
            # Get latest release from GitHub API
            response = requests.get(f"{self.repo_url}/releases/latest", timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name'].lstrip('v')
                
                return {
                    'update_available': self.is_newer_version(latest_version, self.current_version),
                    'latest_version': latest_version,
                    'current_version': self.current_version,
                    'release_notes': release_data.get('body', ''),
                    'published_at': release_data.get('published_at', ''),
                    'download_url': release_data.get('zipball_url', '')
                }
            else:
                # Fallback: check main branch commits
                response = requests.get(f"{self.repo_url}/commits/main", timeout=10)
                if response.status_code == 200:
                    commit_data = response.json()
                    latest_commit = commit_data['sha'][:8]
                    
                    # Check if we have this commit
                    try:
                        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                              cwd=self.install_dir, capture_output=True, text=True)
                        current_commit = result.stdout.strip()
                        
                        return {
                            'update_available': latest_commit != current_commit,
                            'latest_version': f"main-{latest_commit}",
                            'current_version': f"main-{current_commit}",
                            'release_notes': commit_data['commit']['message'],
                            'published_at': commit_data['commit']['committer']['date'],
                            'download_url': None
                        }
                    except Exception:
                        return {'update_available': False, 'error': 'Git not available'}
                        
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return {'update_available': False, 'error': str(e)}
    
    def is_newer_version(self, latest, current):
        """Compare version strings"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except Exception:
            return False
    
    def perform_update(self):
        """Perform system update"""
        try:
            logger.info("Starting system update...")
            
            # Record update attempt
            self.log_update_attempt()
            
            # Change to install directory
            os.chdir(self.install_dir)
            
            # Backup current version
            backup_result = subprocess.run(['cp', '-r', '.', f'../rss_aggregator_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'], 
                                         capture_output=True, text=True)
            
            # Pull latest changes
            git_result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                      capture_output=True, text=True)
            
            if git_result.returncode != 0:
                raise Exception(f"Git pull failed: {git_result.stderr}")
            
            # Update Python dependencies
            pip_result = subprocess.run([f'{self.install_dir}/venv/bin/pip', 'install', '-r', 'requirements.txt'], 
                                      capture_output=True, text=True)
            
            if pip_result.returncode != 0:
                logger.warning(f"Pip install warnings: {pip_result.stderr}")
            
            # Run database migrations if needed
            self.run_migrations()
            
            # Restart services
            restart_result = subprocess.run(['sudo', 'systemctl', 'restart', 'rss-aggregator'], 
                                          capture_output=True, text=True)
            
            if restart_result.returncode != 0:
                raise Exception(f"Service restart failed: {restart_result.stderr}")
            
            # Update version info
            self.update_version_info()
            
            logger.info("System update completed successfully")
            return {'success': True, 'message': 'Update completed successfully'}
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_migrations(self):
        """Run any database migrations"""
        try:
            # Check if new tables or columns need to be added
            conn = get_db_connection()
            
            # Add update_log table if it doesn't exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS update_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_from TEXT,
                    version_to TEXT,
                    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 0,
                    error_message TEXT
                )
            ''')
            
            # Add entertainment_score column if it doesn't exist
            try:
                conn.execute('ALTER TABLE articles ADD COLUMN entertainment_score REAL DEFAULT 0.0')
            except:
                pass  # Column already exists
            
            # Add podcast_script_generated column
            try:
                conn.execute('ALTER TABLE weekly_digests ADD COLUMN podcast_script TEXT')
            except:
                pass  # Column already exists
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
    
    def update_version_info(self):
        """Update version information after successful update"""
        try:
            # Get current commit hash
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                  cwd=self.install_dir, capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            # Update version.json
            version_data = {
                'version': self.get_latest_version_from_git(),
                'build_date': datetime.now().isoformat(),
                'commit_hash': commit_hash,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(f"{self.install_dir}/version.json", 'w') as f:
                json.dump(version_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating version info: {e}")
    
    def get_latest_version_from_git(self):
        """Extract version from git tags or use commit hash"""
        try:
            result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                                  cwd=self.install_dir, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().lstrip('v')
            else:
                # Use commit hash as version
                result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                      cwd=self.install_dir, capture_output=True, text=True)
                return f"dev-{result.stdout.strip()}"
        except Exception:
            return "unknown"
    
    def log_update_attempt(self):
        """Log update attempt to database"""
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO update_log (version_from, version_to, success)
                VALUES (?, ?, 0)
            ''', (self.current_version, 'updating'))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging update attempt: {e}")
    
    def get_update_history(self):
        """Get update history from database"""
        try:
            conn = get_db_connection()
            updates = conn.execute('''
                SELECT * FROM update_log 
                ORDER BY update_date DESC 
                LIMIT 10
            ''').fetchall()
            conn.close()
            return [dict(update) for update in updates]
        except Exception as e:
            logger.error(f"Error getting update history: {e}")
            return []