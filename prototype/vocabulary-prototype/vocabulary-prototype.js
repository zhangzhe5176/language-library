(() => {
  "use strict";

  const LEVEL_ORDER = ["n5", "n4", "n3", "n2", "n1"];
  const STORAGE_KEY = "languageLibrary:vocabularyPrototype:all:v2";
  const LEGACY_STORAGE_KEY = "languageLibrary:vocabularyPrototype:n5:v1";
  const STORAGE_VERSION = 2;
  const STATUS_LABELS = { know: "会", fuzzy: "模糊", unknown: "不会" };
  const FILTER_LABELS = {
    all: "全部",
    unscanned: "未筛查",
    know: "会",
    fuzzy: "模糊",
    unknown: "不会",
    fuzzyUnknown: "模糊＋不会",
  };
  const MANUAL_VOCAB_OVERRIDES = Object.freeze({
    "n5:t7:s60:v204": { reading: "エーティーエム", displayWord: "ATM", meaning: "自动取款机" },
    "n5:t20:s261:v757": { reading: "ティーシャツ", displayWord: "Tシャツ" },
    "n5:t20:s265:v757": { reading: "ティーシャツ", displayWord: "Tシャツ" },
    "n4:t10:s189:v755": { reading: "ティーシャツ", displayWord: "Tシャツ" },
    "n3:t12:s227:v1204": { reading: "じさ", displayWord: "時差", meaning: "时差" },
    "n3:t13:s256:v1359": { reading: "ひゃっかじてん", displayWord: "百科事典", meaning: "百科全书" },
    "n3:t13:s277:v1469": { reading: "かくれる", displayWord: "隠れる", pos: "动词·自动词" },
    "n3:t14:s283:v1501": { reading: "〜い", displayWord: "〜位", meaning: "第～名" },
    "n3:t14:s288:v1526": { reading: "ふく〜", displayWord: "副〜", meaning: "副～" },
    "n3:t14:s293:v1553": { reading: "むく", displayWord: "向く", meaning: "适合", pos: "动词·自动词" },
    "n3:t15:s305:v1605": { reading: "ふあんな", displayWord: "不安な", meaning: "不安的" },
    "n3:t15:s312:v1656": { reading: "つく", displayWord: "付く", pos: "动词·自动词" },
    "n3:t15:s314:v1669": { reading: "ふる", displayWord: "振る", pos: "动词·他动词" },
    "n3:t15:s317:v1689": { reading: "さます", displayWord: "覚ます", pos: "动词·他动词" },
    "n3:t15:s320:v1709": { reading: "〜しょう", displayWord: "〜証", meaning: "～证" },
    "n3:t16:s332:v1771": { reading: "ききめ", displayWord: "効き目" },
    "n3:t17:s348:v1848": { reading: "あき", displayWord: "空き", meaning: "空位" },
    "n3:t17:s350:v1864": { reading: "ささる", displayWord: "刺さる", meaning: "刺入", pos: "动词·自动词" },
    "n3:t18:s356:v1905": { reading: "ゆるやかな", displayWord: "緩やかな", meaning: "缓慢" },
    "n3:t18:s369:v2002": { reading: "へる", displayWord: "減る", meaning: "减少", pos: "动词·自动词" },
  });
  const app = document.querySelector("#vocabularyPrototypeApp");

  let models;
  let state;
  let currentLevel = "n5";
  let filter = "all";
  let query = "";
  let exportScope = "topic";
  let resetScope = "topic";
  let toastTimer;
  let loadNotice = "";

  app.innerHTML = '<section class="vv-panel vv-loading"><p class="vv-kicker">Local prototype</p><h1>正在读取 N5～N1 词汇数据…</h1><p>只读取词汇索引和 Topic 数据，不加载音频或图片。</p></section>';

  window.loadVocabularyPrototypeData().then(boot).catch((error) => {
    app.innerHTML = `<section class="vv-panel vv-error"><p class="vv-kicker">Local prototype</p><h1>词汇数据暂时无法加载</h1><p>${escapeHtml(error.message || "请通过本地预览服务打开此原型页面。")}</p></section>`;
  });

  function boot(rawData) {
    models = Object.fromEntries(LEVEL_ORDER.map((level) => [level, makeModel(level, rawData[level])]));
    state = loadState();
    currentLevel = state.currentLevel;
    render();
    if (loadNotice) showToast(loadNotice);
  }

  function makeModel(level, raw) {
    const data = { ...raw, level, label: raw.label || level.toUpperCase() };
    const topicById = new Map(data.topics.map((topic) => [Number(topic.id), topic]));
    const topicIds = data.topics.map((topic) => Number(topic.id));
    const rawWords = [];
    const storySequenceByTopic = new Map();

    for (const story of data.stories) {
      const topicId = Number(story.topicId);
      const storyNumberInTopic = (storySequenceByTopic.get(topicId) || 0) + 1;
      storySequenceByTopic.set(topicId, storyNumberInTopic);
      for (const row of Array.isArray(story.vocab) ? story.vocab : []) {
        const sourceWord = String(row?.[1] || "").trim();
        const sourceKana = String(row?.[2] || "").trim();
        const sourceVocabNo = String(row?.[0] || "").trim();
        const id = recordId(level, topicId, story.id, sourceVocabNo);
        const manual = MANUAL_VOCAB_OVERRIDES[id] || null;
        const reading = resolveReading(sourceWord, sourceKana, story, manual);
        const displayWord = manual?.displayWord ?? sourceWord;
        const statusKey = `${level}:word:${normalize(sourceWord || reading.value)}`;
        rawWords.push({
          id,
          level,
          topicId,
          storyId: Number(story.id),
          storyNumberInTopic,
          sourceVocabNo,
          sourceWord,
          displayWord,
          kana: reading.value,
          readingSource: reading.source,
          readingReview: reading.review,
          readingReviewReason: reading.reason,
          canScan: Boolean(reading.value && !reading.review),
          kanji: /\p{Script=Han}/u.test(displayWord) ? displayWord : "",
          pos: manual?.pos ?? String(row?.[3] || "").trim(),
          meaning: manual?.meaning ?? String(row?.[4] || "").trim(),
          statusKey,
        });
      }
    }

    const topicWords = new Map(topicIds.map((topicId) => [topicId, []]));
    for (const word of rawWords) {
      if (!topicWords.has(word.topicId)) continue;
      topicWords.get(word.topicId).push(word);
    }

    const words = rawWords.filter((word) => topicWords.has(word.topicId));
    return {
      level,
      data,
      topicById,
      topicIds,
      rawWords,
      words,
      topicWords,
      wordById: new Map(rawWords.map((word) => [word.id, word])),
      validStatusKeys: new Set(words.map((word) => word.statusKey)),
      scannableStatusKeys: new Set(words.filter((word) => word.canScan).map((word) => word.statusKey)),
    };
  }

  function emptyState() {
    return {
      version: STORAGE_VERSION,
      currentLevel: "n5",
      levels: Object.fromEntries(LEVEL_ORDER.map((level) => [level, { currentTopicId: models[level].topicIds[0], statuses: {} }])),
    };
  }

  function loadState() {
    const fallback = emptyState();
    let parsed = null;
    try {
      parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    } catch {
      loadNotice = "本地学习记录无法解析，已保留原记录并使用空白状态继续。";
    }

    if (parsed?.version === STORAGE_VERSION && parsed.levels && typeof parsed.levels === "object") {
      const restored = emptyState();
      restored.currentLevel = LEVEL_ORDER.includes(parsed.currentLevel) ? parsed.currentLevel : "n5";
      for (const level of LEVEL_ORDER) {
        const saved = parsed.levels[level];
        const model = models[level];
        if (!saved || typeof saved !== "object") continue;
        const topicId = Number(saved.currentTopicId);
        if (model.topicIds.includes(topicId)) restored.levels[level].currentTopicId = topicId;
        if (saved.statuses && typeof saved.statuses === "object") {
          for (const [statusKey, value] of Object.entries(saved.statuses)) {
            if (model.scannableStatusKeys.has(statusKey) && Object.hasOwn(STATUS_LABELS, value)) restored.levels[level].statuses[statusKey] = value;
          }
        }
      }
      return restored;
    }

    try {
      const legacy = JSON.parse(localStorage.getItem(LEGACY_STORAGE_KEY) || "null");
      if (legacy?.version === 1 && legacy.statuses && typeof legacy.statuses === "object") {
        for (const [legacyId, value] of Object.entries(legacy.statuses)) {
          const word = models.n5.wordById.get(legacyId);
          if (word && Object.hasOwn(STATUS_LABELS, value)) fallback.levels.n5.statuses[word.statusKey] = value;
        }
        if (Object.keys(fallback.levels.n5.statuses).length) loadNotice = "已安全迁移上一版 N5 学习记录，其他等级从未筛查开始。";
        saveState(fallback);
      }
    } catch {
      loadNotice = "上一版 N5 学习记录无法解析，原记录未被删除。";
    }
    return fallback;
  }

  function saveState(nextState = state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextState));
      return true;
    } catch {
      showToast("当前浏览器无法保存本地记录。");
      return false;
    }
  }

  function levelModel(level = currentLevel) { return models[level]; }
  function levelState(level = currentLevel) { return state.levels[level]; }
  function currentTopicId() { return levelState().currentTopicId; }
  function currentTopic() { return levelModel().topicById.get(currentTopicId()); }
  function currentTopicIndex() { return levelModel().topicIds.indexOf(currentTopicId()); }
  function topicLabel(topicId) { return `Topic${String(topicId).padStart(2, "0")}`; }
  function statusOf(word) { return levelState(word.level).statuses[word.statusKey] || ""; }
  function wordsForTopic(level, topicId) { return models[level].topicWords.get(topicId) || []; }

  function recordId(level, topicId, storyId, sourceVocabNo) { return `${level}:t${topicId}:s${String(storyId)}:v${String(sourceVocabNo)}`; }

  function wordsForExportScope(scope = exportScope) {
    const model = levelModel();
    const topicIds = scope === "level" ? model.topicIds : [currentTopicId()];
    const result = [];
    for (const topicId of topicIds) {
      for (const story of model.data.stories) {
        if (Number(story.topicId) !== topicId) continue;
        for (const row of Array.isArray(story.vocab) ? story.vocab : []) {
          const sourceVocabNo = String(row?.[0] || "").trim();
          const word = model.wordById.get(recordId(currentLevel, topicId, story.id, sourceVocabNo));
          if (word) result.push(word);
        }
      }
    }
    return result;
  }

  function exportStats(scope = exportScope) {
    const counts = { know: 0, fuzzy: 0, unknown: 0 };
    for (const word of wordsForExportScope(scope)) {
      const status = statusOf(word);
      if (status) counts[status] += 1;
    }
    return counts;
  }

  function stats(level = currentLevel, topicId = currentTopicId()) {
    const list = wordsForTopic(level, topicId);
    const counts = { know: 0, fuzzy: 0, unknown: 0 };
    for (const word of list) {
      const status = statusOf(word);
      if (status) counts[status] += 1;
    }
    const screened = counts.know + counts.fuzzy + counts.unknown;
    const readingReview = list.filter((word) => word.readingReview).length;
    return { total: list.length, screened, unscanned: list.length - screened, readingReview, ...counts, ratio: list.length ? Math.round((screened / list.length) * 100) : 0 };
  }

  function topicStatus(level, topicId) {
    const current = stats(level, topicId);
    let tone = "muted";
    let label = `仍有 ${current.unscanned} 个未筛查`;
    if (current.readingReview) label += ` · ${current.readingReview} 个读音待核对`;
    if (!current.unscanned && current.unknown) { tone = "red"; label = `${current.unknown} 个不会`; }
    else if (!current.unscanned && current.fuzzy) { tone = "yellow"; label = `${current.fuzzy} 个模糊`; }
    else if (!current.unscanned && current.know === current.total) { tone = "green"; label = "已掌握"; }
    return { ...current, tone, label };
  }

  function levelStats(level = currentLevel) {
    const model = models[level];
    const topics = model.topicIds.map((topicId) => topicStatus(level, topicId));
    const total = topics.reduce((sum, item) => sum + item.total, 0);
    const screened = topics.reduce((sum, item) => sum + item.screened, 0);
    return { topicTotal: topics.length, completedTopics: topics.filter((item) => !item.unscanned).length, incompleteTopics: topics.filter((item) => item.unscanned).length, total, screened, ratio: total ? Math.round((screened / total) * 100) : 0 };
  }

  function matches(word) {
    const needle = normalize(query).toLocaleLowerCase();
    if (!needle) return true;
    return [word.sourceWord, word.displayWord, word.kanji, word.kana, word.meaning].join(" ").toLocaleLowerCase().includes(needle);
  }

  function passesFilter(word) {
    const status = statusOf(word);
    if (filter === "all") return true;
    if (filter === "unscanned") return !status;
    if (filter === "fuzzyUnknown") return status === "fuzzy" || status === "unknown";
    return status === filter;
  }

  function visibleWords() { return wordsForTopic(currentLevel, currentTopicId()).filter((word) => matches(word) && passesFilter(word)); }

  function selectLevel(level) {
    if (!LEVEL_ORDER.includes(level) || level === currentLevel) return;
    currentLevel = level;
    state.currentLevel = level;
    query = "";
    filter = "all";
    saveState();
    render();
    document.querySelector("[data-topic-overview]")?.scrollIntoView({ behavior: "instant", block: "start" });
  }

  function setCurrentTopic(topicId) {
    const model = levelModel();
    if (!model.topicIds.includes(topicId) || topicId === currentTopicId()) return;
    levelState().currentTopicId = topicId;
    query = "";
    filter = "all";
    saveState();
    render();
    document.querySelector("[data-word-section]")?.scrollIntoView({ behavior: "instant", block: "start" });
  }

  function moveTopic(offset) {
    const nextIndex = currentTopicIndex() + offset;
    const ids = levelModel().topicIds;
    if (nextIndex < 0 || nextIndex >= ids.length) return;
    setCurrentTopic(ids[nextIndex]);
  }

  function render() {
    const model = levelModel();
    const topic = currentTopic();
    const currentStats = stats();
    const visible = visibleWords();
    const overall = levelStats();
    const currentExportStats = exportStats();
    app.innerHTML = `
      <header class="vv-hero">
        <div><p class="vv-kicker">Language Library · V1.2 本地隔离候选版</p><h1>N5～N1 单词筛查与薄弱 Topic 提示</h1><p>每次只测试一个等级的一个 Topic；数据来自项目现有 N5～N1 词汇文件。</p></div>
        <span class="vv-badge">未接入正式网站</span>
      </header>

      <section class="vv-panel vv-level-panel" aria-labelledby="vv-level-title">
        <div class="vv-section-head"><div><p class="vv-kicker">Level switch</p><h2 id="vv-level-title">选择等级</h2></div><p>学习记录按等级隔离保存</p></div>
        <div class="vv-level-switch" role="tablist" aria-label="等级切换">${LEVEL_ORDER.map((level) => `<button class="vv-level-tab" type="button" role="tab" data-level="${level}" aria-selected="${level === currentLevel}">${level.toUpperCase()}</button>`).join("")}</div>
        <div class="vv-level-summary" aria-label="当前等级简略统计">${statCard("Topic 总数", overall.topicTotal)}${statCard("已完成 Topic", overall.completedTopics, "green")}${statCard("未完成 Topic", overall.incompleteTopics)}${statCard("目标生词", overall.total)}${statCard("已筛查", overall.screened)}${statCard("等级完成比例", `${overall.ratio}%`)}</div>
      </section>

      <details class="vv-panel vv-howto" open><summary>怎么玩？</summary><ul><li>每次只测试一个 Topic 的目标生词，先只看假名判断。</li><li>选择会、模糊、不会后，显示日语汉字和中文释义。</li><li>绿色代表会，黄色代表模糊，红色代表不会；未选择代表未筛查。</li><li>一个 Topic 全部筛查完成后，显示该 Topic 的掌握状态。</li><li>学习记录保存在当前浏览器，不上传云端；更换设备、清理浏览器数据或使用无痕模式后，记录可能丢失。</li><li>可以重置当前 Topic 或当前等级重新检测。</li></ul></details>

      <section class="vv-panel vv-topic-overview" aria-labelledby="vv-overview-title" data-topic-overview>
        <details class="vv-topic-details" open><summary><span><span class="vv-kicker">Topic overview</span><strong id="vv-overview-title">${currentLevel.toUpperCase()} Topic 总览</strong></span><span class="vv-topic-summary">当前 ${topicLabel(currentTopicId())} · ${escapeHtml(topic?.title || "")} · ${currentStats.screened} / ${currentStats.total} 已筛查</span></summary><div class="vv-topic-overview-list">${model.topicIds.map((topicId) => topicCard(topicId)).join("")}</div></details>
      </section>

      <section class="vv-panel vv-current-topic" aria-labelledby="vv-current-topic-title">
        <div class="vv-topic-nav"><button class="vv-topic-nav-btn" type="button" data-topic-prev ${currentTopicIndex() === 0 ? "disabled" : ""}>← 上一个 Topic</button><div class="vv-current-topic-heading"><p class="vv-kicker">当前等级：${currentLevel.toUpperCase()} · ${currentTopicIndex() + 1} / ${model.topicIds.length}</p><h2 id="vv-current-topic-title">${topicLabel(currentTopicId())} · ${escapeHtml(topic?.title || "")}</h2><p>${escapeHtml(topic?.english || "")} · ${currentStats.total} 个目标生词${currentStats.readingReview ? ` · ${currentStats.readingReview} 个读音待核对` : ""}</p></div><button class="vv-topic-nav-btn" type="button" data-topic-next ${currentTopicIndex() === model.topicIds.length - 1 ? "disabled" : ""}>下一个 Topic →</button></div>
        <div class="vv-stats">${statCard("总词数", currentStats.total)}${statCard("已筛查", currentStats.screened)}${statCard("未筛查", currentStats.unscanned)}${statCard("会", currentStats.know, "green")}${statCard("模糊", currentStats.fuzzy, "yellow")}${statCard("不会", currentStats.unknown, "red")}${statCard("完成比例", `${currentStats.ratio}%`)}</div>
      </section>

      <section class="vv-panel vv-word-section" data-word-section aria-labelledby="vv-list-title"><div class="vv-toolbar-head"><div><p class="vv-kicker">${currentLevel.toUpperCase()} · ${topicLabel(currentTopicId())}</p><h2 id="vv-list-title">目标生词卡</h2></div><label class="vv-search"><span aria-hidden="true">⌕</span><span class="vv-sr-only">搜索日语汉字、假名或中文释义</span><input type="search" value="${escapeAttr(query)}" placeholder="搜索汉字、假名或中文释义" data-search autocomplete="off" /></label></div><div class="vv-filter-row" role="group" aria-label="状态筛选">${Object.entries(FILTER_LABELS).map(([id, label]) => `<button class="vv-filter" type="button" data-filter="${id}" aria-pressed="${filter === id}">${label}</button>`).join("")}</div><p class="vv-count-note" data-result-count>当前显示 ${visible.length} / ${currentStats.total} 个词</p><div class="vv-word-list" data-word-list>${visible.length ? visible.map(wordCard).join("") : '<div class="vv-empty">没有符合当前搜索和筛选条件的词。请尝试清空搜索词或切换筛选。</div>'}</div>${completionCard(currentStats)}</section>

      <section class="vv-panel" aria-labelledby="vv-export-title"><div class="vv-section-head"><div><p class="vv-kicker">Offline workbook</p><h2 id="vv-export-title">导出词汇</h2></div><p>不受当前搜索和筛选影响</p></div><div class="vv-export-scope" role="group" aria-label="导出范围"><span class="vv-export-scope-label">导出范围</span>${exportScopeButton("topic", "当前 Topic")}${exportScopeButton("level", "当前等级累计")}</div><p class="vv-export-note">当前范围：${exportScope === "topic" ? `${topicLabel(currentTopicId())} · ${escapeHtml(topic?.title || "")}` : `${currentLevel.toUpperCase()} 全部 Topic`}；导出保留原始重复记录和顺序。</p><div class="vv-export-grid">${exportButton("fuzzy", "导出模糊词汇", currentExportStats.fuzzy)}${exportButton("unknown", "导出不会词汇", currentExportStats.unknown)}${exportButton("fuzzyUnknown", "导出模糊＋不会词汇", currentExportStats.fuzzy + currentExportStats.unknown)}</div></section>

      <section class="vv-panel vv-data-management" aria-labelledby="vv-data-title"><div><p class="vv-kicker">Data management</p><h2 id="vv-data-title">数据管理</h2><p>重置只影响当前等级筛查状态，不删除词汇、故事、音频或其他网站内容。</p></div><div class="vv-reset-actions"><button class="vv-reset-btn" type="button" data-reset-topic>重置当前 Topic</button><button class="vv-reset-btn" type="button" data-reset-level>重置当前 ${currentLevel.toUpperCase()} 等级</button></div></section>

      <dialog class="vv-modal" data-reset-dialog><div class="vv-modal-body"><h2 data-reset-title>确认重置筛查记录？</h2><p data-reset-description>此操作无法直接撤销。</p><div class="vv-modal-actions"><button class="vv-modal-btn" type="button" data-action="cancel">取消</button><button class="vv-modal-btn" type="button" data-action="confirm">确认重置</button></div></div></dialog><div class="vv-toast" data-toast hidden></div>
    `;
    bindEvents();
  }

  function statCard(label, value, tone = "") { return `<div class="vv-stat" data-tone="${tone}"><strong>${value}</strong><span>${label}</span></div>`; }

  function topicCard(topicId) {
    const topic = levelModel().topicById.get(topicId);
    const current = topicStatus(currentLevel, topicId);
    const selected = topicId === currentTopicId();
    return `<button class="vv-topic-card" type="button" data-topic-id="${topicId}" aria-pressed="${selected}" data-current="${selected}"><span class="vv-topic-card-title">${topicLabel(topicId)} · ${escapeHtml(topic?.title || "")}</span><span class="vv-topic-card-meta">${current.total} 个目标词 · 已筛查 ${current.screened} / ${current.total}</span><span class="vv-topic-card-status" data-tone="${current.tone}">${current.label}</span></button>`;
  }

  function completionCard(currentStats) {
    if (currentStats.unscanned) return "";
    const tone = currentStats.unknown ? "red" : currentStats.fuzzy ? "yellow" : "green";
    const nextAvailable = currentTopicIndex() < levelModel().topicIds.length - 1;
    return `<div class="vv-completion" data-completion data-tone="${tone}"><div><p class="vv-kicker">Topic complete</p><h3>本 Topic 筛查完成</h3><p>会：${currentStats.know} · 模糊：${currentStats.fuzzy} · 不会：${currentStats.unknown}</p></div><div class="vv-completion-actions"><button class="vv-secondary-btn" type="button" data-review-topic>复习本 Topic 短文（后续实现）</button>${nextAvailable ? '<button class="vv-primary-btn" type="button" data-topic-next>进入下一个 Topic</button>' : ""}</div></div>`;
  }

  function wordCard(word) {
    const selected = statusOf(word);
    const answerWord = word.displayWord && !isKanaReading(stripSourceMarkers(word.displayWord)) ? `<span class="vv-word-answer-kanji">${escapeHtml(word.displayWord)}</span>` : "";
    const answer = selected ? `<div class="vv-word-answer" aria-live="polite">${answerWord}<span class="vv-word-answer-meaning">${escapeHtml(word.meaning)}</span></div>` : "";
    const readingLabel = `<div class="vv-word-kana">${escapeHtml(word.kana)}</div>`;
    const accessibleWord = word.kana;
    return `<article class="vv-word-card" data-word-id="${escapeAttr(word.id)}" data-selected="${selected}" data-reading-review="${word.readingReview}"><div class="vv-word-card-content">${readingLabel}${answer}</div><div class="vv-status-group" role="group" aria-label="${escapeAttr(accessibleWord)}的筛查状态">${Object.entries(STATUS_LABELS).map(([id, label]) => `<button class="vv-status" type="button" data-status="${id}" aria-pressed="${selected === id}" ${word.canScan ? "" : "disabled"} title="${word.canScan ? `${label}：${selected === id ? "已选择，再次点击取消" : "选择此状态"}` : "读音待核对，暂不能选择状态"}" aria-label="${escapeAttr(accessibleWord)}：${word.canScan ? label : "读音待核对，暂不能选择"}${selected === id ? "，已选择，再次点击取消" : ""}">${label}</button>`).join("")}</div></article>`;
  }

  function exportButton(type, label, count) { return `<button class="vv-export-btn" type="button" data-export="${type}"><strong>${label}</strong><small>${count} 个符合条件</small></button>`; }
  function exportScopeButton(scope, label) { return `<button class="vv-export-scope-btn" type="button" data-export-scope="${scope}" aria-pressed="${exportScope === scope}">${label}</button>`; }

  function bindEvents() {
    app.querySelector("[data-search]").addEventListener("input", (event) => { query = event.target.value; render(); focusSearch(); });
    app.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => { filter = button.dataset.filter; render(); }));
    app.querySelectorAll("[data-level]").forEach((button) => button.addEventListener("click", () => selectLevel(button.dataset.level)));
    app.querySelectorAll("[data-topic-id]").forEach((button) => button.addEventListener("click", () => setCurrentTopic(Number(button.dataset.topicId))));
    app.querySelectorAll("[data-topic-prev]").forEach((button) => button.addEventListener("click", () => moveTopic(-1)));
    app.querySelectorAll("[data-topic-next]").forEach((button) => button.addEventListener("click", () => moveTopic(1)));
    app.querySelectorAll("[data-export-scope]").forEach((button) => button.addEventListener("click", () => { exportScope = button.dataset.exportScope; render(); }));
    app.querySelectorAll("[data-status]").forEach((button) => button.addEventListener("click", () => {
      const card = button.closest("[data-word-id]");
      const word = card && levelModel().wordById.get(card.dataset.wordId);
      if (!word || !word.canScan) return;
      const next = button.dataset.status;
      const statuses = levelState(word.level).statuses;
      if (statuses[word.statusKey] === next) delete statuses[word.statusKey];
      else statuses[word.statusKey] = next;
      saveState();
      render();
    }));
    app.querySelectorAll("[data-export]").forEach((button) => button.addEventListener("click", () => exportWords(button.dataset.export, exportScope)));
    app.querySelector("[data-reset-topic]").addEventListener("click", () => openResetDialog("topic"));
    app.querySelector("[data-reset-level]").addEventListener("click", () => openResetDialog("level"));
    app.querySelectorAll("[data-review-topic]").forEach((button) => button.addEventListener("click", () => showToast("复习本 Topic 短文跳转：后续实现。")));
    app.querySelector("[data-action=cancel]").addEventListener("click", () => app.querySelector("[data-reset-dialog]").close());
    app.querySelector("[data-action=confirm]").addEventListener("click", confirmReset);
  }

  function focusSearch() { const input = app.querySelector("[data-search]"); if (input) { input.focus(); input.setSelectionRange(input.value.length, input.value.length); } }

  function openResetDialog(scope) {
    resetScope = scope;
    const dialog = app.querySelector("[data-reset-dialog]");
    const level = currentLevel.toUpperCase();
    app.querySelector("[data-reset-title]").textContent = scope === "level" ? `确认重置当前 ${level} 等级？` : `确认重置${topicLabel(currentTopicId())}？`;
    app.querySelector("[data-reset-description]").textContent = scope === "level" ? `这会清空当前 ${level} 的全部 Topic 学习状态，其他等级不受影响。此操作无法直接撤销。` : `这会清空当前 ${level} 的 ${topicLabel(currentTopicId())} 全部学习状态，其他 Topic 和等级不受影响（同一词在多个 Topic 出现时遵循全站一份状态规则）。此操作无法直接撤销。`;
    dialog.showModal();
  }

  function confirmReset() {
    const model = levelModel();
    const statuses = levelState().statuses;
    if (resetScope === "level") {
      levelState().statuses = {};
    } else {
      for (const word of wordsForTopic(currentLevel, currentTopicId())) delete statuses[word.statusKey];
    }
    saveState();
    app.querySelector("[data-reset-dialog]").close();
    const message = resetScope === "level" ? `当前 ${currentLevel.toUpperCase()} 等级学习记录已重置。` : `${topicLabel(currentTopicId())} 学习记录已重置。`;
    render();
    showToast(message);
    void model;
  }

  function exportWords(type, scope = exportScope) {
    const wanted = type === "fuzzyUnknown" ? ["fuzzy", "unknown"] : [type];
    const rows = wordsForExportScope(scope).filter((word) => wanted.includes(statusOf(word)));
    const label = type === "fuzzy" ? "模糊词汇" : type === "unknown" ? "不会词汇" : "模糊不会词汇";
    const scopeLabel = scope === "topic" ? topicLabel(currentTopicId()) : `${currentLevel.toUpperCase()}当前等级累计`;
    if (!rows.length) { showToast(`${scopeLabel}当前没有符合条件的${label}，未生成文件。`); return; }
    const filename = scope === "topic" ? `${currentLevel.toUpperCase()}_${topicLabel(currentTopicId())}_${label}_${localDate()}.xlsx` : `${currentLevel.toUpperCase()}_累计_${label}_${localDate()}.xlsx`;
    const reviewCount = rows.filter((word) => word.readingReview).length;
    const exportRows = rows.map((word) => {
      const topic = levelModel().topicById.get(word.topicId);
      return [`Topic ${word.topicId} ${topic?.title || ""}`.trim(), `第 ${word.storyNumberInTopic} 篇`, word.readingReview ? "" : word.kana, word.kanji, word.pos, word.meaning];
    });
    const blob = createXlsxBlob([["Topic", "短文", "假名", "日语汉字", "词性", "唯一中文释义"], ...exportRows]);
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast(`已生成 ${filename}，共 ${rows.length} 个词${reviewCount ? `，其中 ${reviewCount} 条读音待核对，假名栏留空` : ""}。`);
  }

  function localDate() { const now = new Date(); return [now.getFullYear(), String(now.getMonth() + 1).padStart(2, "0"), String(now.getDate()).padStart(2, "0")].join("-"); }
  function normalize(value) { return String(value ?? "").normalize("NFKC").replace(/\s+/g, "").trim(); }

  function resolveReading(sourceWord, sourceKana, story, manual) {
    if (manual?.reading) return { value: manual.reading, source: "manual-confirmation", review: false, reason: "" };
    if (sourceKana) return { value: sourceKana, source: "vocab[2]", review: false, reason: "" };
    const sourceReading = stripSourceMarkers(sourceWord);
    if (isKanaReading(sourceReading)) return { value: sourceReading, source: "sourceWord", review: false, reason: "" };
    const rawReading = recoverReadingFromRaw(sourceWord, story);
    if (rawReading) return { value: rawReading.value, source: rawReading.source, review: false, reason: "" };
    return {
      value: "",
      source: "",
      review: true,
      reason: `vocab[2] 为空；已检查 vocabRaw、ocrText 和 Story 其他字段，未找到可唯一确认的完整读音。原始词形：${sourceWord}`,
    };
  }

  function stripSourceMarkers(value) {
    return String(value ?? "").normalize("NFKC").replace(/[+＋=＝→←↑↓~〜～①②③④⑤⑥⑦⑧⑨⑩0-9?？（）()\[\]［］]/gu, "").trim();
  }

  function isKanaReading(value) { return /^[ぁ-ゖァ-ヺー・／/、\s]+$/u.test(String(value || "")); }

  function recoverReadingFromRaw(sourceWord, story) {
    if (!sourceWord || !/\p{Script=Han}/u.test(sourceWord)) return null;
    const sources = Array.isArray(story.vocabRaw) ? story.vocabRaw.map((value) => ({ source: "vocabRaw", text: String(value || "") })) : [];
    for (const item of sources) {
      const compact = item.text.replace(/\s+/gu, "").trim();
      const index = compact.indexOf(sourceWord);
      if (index < 0) continue;
      const prefix = compact.slice(0, index).match(/[ぁ-ゖァ-ヺー]{2,}$/u)?.[0] || "";
      const suffix = compact.slice(index + sourceWord.length).match(/^[ぁ-ゖァ-ヺー]{2,}$/u)?.[0] || "";
      const candidate = prefix || suffix;
      const exactPair = candidate && (compact === `${candidate}${sourceWord}` || compact === `${sourceWord}${candidate}`);
      if (exactPair && candidate.length >= Math.max(2, sourceWord.length - 1) && isKanaReading(candidate)) return { value: candidate, source: item.source };
    }
    return null;
  }

  function createXlsxBlob(rows) {
    const sheetName = `${currentLevel.toUpperCase()}词汇`;
    const files = {
      "[Content_Types].xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>`,
      "_rels/.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
      "xl/workbook.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="${escapeXml(sheetName)}" sheetId="1" r:id="rId1"/></sheets></workbook>`,
      "xl/_rels/workbook.xml.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>`,
      "xl/worksheets/sheet1.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${rows.map((row, rowIndex) => `<row r="${rowIndex + 1}">${row.map((value, colIndex) => `<c r="${columnName(colIndex)}${rowIndex + 1}" t="inlineStr"><is><t>${escapeXml(value)}</t></is></c>`).join("")}</row>`).join("")}</sheetData></worksheet>`,
    };
    return new Blob([zipStore(files)], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
  }

  function columnName(index) { let name = ""; for (let n = index + 1; n; n = Math.floor((n - 1) / 26)) name = String.fromCharCode(65 + ((n - 1) % 26)) + name; return name; }
  function escapeXml(value) { return String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;"); }
  function escapeHtml(value) { return escapeXml(value); }
  function escapeAttr(value) { return escapeXml(value); }

  function zipStore(files) {
    const encoder = new TextEncoder(); const chunks = []; const central = []; let offset = 0;
    for (const [name, text] of Object.entries(files)) {
      const nameBytes = encoder.encode(name); const data = encoder.encode(text); const crc = crc32(data);
      const local = new Uint8Array(30 + nameBytes.length + data.length); const view = new DataView(local.buffer);
      view.setUint32(0, 0x04034b50, true); view.setUint16(4, 20, true); view.setUint16(6, 0x800, true); view.setUint16(8, 0, true); view.setUint16(10, 0, true); view.setUint16(12, 0, true); view.setUint32(14, crc, true); view.setUint32(18, data.length, true); view.setUint32(22, data.length, true); view.setUint16(26, nameBytes.length, true); view.setUint16(28, 0, true); local.set(nameBytes, 30); local.set(data, 30 + nameBytes.length); chunks.push(local);
      const entry = new Uint8Array(46 + nameBytes.length); const entryView = new DataView(entry.buffer);
      entryView.setUint32(0, 0x02014b50, true); entryView.setUint16(4, 20, true); entryView.setUint16(6, 20, true); entryView.setUint16(8, 0x800, true); entryView.setUint16(10, 0, true); entryView.setUint16(12, 0, true); entryView.setUint16(14, 0, true); entryView.setUint32(16, crc, true); entryView.setUint32(20, data.length, true); entryView.setUint32(24, data.length, true); entryView.setUint16(28, nameBytes.length, true); entryView.setUint16(30, 0, true); entryView.setUint16(32, 0, true); entryView.setUint16(34, 0, true); entryView.setUint16(36, 0, true); entryView.setUint32(38, 0, true); entryView.setUint32(42, offset, true); entry.set(nameBytes, 46); central.push(entry); offset += local.length;
    }
    const centralSize = central.reduce((sum, item) => sum + item.length, 0); const end = new Uint8Array(22); const endView = new DataView(end.buffer);
    endView.setUint32(0, 0x06054b50, true); endView.setUint16(8, central.length, true); endView.setUint16(10, central.length, true); endView.setUint32(12, centralSize, true); endView.setUint32(16, offset, true);
    return concatBytes([...chunks, ...central, end]);
  }

  function concatBytes(items) { const total = items.reduce((sum, item) => sum + item.length, 0); const output = new Uint8Array(total); let offset = 0; for (const item of items) { output.set(item, offset); offset += item.length; } return output; }
  function crc32(bytes) { let crc = 0xffffffff; for (const byte of bytes) { crc ^= byte; for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0); } return (crc ^ 0xffffffff) >>> 0; }
  function showToast(message) { const toast = app.querySelector("[data-toast]"); if (!toast) return; toast.textContent = message; toast.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => { toast.hidden = true; }, 3200); }

  window.__vocabularyPrototype = {
    STORAGE_KEY,
    LEVEL_ORDER,
    getCurrentLevel: () => currentLevel,
    getCurrentTopicId: currentTopicId,
    getModels: () => models,
    getState: () => JSON.parse(JSON.stringify(state)),
    stats,
    levelStats,
    topicStatus,
    setCurrentTopic,
    selectLevel,
    createXlsxBlob,
  };
})();
