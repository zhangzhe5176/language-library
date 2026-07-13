(function initLanguageLibraryApp() {
  "use strict";

  const LEVEL_IDS = ["n1", "n2", "n3", "n4", "n5"];
  const LEVEL_COPY = {
    n1: { tone: "最高阶语境、论文表达与抽象词汇", eyebrow: "最高阶阅读与语境" },
    n2: { tone: "职场与社会表达的进阶训练", eyebrow: "进阶阅读与自然表达" },
    n3: { tone: "从基础会话过渡到自然表达", eyebrow: "中级阅读与生活表达" },
    n4: { tone: "生活场景、短句理解和常用词", eyebrow: "基础阅读与日常会话" },
    n5: { tone: "入门对话、发音和基础词汇", eyebrow: "入门阅读与基础表达" },
  };
  const page = document.body.dataset.page || "portal";
  const currentLevel = document.body.dataset.level || "";
  const basePath = document.body.dataset.base || ".";
  const app = document.querySelector("#app");
  const dataCache = new Map();
  const storeCache = new Map();
  let activeAudio = null;

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function levelLabel(level) {
    return String(level).toUpperCase();
  }

  function rootUrl(path) {
    return `${basePath}/${path}`;
  }

  function portalUrl() {
    return rootUrl("index.html");
  }

  function japaneseUrl() {
    return rootUrl("levels/japanese/index.html");
  }

  function levelUrl(level, name = "index.html") {
    return rootUrl(`levels/${level}/${name}`);
  }

  function storyUrl(level, story) {
    if (!story) return levelUrl(level, "topics.html");
    return `${levelUrl(level, "topic.html")}?topic=${story.topicId}&story=${story.id}`;
  }

  function topicUrl(level, topicId, storyId = "") {
    const storyPart = storyId ? `&story=${storyId}` : "";
    return `${levelUrl(level, "topic.html")}?topic=${topicId}${storyPart}`;
  }

  function safeLocalStorage() {
    try {
      return window.localStorage;
    } catch (error) {
      const memory = new Map();
      return {
        getItem(key) { return memory.has(key) ? memory.get(key) : null; },
        setItem(key, value) { memory.set(key, String(value)); },
      };
    }
  }

  function normalizeLevelData(level, raw) {
    const stories = Array.isArray(raw?.stories) ? raw.stories : [];
    const topics = Array.isArray(raw?.topics) ? raw.topics : [];
    return {
      ...raw,
      level,
      label: raw?.label || levelLabel(level),
      audioBase: raw?.audioBase || (level === "n3" ? "assets/audio" : `assets/${level}/audio`),
      topics,
      stories,
      numberedWordCount: stories.reduce((sum, story) => sum + (story.vocab?.length || 0), 0),
    };
  }

  function preloadedData(level) {
    if (level === "n3" && window.N3_DATA) return window.N3_DATA;
    if (window.LEVEL_DATA?.level === level) return window.LEVEL_DATA;
    return null;
  }

  function injectDataScript(level) {
    return new Promise((resolve, reject) => {
      if (level === "n3") delete window.N3_DATA;
      else delete window.LEVEL_DATA;
      const script = document.createElement("script");
      script.src = rootUrl(`data/${level}-data.js`);
      script.dataset.levelData = level;
      script.onload = () => {
        const raw = level === "n3" ? window.N3_DATA : window.LEVEL_DATA;
        if (raw) resolve(raw);
        else reject(new Error(`${levelLabel(level)} 数据文件未提供可用内容。`));
      };
      script.onerror = () => reject(new Error(`${levelLabel(level)} 数据文件加载失败。`));
      document.head.appendChild(script);
    });
  }

  async function loadLevelData(level) {
    if (dataCache.has(level)) return dataCache.get(level);
    const raw = preloadedData(level) || await injectDataScript(level);
    const normalized = normalizeLevelData(level, raw);
    dataCache.set(level, normalized);
    return normalized;
  }

  async function loadAllLevels() {
    const result = [];
    for (const level of LEVEL_IDS) result.push(await loadLevelData(level));
    return result;
  }

  function levelStore(level) {
    if (!storeCache.has(level)) {
      const stateApi = window.LanguageLibraryState;
      if (!stateApi) throw new Error("学习状态组件未加载。");
      storeCache.set(level, stateApi.createLevelStorage(safeLocalStorage(), level));
    }
    return storeCache.get(level);
  }

  function validStorySet(data) {
    return new Set(data.stories.map((story) => String(story.id)));
  }

  function cleanStoredSet(set, data) {
    const valid = validStorySet(data);
    return new Set([...set].filter((id) => valid.has(String(id))));
  }

  function vocabCount(data) {
    return data.stories.reduce((sum, story) => sum + (story.vocab?.length || 0), 0);
  }

  function topicStories(data, topicId) {
    return data.stories.filter((story) => Number(story.topicId) === Number(topicId)).sort((a, b) => a.id - b.id);
  }

  function topicFor(data, story) {
    return data.topics.find((topic) => Number(topic.id) === Number(story?.topicId));
  }

  function progressFor(stories, learnedSet) {
    const total = stories.length;
    const learned = stories.filter((story) => learnedSet.has(String(story.id))).length;
    return { learned, total, percent: total ? Math.round((learned / total) * 100) : 0 };
  }

  function progressMarkup(progress, label = "学习进度") {
    return `
      <div class="progress" aria-label="${escapeHtml(label)} ${progress.learned}/${progress.total}">
        <span style="--value:${progress.percent}%"></span>
      </div>
      <div class="progressMeta"><span>${escapeHtml(label)}</span><strong>${progress.learned}/${progress.total} · ${progress.percent}%</strong></div>
    `;
  }

  function continueStory(data, store) {
    const recentId = String(store.recent?.storyId || "");
    return data.stories.find((story) => String(story.id) === recentId) || data.stories[0] || null;
  }

  function navMarkup(active, level = "", data = null, store = null) {
    const links = [{ id: "portal", label: "语言", href: portalUrl() }];
    if (active !== "portal") links.push({ id: "japanese", label: "日语", href: japaneseUrl() });
    if (level) {
      const currentStory = data && store ? continueStory(data, store) : null;
      links.push(
        { id: "level", label: levelLabel(level), href: levelUrl(level) },
        { id: "topics", label: "Topics", href: levelUrl(level, "topics.html") },
        { id: "lesson", label: "学习", href: currentStory ? storyUrl(level, currentStory) : levelUrl(level, "topics.html") },
      );
    }
    return `
      <header class="topbar">
        <a class="brand" href="${portalUrl()}"><span class="brandMark">語</span><span>Language Library</span></a>
        <nav class="nav nav-${links.length}" aria-label="主导航">
          ${links.map((link) => `<a class="${active === link.id ? "active" : ""}" ${active === link.id ? 'aria-current="page"' : ""} href="${link.href}">${link.label}</a>`).join("")}
        </nav>
      </header>
    `;
  }

  function renderPage(content, { active = "portal", level = "", data = null, store = null, bottomBar = false, modal = "" } = {}) {
    app.innerHTML = `
      <div class="page ${bottomBar ? "hasBottomBar" : ""}">
        <div class="shell">
          ${navMarkup(active, level, data, store)}
          ${content}
        </div>
      </div>
      ${modal}
    `;
  }

  function loadingPage(active = "portal", level = "") {
    renderPage(`<section class="panel loadingState" aria-live="polite"><span class="loadingDot"></span><p>正在整理学习内容…</p></section>`, { active, level });
  }

  function renderError(message, active = "portal", level = "") {
    renderPage(`
      <section class="panel errorState">
        <span class="eyebrow">暂时无法打开</span>
        <h1>学习内容加载失败</h1>
        <p>${escapeHtml(message)}</p>
        <a class="btn primary" href="${level ? levelUrl(level) : portalUrl()}">返回首页</a>
      </section>
    `, { active, level });
  }

  function stat(value, label) {
    return `<div class="miniStat"><strong>${value}</strong><span>${escapeHtml(label)}</span></div>`;
  }

  function renderPortal() {
    const languages = [
      { symbol: "日", name: "日语", path: "JLPT N1–N5", description: "从真实短文、音频和词汇开始持续学习。", available: true },
      { symbol: "En", name: "英语", path: "Vocabulary & Reading", description: "英文词汇、阅读和听力路径。" },
      { symbol: "한", name: "韩语", path: "TOPIK Path", description: "韩语等级与场景学习路径。" },
      { symbol: "Fr", name: "法语", path: "CEFR Path", description: "法语分阶段阅读与听力路径。" },
      { symbol: "Es", name: "西班牙语", path: "CEFR Path", description: "西班牙语分阶段学习路径。" },
    ];
    renderPage(`
      <section class="hero">
        <div>
          <span class="eyebrow">多语言学习入口</span>
          <h1>从语言开始，建立持续学习的节奏。</h1>
          <p class="lead">选择一门语言，在阅读、听力和词汇之间反复练习，让每次学习都能自然衔接上一次进度。</p>
          <div class="actions"><a class="btn primary" href="${japaneseUrl()}">进入日语学习</a></div>
        </div>
        <aside class="panel heroPanel">
          <div class="jpLine heroJapanese">今日も、<br />一つずつ深く読む。</div>
          <p>围绕内容、进度和连续学习，一步一步积累理解。</p>
          <div class="miniStats">${stat(5, "语言入口")}${stat(5, "JLPT 等级")}${stat(1, "统一学习线")}</div>
        </aside>
      </section>
      <div class="sectionHead">
        <div><span class="kicker">Language paths</span><h2>选择要学习的语言</h2></div>
        <p>日语内容已开放，其他语言正在规划中。</p>
      </div>
      <section class="grid languageGrid" aria-label="语言入口">
        ${languages.map((language, index) => {
          const body = `
            <span class="languageSymbol">${language.symbol}</span>
            <span><span class="kicker">${language.path}</span><h3>${language.name}</h3><p>${language.description}</p></span>
            <span class="languageStatus">${language.available ? "可开始学习" : "规划中"}</span>`;
          return language.available
            ? `<a class="card languageCard available" style="--delay:${index * 45}ms" href="${japaneseUrl()}">${body}</a>`
            : `<article class="card languageCard planned" style="--delay:${index * 45}ms">${body}</article>`;
        }).join("")}
      </section>
    `, { active: "portal" });
    document.title = "Language Library · 语言学习入口";
  }

  function levelSummary(data, store) {
    const learned = cleanStoredSet(store.learned, data);
    const favorites = cleanStoredSet(store.favorites, data);
    const recent = continueStory(data, store);
    return {
      progress: progressFor(data.stories, learned),
      favoriteCount: favorites.size,
      recent,
      recentLabel: store.recent && recent ? recent.title : "尚未开始",
    };
  }

  function japaneseLevelCard(data, store, index) {
    const summary = levelSummary(data, store);
    const label = levelLabel(data.level);
    return `
      <article class="card levelCard" style="--delay:${index * 45}ms">
        <div class="levelCardTop"><span class="levelBadge">${label}</span><span class="meta">${LEVEL_COPY[data.level].tone}</span></div>
        <h3><a href="${levelUrl(data.level)}">${label} 学习库</a></h3>
        <p>${data.topics.length} Topics · ${data.stories.length} 条 · ${vocabCount(data)} 词</p>
        ${progressMarkup(summary.progress)}
        <div class="levelMeta"><span>${summary.favoriteCount} 收藏</span><span>最近：${escapeHtml(summary.recentLabel)}</span></div>
        <div class="actions compactActions">
          <a class="btn" href="${levelUrl(data.level)}">进入 ${label}</a>
          <a class="btn primary" href="${storyUrl(data.level, summary.recent)}">${store.recent ? "继续学习" : "从第一篇开始"}</a>
        </div>
      </article>
    `;
  }

  async function renderJapanese() {
    loadingPage("japanese");
    const levels = await loadAllLevels();
    const summaries = levels.map((data) => ({ data, store: levelStore(data.level) }));
    const totalTopics = levels.reduce((sum, data) => sum + data.topics.length, 0);
    const totalStories = levels.reduce((sum, data) => sum + data.stories.length, 0);
    const totalVocab = levels.reduce((sum, data) => sum + vocabCount(data), 0);
    const mostRecent = summaries
      .filter(({ store }) => store.recent?.updatedAt)
      .sort((a, b) => String(b.store.recent.updatedAt).localeCompare(String(a.store.recent.updatedAt)))[0];
    const continueData = mostRecent?.data || levels[0];
    const continueStore = mostRecent?.store || levelStore(continueData.level);
    const recentStory = continueStory(continueData, continueStore);

    renderPage(`
      <section class="hero">
        <div>
          <span class="eyebrow">日本語 · N1–N5</span>
          <h1>把五个等级组织成一条连续学习线。</h1>
          <p class="lead">从适合当前程度的等级开始，按 Topic 阅读、听音频、记词汇，并随时回到上次的学习位置。</p>
          <div class="actions">
            <a class="btn primary" href="${storyUrl(continueData.level, recentStory)}">${mostRecent ? `继续学习 ${levelLabel(continueData.level)}` : "从 N1 第一篇开始"}</a>
            <a class="btn" href="${levelUrl("n1")}">查看等级内容</a>
          </div>
        </div>
        <aside class="panel heroPanel">
          <div class="jpLine heroJapanese">読む・聴く・覚える</div>
          <p>阅读理解、听力输入和词汇积累相互衔接。</p>
          <div class="miniStats">${stat(totalTopics, "Topics")}${stat(totalStories, "故事")}${stat(totalVocab, "词汇")}</div>
        </aside>
      </section>
      <div class="sectionHead"><div><span class="kicker">JLPT levels</span><h2>选择学习等级</h2></div><p>进度、收藏和最近学习都保存在当前浏览器中。</p></div>
      <section class="grid levelGrid">${summaries.map(({ data, store }, index) => japaneseLevelCard(data, store, index)).join("")}</section>
    `, { active: "japanese" });
    document.title = "日语学习 · Language Library";
  }

  function storySearchText(story) {
    return [
      story.id,
      story.title,
      ...(story.japanese || []).map((line) => `${line.speaker || ""} ${line.text || ""}`),
      ...(story.naturalChinese || []),
      ...(story.originalChinese || []),
      ...(story.vocab || []).flat(),
      ...(story.vocabRaw || []),
    ].join(" ").toLowerCase();
  }

  function topicSearchText(data, topic) {
    return [
      topic.id,
      topic.title,
      topic.reading,
      topic.english,
      ...topicStories(data, topic.id).map(storySearchText),
    ].join(" ").toLowerCase();
  }

  function topicStatus(progress) {
    if (!progress.learned) return { id: "new", label: "未学" };
    if (progress.learned === progress.total) return { id: "done", label: "已完成" };
    return { id: "learning", label: "学习中" };
  }

  function topicCard(data, topic, store, index = 0) {
    const list = topicStories(data, topic.id);
    const learned = cleanStoredSet(store.learned, data);
    const favorites = cleanStoredSet(store.favorites, data);
    const progress = progressFor(list, learned);
    const status = topicStatus(progress);
    const favorite = list.some((story) => favorites.has(String(story.id)));
    const firstUnlearned = list.find((story) => !learned.has(String(story.id))) || list[0];
    return `
      <article class="card topicCard" data-topic-id="${topic.id}" data-topic-status="${status.id}" data-topic-favorite="${favorite}" style="--delay:${index * 24}ms">
        <div class="topicTop">
          <div><span class="kicker">Topic ${String(topic.id).padStart(2, "0")}</span><h3>${escapeHtml(topic.title)}</h3><div class="meta">${escapeHtml(topic.reading || topic.english || "")}</div></div>
          <span class="badge ${status.id}">${status.label}</span>
        </div>
        <p>${list.length} 条 · ${list.reduce((sum, story) => sum + (story.vocab?.length || 0), 0)} 词${favorite ? " · 已收藏" : ""}</p>
        ${progressMarkup(progress, "Topic 进度")}
        <a class="btn" href="${storyUrl(data.level, firstUnlearned)}">${progress.learned ? "继续本 Topic" : "开始学习"}</a>
      </article>
    `;
  }

  function topicExplorer(data, store, heading = "Topic 目录") {
    return `
      <section class="topicExplorer">
        <div class="sectionHead"><div><span class="kicker">${levelLabel(data.level)} contents</span><h2>${heading}</h2></div><p><span data-visible-topic-count>${data.topics.length}</span> / ${data.topics.length} Topics</p></div>
        <div class="toolbar">
          <label class="search">⌕ <input type="search" placeholder="搜索 Topic、日文、中文或词汇" data-topic-search autocomplete="off" /></label>
          <div class="chipRow" role="group" aria-label="Topic 筛选">
            <button class="chip active" type="button" data-topic-filter="all">全部</button>
            <button class="chip" type="button" data-topic-filter="favorites">收藏</button>
            <button class="chip" type="button" data-topic-filter="learned">已学</button>
            <button class="chip" type="button" data-topic-filter="unlearned">未学</button>
          </div>
        </div>
        <div class="grid topicGrid" data-topic-list>${data.topics.map((topic, index) => topicCard(data, topic, store, index)).join("")}</div>
        <div class="panel emptyState" data-topic-empty hidden><h3>没有匹配的 Topic</h3><p>请清空搜索词或切换筛选状态。</p></div>
      </section>
    `;
  }

  function bindTopicExplorer(data) {
    const search = document.querySelector("[data-topic-search]");
    const buttons = [...document.querySelectorAll("[data-topic-filter]")];
    const cards = [...document.querySelectorAll("[data-topic-list] [data-topic-id]")];
    const count = document.querySelector("[data-visible-topic-count]");
    const empty = document.querySelector("[data-topic-empty]");
    const requested = new URLSearchParams(window.location.search).get("filter");
    let filter = ["favorites", "learned", "unlearned"].includes(requested) ? requested : "all";

    function apply() {
      const query = String(search?.value || "").trim().toLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const topic = data.topics.find((item) => String(item.id) === card.dataset.topicId);
        const queryMatch = !query || topicSearchText(data, topic).includes(query);
        const status = card.dataset.topicStatus;
        const filterMatch = filter === "all"
          || (filter === "favorites" && card.dataset.topicFavorite === "true")
          || (filter === "learned" && (status === "learning" || status === "done"))
          || (filter === "unlearned" && status !== "done");
        card.hidden = !(queryMatch && filterMatch);
        if (!card.hidden) visible += 1;
      });
      if (count) count.textContent = String(visible);
      if (empty) empty.hidden = visible !== 0;
      buttons.forEach((button) => {
        const active = button.dataset.topicFilter === filter;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
      });
    }

    search?.addEventListener("input", apply);
    buttons.forEach((button) => button.addEventListener("click", () => {
      filter = button.dataset.topicFilter;
      apply();
    }));
    apply();
  }

  async function renderLevelHome() {
    loadingPage("level", currentLevel);
    const data = await loadLevelData(currentLevel);
    const store = levelStore(currentLevel);
    const summary = levelSummary(data, store);
    const recentTopic = topicFor(data, summary.recent);
    renderPage(`
      <section class="hero">
        <div>
          <span class="eyebrow">${levelLabel(currentLevel)} · ${LEVEL_COPY[currentLevel].eyebrow}</span>
          <h1>围绕 Topic 推进，随时回到最近一篇。</h1>
          <p class="lead">${LEVEL_COPY[currentLevel].tone}。先听音频，再读日文，需要时展开中文和词汇。</p>
          <div class="actions">
            <a class="btn primary" href="${storyUrl(currentLevel, summary.recent)}">${store.recent ? `继续：${escapeHtml(summary.recent.title)}` : "从第一篇开始"}</a>
            <a class="btn" href="${levelUrl(currentLevel, "topics.html")}">查看全部 Topic</a>
          </div>
        </div>
        <aside class="panel heroPanel">
          <span class="kicker">学习概况</span>
          <div class="miniStats">${stat(data.topics.length, "Topics")}${stat(data.stories.length, "故事")}${stat(vocabCount(data), "词汇")}</div>
          ${progressMarkup(summary.progress)}
          <p>${summary.favoriteCount} 条收藏 · ${store.recent ? `最近学习 ${escapeHtml(recentTopic?.title || "")}` : "尚无学习记录"}</p>
        </aside>
      </section>
      ${topicExplorer(data, store)}
    `, { active: "level", level: currentLevel, data, store });
    bindTopicExplorer(data);
    document.title = `${levelLabel(currentLevel)} 学习首页 · Language Library`;
  }

  async function renderTopicsPage() {
    loadingPage("topics", currentLevel);
    const data = await loadLevelData(currentLevel);
    const store = levelStore(currentLevel);
    renderPage(`
      <section class="pageHero">
        <span class="eyebrow">${levelLabel(currentLevel)} · Topic 目录</span>
        <h1>按主题推进，把每一篇都放进清晰的语境中。</h1>
        <p class="lead">可按 Topic、日文、中文或词汇搜索，也可只看收藏、已学或未学内容。</p>
      </section>
      ${topicExplorer(data, store, `全部 ${levelLabel(currentLevel)} Topics`)}
    `, { active: "topics", level: currentLevel, data, store });
    bindTopicExplorer(data);
    document.title = `${levelLabel(currentLevel)} Topic 目录 · Language Library`;
  }

  function resolveStory(data) {
    const params = new URLSearchParams(window.location.search);
    const legacyTopic = Number(document.body.dataset.topic || 0);
    const topicId = Number(params.get("topic") || legacyTopic || data.topics[0]?.id || 0);
    const requestedStoryId = Number(params.get("story") || 0);
    const requested = requestedStoryId ? data.stories.find((story) => story.id === requestedStoryId) : null;
    if (requested && (!topicId || Number(requested.topicId) === topicId)) return requested;
    return topicStories(data, topicId)[0] || data.stories[0] || null;
  }

  function japaneseMarkup(story) {
    return (story.japanese || []).map((line) => `
      <p>${line.speaker ? `<span class="speaker">${escapeHtml(line.speaker)}</span>` : ""}${escapeHtml(line.text || "")}</p>
    `).join("") || `<p class="mutedText">暂无可显示的日文。</p>`;
  }

  function translationMarkup(lines, emptyText) {
    return (lines || []).map((line) => `<p>${escapeHtml(line)}</p>`).join("") || `<p class="mutedText">${emptyText}</p>`;
  }

  function vocabMarkup(story) {
    if (!story.vocab?.length) return `<p class="mutedText">暂无结构化词汇。</p>`;
    return `<ul class="vocabList">${story.vocab.map((row) => `
      <li class="vocabItem">
        <strong class="vocabNo">${escapeHtml(row[0])}</strong>
        <span><b>${escapeHtml(row[1])}</b><br /><span class="kana">${escapeHtml(row[2] || "—")}</span></span>
        <span class="pos">${escapeHtml(row[3] || "")} · ${escapeHtml(row[4] || "")}</span>
      </li>
    `).join("")}</ul>`;
  }

  function sourceMarkup(story) {
    if (!story.images?.length) return `<p class="mutedText">暂无可查看的原书图片。</p>`;
    return `<div class="sourceGrid">${story.images.map((image, index) => `
      <button class="sourcePreview" type="button" data-source-image="${rootUrl(image)}" data-source-alt="No. ${story.id} 原书图片 ${index + 1}">
        <img loading="lazy" src="${rootUrl(image)}" alt="No. ${story.id} 原书图片 ${index + 1}" />
        <span>点击放大</span>
      </button>
    `).join("")}</div>`;
  }

  function navButton(story, label, direction, level) {
    if (!story) return `<span class="btn disabled" aria-disabled="true">${direction === "previous" ? "← " : ""}${label}${direction === "next" ? " →" : ""}</span>`;
    return `<a class="btn ${direction === "next" ? "primary" : ""}" data-story-nav="${direction}" href="${storyUrl(level, story)}">${direction === "previous" ? "← " : ""}${label}${direction === "next" ? " →" : ""}</a>`;
  }

  function imageModalMarkup() {
    return `
      <div class="imageModal" data-image-modal hidden role="dialog" aria-modal="true" aria-label="原书图片大图">
        <button class="modalBackdrop" type="button" data-image-close aria-label="关闭原图"></button>
        <div class="modalPanel">
          <button class="modalClose" type="button" data-image-close aria-label="关闭原图">×</button>
          <img data-modal-image alt="" />
        </div>
      </div>
    `;
  }

  async function renderLessonPage() {
    loadingPage("lesson", currentLevel);
    const data = await loadLevelData(currentLevel);
    const store = levelStore(currentLevel);
    const story = resolveStory(data);
    if (!story) throw new Error(`${levelLabel(currentLevel)} 没有可显示的学习条目。`);
    const ordered = [...data.stories].sort((a, b) => a.id - b.id);
    const index = ordered.findIndex((item) => item.id === story.id);
    const previous = index > 0 ? ordered[index - 1] : null;
    const next = index >= 0 && index < ordered.length - 1 ? ordered[index + 1] : null;
    const topic = topicFor(data, story);
    store.setRecent({ storyId: story.id, topicId: story.topicId, updatedAt: new Date().toISOString() });
    const learned = store.learned.has(String(story.id));
    const favorite = store.favorites.has(String(story.id));
    const audioSrc = rootUrl(`${data.audioBase}/${story.audio}`);

    renderPage(`
      <section class="lessonLayout">
        <article class="panel lessonCard">
          <div class="lessonHeader">
            <div>
              <span class="eyebrow">${levelLabel(currentLevel)} · Topic ${story.topicId} ${escapeHtml(topic?.title || "")} · #${story.id}</span>
              <h1>${escapeHtml(story.title)}</h1>
            </div>
            <button class="audioButton" type="button" data-audio-toggle aria-label="播放官方音频" aria-pressed="false"><span data-audio-icon>▶</span><span class="srOnly" data-audio-label>播放音频</span></button>
          </div>
          <div class="audioStatus" aria-live="polite" data-audio-status>官方音频 · ${escapeHtml(story.audio)}</div>
          <audio data-audio-element preload="metadata" src="${audioSrc}"></audio>
          <div class="japaneseText">${japaneseMarkup(story)}</div>
          <details class="toggleBlock" open data-section="chinese">
            <summary class="toggleHead">中文理解 <span>展开 / 收起</span></summary>
            <div class="toggleBody">
              <div class="translationText">${translationMarkup(story.naturalChinese, "暂无中文理解。")}</div>
              <details class="originalTranslation"><summary>原书中文</summary><div>${translationMarkup(story.originalChinese, "暂无原书中文。")}</div></details>
            </div>
          </details>
          <details class="toggleBlock" open data-section="vocab">
            <summary class="toggleHead">词汇 <span>${story.vocab?.length || 0} 词</span></summary>
            <div class="toggleBody">${vocabMarkup(story)}</div>
          </details>
          <section class="lessonNavigation" aria-label="上一篇和下一篇">
            ${navButton(previous, "上一篇", "previous", currentLevel)}
            <a class="btn ghost" href="${levelUrl(currentLevel, "topics.html")}">返回 Topic 目录</a>
            ${navButton(next, "下一篇", "next", currentLevel)}
          </section>
        </article>
        <aside class="sideStack">
          <section class="panel sideCard">
            <h3>学习状态</h3>
            <p>已学、收藏和最近学习位置会保存在当前浏览器中。</p>
            <div class="chipRow">
              <button class="chip ${learned ? "active" : ""}" type="button" data-learn-toggle aria-pressed="${learned}">${learned ? "✓ 已学" : "标记已学"}</button>
              <button class="chip ${favorite ? "active" : ""}" type="button" data-favorite-toggle aria-pressed="${favorite}">${favorite ? "★ 已收藏" : "☆ 收藏"}</button>
            </div>
          </section>
          <section class="panel sideCard">
            <h3>原书图片</h3>
            ${sourceMarkup(story)}
          </section>
          <section class="panel sideCard">
            <h3>当前位置</h3>
            <p>${levelLabel(currentLevel)} · Topic ${story.topicId} · No. ${story.id} / ${data.stories.length}</p>
            <a class="btn ghost" href="${levelUrl(currentLevel, "topics.html")}">← 返回目录</a>
          </section>
        </aside>
      </section>
      <nav class="bottomBar" aria-label="手机端学习操作">
        <a href="${levelUrl(currentLevel, "topics.html")}">目录</a>
        <button type="button" data-audio-toggle data-audio-mini><span data-audio-label>播放</span></button>
        <button type="button" data-favorite-toggle data-favorite-mini>${favorite ? "已收藏" : "收藏"}</button>
        <button type="button" data-learn-toggle data-learn-mini>${learned ? "已学" : "未学"}</button>
      </nav>
    `, { active: "lesson", level: currentLevel, data, store, bottomBar: true, modal: imageModalMarkup() });

    bindLessonInteractions({ data, store, story });
    document.title = `${story.title} · ${levelLabel(currentLevel)} · Language Library`;
  }

  function bindLessonInteractions({ store, story }) {
    const storyId = String(story.id);
    const learnedButtons = [...document.querySelectorAll("[data-learn-toggle]")];
    const favoriteButtons = [...document.querySelectorAll("[data-favorite-toggle]")];

    function updateStateButtons() {
      const learned = store.learned.has(storyId);
      const favorite = store.favorites.has(storyId);
      learnedButtons.forEach((button) => {
        button.classList.toggle("active", learned);
        button.setAttribute("aria-pressed", String(learned));
        button.textContent = button.hasAttribute("data-learn-mini") ? (learned ? "已学" : "未学") : (learned ? "✓ 已学" : "标记已学");
      });
      favoriteButtons.forEach((button) => {
        button.classList.toggle("active", favorite);
        button.setAttribute("aria-pressed", String(favorite));
        button.textContent = button.hasAttribute("data-favorite-mini") ? (favorite ? "已收藏" : "收藏") : (favorite ? "★ 已收藏" : "☆ 收藏");
      });
    }

    learnedButtons.forEach((button) => button.addEventListener("click", () => {
      store.toggleLearned(storyId);
      updateStateButtons();
    }));
    favoriteButtons.forEach((button) => button.addEventListener("click", () => {
      store.toggleFavorite(storyId);
      updateStateButtons();
    }));
    bindAudio();
    bindImageModal();
  }

  function bindAudio() {
    const audio = document.querySelector("[data-audio-element]");
    const buttons = [...document.querySelectorAll("[data-audio-toggle]")];
    const status = document.querySelector("[data-audio-status]");
    if (!audio || !buttons.length) return;
    if (activeAudio && activeAudio !== audio) {
      activeAudio.pause();
      activeAudio.currentTime = 0;
    }
    activeAudio = audio;

    function setAudioState(name, message) {
      buttons.forEach((button) => {
        button.classList.toggle("playing", name === "playing");
        button.classList.toggle("loading", name === "loading");
        button.setAttribute("aria-pressed", String(name === "playing"));
        const label = button.querySelector("[data-audio-label]");
        const icon = button.querySelector("[data-audio-icon]");
        if (label) label.textContent = name === "playing" ? (button.hasAttribute("data-audio-mini") ? "暂停" : "暂停音频") : (button.hasAttribute("data-audio-mini") ? "播放" : "播放音频");
        if (icon) icon.textContent = name === "playing" ? "Ⅱ" : (name === "loading" ? "…" : "▶");
      });
      if (status && message) status.textContent = message;
    }

    buttons.forEach((button) => button.addEventListener("click", async () => {
      if (!audio.paused) {
        audio.pause();
        return;
      }
      setAudioState("loading", "正在加载官方音频…");
      try {
        await audio.play();
      } catch (error) {
        setAudioState("error", "音频暂时无法播放，请检查浏览器设置或稍后重试。");
      }
    }));
    audio.addEventListener("loadstart", () => setAudioState("loading", "正在加载官方音频…"));
    audio.addEventListener("loadedmetadata", () => {
      if (audio.paused) setAudioState("paused", "官方音频已就绪。");
    });
    audio.addEventListener("canplay", () => {
      if (audio.paused) setAudioState("paused", "官方音频已就绪。");
    });
    audio.addEventListener("waiting", () => setAudioState("loading", "音频正在缓冲…"));
    audio.addEventListener("playing", () => setAudioState("playing", "官方音频播放中。"));
    audio.addEventListener("pause", () => {
      if (!audio.ended) setAudioState("paused", "音频已暂停。");
    });
    audio.addEventListener("ended", () => setAudioState("paused", "音频播放完成。"));
    audio.addEventListener("error", () => setAudioState("error", "音频文件加载失败，请稍后重试。"));
    window.addEventListener("beforeunload", () => {
      audio.pause();
      audio.currentTime = 0;
    }, { once: true });
  }

  function bindImageModal() {
    const modal = document.querySelector("[data-image-modal]");
    const modalImage = modal?.querySelector("[data-modal-image]");
    const triggers = [...document.querySelectorAll("[data-source-image]")];
    const closeButtons = [...document.querySelectorAll("[data-image-close]")];
    if (!modal || !modalImage) return;

    function open(trigger) {
      modalImage.src = trigger.dataset.sourceImage;
      modalImage.alt = trigger.dataset.sourceAlt || "原书图片";
      modal.hidden = false;
      document.body.classList.add("modalOpen");
      modal.querySelector(".modalClose")?.focus();
    }

    function close() {
      modal.hidden = true;
      modalImage.removeAttribute("src");
      document.body.classList.remove("modalOpen");
    }

    triggers.forEach((trigger) => trigger.addEventListener("click", () => open(trigger)));
    closeButtons.forEach((button) => button.addEventListener("click", close));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !modal.hidden) close();
    });
  }

  async function bootstrap() {
    if (!app) return;
    if (page === "portal") return renderPortal();
    if (page === "japanese") return renderJapanese();
    if (!LEVEL_IDS.includes(currentLevel)) return renderError("页面未指定有效的日语等级。");
    if (page === "level-home") return renderLevelHome();
    if (page === "topics") return renderTopicsPage();
    if (page === "topic") return renderLessonPage();
    return renderError("无法识别当前页面。", "level", currentLevel);
  }

  bootstrap().catch((error) => {
    console.error(error);
    renderError(error?.message || "请刷新页面后重试。", currentLevel ? "level" : page, currentLevel);
  });
})();
