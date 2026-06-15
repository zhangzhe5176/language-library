#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


DATA = Path("/Users/wise/Documents/日本語/n3-web-sample/data/n3-data.js")


TOPIC_RANGES = {
    11: range(200, 216),
    12: range(216, 246),
    13: range(246, 282),
}


IMAGE_OVERRIDES = {
    215: ["assets/entries/T215_1.png"],
    245: ["assets/entries/T245_1.png", "assets/entries/T245_2.png"],
    281: ["assets/entries/T281_1.png", "assets/entries/T281_2.png"],
}


ROUTE_ONLY = {
    282: 14,
}


MEANING_FIXES = {
    "兵兵球": "乒乓球",
    "奥会": "奥运会",
    "人境": "入境",
    "清假": "请假",
    "公": "为什么",
    "肘候": "时候",
    "紅録灯": "红绿灯",
    "単人": "单人",
    "双人": "双人",
    "家": "家乡",
    "光": "尽头",
    "本": "书",
    "又": "叉号",
    "※写": "竖写",
    "振告": "报告",
    "用紙": "用纸",
    "目泉": "目录",
}


MANUAL_VOCAB = {
    # Topic 11 OCR omissions / broken numbering.
    1077: ["1077", "かゆい", "", "イ形", "痒的"],
    1086: ["1086", "タイヤ", "", "名", "轮胎"],
    1091: ["1091", "蒸し暑い", "むしあつい", "イ形", "闷热的"],
    1094: ["1094", "からからな", "", "ナ形", "干渴的，干透的"],
    1107: ["1107", "はだし", "", "名", "赤脚"],
    1109: ["1109", "～化", "か", "接尾", "～化"],
    1111: ["1111", "気候", "きこう", "名", "气候"],
    1112: ["1112", "おかしい", "", "イ形", "奇怪的"],
    1114: ["1114", "無関係な", "むかんけいな", "ナ形", "无关的"],
    1115: ["1115", "崩れる", "くずれる", "動2自", "崩溃，倒塌"],
    1116: ["1116", "崩す", "くずす", "動1他", "弄坏，破坏"],
    1117: ["1117", "マフラー", "", "名", "围巾"],
    1118: ["1118", "けっこう", "", "副", "相当，很"],
    1119: ["1119", "めちゃめちゃな", "", "ナ形", "乱七八糟的"],
    1120: ["1120", "こぼす", "", "動1他", "洒出，流出"],
    1122: ["1122", "津波", "つなみ", "名", "海啸"],
    1123: ["1123", "瞬間", "しゅんかん", "名", "瞬间"],
    1124: ["1124", "奪う", "うばう", "動1他", "夺走"],
    1127: ["1127", "濡れる", "ぬれる", "動2自", "淋湿"],
    1128: ["1128", "雷", "かみなり", "名", "雷"],
    1132: ["1132", "散る", "ちる", "動1自", "凋落，散落"],
    1133: ["1133", "上旬", "じょうじゅん", "名", "上旬"],
    1139: ["1139", "旗", "はた", "名", "旗子"],
    1140: ["1140", "凍る", "こおる", "動1自", "结冰"],
    1141: ["1141", "照る", "てる", "動1自", "照耀"],
    1143: ["1143", "昇る", "のぼる", "動1自", "升起"],
    1146: ["1146", "キャンプする", "", "名・動3自", "露营"],
    # Topic 12 omissions / broken numbering.
    1152: ["1152", "ただ", "", "副", "只是"],
    1153: ["1153", "ぶらぶらする", "", "動3自", "闲逛"],
    1159: ["1159", "芸術", "げいじゅつ", "名", "艺术"],
    1169: ["1169", "停車する", "ていしゃ", "名・動3自", "停车"],
    1173: ["1173", "線路", "せんろ", "名", "铁路轨道"],
    1174: ["1174", "越える", "こえる", "動2他", "越过"],
    1175: ["1175", "ええと", "", "感", "嗯，那个"],
    1177: ["1177", "ついて行く", "ついていく", "動1自", "跟着去"],
    1178: ["1178", "日付", "ひづけ", "名", "日期"],
    1179: ["1179", "便", "びん", "名", "班次"],
    1185: ["1185", "出身地", "しゅっしんち", "名", "出身地，家乡"],
    1189: ["1189", "あと", "", "副", "还剩，之后"],
    1191: ["1191", "ぎりぎりな", "", "ナ形", "勉强，紧迫"],
    1193: ["1193", "ふるさと", "", "名", "故乡"],
    1194: ["1194", "向かう", "むかう", "動1自", "前往"],
    1201: ["1201", "信号", "しんごう", "名", "信号灯"],
    1209: ["1209", "もったいない", "", "イ形", "可惜，浪费"],
    1213: ["1213", "それで", "", "接続", "所以，因此"],
    1216: ["1216", "かなり", "", "副", "相当，非常"],
    1210: ["1210", "ビーチ", "", "名", "海滩"],
    1211: ["1211", "迷う", "まよう", "動1自", "犹豫，迷路"],
    1232: ["1232", "偽物", "にせもの", "名", "假货"],
    1234: ["1234", "そっくりな", "", "ナ形", "很像的"],
    1236: ["1236", "免許証", "めんきょしょう", "名", "许可证，执照"],
    1260: ["1260", "指定席", "していせき", "名", "指定座位"],
    1262: ["1262", "市場", "いちば", "名", "市场"],
    1275: ["1275", "だって", "", "接続", "因为，可是"],
    1278: ["1278", "サークル", "", "名", "社团，小组"],
    1291: ["1291", "偶然", "ぐうぜん", "名・副", "偶然"],
    1293: ["1293", "網棚", "あみだな", "名", "行李架"],
    # Topic 13 OCR omissions / broken numbering.
    1320: ["1320", "ばかな", "", "ナ形", "愚蠢的"],
    1321: ["1321", "ふらふらな", "", "ナ形", "摇摇晃晃的"],
    1348: ["1348", "ばつ", "", "名", "叉号，错误标记"],
    1349: ["1349", "すっかり", "", "副", "完全"],
    1358: ["1358", "まるで", "", "副", "简直，好像"],
    1370: ["1370", "問題集", "もんだいしゅう", "名", "习题集"],
    1388: ["1388", "いじめ", "", "名・動3他", "欺凌"],
    1394: ["1394", "カンニングする", "", "名・動3自", "作弊"],
    1412: ["1412", "マナー", "", "名", "礼仪，规矩"],
    1419: ["1419", "直接", "ちょくせつ", "名・副", "直接"],
    1431: ["1431", "廊下", "ろうか", "名", "走廊"],
    1440: ["1440", "歴史", "れきし", "名", "历史"],
    1452: ["1452", "四角い", "しかくい", "イ形", "四角的"],
    1453: ["1453", "開始する", "かいし", "名・動3他", "开始"],
    1455: ["1455", "プリントする", "", "名・動3他", "打印，讲义"],
    1464: ["1464", "集まり", "あつまり", "名", "聚会，集合"],
    1465: ["1465", "集会", "しゅうかい", "名", "集会"],
    1471: ["1471", "思い出", "おもいで", "名", "回忆"],
    1476: ["1476", "印象", "いんしょう", "名", "印象"],
    1477: ["1477", "印象的な", "いんしょうてきな", "ナ形", "印象深刻的"],
    1478: ["1478", "地味な", "じみな", "ナ形", "朴素的，不显眼的"],
    1485: ["1485", "こける", "", "動2自", "摔倒，绊倒"],
    1486: ["1486", "ぶつける", "", "動2他", "撞上，碰到"],
    1489: ["1489", "委員会", "いいんかい", "名", "委员会"],
    1490: ["1490", "中心", "ちゅうしん", "名", "中心"],
}


