const LEVELS = [
  { id: "n1", label: "N1", topics: 27, stories: 494, vocab: 2571, progress: 72, favorites: 18, recent: "Topic 27 科学", tone: "最高阶语境、论文表达、抽象词汇" },
  { id: "n2", label: "N2", topics: 23, stories: 452, vocab: 2360, progress: 61, favorites: 12, recent: "Topic 5 テクノロジー", tone: "职场与社会表达的进阶训练" },
  { id: "n3", label: "N3", topics: 18, stories: 371, vocab: 2014, progress: 54, favorites: 21, recent: "Topic 1 食事", tone: "从基础会话过渡到自然表达" },
  { id: "n4", label: "N4", topics: 13, stories: 262, vocab: 1035, progress: 48, favorites: 9, recent: "Topic 4 町", tone: "生活场景、短句理解和常用词" },
  { id: "n5", label: "N5", topics: 24, stories: 373, vocab: 1136, progress: 36, favorites: 15, recent: "Topic 3 カフェ", tone: "入门对话、发音和基础词汇" },
];

const TOPICS = [
  { id: 1, title: "食事", reading: "しょくじ", stories: 16, vocab: 74, progress: 100, status: "已完成", favorite: true },
  { id: 2, title: "家事", reading: "かじ", stories: 16, vocab: 79, progress: 80, status: "学习中", favorite: false },
  { id: 3, title: "買い物", reading: "かいもの", stories: 10, vocab: 45, progress: 62, status: "学习中", favorite: true },
  { id: 4, title: "ファッション", reading: "", stories: 16, vocab: 62, progress: 36, status: "未完成", favorite: false },
  { id: 5, title: "テクノロジー", reading: "", stories: 26, vocab: 109, progress: 28, status: "未完成", favorite: false },
  { id: 27, title: "科学", reading: "かがく", stories: 15, vocab: 76, progress: 18, status: "最近", favorite: true },
];

const LESSON = {
  level: "N1",
  topic: "Topic 1 食事",
  id: 1,
  title: "脂肪がつきやすい体質なので",
  audio: "../../assets/n1/audio/T1.mp3",
  image: "../../assets/n1/pages/page-017.jpeg",
  japanese: [
    "脂肪がつきやすい体質なので、食べる物、食べる時間には気をつけている。",
    "それなのに、母が横でお菓子の封を開けたものだから、つい一緒に間食してしまった。",
    "なんて愚かなんだ、私は！",
  ],
  chinese: "我属于容易长脂肪的体质，所以一直很注意吃什么、什么时候吃。可是妈妈在旁边打开了零食袋，我就不小心跟着一起吃了点心。我真是太愚蠢了！",
  vocab: [
    ["1", "脂肪", "しぼう", "名", "脂肪"],
    ["2", "体質", "たいしつ", "名", "体质"],
    ["3", "封", "ふう", "名", "封"],
    ["4", "間食［する］", "かんしょく", "名・動3自", "点心"],
    ["5", "愚かな", "おろか", "ナ", "愚蠢"],
  ],
};

const LANGUAGES = [
  { symbol: "日", name: "日语", path: "JLPT N1–N5", description: "已完成 N1–N5 全等级内容，从真实短文、音频和词汇继续学习。", status: "可开始学习", available: true },
  { symbol: "En", name: "英语", path: "Vocabulary & Reading", description: "英文词汇、阅读和听力入口。", status: "规划中", available: false },
  { symbol: "한", name: "韩语", path: "TOPIK Path", description: "韩语等级与场景学习路径。", status: "规划中", available: false },
  { symbol: "Fr", name: "法语", path: "CEFR Path", description: "法语分阶段阅读与听力路径。", status: "规划中", available: false },
  { symbol: "Es", name: "西班牙语", path: "CEFR Path", description: "西班牙语分阶段学习路径。", status: "规划中", available: false },
];

const app = document.querySelector("#app");
const page = document.body.dataset.prototypePage;

