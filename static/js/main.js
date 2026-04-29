function isMobileNavViewport() {
    return window.innerWidth <= 1024;
}

function setMobileMenuState(isOpen) {
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("menu-toggle-btn");
    if (!sidebar || !menuButton) {
        return;
    }

    sidebar.classList.toggle("open", isOpen);
    document.body.classList.toggle("mobile-nav-open", isOpen);
    menuButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
}

function toggleMenu() {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) {
        return;
    }

    if (isMobileNavViewport()) {
        setMobileMenuState(!sidebar.classList.contains("open"));
        return;
    }

    document.body.classList.toggle("sidebar-collapsed");
}

function initNavigationMenu() {
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("menu-toggle-btn");
    const overlay = document.getElementById("mobile-nav-overlay");
    if (!sidebar || !menuButton) {
        return;
    }

    menuButton.addEventListener("click", (event) => {
        event.stopPropagation();
        // Inline onclick is the fallback path; avoid toggling twice.
        if (!menuButton.hasAttribute("onclick")) {
            toggleMenu();
        }
    });

    if (overlay) {
        overlay.addEventListener("click", () => setMobileMenuState(false));
    }

    sidebar.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            if (isMobileNavViewport()) {
                setMobileMenuState(false);
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && sidebar.classList.contains("open") && isMobileNavViewport()) {
            setMobileMenuState(false);
        }
    });

    window.addEventListener("resize", () => {
        if (!isMobileNavViewport()) {
            setMobileMenuState(false);
        }
    });
}

function initTrendCardLinks() {
    document.addEventListener("click", (event) => {
        const card = event.target.closest(".trend-card[data-card-link]");
        if (!card || event.target.closest("a")) {
            return;
        }
        const link = card.getAttribute("data-card-link");
        if (link) {
            window.open(link, "_blank");
        }
    });
}

function sendEmail() {
            alert("Report prepared. Email sending can be connected later.");
}

        function getStoredTheme() {
            try {
                return localStorage.getItem("ttm-theme");
            } catch (error) {
                return null;
            }
        }

        function persistTheme(theme) {
            try {
                localStorage.setItem("ttm-theme", theme);
            } catch (error) {
                return;
            }
        }

        function applyTheme(theme) {
            const useDarkMode = theme !== "light";
            document.body.classList.toggle("dark-mode", useDarkMode);

            const toggle = document.getElementById("toggle");
            if (toggle) {
                toggle.checked = useDarkMode;
            }
        }

        function initThemeToggle() {
            const toggle = document.getElementById("toggle");
            const storedTheme = getStoredTheme();
            const initialTheme = storedTheme === "light" ? "light" : "dark";

            applyTheme(initialTheme);

            if (!toggle) {
                return;
            }

            toggle.addEventListener("change", () => {
                const nextTheme = toggle.checked ? "dark" : "light";
                applyTheme(nextTheme);
                persistTheme(nextTheme);
            });
        }

        function escapeHtml(value) {
            return String(value || "")
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&#039;");
        }

        function updateNetworkStatus() {
            const statusText = document.getElementById("network-status-text");
            const statusDot = document.getElementById("network-status-dot");
            if (!statusText || !statusDot) {
                return;
            }

            const online = navigator.onLine;
            statusText.textContent = online ? "Signal feed live" : "Signal feed offline";
            statusDot.classList.toggle("network-status-online", online);
            statusDot.classList.toggle("network-status-offline", !online);
        }

        window.addEventListener("online", updateNetworkStatus);
        window.addEventListener("offline", updateNetworkStatus);

        function initTicker() {
            const shells = document.querySelectorAll("[data-ticker]");
            shells.forEach((shell) => {
                const track = shell.querySelector("[data-ticker-track]");
                const baseGroup = shell.querySelector("[data-ticker-group]");
                if (!track || !baseGroup) {
                    return;
                }

                track.querySelectorAll("[data-ticker-clone='true']").forEach((clone) => clone.remove());

                const viewportWidth = shell.clientWidth;
                const baseWidth = Math.ceil(baseGroup.getBoundingClientRect().width);
                if (!viewportWidth || !baseWidth) {
                    return;
                }

                const speed = Number(shell.dataset.tickerSpeed || 92);
                let renderedWidth = baseWidth;

                while (renderedWidth < viewportWidth + baseWidth) {
                    const clone = baseGroup.cloneNode(true);
                    clone.setAttribute("aria-hidden", "true");
                    clone.dataset.tickerClone = "true";
                    track.appendChild(clone);
                    renderedWidth += baseWidth;
                }

                track.style.setProperty("--ticker-distance", `-${baseWidth}px`);
                track.style.setProperty("--ticker-duration", `${(baseWidth / speed).toFixed(2)}s`);
            });
        }

        let tickerResizeTimer = null;

        function scheduleTickerInit() {
            if (tickerResizeTimer) {
                clearTimeout(tickerResizeTimer);
            }
            tickerResizeTimer = setTimeout(initTicker, 120);
        }

        // Highlight active link
        document.addEventListener("DOMContentLoaded", () => {
            initThemeToggle();
            initNavigationMenu();
            setMobileMenuState(false);
            initTrendCardLinks();
            const path = window.location.pathname;
            const links = document.querySelectorAll('.sidebar .nav-link');
            links.forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                }
            });
            updateNetworkStatus();
            initTicker();
        });

        window.addEventListener("load", initTicker);
        window.addEventListener("resize", scheduleTickerInit);

