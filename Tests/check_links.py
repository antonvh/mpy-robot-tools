#!/usr/bin/env python3
"""Check for dead links in markdown and documentation files."""

import re
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
import subprocess

def find_markdown_files(repo_root):
    """Find all markdown files in the repository."""
    md_files = []
    for root, dirs, files in os.walk(repo_root):
        # Skip hidden directories and common ignore patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '.venv']]
        for file in files:
            if file.endswith('.md') or file.endswith('.rst'):
                md_files.append(os.path.join(root, file))
    return md_files

def extract_links(file_path):
    """Extract all links from a markdown/rst file."""
    links = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Markdown links: [text](url)
        md_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        links.extend([(text, url, 'markdown') for text, url in md_links])
        
        # Reference-style links: [text][ref] and [ref]: url
        ref_links = re.findall(r'^\[([^\]]+)\]:\s*(.+)$', content, re.MULTILINE)
        links.extend([(ref, url, 'reference') for ref, url in ref_links])
        
        # URLs in angle brackets: <url>
        angle_urls = re.findall(r'<(https?://[^>]+)>', content)
        links.extend([('', url, 'angle') for url in angle_urls])
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return links

def check_local_link(link, file_path, repo_root):
    """Check if a local file link exists."""
    # Remove anchors (#section)
    link = link.split('#')[0]
    
    # Skip empty links (pure anchors)
    if not link:
        return True
    
    # Resolve relative to the file's directory
    file_dir = os.path.dirname(file_path)
    full_path = os.path.join(file_dir, link)
    full_path = os.path.normpath(full_path)
    
    return os.path.exists(full_path)

def check_links_in_file(file_path, repo_root):
    """Check all links in a file and return broken ones."""
    broken = []
    links = extract_links(file_path)
    
    for text, url, link_type in links:
        url = url.strip()
        
        # Skip mailto links
        if url.startswith('mailto:'):
            continue
            
        # Skip anchors-only
        if url.startswith('#'):
            continue
        
        parsed = urlparse(url)
        
        # Check local file links
        if not parsed.scheme or parsed.scheme == 'file':
            if not check_local_link(url, file_path, repo_root):
                broken.append((url, text, 'Local file not found'))
        # Skip external HTTP/HTTPS links for now (would require network calls)
        # You can enable this if you want to check external links too
        # elif parsed.scheme in ['http', 'https']:
        #     # Could add requests library check here
        #     pass
    
    return broken

def main():
    """Main function to check all links."""
    try:
        repo_root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
    except:
        print("Not in a git repository")
        return 1
    
    print("Checking links in markdown and documentation files...")
    
    md_files = find_markdown_files(repo_root)
    
    if not md_files:
        print("No markdown files found.")
        return 0
    
    total_broken = 0
    files_with_broken = []
    
    for file_path in md_files:
        rel_path = os.path.relpath(file_path, repo_root)
        broken = check_links_in_file(file_path, repo_root)
        
        if broken:
            total_broken += len(broken)
            files_with_broken.append((rel_path, broken))
    
    if total_broken > 0:
        print(f"\n❌ Found {total_broken} broken link(s):\n")
        for file_path, broken_links in files_with_broken:
            print(f"  {file_path}:")
            for url, text, reason in broken_links:
                print(f"    - {url}")
                if text:
                    print(f"      Text: {text}")
                print(f"      Reason: {reason}")
            print()
        return 1
    else:
        print(f"✓ All links checked in {len(md_files)} file(s). No broken links found.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
