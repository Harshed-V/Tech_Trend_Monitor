import re
import os

# 1. Update CSS File
css_append = """
/* Auto-refactored Component Classes */
.hero-bg-blur { position: absolute; top: -160px; left: 50%; width: 1100px; height: 600px; transform: translateX(-50%); border-radius: 50%; background: rgba(245, 158, 11, 0.06); filter: blur(140px); pointer-events: none; z-index: 0; }
.hero-section { margin-top: 24px; position: relative; z-index: 10; }
.hero-layout { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 40px; }
.hero-content { max-width: 600px; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; border-radius: 20px; border: 1px solid var(--border-color); background: var(--bg-surface); padding: 4px 12px; margin-bottom: 24px; }
.hero-title-main { font-size: clamp(48px, 6vw, 88px); line-height: 0.95; letter-spacing: -0.02em; }
.hero-accent-text { font-style: italic; white-space: nowrap; }
.hero-subtitle { margin-top: 20px; max-width: 600px; font-size: 15px; line-height: 1.6; color: var(--text-muted); }
.hero-side-panel { width: 100%; max-width: 380px; display: flex; flex-direction: column; gap: 16px; }
.glass-card { border-radius: 16px; border: 1px solid var(--border-color); background: var(--bg-surface); padding: 20px; box-shadow: var(--glass-shadow); }
.flex-center-gap { display: flex; align-items: center; gap: 8px; }
.stat-value { margin-top: 12px; font-size: 24px; letter-spacing: -0.02em; }
.stat-footer { margin-top: 16px; display: flex; align-items: center; gap: 8px; }
.signal-dot-green { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--signal); }
.signal-dot-purple { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--accent-primary); }
.stat-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.mini-feed-list { display: flex; flex-direction: column; gap: 12px; }
.mini-feed-item { display: flex; flex-direction: column; gap: 6px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); cursor: pointer; transition: opacity 0.2s; opacity: 0.85; }
.mini-feed-item:hover { opacity: 1; }
.mini-feed-item-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.mini-feed-item-title { font-size: 14px; font-weight: 500; margin: 0; color: var(--text-main); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.mini-feed-item-score { background: var(--pill-bg); padding: 2px 6px; border-radius: 6px; border: 1px solid var(--border-color); white-space: nowrap; }
.mini-feed-item-meta { display: flex; align-items: center; gap: 6px; font-size: 11px; }
.text-accent { color: var(--accent-primary); }
.toolbar-form { margin-top: 64px; border-radius: 16px; padding: 8px 16px 8px 24px; background: var(--bg-surface-solid); border: 1px solid var(--border-color); display: flex; align-items: center; gap: 16px; box-shadow: var(--glass-shadow); }
.toolbar-search-wrapper { display: flex; flex: 1; align-items: center; gap: 12px; position: relative; }
.toolbar-search-input { border: none; background: transparent; box-shadow: none; flex: 1; padding: 12px 0; font-size: 15px; outline: none; }
.toolbar-hotkey { display: flex; align-items: center; justify-content: center; background: var(--pill-bg); color: var(--pill-text); border-radius: 6px; padding: 4px 6px; font-size: 12px; font-weight: 500; font-family: sans-serif; gap: 4px; border: 1px solid var(--border-color); }
.toolbar-toggle-group { padding: 4px; background: var(--pill-bg); border: 1px solid var(--border-color); border-radius: 12px; display: flex; align-items: center; gap: 4px; }
.trend-button-small { font-size: 13px; }
.reports-btn { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--text-muted); text-decoration: none; }
.dashboard-section { margin-top: 64px; }
.insights-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.insights-title { font-size: 36px; letter-spacing: -0.02em; margin-bottom: 24px; }
.insight-card { text-align: left; padding: 24px; position: relative; overflow: hidden; }
.insight-glow { position: absolute; top: -40px; right: -40px; width: 160px; height: 160px; border-radius: 50%; background: rgba(245, 158, 11, 0.05); filter: blur(40px); pointer-events: none; }
.insight-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.insight-label { margin: 0; }
.insight-value { font-size: 44px; line-height: 1; color: var(--text-main); position: relative; z-index: 2; }
.insight-subtext { margin-top: 12px; position: relative; z-index: 2; }
.feed-header-section { margin-top: 64px; }
.feed-header-row { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.feed-header-label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.feed-header-title { font-size: 36px; letter-spacing: -0.02em; margin: 0; }
.feed-search-wrapper { position: relative; }
.feed-search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
.feed-search-input { padding-left: 36px; padding-right: 16px; padding-top: 10px; padding-bottom: 10px; width: 220px; border-radius: 99px; background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-main); font-size: 13px; outline: none; transition: all 0.2s; box-shadow: var(--card-shadow); }
.feed-search-input:focus { border-color: var(--accent-primary); box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.2); }
.repo-list-container { display: flex; flex-direction: column; gap: 16px; }

/* Empty States */
.empty-state { text-align: center; padding: 60px 24px; }
.empty-state-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.8; }
.empty-state-title { font-size: 20px; color: var(--text-main); margin-bottom: 8px; }
.empty-state-text { color: var(--text-muted); font-size: 15px; }

/* Global nav links */
.nav-link-base { color: inherit; text-decoration: none; }
"""

