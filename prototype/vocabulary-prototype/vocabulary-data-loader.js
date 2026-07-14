(() => {
  "use strict";

  const LEVELS = ["n5", "n4", "n3", "n2", "n1"];

  function loadScript(level) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = `../../data/${level}-data.js`;
      script.async = false;
      script.onload = () => {
        const data = window.LEVEL_DATA || window.N3_DATA;
        if (!data || !Array.isArray(data.topics) || !Array.isArray(data.stories)) {
          reject(new Error(`无法读取 ${level.toUpperCase()} 数据结构。`));
          return;
        }
        resolve(data);
        delete window.LEVEL_DATA;
        delete window.N3_DATA;
        script.remove();
      };
      script.onerror = () => reject(new Error(`无法加载 ${level.toUpperCase()} 数据文件。`));
      document.head.appendChild(script);
    });
  }

  window.loadVocabularyPrototypeData = async () => {
    const data = {};
    for (const level of LEVELS) data[level] = await loadScript(level);
    return data;
  };
})();