let currentPage = 1;
    let loadingMore = false;
    let hasMore = true;
    let searchTimer = null;
    let activeSearchController = null;
    let initialFeedHTML = "";
    const searchCache = new Map();
    const selectedType = window.APP_CONFIG ? window.APP_CONFIG.selectedType : 'weekly';

    function getSearchQuery() {
        const feed = document.querySelector(".js-feed-search, #feed-search, #search");
        const value = (feed && feed.value) || "";
        return value.toLowerCase();
    }

    function renderSearchResults(items) {
        const feed = document.getElementById("feed");
        const status = document.getElementById("feed-status");
        if (!feed || !status) {
            return;
        }

        feed.innerHTML = "";

        if (!items.length) {
            status.innerText = "No results found";
            hasMore = false;
            return;
        }

        for (let i = 0; i < items.length; i++) {
            feed.appendChild(createCard(items[i], i + 1));
        }

        status.innerText = `${items.length} result${items.length === 1 ? "" : "s"}`;
        currentPage = 1;
        hasMore = false;
    }

    async function runSearch(query) {
        const feed = document.getElementById("feed");
        const status = document.getElementById("feed-status");
        if (!feed || !status) {
            return;
        }

        const normalizedQuery = (query || "").trim().toLowerCase();
        if (!normalizedQuery) {
            return;
        }

        if (searchCache.has(normalizedQuery)) {
            renderSearchResults(searchCache.get(normalizedQuery));
            return;
        }

        if (activeSearchController) {
            activeSearchController.abort();
        }
        activeSearchController = new AbortController();

        status.innerText = "Searching...";

        try {
            const response = await fetch(
                `/api/trends?type=${selectedType}&page=1&q=${encodeURIComponent(normalizedQuery)}`,
                {
                    signal: activeSearchController.signal,
                    headers: { "Accept": "application/json" }
                }
            );
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (normalizedQuery !== getSearchQuery()) {
                return;
            }

            const items = Array.isArray(data.items) ? data.items : [];
            searchCache.set(normalizedQuery, items);
            renderSearchResults(items);
        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }
            status.innerText = "Search failed";
        } finally {
            activeSearchController = null;
        }
    }

    function filterItems() {
        const query = getSearchQuery();
        const feed = document.getElementById("feed");
        const status = document.getElementById("feed-status");
        if (!feed || !status) {
            return;
        }

        if (!query) {
            if (searchTimer) clearTimeout(searchTimer);
            if (activeSearchController) {
                activeSearchController.abort();
                activeSearchController = null;
            }
            feed.innerHTML = initialFeedHTML;
            status.innerText = "Scroll for more trending signals.";
            currentPage = 1;
            hasMore = true;
            return;
        }

        if (searchTimer) clearTimeout(searchTimer);
        searchTimer = setTimeout(() => runSearch(query), 300);
    }

    
    function createCard(item, index) {
        let article = document.createElement("article");
        article.className = "card trend-card";
        article.setAttribute("data-card-link", escapeHtml(item.link));
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
    }

    async function loadMoreItems() {
        if (loadingMore || !hasMore || getSearchQuery()) return;
        loadingMore = true;
        let status = document.getElementById("feed-status");
        status.innerText = "Loading more trending signals...";

        try {
            let nextPage = currentPage + 1;
            let response = await fetch(`/api/trends?type=${selectedType}&page=${nextPage}`);
            let data = await response.json();
            let feed = document.getElementById("feed");

            if (!data.items || data.items.length === 0) {
                hasMore = false;
                status.innerText = "You are caught up for now.";
                return;
            }

            let currentTotal = document.querySelectorAll('.card').length;
            for (let i = 0; i < data.items.length; i++) {
                feed.appendChild(createCard(data.items[i], currentTotal + i + 1));
            }
            currentPage = nextPage;
            status.innerText = "Scroll for more trending signals.";
        } catch (error) {
            status.innerText = "Could not load more trends. Try again.";
        } finally {
            loadingMore = false;
        }
    }

    window.addEventListener("scroll", function () {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            loadMoreItems();
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        const toolbar = document.querySelector("form.toolbar-form");
        const feed = document.getElementById("feed");
        const searchInput = document.querySelector(".js-feed-search, #feed-search, #search");
        if (feed) {
            initialFeedHTML = feed.innerHTML;
        }

        if (searchInput) {
            searchInput.addEventListener("input", filterItems);
            searchInput.addEventListener("keydown", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                }
            });
        }

        const periodToggleInputs = document.querySelectorAll(".js-type-toggle .period-toggle-input");
        periodToggleInputs.forEach((input) => {
            input.addEventListener("change", function () {
                if (!input.form) {
                    return;
                }
                if (typeof input.form.requestSubmit === "function") {
                    input.form.requestSubmit();
                    return;
                }
                input.form.submit();
            });
        });

        if (toolbar) {
            toolbar.addEventListener("submit", function (event) {
                const active = document.activeElement;
                if (active && active.id === "feed-search") {
                    event.preventDefault();
                }
            });
        }
    });
