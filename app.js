const data = window.N3_DATA || { topics: [], stories: [] };
const topics = data.topics;
const stories = data.stories;
const basePath = document.body.dataset.base || ".";
const page = document.body.dataset.page || "levels";

const state = {
  query: "",
  filter: "all",
  hideChinese: true,
  learned: new Set(JSON.parse(localStorage.getItem("n3Learned") || "[]")),
  starred: new Set(JSON.parse(localStorage.getItem("n3Starred") || "[]")),
};

function topicUrl(topicId) {
  return `${basePath}/levels/n3/topic-${String(topicId).padStart(2, "0")}.html`;
}

function topicFor(story) {
  return topics.find((topic) => topic.id === story.topicId);
}

function topicStories(topicId) {
  return stories.filter((story) => story.topicId === topicId).sort((a, b) => a.id - b.id);
}

function typeLabel(type) {
  return type === "dialogue" ? "对话" : "短文";
}

function statusLabel(status) {
  return isCheckedStatus(status) ? "已校对" : "OCR未校对";
}

function isCheckedStatus(status) {
  return status === "样张已校对" || status === "已校对";
}

function progressFor(list) {
  const total = list.length || 0;
  const learned = list.filter((story) => state.learned.has(String(story.id))).length;
  const percent = total ? Math.round((learned / total) * 100) : 0;
  return { learned, total, percent };
}

function progressMarkup(progress, label = "学习进度") {
  return `
    <div class="progressMeter" aria-label="${label} ${progress.learned}/${progress.total}">
      <div class="progressLabel"><span>${label}</span><strong>${progress.learned}/${progress.total}</strong></div>
      <span class="progressTrack"><span style="width: ${progress.percent}%"></span></span>
    </div>
  `;
}