JP_CN = {
    200: ("天気予報と大雨注意報", ["天気予報によると、現在大雨注意報が出ている。午後からにわか雨が降るので、早めに毛布とシーツを取り込まなければならない。"], "根据天气预报，现在发布了大雨注意报。下午会下阵雨，所以必须早点把毛毯和床单收进来。"),
    201: ("大陸移動説", ["大陸が地球の上を移動して、現在の世界ができたという説が1912年に発表された。"], "大陆在地球表面移动并形成了现在世界的这一学说，于1912年被发表。"),
    202: ("防災意識と梅雨", ["海外と比較して、日本は防災の意識が強い。梅雨のシーズンだが、今年は大きな被害が出ないことを祈っている。"], "和国外相比，日本的防灾意识很强。现在是梅雨季，我祈祷今年不要出现严重灾害。"),
    203: ("花粉の日", ["今日は花粉がたくさん飛んでいる。目がかゆくて、鼻もむずむずするので、外出はやめておこう。"], "今天花粉飞得很多。眼睛痒，鼻子也发痒，还是不要出门了。"),
    204: ("台風と停電", ["台風が近づいているので、大雨、強風、洪水の被害が心配である。電柱が倒れて、突然停電したり、断水したりするかもしれない。"], "台风正在接近，所以担心大雨、强风和洪水造成灾害。电线杆可能会倒，突然停电或停水。"),
    205: ("雨の日の自転車", ["雨の日にレインコートを着て自転車に乗っていたら、タイヤが滑って転びそうになったが、何とか無事だった。"], "雨天穿着雨衣骑自行车时，轮胎打滑差点摔倒，不过总算平安无事。"),
    206: ("日本の蒸し暑い夏", ["日本の夏は湿度が高くて蒸し暑い。クーラーや扇風機を使わなかったら、すぐにのどがからからになり、息ができなくなる。"], "日本夏天湿度高，非常闷热。如果不用空调或电风扇，喉咙很快就会干得难受，甚至难以呼吸。"),
    207: ("都会の地面温度", ["田舎と比べると、都会はコンクリートに囲まれているので、なかなか地面の温度が下がりにくい。"], "和乡下相比，城市被混凝土包围，地面温度很难降下来。"),
    208: ("震度5強の地震", ["昨日、震度5強の地震があり、かなり揺れた。海岸の近くにいて、今にも津波が来そうだったので、はだしで近くの家の屋根の上に逃げた。"], "昨天发生了震度5强的地震，摇晃得很厉害。我在海岸附近，感觉海啸马上就要来，于是光着脚逃到附近房子的屋顶上。"),
    209: ("地球温暖化の影響", ["地球温暖化の影響で最近の気候はおかしい。森林を切りすぎたことは無関係ではなく、いろんなバランスが崩れているのだろう。"], "受全球变暖影响，最近的气候很异常。过度砍伐森林并非毫无关系，各种平衡大概正在崩坏。"),
    210: ("初めてのマフラー", ["子どもが初めてマフラーを巻いたが、うまく巻けず、けっこうめちゃめちゃだった。顔を見ると、悔しくて涙をこぼしていた。"], "孩子第一次围围巾，但怎么也围不好，弄得相当乱。看他的表情，是因为不甘心而流泪了。"),
    211: ("津波への備え", ["津波は、瞬間のうちに多くの命を奪ってしまう。被害を防ぐために、逃げる場所を確かめておいたほうがいい。"], "海啸会在一瞬间夺走许多生命。为了防止受害，最好事先确认逃生地点。"),
    212: ("雷と窓ガラス", ["ひどい雨で、服が濡れてしまった。家に着いてからも、風はどんどん強くなり、雷も鳴り始めた。窓ガラスが揺れている。"], "雨下得很大，衣服都湿了。到家后风也越来越强，雷也开始响，窗玻璃都在晃动。"),
    213: ("4月上旬の暑さ", ["まだ桜が散りつつある4月上旬だが、気温が25度もあるので、汗がたくさん出る。"], "虽然才四月上旬，樱花还在凋落，但气温已经有25度，出了很多汗。"),
    214: ("凍った旗", ["今日はとても寒いので、外に置いていた旗が凍っている。でも、日が照れば、すぐに元に戻るだろう。"], "今天非常冷，放在外面的旗子都冻住了。不过太阳一照，应该很快就会恢复原状。"),
    215: ("日の出と夕日", ["A: 旅行に行くなら、太陽が昇るところを楽しみたい。でも、夕日が沈むところもいいなあ。一度に両方は無理かな。", "B: 景色のいいところでテントを張って、キャンプするってのはどう？"], "A：如果去旅行，我想欣赏太阳升起的地方。不过看夕阳落下也不错。一次同时享受两种景色是不是太难了？ B：在景色好的地方搭帐篷露营怎么样？"),
}


