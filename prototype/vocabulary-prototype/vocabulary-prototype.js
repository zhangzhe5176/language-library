(() => {
  "use strict";

  const DATA = window.LEVEL_DATA;
  const STORAGE_KEY = "languageLibrary:vocabularyPrototype:n5:v1";
  const STORAGE_VERSION = 1;
  const STATUS_LABELS = { know: "会", fuzzy: "模糊", unknown: "不会" };
  const FILTER_LABELS = {
    all: "全部",
    unscanned: "未筛查",
    know: "会",
    fuzzy: "模糊",
    unknown: "不会",
    fuzzyUnknown: "模糊＋不会",
  };
  const TARGET_SPECS = [
    { topicId: 1, storyId: 1, vocabNo: "1" },
    { topicId: 1, storyId: 2, vocabNo: "2" },
    { topicId: 1, storyId: 2, vocabNo: "3" },
    { topicId: 1, storyId: 3, vocabNo: "4" },
    { topicId: 1, storyId: 3, vocabNo: "5" },
    { topicId: 1, storyId: 4, vocabNo: "6" },
    { topicId: 1, storyId: 6, vocabNo: "8" },
    { topicId: 1, storyId: 6, vocabNo: "9" },
    { topicId: 2, storyId: 9, vocabNo: "14" },
    { topicId: 2, storyId: 9, vocabNo: "15" },
    { topicId: 2, storyId: 10, vocabNo: "16" },
    { topicId: 2, storyId: 11, vocabNo: "17" },
    { topicId: 2, storyId: 11, vocabNo: "18" },
    { topicId: 2, storyId: 12, vocabNo: "19" },
    { topicId: 2, storyId: 13, vocabNo: "20" },
    { topicId: 2, storyId: 13, vocabNo: "21" },
    { topicId: 3, storyId: 17, vocabNo: "27" },
    { topicId: 3, storyId: 18, vocabNo: "28" },
    { topicId: 3, storyId: 19, vocabNo: "29" },
    { topicId: 3, storyId: 19, vocabNo: "30" },
    { topicId: 3, storyId: 20, vocabNo: "31" },
    { topicId: 3, storyId: 20, vocabNo: "32" },
    { topicId: 3, storyId: 20, vocabNo: "33" },
    { topicId: 3, storyId: 22, vocabNo: "37" },
  ];

  const app = document.querySelector("#vocabularyPrototypeApp");
  if (!DATA || DATA.level !== "n5") {
    app.innerHTML = '<section class="vv-panel"><h1>无法加载 N5 数据</h1><p>请通过本地预览服务打开此原型页面。</p></section>';
    return;
  }

  const topicById = new Map(DATA.topics.map((topic) => [Number(topic.id), topic]));
  const words = TARGET_SPECS.map((spec) => makeWord(spec));
  const wordById = new Map(words.map((word) => [word.id, word]));
  const unitIds = [...new Set(words.map((word) => word.topicId))];
  let state = loadState();
  let filter = "all";
  let query = "";

  function makeWord(spec) {
    const story = DATA.stories.find((item) => Number(item.id) === spec.storyId && Number(item.topicId) === spec.topicId);
    const row = story?.vocab?.find((item) => String(item[0]) === String(spec.vocabNo));
    if (!story || !row) throw new Error(`Missing N5 vocabulary source: ${JSON.stringify(spec)}`);
    const sourceWord = String(row[1] || "");
    const kana = String(row[2] || sourceWord);
    const kanji = /[\u3400-\u9fff]/u.test(sourceWord) ? sourceWord : "";
    const topic = topicById.get(spec.topicId);
    return {
      id: `n5:t${spec.topicId}:s${spec.storyId}:v${spec.vocabNo}`,
      topicId: spec.topicId,
      storyId: spec.storyId,
      sourceVocabNo: String(spec.vocabNo),
      kana,
      kanji,
      pos: String(row[3] || ""),
      meaning: String(row[4] || ""),
      unitLabel: `Topic ${String(spec.topicId).padStart(2, "0")} · ${topic?.title || ""}`,
    };
  }

  function loadState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (parsed?.version !== STORAGE_VERSION || parsed.level !== "n5" || typeof parsed.statuses !== "object") return emptyState();
      const statuses = {};
      for (const [id, value] of Object.entries(parsed.statuses)) {
        if (wordById.has(id) && Object.hasOwn(STATUS_LABELS, value)) statuses[id] = value;
      }
      return { version: STORAGE_VERSION, level: "n5", statuses };
    } catch {
      return emptyState();
    }
  }

  function emptyState() { return { version: STORAGE_VERSION, level: "n5", statuses: {} }; }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      return true;
    } catch {
      showToast("当前浏览器无法保存本地记录。");
      return false;
    }
  }

  function statusOf(word) { return state.statuses[word.id] || ""; }

  function stats() {
    const counts = { know: 0, fuzzy: 0, unknown: 0 };
    for (const word of words) {
      const status = statusOf(word);
      if (status) counts[status] += 1;
    }
    const screened = counts.know + counts.fuzzy + counts.unknown;
    return { total: words.length, screened, unscanned: words.length - screened, ...counts, ratio: words.length ? Math.round((screened / words.length) * 100) : 0 };
  }

  function unitStats(topicId) {
    const list = words.filter((word) => word.topicId === topicId);
    const counts = { know: 0, fuzzy: 0, unknown: 0, unscanned: 0 };
    for (const word of list) {
      const status = statusOf(word);
      if (status) counts[status] += 1;
      else counts.unscanned += 1;
    }
    let tone = "muted";
    let label = `仍有 ${counts.unscanned} 个未筛查`;
    if (!counts.unscanned && counts.unknown) { tone = "red"; label = `${counts.unknown} 个不会`; }
    else if (!counts.unscanned && counts.fuzzy) { tone = "yellow"; label = `${counts.fuzzy} 个模糊`; }
    else if (!counts.unscanned && counts.know === list.length) { tone = "green"; label = "已掌握"; }
    return { ...counts, total: list.length, tone, label };
  }

  function matches(word) {
    const needle = query.trim().toLocaleLowerCase();
    if (!needle) return true;
    return [word.kanji, word.kana, word.meaning].join(" ").toLocaleLowerCase().includes(needle);
  }

  function passesFilter(word) {
    const status = statusOf(word);
    if (filter === "all") return true;
    if (filter === "unscanned") return !status;
    if (filter === "fuzzyUnknown") return status === "fuzzy" || status === "unknown";
    return status === filter;
  }

  function visibleWords() { return words.filter((word) => matches(word) && passesFilter(word)); }

  function render() {
    const currentStats = stats();
    const visible = visibleWords();
    app.innerHTML = `
      <header class="vv-hero">
        <div>
          <p class="vv-kicker">Language Library · V1.2 本地隔离原型</p>
          <h1>N5 单词筛查与薄弱单元提示</h1>
          <p>只展示 3 个真实 N5 Topic 的目标生词，共 ${words.length} 个；用于体验筛查、提示和导出流程。</p>
        </div>
        <span class="vv-badge">未接入正式网站</span>
      </header>

      <details class="vv-panel vv-howto" open>
        <summary>怎么玩？</summary>
        <ul>
          <li>绿色代表会，黄色代表模糊，红色代表不会。</li>
          <li>三个方块均为空代表未筛查。</li>
          <li>每个单词只能选择一个状态，再次点击当前状态可取消。</li>
          <li>学习记录保存在当前浏览器，不上传云端。</li>
          <li>更换设备、清理浏览器数据或使用无痕模式后，记录可能丢失。</li>
          <li>可以随时重置学习记录，重新进行检测。</li>
        </ul>
      </details>

      <section class="vv-panel" aria-labelledby="vv-stats-title">
        <div class="vv-section-head"><div><p class="vv-kicker">Progress</p><h2 id="vv-stats-title">筛查进度</h2></div><p>状态变化后即时更新</p></div>
        <div class="vv-stats">
          ${statCard("总词数", currentStats.total)}
          ${statCard("已筛查", currentStats.screened)}
          ${statCard("未筛查", currentStats.unscanned)}
          ${statCard("会", currentStats.know, "green")}
          ${statCard("模糊", currentStats.fuzzy, "yellow")}
          ${statCard("不会", currentStats.unknown, "red")}
          ${statCard("完成比例", `${currentStats.ratio}%`)}
        </div>
      </section>

      <section class="vv-panel" aria-labelledby="vv-unit-title">
        <div class="vv-section-head"><div><p class="vv-kicker">Target words only</p><h2 id="vv-unit-title">单元薄弱提示</h2></div><p>只按各 Topic 自己的目标生词计算</p></div>
        <div class="vv-unit-grid">${unitIds.map(unitCard).join("")}</div>
      </section>

      <section class="vv-panel" aria-labelledby="vv-list-title">
        <div class="vv-toolbar-head">
          <div><p class="vv-kicker">N5 vocabulary</p><h2 id="vv-list-title">目标生词表</h2></div>
          <label class="vv-search"><span aria-hidden="true">⌕</span><span class="vv-sr-only">搜索日语汉字、假名或中文释义</span><input type="search" value="${escapeAttr(query)}" placeholder="搜索汉字、假名或中文释义" data-search autocomplete="off" /></label>
        </div>
        <div class="vv-filter-row" role="group" aria-label="状态筛选">${Object.entries(FILTER_LABELS).map(([id, label]) => `<button class="vv-filter" type="button" data-filter="${id}" aria-pressed="${filter === id}">${label}</button>`).join("")}</div>
        <p class="vv-count-note" data-result-count>当前显示 ${visible.length} / ${words.length} 个词</p>
        <div class="vv-word-list" data-word-list>${visible.length ? visible.map(wordRow).join("") : '<div class="vv-empty">没有符合当前搜索和筛选条件的词。请尝试清空搜索词或切换筛选。</div>'}</div>
      </section>

      <section class="vv-panel" aria-labelledby="vv-export-title">
        <div class="vv-section-head"><div><p class="vv-kicker">Offline workbook</p><h2 id="vv-export-title">导出学习清单</h2></div><p>导出范围不受当前搜索和筛选影响</p></div>
        <div class="vv-export-grid">
          ${exportButton("fuzzy", "导出模糊词汇", currentStats.fuzzy)}
          ${exportButton("unknown", "导出不会词汇", currentStats.unknown)}
          ${exportButton("fuzzyUnknown", "导出模糊＋不会词汇", currentStats.fuzzy + currentStats.unknown)}
        </div>
      </section>

      <section class="vv-panel vv-data-management" aria-labelledby="vv-data-title">
        <div><p class="vv-kicker">Data management</p><h2 id="vv-data-title">数据管理</h2><p>这里只重置当前 N5 原型的筛查记录，不删除词汇、故事、音频或其他等级数据。</p></div>
        <button class="vv-reset-btn" type="button" data-reset>重置当前 N5 学习记录</button>
      </section>

      <dialog class="vv-modal" data-reset-dialog>
        <div class="vv-modal-body">
          <h2>确认重置 N5 筛查记录？</h2>
          <p>这会清空当前原型中全部「会、模糊、不会」状态，恢复为未筛查。此操作无法直接撤销。</p>
          <div class="vv-modal-actions"><button class="vv-modal-btn" type="button" data-action="cancel">取消</button><button class="vv-modal-btn" type="button" data-action="confirm">确认重置</button></div>
        </div>
      </dialog>
      <div class="vv-toast" data-toast hidden></div>
    `;
    bindEvents();
  }

  function statCard(label, value, tone = "") { return `<div class="vv-stat" data-tone="${tone}"><strong>${value}</strong><span>${label}</span></div>`; }

  function unitCard(topicId) {
    const topic = topicById.get(topicId);
    const current = unitStats(topicId);
    return `<article class="vv-unit" data-status="${current.tone}"><div class="vv-unit-head"><div><h3>Topic ${String(topicId).padStart(2, "0")} · ${escapeHtml(topic?.title || "")}</h3><p>${escapeHtml(topic?.english || "")}</p></div><span class="vv-kicker">${current.total} 个目标词</span></div><div class="vv-unit-meta">已筛查 ${current.total - current.unscanned} / ${current.total}</div><div class="vv-unit-status" data-tone="${current.tone}">${current.label}</div></article>`;
  }

  function wordRow(word) {
    const selected = statusOf(word);
    const answer = selected ? `<div class="vv-word-answer" aria-live="polite">${word.kanji ? `<span class="vv-word-answer-kanji">${escapeHtml(word.kanji)}</span>` : ""}<span class="vv-word-answer-meaning">${escapeHtml(word.meaning)}</span></div>` : "";
    return `<article class="vv-word-row" data-word-id="${word.id}" data-selected="${selected}">
      <div class="vv-word-main"><div class="vv-word-kana">${escapeHtml(word.kana)}</div>${answer}</div>
      <div class="vv-status-group" role="group" aria-label="${escapeAttr(word.kana)}的筛查状态">${Object.entries(STATUS_LABELS).map(([id, label]) => `<button class="vv-status" type="button" data-status="${id}" aria-pressed="${selected === id}" title="${label}：${selected === id ? "已选择，再次点击取消" : "选择此状态"}" aria-label="${escapeAttr(word.kana)}：${label}${selected === id ? "，已选择，再次点击取消" : ""}">${label}</button>`).join("")}</div>
    </article>`;
  }

  function exportButton(type, label, count) { return `<button class="vv-export-btn" type="button" data-export="${type}"><strong>${label}</strong><small>${count} 个符合条件</small></button>`; }

  function bindEvents() {
    app.querySelector("[data-search]").addEventListener("input", (event) => { query = event.target.value; render(); focusSearch(); });
    app.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => { filter = button.dataset.filter; render(); }));
    app.querySelectorAll("[data-status]").forEach((button) => button.addEventListener("click", () => {
      const row = button.closest("[data-word-id]");
      const id = row?.dataset.wordId;
      if (!id || !wordById.has(id)) return;
      const next = button.dataset.status;
      if (state.statuses[id] === next) delete state.statuses[id];
      else state.statuses[id] = next;
      saveState();
      render();
    }));
    app.querySelectorAll("[data-export]").forEach((button) => button.addEventListener("click", () => exportWords(button.dataset.export)));
    app.querySelector("[data-reset]").addEventListener("click", () => app.querySelector("[data-reset-dialog]").showModal());
    app.querySelector("[data-action=cancel]").addEventListener("click", () => app.querySelector("[data-reset-dialog]").close());
    app.querySelector("[data-action=confirm]").addEventListener("click", () => {
      state = emptyState();
      saveState();
      app.querySelector("[data-reset-dialog]").close();
      render();
      showToast("N5 学习记录已重置，所有词恢复为未筛查。");
    });
  }

  function focusSearch() { const input = app.querySelector("[data-search]"); if (input) { input.focus(); input.setSelectionRange(input.value.length, input.value.length); } }

  function exportWords(type) {
    const wanted = type === "fuzzyUnknown" ? ["fuzzy", "unknown"] : [type];
    const rows = words.filter((word) => wanted.includes(statusOf(word)));
    if (!rows.length) { showToast(`当前没有符合条件的${type === "fuzzy" ? "模糊" : type === "unknown" ? "不会" : "模糊＋不会"}词汇，未生成文件。`); return; }
    const label = type === "fuzzy" ? "模糊词汇" : type === "unknown" ? "不会词汇" : "模糊不会词汇";
    const date = localDate();
    const filename = `N5_${label}_${date}.xlsx`;
    const exportRows = rows.map((word) => [word.kana, word.kanji, word.pos, word.meaning]);
    const blob = createXlsxBlob([["假名", "日语汉字", "词性", "唯一中文释义"], ...exportRows]);
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast(`已生成 ${filename}，共 ${rows.length} 个词。`);
  }

  function localDate() { const now = new Date(); return [now.getFullYear(), String(now.getMonth() + 1).padStart(2, "0"), String(now.getDate()).padStart(2, "0")].join("-"); }

  function createXlsxBlob(rows) {
    const files = {
      "[Content_Types].xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>`,
      "_rels/.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
      "xl/workbook.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="N5词汇" sheetId="1" r:id="rId1"/></sheets></workbook>`,
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

  let toastTimer;
  function showToast(message) { const toast = app.querySelector("[data-toast]"); if (!toast) return; toast.textContent = message; toast.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => { toast.hidden = true; }, 3200); }

  window.__vocabularyPrototype = { STORAGE_KEY, words, stats, unitStats, getState: () => JSON.parse(JSON.stringify(state)), createXlsxBlob };
  render();
})();