function saveState() {
  localStorage.setItem("n3Learned", JSON.stringify([...state.learned]));
  localStorage.setItem("n3Starred", JSON.stringify([...state.starred]));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightFocus(text, focusWords = []) {
  let html = escapeHtml(text);
  const words = [...focusWords].sort((a, b) => b.length - a.length);
  for (const word of words) {
    if (!word) continue;
    html = html.replace(new RegExp(escapeRegExp(escapeHtml(word)), "g"), `<span class="focus">${escapeHtml(word)}</span>`);
  }
  return html;
}

function focusWordsFor(story) {
  const words = new Set(story.focus || []);
  for (const row of story.vocab || []) {
    const word = cleanVocabWord(row?.[1]);
    if (!word) continue;
    words.add(word);
    if (word.endsWith("する")) words.add(word.slice(0, -2));
    const bracketIndex = word.indexOf("[");
    if (bracketIndex > 0) words.add(word.slice(0, bracketIndex));
  }
  return [...words].filter((word) => shouldHighlightWord(word));
}

function cleanVocabWord(word) {
  return String(word || "")
    .replace(/[＋+←→〃]/g, "")
    .replace(/［/g, "[")
    .replace(/］/g, "]")
    .trim();
}

function shouldHighlightWord(word) {
  if (!word || word.includes("～") || word.includes("未確認")) return false;
  if (/^(名|動|副|接尾|接頭|接続|ナ|イ|感|語句|名動3目|名動3他)$/.test(word)) return false;
  if (/^[ぁ-ゖー]+$/.test(word) && word.length < 2) return false;
  return word.length >= 1;
}

function storySearchText(story) {
  return [
    story.id,
    story.title,
    topicFor(story)?.title,
    typeLabel(story.type),
    ...(story.japanese || []).map((line) => line.text),
    ...(story.naturalChinese || []),
    ...(story.originalChinese || []),
    ...(story.vocabRaw || []),
    story.ocrText || "",
  ]
    .join(" ")
    .toLowerCase();
}

function shell(content, className = "siteShell") {
  const app = document.querySelector("#app");
  if (app) {
    app.className = className;
    app.innerHTML = content;
  }
}

function renderLevels() {
  const n3Count = stories.length || 371;
  const body = document.querySelector("main.siteShell");
  if (!body) return;
  const activeCard = body.querySelector(".levelCard.active strong");
  if (activeCard) activeCard.textContent = `${n3Count} 段`;
}

function renderN3Home() {
  const activeTopics = topics.filter((topic) => topicStories(topic.id).length > 0);
  const progress = progressFor(stories);
  shell(`
    <section class="heroPanel compact productHero">
      <div>
        <p class="eyebrow">JLPT N3 · Study Library</p>
        <h1>N3 迷你故事学习</h1>
        <p class="lead">像 Apple 产品页一样减少干扰：先听音频，再读日文，需要时再展开中文、词汇和原图。共 ${stories.length} 段，所有进度只保存在本地浏览器。</p>
        ${progressMarkup(progress, "总体进度")}
      </div>
      <a class="primaryLink" href="./topics.html">进入目录</a>
    </section>
    <section class="statGrid" aria-label="统计">
      <div class="statCard"><span>段落</span><strong>${stories.length}</strong></div>
      <div class="statCard"><span>Topic</span><strong>${activeTopics.length}</strong></div>
      <div class="statCard"><span>已学</span><strong>${progress.percent}%</strong></div>
    </section>
    <section>
      <div class="sectionHead">
        <h2>Topic 目录</h2>
        <a href="./topics.html">查看全部</a>
      </div>
      <div class="topicGrid compactTopicGrid">${topicCards(topics)}</div>
    </section>
  `);
}

function renderTopicsPage() {
  shell(`
    <section class="pageTitle">
      <p class="eyebrow">N3 Contents</p>
      <h1>Topic 目录</h1>
      <p>完整版按原书 Topic 和小喇叭编号顺序排列。点击 Topic 进入对应章节。</p>
    </section>
    <div class="topicGrid">${topicCards(topics)}</div>
  `);
}

function topicCards(topicList) {
  return topicList
    .map((topic) => {
      const topicList = topicStories(topic.id);
      const count = topicList.length;
      const progress = progressFor(topicList);
      return `
        <a class="topicCard active" href="${topicUrl(topic.id)}">
          <span class="topicNo">Topic ${topic.id}</span>
          <strong>${escapeHtml(topic.title)}</strong>
          <em>${escapeHtml(topic.english)}${topic.reading ? ` · ${escapeHtml(topic.reading)}` : ""}</em>
          <small>${count} 段 · p.${topic.page}</small>
          ${progressMarkup(progress, "已学")}
        </a>
      `;
    })
    .join("");
}

function renderTopicPage() {
  const topicId = Number(document.body.dataset.topic);
  const topic = topics.find((item) => item.id === topicId);
  if (!topic) return;

  const allStories = topicStories(topicId);
  const filtered = filterStories(allStories);
  const progress = progressFor(allStories);
  shell(`
    <aside class="chapterNav" aria-label="章节导航">
      <a class="backLink" href="./topics.html">返回目录</a>
      <h2>N3</h2>
      ${progressMarkup(progress, "本章进度")}
      <div class="chapterLinks">${topics
        .map((item) => {
          const itemStories = topicStories(item.id);
          const itemProgress = progressFor(itemStories);
          return `
          <a class="${item.id === topicId ? "active" : ""}" href="${topicUrl(item.id)}">
            <span>Topic ${item.id}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <em>${itemProgress.learned}/${itemStories.length} 已学</em>
          </a>`;
        })
        .join("")}</div>
    </aside>
    <section class="studyMain">
      <div class="topicHeader productHero">
        <p class="eyebrow">Topic ${topic.id} · Learn by listening</p>
        <h1>${escapeHtml(topic.title)}</h1>
        <p>${escapeHtml(topic.english)}${topic.reading ? ` · ${escapeHtml(topic.reading)}` : ""}。本章 ${allStories.length} 段，当前显示 <span id="visibleCount">${filtered.length}</span> 段。</p>
        ${progressMarkup(progress, "本章进度")}
        <div class="toolbarInline">
          <label class="searchBox"><span>搜索本章</span><input id="searchInput" type="search" value="${escapeHtml(state.query)}" placeholder="编号、日文、中文、词汇" autocomplete="off" /></label>
          <div class="controlGroup" role="group" aria-label="类型筛选">
            ${filterButton("all", "全部")}
            ${filterButton("dialogue", "对话")}
            ${filterButton("short", "短文")}
            ${filterButton("starred", "收藏")}
            ${filterButton("unlearned", "未学")}
            ${filterButton("unchecked", "未校对")}
          </div>
          <label class="switch"><input id="hideChinese" type="checkbox" ${state.hideChinese ? "checked" : ""} /><span>学习模式</span></label>
        </div>
      </div>
      <div id="cardList" class="cardList" aria-live="polite">${renderStoryList(filtered)}</div>
    </section>
  `, "studyShell");

  bindTopicControls();
}

function renderStoryList(list) {
  if (!list.length) {
    return `
      <div class="emptyState">
        <p class="eyebrow">No Results</p>
        <h2>没有匹配的学习卡片</h2>
        <p>试试清空搜索词，或切换到“全部”。</p>
      </div>
    `;
  }
  return list.map(renderStoryCard).join("");
}

function updateTopicResults() {
  const topicId = Number(document.body.dataset.topic);
  const filtered = filterStories(topicStories(topicId));
  const count = document.querySelector("#visibleCount");
  const list = document.querySelector("#cardList");
  if (count) count.textContent = filtered.length;
  if (list) list.innerHTML = renderStoryList(filtered);
  bindStoryActions();
}

function filterButton(value, label) {
  return `<button class="segButton ${state.filter === value ? "active" : ""}" type="button" data-filter="${value}">${label}</button>`;
}

function filterStories(list) {
  const query = state.query.trim().toLowerCase();
  return list.filter((story) => {
    const id = String(story.id);
    const passesFilter =
      state.filter === "all" ||
      story.type === state.filter ||
      (state.filter === "starred" && state.starred.has(id)) ||
      (state.filter === "unlearned" && !state.learned.has(id)) ||
      (state.filter === "unchecked" && !isCheckedStatus(story.reviewStatus));
    return passesFilter && (!query || storySearchText(story).includes(query));
  });
}

function bindTopicControls() {
  document.querySelector("#searchInput")?.addEventListener("input", (event) => {
    state.query = event.target.value;
    updateTopicResults();
  });

  document.querySelectorAll(".segButton").forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      document.querySelectorAll(".segButton").forEach((item) => item.classList.toggle("active", item === button));
      updateTopicResults();
    });
  });

  document.querySelector("#hideChinese")?.addEventListener("change", (event) => {
    state.hideChinese = event.target.checked;
    updateTopicResults();
  });

  bindStoryActions();
}