def speaker_line(text: str) -> dict:
    if text.startswith("A: "):
        return {"speaker": "A", "text": text[3:]}
    if text.startswith("B: "):
        return {"speaker": "B", "text": text[3:]}
    return {"text": text}


def normalize_meaning(raw: str) -> str:
    parts = raw.replace("【", "[").replace("】", "]").split("/")
    if len(parts) >= 2:
        meaning = parts[1]
    else:
        meaning = raw
    meaning = meaning.strip(" []［］「」")
    return MEANING_FIXES.get(meaning, meaning) or "待校正"


def clean_token(text: str) -> str:
    return re.sub(r"\s+", "", text.replace("［", "[").replace("］", "]").replace("＋", "+")).strip()


POS_RE = re.compile(r"(名|動|副|接尾|接頭|接続|ナ|イ|感)")
KANA_RE = re.compile(r"^[ぁ-ゖー〜～・]+$")


def parse_vocab(story: dict, min_no: int, max_no: int) -> list[list[str]]:
    raw = [str(x).strip() for x in story.get("vocabRaw") or [] if str(x).strip()]
    indexes = []
    for i, item in enumerate(raw):
        if item.isdigit() and min_no <= int(item) <= max_no:
            indexes.append((int(item), i))
    rows = []
    for idx, (no, start) in enumerate(indexes):
        end = indexes[idx + 1][1] if idx + 1 < len(indexes) else len(raw)
        block = raw[start + 1 : end]
        row = parse_vocab_block(no, block)
        if row[1] != "未確認":
            rows.append(row)
    for no, row in MANUAL_VOCAB.items():
        if min_no <= no <= max_no and row_belongs_to_story(no, story["id"]):
            if all(existing[0] != str(no) for existing in rows):
                rows.append(row)
    rows.sort(key=lambda row: int(row[0]))
    return rows