function layout(content, active = "") {
  return `
    <div class="page">
      <div class="shell">
        <header class="topbar">
          <a class="brand" href="./index.html"><span class="brandMark">語</span><span>Language Library</span></a>
          <nav class="nav" aria-label="原型导航">
            <a class="${active === "portal" ? "active" : ""}" href="./index.html">语言</a>
            <a class="${active === "japanese" ? "active" : ""}" href="./japanese.html">日语</a>
            <a class="${active === "level" ? "active" : ""}" href="./level.html">N1</a>
            <a class="${active === "topics" ? "active" : ""}" href="./topics.html">Topics</a>
            <a class="${active === "lesson" ? "active" : ""}" href="./lesson.html">学习</a>
          </nav>
        </header>
        ${content}
      </div>
    </div>
  `;
}

function stat(n, label) {
  return `<div class="miniStat"><strong>${n}</strong><span>${label}</span></div>`;
}

function renderPortal() {
  app.innerHTML = layout(`
    <section class="hero">
      <div>
        <span class="eyebrow">新版入口原型 · GitHub Pages 静态可用</span>
        <h1>从语言开始，而不是从等级开始。</h1>
        <p class="lead">根首页只承担语言分流。日语进入独立首页后，再选择 N1–N5 等级，减少旧版首页的信息密度，让长期学习路径更清晰。</p>
        <div class="actions">
          <a class="btn primary" href="./japanese.html">进入日语首页</a>
          <a class="btn" href="./lesson.html">查看学习页</a>
        </div>
      </div>
      <aside class="panel heroPanel">
        <div class="jpLine">今日も、<br />一つずつ深く読む。</div>
        <p>以内容、进度和连续学习为核心；弱化后台感，保留日语学习氛围。</p>
        <div class="miniStats">${stat("5", "语言入口")}${stat("5", "JLPT 等级")}${stat("1", "统一体验")}</div>
      </aside>
    </section>
    <div class="sectionHead">
      <div>
        <span class="kicker">Language paths</span>
        <h2>选择要继续的语言</h2>
      </div>
      <p>日语内容现已可用；其他语言保留清晰入口，并明确标注当前状态。</p>
    </div>
    <section class="grid languageGrid">
      ${LANGUAGES.map((language, i) => {
        const content = `
          <span class="languageSymbol">${language.symbol}</span>
          <span>
            <span class="kicker">${language.path}</span>
            <h3>${language.name}</h3>
            <p>${language.description}</p>
          </span>
          <span class="languageStatus">${language.status}</span>`;
        return language.available
          ? `<a class="card languageCard available" style="animation-delay:${i * 45}ms" href="./japanese.html">${content}</a>`
          : `<article class="card languageCard planned" style="animation-delay:${i * 45}ms">${content}</article>`;
      }).join("")}
    </section>
  `, "portal");
}

function levelCard(level) {
  return `
    <a class="card levelCard" href="./level.html" data-level-card="${level.id}">
      <span class="kicker">${level.label}</span>
      <h3>${level.tone}</h3>
      <p>${level.topics} Topics · ${level.stories} 条 · ${level.vocab} 词</p>
      <div class="progress" aria-label="${level.label} 学习进度"><span style="--value:${level.progress}%"></span></div>
      <div class="meta">${level.progress}% 已学 · ${level.favorites} 收藏 · 最近：${level.recent}</div>
    </a>
  `;
}

function renderJapanese() {
  const totalStories = LEVELS.reduce((s, l) => s + l.stories, 0);
  const totalVocab = LEVELS.reduce((s, l) => s + l.vocab, 0);
  app.innerHTML = layout(`
    <section class="hero">
      <div>
        <span class="eyebrow">日本語 · N1–N5</span>
        <h1>把五个等级组织成一条连续学习线。</h1>
        <p class="lead">日语首页展示真实内容规模、学习进度、收藏和最近学习入口。正式改版时可直接接入现有 localStorage 状态。</p>
        <div class="actions">
          <a class="btn primary" href="./level.html">继续学习 N1</a>
          <a class="btn" href="./topics.html">浏览 Topic</a>
        </div>
      </div>
      <aside class="panel heroPanel">
        <div class="jpLine">読む・聴く・覚える</div>
        <div class="miniStats">${stat(LEVELS.length, "等级")}${stat(totalStories, "故事")}${stat(totalVocab, "词汇")}</div>
      </aside>
    </section>
    <section class="grid levelGrid">${LEVELS.map(levelCard).join("")}</section>
  `, "japanese");
}

