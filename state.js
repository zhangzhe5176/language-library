(function initLanguageLibraryState(globalScope) {
  "use strict";

  const PREFIX = "languageLibrary:v2";

  function levelKey(level, name) {
    return `${PREFIX}:${String(level).toLowerCase()}:${name}`;
  }

  function normalizeIds(values) {
    if (!Array.isArray(values)) return [];
    return [...new Set(values.map((value) => String(value)).filter((value) => /^\d+$/.test(value)))];
  }

  function readJson(storage, key) {
    try {
      const raw = storage.getItem(key);
      if (raw === null) return { exists: false, valid: true, value: null, raw: null };
      return { exists: true, valid: true, value: JSON.parse(raw), raw };
    } catch (error) {
      return { exists: true, valid: false, value: null, raw: null, error };
    }
  }

  function writeJson(storage, key, value) {
    try {
      storage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      return false;
    }
  }

  function normalizeRecent(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === "number" || typeof value === "string") {
      const storyId = String(value);
      return /^\d+$/.test(storyId) ? { storyId } : null;
    }
    if (typeof value !== "object") return null;
    const storyId = String(value.storyId ?? value.id ?? "");
    if (!/^\d+$/.test(storyId)) return null;
    const topicId = String(value.topicId ?? "");
    return {
      storyId,
      ...( /^\d+$/.test(topicId) ? { topicId } : {} ),
      ...( value.updatedAt ? { updatedAt: String(value.updatedAt) } : {} ),
    };
  }

  function migrateLegacyState(storage, level) {
    const normalizedLevel = String(level).toLowerCase();
    const markerKey = levelKey(normalizedLevel, "legacy-migrated");
    try {
      if (storage.getItem(markerKey) === "1") return { status: "already-migrated", changed: false };
    } catch (error) {
      return { status: "unavailable", changed: false };
    }

    const mappings = [
      { target: "learned", legacy: `${normalizedLevel}Learned` },
      { target: "favorites", legacy: `${normalizedLevel}Starred` },
    ];
    let changed = false;

    for (const mapping of mappings) {
      const targetKey = levelKey(normalizedLevel, mapping.target);
      const current = readJson(storage, targetKey);
      const legacy = readJson(storage, mapping.legacy);
      if (!current.valid || !legacy.valid) return { status: "invalid-json", changed: false };
      if (current.exists && !Array.isArray(current.value)) return { status: "invalid-new-state", changed: false };
      if (legacy.exists && !Array.isArray(legacy.value)) return { status: "invalid-legacy-state", changed: false };

      const merged = normalizeIds([
        ...(current.exists ? current.value : []),
        ...(legacy.exists ? legacy.value : []),
      ]);
      const currentIds = normalizeIds(current.exists ? current.value : []);
      if (legacy.exists && JSON.stringify(merged) !== JSON.stringify(currentIds)) {
        if (!writeJson(storage, targetKey, merged)) return { status: "write-failed", changed: false };
        changed = true;
      } else if (!current.exists && legacy.exists) {
        if (!writeJson(storage, targetKey, merged)) return { status: "write-failed", changed: false };
        changed = true;
      }
    }

    const recentKey = levelKey(normalizedLevel, "recent");
    const currentRecent = readJson(storage, recentKey);
    const legacyRecent = readJson(storage, `${normalizedLevel}Recent`);
    if (!currentRecent.valid || !legacyRecent.valid) return { status: "invalid-json", changed: false };
    if (currentRecent.exists && !normalizeRecent(currentRecent.value)) {
      return { status: "invalid-new-state", changed: false };
    }
    if (!currentRecent.exists && legacyRecent.exists) {
      const recent = normalizeRecent(legacyRecent.value);
      if (!recent) return { status: "invalid-legacy-state", changed: false };
      if (!writeJson(storage, recentKey, recent)) return { status: "write-failed", changed: false };
      changed = true;
    }

    try {
      storage.setItem(markerKey, "1");
    } catch (error) {
      return { status: "marker-write-failed", changed };
    }
    return { status: "migrated", changed };
  }

  function createLevelStorage(storage, level) {
    const normalizedLevel = String(level).toLowerCase();
    const migration = migrateLegacyState(storage, normalizedLevel);
    const keys = {
      learned: levelKey(normalizedLevel, "learned"),
      favorites: levelKey(normalizedLevel, "favorites"),
      recent: levelKey(normalizedLevel, "recent"),
    };

    function readSet(name) {
      const parsed = readJson(storage, keys[name]);
      return new Set(parsed.valid && Array.isArray(parsed.value) ? normalizeIds(parsed.value) : []);
    }

    const learned = readSet("learned");
    const favorites = readSet("favorites");
    const recentParsed = readJson(storage, keys.recent);
    let recent = recentParsed.valid ? normalizeRecent(recentParsed.value) : null;

    function persistSet(name, set) {
      return writeJson(storage, keys[name], [...set]);
    }

    function toggle(name, id) {
      const set = name === "learned" ? learned : favorites;
      const normalizedId = String(id);
      if (set.has(normalizedId)) set.delete(normalizedId);
      else set.add(normalizedId);
      if (!persistSet(name, set)) {
        if (set.has(normalizedId)) set.delete(normalizedId);
        else set.add(normalizedId);
        return false;
      }
      return true;
    }

    function setRecent(value) {
      const normalized = normalizeRecent(value);
      if (!normalized || !writeJson(storage, keys.recent, normalized)) return false;
      recent = normalized;
      return true;
    }

    return {
      level: normalizedLevel,
      keys,
      migration,
      learned,
      favorites,
      get recent() { return recent; },
      toggleLearned(id) { return toggle("learned", id); },
      toggleFavorite(id) { return toggle("favorites", id); },
      setRecent,
    };
  }

  const api = {
    PREFIX,
    createLevelStorage,
    levelKey,
    migrateLegacyState,
    normalizeIds,
    normalizeRecent,
    readJson,
  };

  globalScope.LanguageLibraryState = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