def row_belongs_to_story(no: int, story_id: int) -> bool:
    expected = {
        **{n: 200 for n in range(1056, 1064)}, **{n: 201 for n in range(1064, 1068)}, **{n: 202 for n in range(1068, 1075)},
        **{n: 203 for n in range(1075, 1079)}, **{n: 204 for n in range(1079, 1085)}, **{n: 205 for n in range(1085, 1090)},
        **{n: 206 for n in range(1090, 1096)}, **{n: 207 for n in range(1096, 1101)}, **{n: 208 for n in range(1101, 1109)},
        **{n: 209 for n in range(1109, 1117)}, **{n: 210 for n in range(1117, 1121)}, **{n: 211 for n in range(1121, 1127)},
        **{n: 212 for n in range(1127, 1131)}, **{n: 213 for n in range(1131, 1139)}, **{n: 214 for n in range(1139, 1142)},
        **{n: 215 for n in range(1142, 1147)}, **{n: 216 for n in range(1147, 1154)}, **{n: 218 for n in range(1159, 1163)},
        **{n: 219 for n in range(1163, 1171)}, **{n: 220 for n in range(1171, 1178)}, **{n: 221 for n in range(1178, 1181)},
        **{n: 222 for n in range(1181, 1185)}, **{n: 223 for n in range(1185, 1189)}, **{n: 225 for n in range(1192, 1197)},
        **{n: 226 for n in range(1197, 1203)}, **{n: 227 for n in range(1203, 1209)}, **{n: 228 for n in range(1210, 1217)},
        **{n: 231 for n in range(1231, 1235)}, **{n: 232 for n in range(1235, 1239)}, **{n: 236 for n in range(1258, 1261)},
        **{n: 244 for n in range(1290, 1294)},
        1189: 224, 1191: 224, 1209: 227, 1262: 237, 1275: 240, 1278: 241,
        **{n: 250 for n in range(1320, 1322)}, **{n: 255 for n in range(1348, 1350)}, **{n: 256 for n in range(1358, 1359)},
        **{n: 258 for n in range(1370, 1371)}, **{n: 262 for n in range(1388, 1389)}, **{n: 263 for n in range(1394, 1395)},
        **{n: 266 for n in range(1412, 1413)}, **{n: 267 for n in range(1419, 1420)}, **{n: 270 for n in range(1431, 1432)},
        **{n: 272 for n in range(1440, 1441)}, **{n: 273 for n in range(1452, 1454)}, **{n: 274 for n in range(1455, 1456)},
        **{n: 276 for n in range(1464, 1466)}, **{n: 278 for n in range(1471, 1479)}, **{n: 280 for n in range(1485, 1487)},
        **{n: 281 for n in range(1489, 1491)},
    }
    return expected.get(no) == story_id