function renderLevel() {
  const n1 = LEVELS[0];
  app.innerHTML = layout(`
    <section class="hero">
      <div>
        <span class="eyebrow">N1 · 最高阶阅读与语境</span>
        <h1>围绕 Topic 推进，随时回到最近一条。</h1>
        <p class="lead">等级首页统一承载等级介绍、进度、继续学习、Topic 入口、搜索和收藏入口。原型以 N1 展示，但结构可复用于 N2–N5。</p>
        <div class="actions">
          <a class="btn primary" href="./lesson.html">继续：脂肪がつきやすい体質なので</a>
          <a class="btn" href="./topics.html">查看全部 Topic</a>
        </div>
      </div>
      <aside class="panel heroPanel">
        <span class="kicker">学习概况</span>
        <div class="miniStats">${stat(n1.topics, "Topics")}${stat(n1.stories, "故事")}${stat(n1.vocab, "词汇")}</div>
        <p>收藏 ${n1.favorites} 条，学习进度 ${n1.progress}%。</p>
        <div class="progress"><span style="--value:${n1.progress}%"></span></div>
      </aside>
    </section>
    <div class="toolbar">
      <label class="search">⌕ <input type="search" placeholder="搜索 Topic、日文、中文、词汇" data-search /></label>
      <div class="chipRow">
        <button class="chip active" data-filter="all">全部</button>
        <button class="chip" data-filter="fav">收藏</button>
        <button class="chip" data-filter="learning">学习中</button>
      </div>
    </div>
    <section class="grid topicGrid" data-topic-list>${TOPICS.map(topicCard).join("")}</section>
  `, "level");
  bindTopicFilters();
}

function topicCard(t) {
  return `
    <article class="card topicCard" data-title="${t.title} ${t.reading}" data-fav="${t.favorite}" data-learning="${t.progress < 100}">
      <div class="topicTop">
        <div>
          <span class="kicker">Topic ${String(t.id).padStart(2, "0")}</span>
          <h3>${t.title}</h3>
          <div class="meta">${t.reading || "—"} · ${t.stories} 条 · ${t.vocab} 词</div>
        </div>
        <span class="badge ${t.progress === 100 ? "done" : ""}">${t.status}</span>
      </div>
      <div class="progress"><span style="--value:${t.progress}%"></span></div>
      <div class="chipRow">
        ${t.favorite ? `<span class="badge fav">★ 收藏</span>` : `<span class="badge">☆ 未收藏</span>`}
        <span class="badge">${t.progress}%</span>
      </div>
      <a class="btn" href="./lesson.html">进入学习</a>
    </article>
  `;
}

function renderTopics() {
  app.innerHTML = layout(`
    <section>
      <span class="eyebrow">N1 Topic 目录</span>
      <h1>按主题推进，而不是被列表淹没。</h1>
      <p class="lead">目录页保留搜索、收藏筛选和状态；Topic 卡片强调故事数量、词汇数量和进度。</p>
      <div class="toolbar">
        <label class="search">⌕ <input type="search" placeholder="搜索 Topic，例如 科学 / 食事" data-search /></label>
        <div class="chipRow">
          <button class="chip active" data-filter="all">全部</button>
          <button class="chip" data-filter="fav">收藏</button>
          <button class="chip" data-filter="learning">未完成</button>
        </div>
      </div>
      <div class="grid topicGrid" data-topic-list>${TOPICS.map(topicCard).join("")}</div>
    </section>
  `, "topics");
  bindTopicFilters();
}

