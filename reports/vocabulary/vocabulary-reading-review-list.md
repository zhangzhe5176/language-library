# N5～N1 读音待核对清单

审计日期：2026-07-14

本清单只包含项目现有数据中无法唯一确认读音的 20 条目标生词记录。记录没有被删除，仍按原始位置生成词卡；词卡显示“读音待核对”，三个状态按钮禁用。导出时假名栏留空，并在生成前提示待核对数量。

## 检查范围

逐条检查了以下字段和关联结构：

- vocab[1] 原始日语词形及其中的括号、标记读音
- vocab[2] 结构化读音字段
- vocabRaw
- ocrText
- Story 其他字段：id、topicId、page、type、title、audio、images、japanese、focus、naturalChinese、originalChinese、reviewStatus
- Topic 的 reading
- N5～N1 其他等级数据中的同名字段结构

判断规则是不联网、不查词典、不依据语言模型猜读音；只有 vocabRaw 中完整连续且能唯一对应原始词形的结构才可恢复。N5 もう少し 的 vocabRaw 为 もうすこしもう少し，已恢复为 もうすこし，因此不在本清单中。

## 待读音核对记录

| 等级 | Topic | 原始序号 | 原始词形 | 词性 | 中文释义 | 已检查的读音字段 | 原始数据位置 | 无法确认的原因 |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| N5 | Topic07 位置・場所1 | 204 | ATM | 名 | 提款机 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n5-data.js → stories[id=60].vocab[row 204] | 拉丁字母缩写；项目内没有完整日语读音字段，正文上下文不能唯一确认 |
| N5 | Topic20 服・体 | 757 | Tシャツ | 名 | T恤 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n5-data.js → stories[id=261].vocab[row 757] | 片假名与拉丁字母混合；没有完整独立读音字段，不猜测常见外来语读法 |
| N5 | Topic20 服・体 | 757 | Tシャツ | 名 | T恤 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n5-data.js → stories[id=265].vocab[row 757] | 片假名与拉丁字母混合；没有完整独立读音字段，不猜测常见外来语读法 |
| N4 | Topic10 ジム・グラウンド | 755 | Tシャツ | 名 | T恤 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n4-data.js → stories[id=189].vocab[row 755] | 片假名与拉丁字母混合；没有完整独立读音字段，不猜测常见外来语读法 |
| N3 | Topic12 旅行 | 1204 | +時差 | 名 | 肘差 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=227].vocab[row 1204] | 去除 + 后仍为汉字词；原始数据只有正文碎片，无法唯一确认完整读音 |
| N3 | Topic13 学校 | 1359 | 百科事典 | 名 | 百科全 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=256].vocab[row 1359] | OCR 正文中只有相邻句子假名，不能把上下文假定为该词读音 |
| N3 | Topic13 学校 | 1469 | 隠れる | 動2自 | 躲起来 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=277].vocab[row 1469] | 正文附近的 かく 属于其他词，不能映射为该词完整读音 |
| N3 | Topic14 仕事 | 1501 | 〜位 | 接尾～position | ～名 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=283].vocab[row 1501] | 接尾构词占位形式，没有独立完整读音 |
| N3 | Topic14 仕事 | 1526 | 副～ | 副～ | 副~ | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=288].vocab[row 1526] | 接头构词占位形式，没有独立完整读音 |
| N3 | Topic14 仕事 | 1553 | 向く | 動1自 | 向 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=293].vocab[row 1553] | 正文附近的 む 属于 向ける，不能映射为该词完整读音 |
| N3 | Topic15 人生 | 1605 | 不安な | 語句 | 不安 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=305].vocab[row 1605] | 正文只有不完整的 ふ、あん 碎片，缺少完整对应关系 |
| N3 | Topic15 人生 | 1656 | 付く | 動1目 | 附着，获得 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=312].vocab[row 1656] | 没有完整独立读音字段 |
| N3 | Topic15 人生 | 1669 | 振る | 動1他 | 甩掉，抛弃 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=314].vocab[row 1669] | 没有完整独立读音字段 |
| N3 | Topic15 人生 | 1689 | 覚ます | 動1他 | 清醒 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=317].vocab[row 1689] | 附近的 ご 属于 覚める，不能映射为该词完整读音 |
| N3 | Topic15 人生 | 1709 | 〜証 | 接尾 | ~i | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=320].vocab[row 1709] | 接尾占位形式；附近读音属于其他词 |
| N3 | Topic16 健康 | 1771 | +効きめ | 名 | 效果 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=332].vocab[row 1771] | 去除 + 后仍没有完整独立读音字段，附近的 き 不足以确认 |
| N3 | Topic17 マナー | 1864 | 刺さる | 動1自 | 刺入 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=350].vocab[row 1864] | 附近的 さ 属于 刺す，不是该词完整读音 |
| N3 | Topic18 社会 | 1905 | 緩やかな | 語句 | 缓慢 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=356].vocab[row 1905] | 没有完整独立读音字段，正文上下文不足以唯一确认 |
| N3 | Topic18 社会 | 2002 | 減る | 動1目 | 减少 | vocab[2]、vocabRaw、ocrText、Story 其他字段 | data/n3-data.js → stories[id=369].vocab[row 2002] | 没有完整独立读音字段，正文上下文不足以唯一确认 |

## 按等级统计

| 等级 | 待读音核对 |
| --- | ---: |
| N5 | 3 |
| N4 | 1 |
| N3 | 16 |
| N2 | 0 |
| N1 | 0 |
| **合计** | **20** |