with open('static/css/style.css', 'a', encoding='utf-8') as f:
    f.write(css_append)


# 2. Refactor main.js createCard
main_js_path = 'static/js/main.js'
with open(main_js_path, 'r', encoding='utf-8') as f:
    main_js = f.read()

# I will replace the createCard string in main.js with the refactored one.
new_createCard = """
    function createCard(item, index) {
        let article = document.createElement("article");
        article.className = "card trend-card";
        article.setAttribute("onclick", `if (!event.target.closest('a')) window.open('${escapeHtml(item.link)}', '_blank');`);
        article.innerHTML = `
            <div class="card-ambient-glow"></div>
            <div class="card-header-row">
                <div class="card-content">
                    <div class="card-meta-row">
                        <span class="font-mono text-[11px] text-muted">#${String(index).padStart(2, '0')}</span>
                        <span class="card-dot"></span>
                        <span class="font-mono text-[11px] uppercase tracking-wider text-muted">${escapeHtml(item.source)}</span>
                    </div>
                    <h3 class="card-title">
                        <a href="${escapeHtml(item.link)}" target="_blank">${escapeHtml(item.title)}</a>
                    </h3>
                    <p class="card-desc">
                        ${escapeHtml(item.description || "No description available.")}
                    </p>
                </div>
                <div class="card-spark-container">
                    <svg viewBox="0 0 120 32" class="card-spark-svg">
                        <defs>
                            <linearGradient id="spark-js-${index}" x1="0" x2="0" y1="0" y2="1">
                                <stop offset="0%" stop-color="var(--accent-primary)" stop-opacity="0.6" />
                                <stop offset="100%" stop-color="var(--accent-primary)" stop-opacity="0" />
                            </linearGradient>
                        </defs>
                        <path d="M0,24 L15,18 L30,22 L45,12 L60,16 L75,8 L90,14 L105,4 L120,10" fill="none" stroke="var(--accent-primary)" stroke-width="1.5" />
                        <path d="M0,24 L15,18 L30,22 L45,12 L60,16 L75,8 L90,14 L105,4 L120,10 L120,32 L0,32 Z" fill="url(#spark-js-${index})" />
                    </svg>
                </div>
            </div>
            <div class="card-why-box">
                <p class="card-why-text">
                    <span class="font-mono text-[11px] uppercase tracking-wider card-why-label">Why trending — </span>
                    ${escapeHtml(item.why_trending)}
                </p>
            </div>
            <div class="card-footer-row">
                <span class="card-pill-muted font-mono text-[11px] uppercase tracking-widest text-muted">
                    ${item.source.toLowerCase() === 'github' ? 
                        `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.03c3.15-.38 6.5-1.4 6.5-7.17a5.2 5.2 0 0 0-1.5-3.8c.16-.4.65-2-.15-3.8 0 0-1.2-.38-3.9 1.4a13.3 13.3 0 0 0-7 0C6.2 2.5 5 2.88 5 2.88c-.8 1.8-.3 3.4-.15 3.8A5.2 5.2 0 0 0 3 9.8c0 5.77 3.35 6.79 6.5 7.17A4.8 4.8 0 0 0 8 20v2"></path></svg>` : 
                        `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`
                    }
                    ${escapeHtml(item.source)}
                </span>
                <span class="card-pill-accent font-mono text-[11px] uppercase tracking-widest">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"></line><line x1="4" y1="15" x2="20" y2="15"></line><line x1="10" y1="3" x2="8" y2="21"></line><line x1="16" y1="3" x2="14" y2="21"></line></svg>
                    ${escapeHtml(item.topic)}
                </span>
                <span class="card-pill-muted font-mono text-[11px] uppercase tracking-widest text-muted">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    ${item.score} ${escapeHtml(item.score_label)}
                </span>
                <a href="${escapeHtml(item.link)}" target="_blank" class="card-btn-open font-mono text-[11px] uppercase tracking-widest hover-accent">
                    Open
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
                </a>
            </div>
        `;
        return article;
    }"""

import re
main_js = re.sub(r'function createCard\(item, index\).*?return article;\n    }', new_createCard, main_js, flags=re.DOTALL)

with open(main_js_path, 'w', encoding='utf-8') as f:
    f.write(main_js)

print("Refactored main.js")