function renderLesson() {
  app.innerHTML = layout(`
    <section class="lessonLayout">
      <article class="panel lessonCard">
        <div class="lessonHeader">
          <div>
            <span class="eyebrow">${LESSON.level} · ${LESSON.topic} · #${LESSON.id}</span>
            <h1>${LESSON.title}</h1>
          </div>
          <button class="audioButton" data-audio aria-label="播放音频">▶</button>
        </div>
        <div class="japaneseText">${LESSON.japanese.map(line => `<p>${line}</p>`).join("")}</div>
        <div class="toggleBlock open">
          <button class="toggleHead" data-toggle>中文理解 <span>收起</span></button>
          <div class="toggleBody"><p>${LESSON.chinese}</p></div>
        </div>
        <div class="toggleBlock open">
          <button class="toggleHead" data-toggle>词汇 <span>收起</span></button>
          <div class="toggleBody">
            <ul class="vocabList">
              ${LESSON.vocab.map(v => `<li class="vocabItem"><strong>${v[0]}</strong><span><b>${v[1]}</b><br><span class="kana">${v[2] || "—"}</span></span><span class="pos">${v[3]} · ${v[4]}</span></li>`).join("")}
            </ul>
          </div>
        </div>
      </article>
      <aside class="sideStack">
        <section class="panel sideCard">
          <h3>学习状态</h3>
          <p>本原型只模拟状态，不写入现有 localStorage。</p>
          <div class="chipRow">
            <button class="chip active" data-learned>✓ 已学</button>
            <button class="chip" data-favorite>☆ 收藏</button>
          </div>
        </section>
        <section class="panel sideCard">
          <h3>原书图片</h3>
          <a class="sourcePreview" href="${LESSON.image}" target="_blank" rel="noreferrer"><img src="${LESSON.image}" alt="N1 原书页预览" /></a>
          <p>点击查看 EPUB 原始图片。</p>
        </section>
        <section class="panel sideCard">
          <h3>导航</h3>
          <div class="actions">
            <a class="btn ghost" href="./topics.html">← 返回目录</a>
            <a class="btn" href="./lesson.html">上一篇</a>
            <a class="btn primary" href="./lesson.html">下一篇</a>
          </div>
        </section>
      </aside>
    </section>
    <nav class="bottomBar" aria-label="手机端操作栏">
      <a href="./topics.html">目录</a>
      <button data-audio-mini>播放</button>
      <button data-favorite-mini>收藏</button>
      <button data-learned-mini>已学</button>
    </nav>
  `, "lesson");
  bindLesson();
}

function bindTopicFilters() {
  const search = document.querySelector("[data-search]");
  const chips = [...document.querySelectorAll("[data-filter]")];
  const cards = [...document.querySelectorAll("[data-topic-list] .topicCard")];
  let mode = "all";
  const apply = () => {
    const q = (search?.value || "").trim().toLowerCase();
    cards.forEach(card => {
      const hit = card.dataset.title.toLowerCase().includes(q);
      const modeHit = mode === "all" || (mode === "fav" && card.dataset.fav === "true") || (mode === "learning" && card.dataset.learning === "true");
      card.style.display = hit && modeHit ? "" : "none";
    });
  };
  search?.addEventListener("input", apply);
  chips.forEach(chip => chip.addEventListener("click", () => {
    chips.forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    mode = chip.dataset.filter;
    apply();
  }));
}

function bindLesson() {
  document.querySelectorAll("[data-toggle]").forEach(button => {
    button.addEventListener("click", () => {
      const block = button.closest(".toggleBlock");
      block.classList.toggle("open");
      button.querySelector("span").textContent = block.classList.contains("open") ? "收起" : "展开";
    });
  });
  const toggleClass = selector => document.querySelectorAll(selector).forEach(button => {
    button.addEventListener("click", () => {
      button.classList.toggle("active");
      if (button.hasAttribute("data-audio") || button.hasAttribute("data-audio-mini")) {
        button.classList.toggle("playing");
        button.textContent = button.classList.contains("playing") ? "Ⅱ" : "▶";
      } else if (button.textContent.includes("收藏")) {
        button.textContent = button.classList.contains("active") ? "★ 已收藏" : "☆ 收藏";
      } else if (button.textContent.includes("已学")) {
        button.textContent = button.classList.contains("active") ? "✓ 已学" : "标记已学";
      }
    });
  });
  toggleClass("[data-audio], [data-audio-mini], [data-favorite], [data-favorite-mini], [data-learned], [data-learned-mini]");
}

if (page === "portal") renderPortal();
if (page === "japanese") renderJapanese();
if (page === "level") renderLevel();
if (page === "topics") renderTopics();
if (page === "lesson") renderLesson();
