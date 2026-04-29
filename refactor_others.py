import re

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = re.sub(old, new, content, flags=re.DOTALL)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# explore.html
replace_in_file('templates/explore.html', [
    (r'<script>\s*function filterItems\(\) \{.*?</script>', ''),
    (r'id="search" placeholder="Search all trends..." onkeyup="filterItems\(\)"', 'id="search" placeholder="Search all trends..." onkeyup="filterItems(event)" onkeydown="if(event.key === \'Enter\') event.preventDefault();"'),
    (r'<form class="toolbar" method="get">', '<form class="toolbar toolbar-form" method="get">'),
    (r'<div class="toggle-group">', '<div class="toggle-group toolbar-toggle-group">')
])

# events.html
replace_in_file('templates/events.html', [
    (r'style="text-align: center; padding: 60px 24px;"', ''),
    (r'style="font-size: 48px; margin-bottom: 16px; opacity: 0.8;"', 'class="empty-state-icon"'),
    (r'style="font-size: 20px; color: var\(--text-main\); margin-bottom: 8px;"', 'class="empty-state-title"'),
    (r'style="color: var\(--text-muted\); font-size: 15px;"', 'class="empty-state-text"'),
    (r'<form class="toolbar" method="get">', '<form class="toolbar toolbar-form" method="get">'),
    (r'<div class="toggle-group">', '<div class="toggle-group toolbar-toggle-group">')
])

# analytics.html - Not sure what inline styles exist here, but let's just make sure <style> and <script> blocks are gone if any.
with open('templates/analytics.html', 'r', encoding='utf-8') as f:
    analytics_content = f.read()
analytics_content = re.sub(r'<style>.*?</style>', '', analytics_content, flags=re.DOTALL)
analytics_content = re.sub(r'<script>.*?</script>', '', analytics_content, flags=re.DOTALL)
with open('templates/analytics.html', 'w', encoding='utf-8') as f:
    f.write(analytics_content)

# reports.html - Same here
with open('templates/reports.html', 'r', encoding='utf-8') as f:
    reports_content = f.read()
reports_content = re.sub(r'<style>.*?</style>', '', reports_content, flags=re.DOTALL)
reports_content = re.sub(r'<script>.*?</script>', '', reports_content, flags=re.DOTALL)
with open('templates/reports.html', 'w', encoding='utf-8') as f:
    f.write(reports_content)

# base.html nav and topbar inline styles
replace_in_file('templates/base.html', [
    (r'style="display: flex; align-items: center; gap: 12px;"', 'class="flex-center-gap"'),
    (r'style="font-weight: 600; font-size: 15px; letter-spacing: -0.01em;"', 'class="nav-title"'),
    (r'style="display: flex; gap: 12px;"', 'class="flex-center-gap"'),
    (r'style="flex: 1; padding: 24px 32px 64px 32px; overflow-y: auto; position: relative;"', 'class="main-content-area"'),
    (r'style="display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 11px; margin-bottom: 16px; padding: 0 12px; color: var\(--text-muted\);"', 'class="sidebar-nav-header font-mono uppercase tracking-wider"')
])

# Append the base.html remaining styles to css
css_base_append = """
.nav-title { font-weight: 600; font-size: 15px; letter-spacing: -0.01em; }
.main-content-area { flex: 1; padding: 24px 32px 64px 32px; overflow-y: auto; position: relative; }
.sidebar-nav-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 11px; margin-bottom: 16px; padding: 0 12px; color: var(--text-muted); }
"""
with open('static/css/style.css', 'a', encoding='utf-8') as f:
    f.write(css_base_append)

print("Refactored others")