def parse_vocab_block(no: int, block: list[str]) -> list[str]:
    meaning_raw = next((x for x in block if "/" in x), "")
    meaning = normalize_meaning(meaning_raw)
    pos = "語句"
    for token in block:
        cleaned = clean_token(token)
        if "/" not in token and POS_RE.search(cleaned):
            pos = cleaned
            break
        if "/" in token and POS_RE.match(token.split("/")[0]):
            pos = clean_token(token.split("/")[0])
            break
    word = "未確認"
    for token in block:
        cleaned = clean_token(token).replace("←", "").replace("→", "")
        if not cleaned or "/" in token or POS_RE.fullmatch(cleaned) or KANA_RE.fullmatch(cleaned):
            continue
        if re.search(r"[一-龯ぁ-ゖァ-ヺA-Za-z〜～+=]", cleaned) and len(cleaned) <= 24:
            word = cleaned
            break
    reading = ""
    for token in reversed(block):
        cleaned = clean_token(token)
        if KANA_RE.fullmatch(cleaned) and len(cleaned) <= 16:
            reading = cleaned
            break
    return [str(no), word, reading, pos, meaning]


def topic_for_story(story_id: int) -> int | None:
    for topic_id, story_range in TOPIC_RANGES.items():
        if story_id in story_range:
            return topic_id
    return None


def main() -> None:
    text = DATA.read_text(encoding="utf-8")
    prefix, raw = text.split("=", 1)
    data = json.loads(raw.strip().rstrip(";"))
    by_id = {story["id"]: story for story in data["stories"]}

    for story_id in range(200, 282):
        story = by_id[story_id]
        topic_id = topic_for_story(story_id)
        if topic_id is None:
            continue
        story["topicId"] = topic_id
        if story_id in JP_CN:
            title, japanese, chinese = JP_CN[story_id]
            story["title"] = title
            story["japanese"] = [speaker_line(line) for line in japanese]
            story["naturalChinese"] = [chinese]
            story["originalChinese"] = [chinese]
        elif story.get("originalChinese"):
            story["naturalChinese"] = story["originalChinese"]
        story["reviewStatus"] = "已校对"
        if story_id in IMAGE_OVERRIDES:
            story["images"] = IMAGE_OVERRIDES[story_id]
        if topic_id == 11:
            story["vocab"] = parse_vocab(story, 1056, 1146)
        elif topic_id == 12:
            story["vocab"] = parse_vocab(story, 1147, 1298)
        elif topic_id == 13:
            story["vocab"] = parse_vocab(story, 1299, 1492)

    for story_id, topic_id in ROUTE_ONLY.items():
        story = by_id[story_id]
        story["topicId"] = topic_id
        if story.get("reviewStatus") == "已校对":
            story["reviewStatus"] = "OCR未校对"

    DATA.write_text(prefix + "= " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("patched Topics 11-13 with vocab meanings and corrected routing")


if __name__ == "__main__":
    main()
