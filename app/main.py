#!/usr/bin/env python3
"""
RSS News Aggregator - Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
import json
import os
import requests
from models import init_db, get_db_connection
from rss_fetcher import RSSFetcher
from ai_analyzer import AIAnalyzer
from updater import SystemUpdater

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Initialize database
init_db()

# Get version info
def get_version_info():
    try:
        with open('/home/pi/rss_aggregator/version.json', 'r') as f:
            return json.load(f)
    except:
        return {'version': '1.0.0', 'build_date': '2025-01-01'}

@app.route('/')
def index():
    """Main dashboard showing today's top stories"""
    conn = get_db_connection()
    
    # Get today's top stories
    today = datetime.now().strftime('%Y-%m-%d')
    stories = conn.execute('''
        SELECT * FROM articles 
        WHERE DATE(published_date) = ? AND relevance_score > 0.6
        ORDER BY relevance_score DESC, published_date DESC
        LIMIT 20
    ''', (today,)).fetchall()
    
    # Get entertainment stories
    entertainment_stories = conn.execute('''
        SELECT * FROM articles 
        WHERE DATE(published_date) >= DATE('now', '-3 days') 
        AND entertainment_score > 0.5 AND relevance_score > 0.3
        ORDER BY entertainment_score DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    version_info = get_version_info()
    
    return render_template('index.html', 
                         stories=stories, 
                         entertainment_stories=entertainment_stories,
                         date=today, 
                         version=version_info)

@app.route('/feeds')
def manage_feeds():
    """RSS feed management page"""
    conn = get_db_connection()
    feeds = conn.execute('SELECT * FROM rss_feeds ORDER BY name').fetchall()
    conn.close()
    return render_template('feeds.html', feeds=feeds)

@app.route('/add_feed', methods=['POST'])
def add_feed():
    """Add new RSS feed"""
    name = request.form['name']
    url = request.form['url']
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO rss_feeds (name, url, active) 
            VALUES (?, ?, 1)
        ''', (name, url))
        conn.commit()
        flash(f'Successfully added feed: {name}', 'success')
    except sqlite3.IntegrityError:
        flash(f'Feed URL already exists: {url}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage_feeds'))

@app.route('/add_bulk_feeds', methods=['POST'])
def add_bulk_feeds():
    """Add multiple RSS feeds from textarea input"""
    feeds_text = request.form['bulk_feeds']
    
    conn = get_db_connection()
    added_count = 0
    error_count = 0
    
    for line in feeds_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Parse line: "Name|URL" or just "URL"
        if '|' in line:
            name, url = line.split('|', 1)
            name = name.strip()
            url = url.strip()
        else:
            url = line.strip()
            name = url.split('/')[-2] if '/' in url else url
        
        try:
            conn.execute('''
                INSERT INTO rss_feeds (name, url, active) 
                VALUES (?, ?, 1)
            ''', (name, url))
            added_count += 1
        except sqlite3.IntegrityError:
            error_count += 1
    
    conn.commit()
    conn.close()
    
    if added_count > 0:
        flash(f'Successfully added {added_count} feeds', 'success')
    if error_count > 0:
        flash(f'{error_count} feeds were duplicates and skipped', 'warning')
    
    return redirect(url_for('manage_feeds'))

