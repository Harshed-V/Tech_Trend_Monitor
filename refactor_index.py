import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    (r'style="position: absolute; top: -160px; left: 50%; width: 1100px; height: 600px; transform: translateX\(-50%\); border-radius: 50%; background: rgba\(245, 158, 11, 0.06\); filter: blur\(140px\); pointer-events: none; z-index: 0;"', 'class="hero-bg-blur"'),
    (r'style="margin-top: 24px; position: relative; z-index: 10;"', 'class="hero-section"'),
    (r'style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 40px;"', 'class="hero-layout"'),
    (r'<div style="max-width: 600px;">', '<div class="hero-content">'),
    (r'style="display: inline-flex; align-items: center; gap: 8px; border-radius: 20px; border: 1px solid var\(--border-color\); background: var\(--bg-surface\); padding: 4px 12px; margin-bottom: 24px;" class="font-mono text-\[11px\] uppercase tracking-widest text-muted"', 'class="hero-badge font-mono text-[11px] uppercase tracking-widest text-muted"'),
    (r'style="font-size: clamp\(48px, 6vw, 88px\); line-height: 0.95; letter-spacing: -0.02em;" class="font-serif"', 'class="hero-title-main font-serif"'),
    (r'style="font-style: italic; white-space: nowrap;"', 'class="hero-accent-text"'),
    (r'style="margin-top: 20px; max-width: 600px; font-size: 15px; line-height: 1.6; color: var\(--text-muted\);"', 'class="hero-subtitle"'),
    (r'style="width: 100%; max-width: 380px; display: flex; flex-direction: column; gap: 16px;"', 'class="hero-side-panel"'),
    (r'style="border-radius: 16px; border: 1px solid var\(--border-color\); background: var\(--bg-surface\); padding: 20px; box-shadow: var\(--glass-shadow\);"', 'class="glass-card"'),
    (r'style="display: flex; align-items: center; gap: 8px;" class="font-mono text-\[11px\] uppercase tracking-widest text-muted"', 'class="flex-center-gap font-mono text-[11px] uppercase tracking-widest text-muted"'),
    (r'style="margin-top: 12px; font-size: 24px; letter-spacing: -0.02em;" class="font-serif"', 'class="stat-value font-serif"'),
    (r'style="margin-top: 16px; display: flex; align-items: center; gap: 8px;" class="font-mono text-\[11px\] uppercase tracking-wider text-muted"', 'class="stat-footer font-mono text-[11px] uppercase tracking-wider text-muted"'),
    (r'style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var\(--signal\);"', 'class="signal-dot-green"'),
    (r'style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var\(--accent-primary\);"', 'class="signal-dot-purple"'),
    (r'style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;" class="font-mono text-\[11px\] uppercase tracking-widest text-muted"', 'class="stat-header font-mono text-[11px] uppercase tracking-widest text-muted"'),
    (r'<div style="display: flex; flex-direction: column; gap: 12px;">', '<div class="mini-feed-list">'),
    (r'style="display: flex; flex-direction: column; gap: 6px; padding-bottom: 12px; border-bottom: 1px solid var\(--border-color\);" class="hover-accent" onclick="window\.open\(\'{{ item\.link }}\', \'_blank\'\)" style="cursor: pointer; transition: opacity 0.2s; opacity: 0.85;" onmouseover="this\.style\.opacity=\'1\'" onmouseout="this\.style\.opacity=\'0.85\'"', 'class="mini-feed-item hover-accent" onclick="window.open(\'{{ item.link }}\', \'_blank\')"'),
    (r'<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">', '<div class="mini-feed-item-header">'),
    (r'style="font-size: 14px; font-weight: 500; margin: 0; color: var\(--text-main\); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;"', 'class="mini-feed-item-title"'),
    (r'class="font-mono text-\[10px\] text-muted" style="background: var\(--pill-bg\); padding: 2px 6px; border-radius: 6px; border: 1px solid var\(--border-color\); white-space: nowrap;"', 'class="mini-feed-item-score font-mono text-[10px] text-muted"'),
    (r'style="display: flex; align-items: center; gap: 6px; font-size: 11px;" class="font-mono uppercase tracking-wider text-muted"', 'class="mini-feed-item-meta font-mono uppercase tracking-wider text-muted"'),
    (r'style="color: var\(--accent-primary\);"', 'class="text-accent"'),
    (r'class="toolbar" method="get" style="margin-top: 64px; border-radius: 16px; padding: 8px 16px 8px 24px; background: var\(--bg-surface-solid\); border: 1px solid var\(--border-color\); display: flex; align-items: center; gap: 16px; box-shadow: var\(--glass-shadow\);"', 'class="toolbar toolbar-form" method="get"'),
    (r'style="display: flex; flex: 1; align-items: center; gap: 12px; position: relative;"', 'class="toolbar-search-wrapper"'),
    (r'style="border: none; background: transparent; box-shadow: none; flex: 1; padding: 12px 0; font-size: 15px;"', 'class="toolbar-search-input"'),
    (r'style="display: flex; align-items: center; justify-content: center; background: var\(--pill-bg\); color: var\(--pill-text\); border-radius: 6px; padding: 4px 6px; font-size: 12px; font-weight: 500; font-family: sans-serif; gap: 4px; border: 1px solid var\(--border-color\);"', 'class="toolbar-hotkey"'),
    (r'class="toggle-group" style="padding: 4px; background: var\(--pill-bg\); border: 1px solid var\(--border-color\); border-radius: 12px; display: flex; align-items: center; gap: 4px;"', 'class="toggle-group toolbar-toggle-group"'),
    (r'style="font-size: 13px;"', 'class="trend-button-small"'),
    (r'style="padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; color: var\(--text-muted\); text-decoration: none;"', 'class="reports-btn"'),
    (r'class="dashboard-section" style="margin-top: 64px;"', 'class="dashboard-section"'),
    (r'style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" class="font-mono text-\[11px\] uppercase tracking-widest text-muted"', 'class="insights-header font-mono text-[11px] uppercase tracking-widest text-muted"'),
    (r'style="font-size: 36px; letter-spacing: -0.02em; margin-bottom: 24px;" class="font-serif"', 'class="insights-title font-serif"'),
    (r'class="insight" style="text-align: left; padding: 24px; position: relative; overflow: hidden;"', 'class="insight insight-card"'),
    (r'style="position: absolute; top: -40px; right: -40px; width: 160px; height: 160px; border-radius: 50%; background: rgba\(245, 158, 11, 0.05\); filter: blur\(40px\); pointer-events: none;"', 'class="insight-glow"'),
    (r'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">', '<div class="insight-header-row">'),
    (r'class="font-mono text-\[11px\] uppercase tracking-widest text-muted" style="margin: 0;"', 'class="insight-label font-mono text-[11px] uppercase tracking-widest text-muted"'),
    (r'class="font-serif" style="font-size: 44px; line-height: 1; color: var\(--text-main\); position: relative; z-index: 2;"', 'class="insight-value font-serif"'),
    (r'class="font-mono text-\[11px\] uppercase tracking-wider text-muted" style="margin-top: 12px; position: relative; z-index: 2;"', 'class="insight-subtext font-mono text-[11px] uppercase tracking-wider text-muted"'),
    (r'<section style="margin-top: 64px;">', '<section class="feed-header-section">'),
    (r'<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">', '<div class="feed-header-row">'),
    (r'style="font-size: 36px; letter-spacing: -0.02em; margin: 0;" class="font-serif"', 'class="feed-header-title font-serif"'),
    (r'<div style="position: relative;">\n            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="position: absolute; left: 14px; top: 50%; transform: translateY\(-50%\); color: var\(--text-muted\); pointer-events: none;"', '<div class="feed-search-wrapper">\n            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="feed-search-icon"'),
    (r'style="padding-left: 36px; padding-right: 16px; padding-top: 10px; padding-bottom: 10px; width: 220px; border-radius: 99px; background: var\(--bg-surface\); border: 1px solid var\(--border-color\); color: var\(--text-main\); font-size: 13px; outline: none; transition: all 0.2s; box-shadow: var\(--card-shadow\);" class="font-mono hover-accent" onfocus="this\.style\.borderColor=\'var\(--accent-primary\)\'; this\.style\.boxShadow=\'0 0 0 2px rgba\(168, 85, 247, 0.2\)\';" onblur="this\.style\.borderColor=\'var\(--border-color\)\'; this\.style\.boxShadow=\'var\(--card-shadow\)\';"', 'class="feed-search-input font-mono hover-accent"'),
    (r'<div id="feed" style="display: flex; flex-direction: column; gap: 16px;">', '<div id="feed" class="repo-list-container">'),
]

for old, new in replacements:
    content = re.sub(old, new, content)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactored index.html")