function bindStoryActions() {
  document.querySelectorAll("[data-action='learn']").forEach((button) => {
    button.addEventListener("click", () => {
      toggleSet(state.learned, button.dataset.id);
      saveState();
      renderTopicPage();
    });
  });

  document.querySelectorAll("[data-action='star']").forEach((button) => {
    button.addEventListener("click", () => {
      toggleSet(state.starred, button.dataset.id);
      saveState();
      updateTopicResults();
    });
  });
}

function toggleSet(set, id) {
  if (set.has(id)) set.delete(id);
  else set.add(id);
}

function renderStoryCard(story) {
  const id = String(story.id);
  const topic = topicFor(story);
  const learned = state.learned.has(id);
  const starred = state.starred.has(id);
  const focusWords = focusWordsFor(story);
  const japanese = (story.japanese || [])
    .map((line) => {
      const speaker = line.speaker ? `<span class="speaker">${escapeHtml(line.speaker)}：</span>` : "";
      return `<p class="jpLine">${speaker}${highlightFocus(line.text, focusWords)}</p>`;
    })
    .join("");
  const naturalChinese = (story.naturalChinese || []).map((line) => `<p>${escapeHtml(line)}</p>`).join("");
  const originalChinese = (story.originalChinese || []).map((line) => `<p>${escapeHtml(line)}</p>`).join("");
  const vocab = story.vocab?.length ? structuredVocab(story.vocab) : rawVocab(story.vocabRaw || []);
  const images = (story.images || [])
    .map((image, index) => `<img loading="lazy" src="${basePath}/${image}" alt="No. ${story.id} 原图对照 ${index + 1}" />`)
    .join("");
  const statusClass = isCheckedStatus(story.reviewStatus) ? "checked" : "unchecked";
  const translationOpen = state.hideChinese ? "" : " open";

  return `
    <article class="storyCard ${learned ? "learnedCard" : ""}" id="story-${story.id}">
      <div class="cardHead">
        <div>
          <div class="metaLine">
            <span class="pill">No. ${story.id}</span>
            <span class="pill">p. ${story.page}</span>
            <span class="pill ${story.type}">${typeLabel(story.type)}</span>
            <span class="pill ${statusClass}">${statusLabel(story.reviewStatus)}</span>
          </div>
          <h2>${escapeHtml(story.title)}</h2>
          <p class="cardSubline">${escapeHtml(topic?.title || "")} · 音频 T${story.id}</p>
        </div>
        <div class="cardActions">
          <button class="iconButton ${learned ? "active" : ""}" type="button" data-action="learn" data-id="${id}" aria-pressed="${learned}">${learned ? "✓ 已学" : "标记已学"}</button>
          <button class="iconButton ${starred ? "active" : ""}" type="button" data-action="star" data-id="${id}" aria-pressed="${starred}">${starred ? "★ 收藏" : "☆ 收藏"}</button>
        </div>
      </div>

      <div class="audioBlock">
        <span>Step 1 · Listen</span>
        <audio controls preload="metadata" src="${basePath}/assets/audio/${story.audio}"></audio>
      </div>

      <section class="japaneseBlock" aria-label="日文原文">
        <div class="studyStep">Step 2 · Read Japanese</div>
        ${japanese || "<p class='mutedText'>OCR 暂未提取到日文。</p>"}
      </section>

      <details class="revealPanel translationBlock"${translationOpen}>
        <summary>Step 3 · 显示中文理解</summary>
        <div class="translationText">${naturalChinese || "<p class='mutedText'>暂无自然中文。</p>"}</div>
        <details class="originalTranslation">
          <summary>原书中文对照</summary>
          <div>${originalChinese || "<p class='mutedText'>暂无原书中文。</p>"}</div>
        </details>
      </details>

      <details class="revealPanel vocabBlock">
        <summary>${story.vocab?.length ? "Step 4 · 词汇" : "Step 4 · 词汇 OCR 草稿"}</summary>
        ${vocab}
      </details>

      <details class="revealPanel sourceImage">
        <summary>原图对照</summary>
        ${images || "<p class='mutedText'>暂无原图。</p>"}
      </details>

    </article>
  `;
}

function structuredVocab(vocab) {
  return `<div class="vocabList">${vocab
    .map(([no, word, reading, kind, meaning]) => {
      const readingText = reading ? `${reading} · ${kind}` : kind;
      return `
        <div class="vocabItem">
          <div class="vocabTop"><span class="vocabWord">${escapeHtml(word)}</span><span class="vocabNo">#${escapeHtml(no)}</span></div>
          <span class="reading">${escapeHtml(readingText)}</span>
          <span class="meaning">${escapeHtml(meaning)}</span>
        </div>`;
    })
    .join("")}</div>`;
}

function rawVocab(lines) {
  if (!lines.length) return "<p class='mutedText'>OCR 暂未提取到词汇表。</p>";
  return `<div class="rawVocab">${lines.map((line) => `<span>${escapeHtml(line)}</span>`).join("")}</div>`;
}

if (page === "levels") renderLevels();
if (page === "n3-home") renderN3Home();
if (page === "topics") renderTopicsPage();
if (page === "topic") renderTopicPage();