@app.route('/toggle_feed/<int:feed_id>')
def toggle_feed(feed_id):
    """Toggle feed active status"""
    conn = get_db_connection()
    conn.execute('''
        UPDATE rss_feeds 
        SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END 
        WHERE id = ?
    ''', (feed_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('manage_feeds'))

@app.route('/weekly')
def weekly_digest():
    """Weekly digest page"""
    conn = get_db_connection()
    
    # Get last 7 days of top stories
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    stories = conn.execute('''
        SELECT * FROM articles 
        WHERE DATE(published_date) >= ? AND relevance_score > 0.7
        ORDER BY relevance_score DESC, published_date DESC
        LIMIT 50
    ''', (week_ago,)).fetchall()
    
    conn.close()
    return render_template('weekly.html', stories=stories)

@app.route('/api/fetch_now')
def fetch_now():
    """Manual trigger for RSS fetching"""
    try:
        fetcher = RSSFetcher()
        analyzer = AIAnalyzer()
        
        # Fetch and analyze
        new_articles = fetcher.fetch_all_feeds()
        analyzed_count = analyzer.analyze_articles(new_articles)
        
        return jsonify({
            'success': True,
            'fetched': len(new_articles),
            'analyzed': analyzed_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
@app.route('/admin')
def admin_console():
    """Admin console for system management"""
    version_info = get_version_info()
    updater = SystemUpdater()
    
    # Get system stats
    conn = get_db_connection()
    stats = {
        'total_articles': conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0],
        'total_feeds': conn.execute('SELECT COUNT(*) FROM rss_feeds').fetchone()[0],
        'active_feeds': conn.execute('SELECT COUNT(*) FROM rss_feeds WHERE active = 1').fetchone()[0],
        'articles_today': conn.execute('SELECT COUNT(*) FROM articles WHERE DATE(published_date) = DATE("now")').fetchone()[0],
        'high_relevance_today': conn.execute('SELECT COUNT(*) FROM articles WHERE DATE(published_date) = DATE("now") AND relevance_score > 0.8').fetchone()[0],
        'entertainment_stories': conn.execute('SELECT COUNT(*) FROM articles WHERE entertainment_score > 0.5').fetchone()[0]
    }
    conn.close()
    
    # Get update history
    update_history = updater.get_update_history()
    
    return render_template('admin.html', 
                         version=version_info, 
                         stats=stats,
                         update_history=update_history)

@app.route('/admin/check_updates')
def check_updates():
    """Check for system updates"""
    updater = SystemUpdater()
    update_info = updater.check_for_updates()
    return jsonify(update_info)

@app.route('/admin/update_system', methods=['POST'])
def update_system():
    """Perform system update"""
    updater = SystemUpdater()
    result = updater.perform_update()
    return jsonify(result)

@app.route('/entertainment')
def entertainment_stories():
    """Page showing entertaining wireless stories"""
    analyzer = AIAnalyzer()
    stories = analyzer.get_entertainment_stories(days=14)
    
    return render_template('entertainment.html', stories=stories)

@app.route('/podcast_script')
def podcast_script():
    """Generate and display podcast script"""
    week_start = request.args.get('week', datetime.now().strftime('%Y-%m-%d'))
    
    analyzer = AIAnalyzer()
    script = analyzer.generate_podcast_script(week_start)
    
    return render_template('podcast.html', script=script, week_start=week_start)

@app.route('/api/generate_podcast', methods=['POST'])
def generate_podcast_script():
    """API endpoint to generate podcast script"""
    week_start = request.json.get('week_start', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        analyzer = AIAnalyzer()
        script = analyzer.generate_podcast_script(week_start)
        
        return jsonify({
            'success': True,
            'script': script,
            'week_start': week_start
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/system_status')
def system_status():
    """Get system status for monitoring"""
    try:
        import subprocess
        
        # Check services
        services = ['rss-aggregator', 'nginx', 'ollama']
        service_status = {}
        
        for service in services:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                  capture_output=True, text=True)
            service_status[service] = result.stdout.strip() == 'active'
        
        # Check disk space
        result = subprocess.run(['df', '/home/pi/rss_aggregator'], 
                              capture_output=True, text=True)
        disk_usage = result.stdout.split('\n')[1].split()[4] if result.returncode == 0 else 'unknown'
        
        return jsonify({
            'services': service_status,
            'disk_usage': disk_usage,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Template filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Template filter to parse JSON strings"""
    try:
        return json.loads(value) if value else []
    except:
        return []

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
@app.route('/article/<int:article_id>')
def view_article(article_id):
    """View full article with social sharing"""
    conn = get_db_connection()
    
    # Get article details
    article = conn.execute('''
        SELECT a.*, f.name as feed_name 
        FROM articles a 
        LEFT JOIN rss_feeds f ON a.feed_id = f.id 
        WHERE a.id = ?
    ''', (article_id,)).fetchone()
    
    if not article:
        return render_template('404.html'), 404
    
    # Get social media config
    social_config = conn.execute('''
        SELECT platform, handle, display_name, enabled 
        FROM social_config 
        WHERE enabled = 1 AND handle != ""
        ORDER BY platform
    ''').fetchall()
    
    conn.close()
    
    return render_template('article.html', 
                         article=dict(article), 
                         social_config=[dict(s) for s in social_config])

@app.route('/admin/social')
def social_media_config():
    """Social media configuration page"""
    conn = get_db_connection()
    social_platforms = conn.execute('''
        SELECT * FROM social_config ORDER BY platform
    ''').fetchall()
    conn.close()
    
    return render_template('social_config.html', 
                         platforms=[dict(p) for p in social_platforms])

@app.route('/admin/social/update', methods=['POST'])
def update_social_config():
    """Update social media configuration"""
    conn = get_db_connection()
    
    for platform in ['twitter', 'linkedin', 'instagram', 'facebook', 'mastodon']:
        handle = request.form.get(f'{platform}_handle', '').strip()
        enabled = 1 if request.form.get(f'{platform}_enabled') else 0
        
        conn.execute('''
            UPDATE social_config 
            SET handle = ?, enabled = ? 
            WHERE platform = ?
        ''', (handle, enabled, platform))
    
    conn.commit()
    conn.close()
    
    flash('Social media configuration updated successfully!', 'success')
    return redirect(url_for('social_media_config'))

@app.route('/api/share/<int:article_id>/<platform>')
def generate_share_content(article_id, platform):
    """Generate social media share content"""
    conn = get_db_connection()
    
    # Get article and social config
    article = conn.execute('''
        SELECT * FROM articles WHERE id = ?
    ''', (article_id,)).fetchone()
    
    social = conn.execute('''
        SELECT handle FROM social_config 
        WHERE platform = ? AND enabled = 1
    ''', (platform,)).fetchone()
    
    conn.close()
    
    if not article or not social:
        return jsonify({'error': 'Article or social config not found'}), 404
    
    # Generate share content based on platform
    base_url = request.url_root.rstrip('/')
    article_url = f"{base_url}/article/{article_id}"
    
    share_data = {
        'url': article_url,
        'title': article['title'],
        'description': article['description'][:200] + '...' if len(article['description']) > 200 else article['description'],
        'image': article['image_url'] or f"{base_url}/static/default-share-image.png",
        'handle': social['handle']
    }
    
    if platform == 'twitter':
        # Twitter/X format
        text = f"{article['title']}\n\n{share_data['description']}\n\n#WirelessTech #WiFi #Technology\n\nvia @{social['handle']}\n{article_url}"
        share_data['share_url'] = f"https://twitter.com/intent/tweet?text={requests.utils.quote(text)}"
        
    elif platform == 'linkedin':
        # LinkedIn format
        share_data['share_url'] = f"https://www.linkedin.com/sharing/share-offsite/?url={requests.utils.quote(article_url)}"
        
    elif platform == 'instagram':
        # Instagram doesn't support direct URL sharing, provide copy text
        text = f"{article['title']}\n\n{share_data['description']}\n\n#WirelessTech #WiFi #Technology #TechNews\n\nRead more at: {article_url}\n\nFollow @{social['handle']} for more wireless tech news!"
        share_data['copy_text'] = text
        share_data['share_url'] = None
        
    elif platform == 'facebook':
        # Facebook format
        share_data['share_url'] = f"https://www.facebook.com/sharer/sharer.php?u={requests.utils.quote(article_url)}"
    
    return jsonify(share_data)
# Import GitHub manager
from github_manager import GitHubManager

@app.route('/admin/github')
def github_config():
    """GitHub configuration and management page"""
    github = GitHubManager()
    
    # Test connection if configured
    connection_status = None
    repo_info = None
    commit_history = None
    
    if github.token and github.username:
        connection_status = github.test_connection()
        if connection_status.get('success'):
            repo_info = github.get_repository_info()
            if repo_info.get('success'):
                commit_history = github.get_commit_history()
    
    return render_template('github_config.html',
                         github_token=github.token,
                         github_username=github.username,
                         github_repo=github.repo_name,
                         connection_status=connection_status,
                         repo_info=repo_info,
                         commit_history=commit_history)

@app.route('/admin/github/save', methods=['POST'])
def save_github_config():
    """Save GitHub configuration"""
    token = request.form.get('github_token', '').strip()
    username = request.form.get('github_username', '').strip()
    repo_name = request.form.get('github_repo', '').strip()
    
    if not token or not username:
        flash('GitHub token and username are required', 'error')
        return redirect(url_for('github_config'))
    
    github = GitHubManager()
    
    if github.save_config(token, username, repo_name):
        # Test the connection
        test_result = github.test_connection()
        if test_result.get('success'):
            flash('GitHub configuration saved and tested successfully!', 'success')
        else:
            flash(f'Configuration saved but connection test failed: {test_result.get("error")}', 'warning')
    else:
        flash('Failed to save GitHub configuration', 'error')
    
    return redirect(url_for('github_config'))

@app.route('/admin/github/create_repo', methods=['POST'])
def create_github_repo():
    """Create a new GitHub repository"""
    repo_name = request.form.get('new_repo_name', '').strip()
    description = request.form.get('repo_description', 'The Wireless Monitor - RSS News Aggregator')
    private = request.form.get('private_repo') == 'on'
    
    if not repo_name:
        flash('Repository name is required', 'error')
        return redirect(url_for('github_config'))
    
    github = GitHubManager()
    result = github.create_repository(repo_name, description, private)
    
    if result.get('success'):
        # Update config with new repo name
        github.save_config(github.token, github.username, repo_name)
        flash(f'Repository "{repo_name}" created successfully!', 'success')
    else:
        flash(f'Failed to create repository: {result.get("error")}', 'error')
    
    return redirect(url_for('github_config'))

@app.route('/admin/github/publish', methods=['POST'])
def publish_to_github():
    """Publish the entire project to GitHub"""
    github = GitHubManager()
    
    if not github.token or not github.username or not github.repo_name:
        flash('GitHub configuration incomplete. Please configure your GitHub settings first.', 'error')
        return redirect(url_for('github_config'))
    
    result = github.publish_project()
    
    if result.get('success'):
        uploaded = result.get('uploaded', 0)
        total = result.get('total', 0)
        flash(f'Successfully published {uploaded}/{total} files to GitHub!', 'success')
    else:
        flash(f'Failed to publish project: {result.get("error")}', 'error')
    
    return redirect(url_for('github_config'))

@app.route('/api/github/test_connection')
def test_github_connection():
    """API endpoint to test GitHub connection"""
    github = GitHubManager()
    result = github.test_connection()
    return jsonify(result)

@app.route('/api/github/repo_info')
def get_github_repo_info():
    """API endpoint to get repository information"""
    github = GitHubManager()
    result = github.get_repository_info()
    return jsonify(result)