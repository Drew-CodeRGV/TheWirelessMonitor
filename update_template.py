#!/usr/bin/env python3
"""Update index.html template to add Mark as Read buttons"""

# Read the template
with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add mark as read button to small article buttons
content = content.replace(
    'padding: 4px 8px;">📋</button>',
    'padding: 4px 8px;">📋</button>\n                                    <button onclick="markAsRead({{ story.id }})" class="btn" style="background: #27ae60; color: white; font-size: 0.7rem; padding: 4px 8px;">✓</button>'
)

# Write back
with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated index.html template with Mark as Read buttons")
