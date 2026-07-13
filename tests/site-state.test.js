"use strict";

const assert = require("node:assert/strict");
const {
  createLevelStorage,
  levelKey,
  migrateLegacyState,
} = require("../state.js");

class MockStorage {
  constructor(initial = {}, failWrites = false) {
    this.values = new Map(Object.entries(initial));
    this.failWrites = failWrites;
  }

  getItem(key) {
    return this.values.has(key) ? this.values.get(key) : null;
  }

  setItem(key, value) {
    if (this.failWrites) throw new Error("write blocked");
    this.values.set(key, String(value));
  }
}

function json(storage, key) {
  const value = storage.getItem(key);
  return value === null ? null : JSON.parse(value);
}

{
  const storage = new MockStorage({
    [levelKey("n3", "learned")]: JSON.stringify(["1", "2"]),
    n3Learned: JSON.stringify([2, 3]),
    n3Starred: JSON.stringify([1, 1, 4]),
    n3Recent: JSON.stringify({ storyId: 5, topicId: 1 }),
  });
  const result = migrateLegacyState(storage, "n3");
  assert.equal(result.status, "migrated");
  assert.deepEqual(json(storage, levelKey("n3", "learned")), ["1", "2", "3"]);
  assert.deepEqual(json(storage, levelKey("n3", "favorites")), ["1", "4"]);
  assert.deepEqual(json(storage, levelKey("n3", "recent")), { storyId: "5", topicId: "1" });
  assert.equal(storage.getItem("n3Learned"), JSON.stringify([2, 3]), "legacy state must remain untouched");
  assert.equal(migrateLegacyState(storage, "n3").status, "already-migrated");
}

{
  const rawNew = "not-an-array";
  const storage = new MockStorage({
    [levelKey("n3", "learned")]: JSON.stringify(rawNew),
    n3Learned: JSON.stringify([7]),
  });
  const result = migrateLegacyState(storage, "n3");
  assert.equal(result.status, "invalid-new-state");
  assert.equal(storage.getItem(levelKey("n3", "learned")), JSON.stringify(rawNew));
  assert.equal(storage.getItem("n3Learned"), JSON.stringify([7]));
}

{
  const storage = new MockStorage({ n3Learned: JSON.stringify([8]) }, true);
  const result = migrateLegacyState(storage, "n3");
  assert.equal(result.status, "write-failed");
  assert.equal(storage.getItem("n3Learned"), JSON.stringify([8]));
}

{
  const storage = new MockStorage();
  const n1 = createLevelStorage(storage, "n1");
  const n2 = createLevelStorage(storage, "n2");
  assert.equal(n1.toggleLearned(1), true);
  assert.equal(n2.learned.has("1"), false, "the same story id must be isolated by level");
  assert.deepEqual(json(storage, levelKey("n1", "learned")), ["1"]);
  assert.equal(json(storage, levelKey("n2", "learned")), null);
}

{
  const storage = new MockStorage({
    [levelKey("n5", "recent")]: JSON.stringify({ storyId: "9", topicId: "2", updatedAt: "new" }),
    n5Recent: JSON.stringify({ storyId: 1, topicId: 1, updatedAt: "old" }),
  });
  migrateLegacyState(storage, "n5");
  assert.deepEqual(json(storage, levelKey("n5", "recent")), { storyId: "9", topicId: "2", updatedAt: "new" });
}

console.log("site-state: all migration and isolation assertions passed");
