#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


DATA = Path("/Users/wise/Documents/日本語/n3-web-sample/data/n3-data.js")


TOPIC_RANGES = {
    14: range(282, 305),
    15: range(305, 321),
}

ROUTE_ONLY = {
    **{sid: 16 for sid in range(321, 326)},
}

IMAGE_OVERRIDES = {
    304: ["assets/entries/T304_1.png", "assets/entries/T304_2.png"],
    320: ["assets/entries/T320_1.png", "assets/entries/T320_2.png"],
}

MEANING_FIXES = {
    "前合": "前台",
    "上上↑月": "上上个月",
    "新姿": "工资",
    "単純": "单纯",
    "作当作当": "作业，工作",
    "反夏": "反复",
    "建【提i］": "建议",
    "恋度": "态度",
    "冉加上": "再加上",
    "知道|ア解了］": "知道，理解",
    "文現": "文职，事务工作",
    "先当【先］": "失业",
    "3": "约，大约",
    "銷告［告］": "销售，营业",
    "取": "职场",
    "肘T": "兼职",
    "新": "时薪，工资",
    "〜底": "～末，月底",
    "活劫": "活动",
    "很多人［很期］": "拥挤，人多",
    "|肘": "临时",
    "招聘［招聘］": "招募，招聘",
    "必券": "义务",
    "收倍人": "收件人",
    "收地址": "收件地址",
    "週整［整］": "调整",
    "制造": "制造",
    "整理【整理］": "整理",
    "命［命］": "命令",
    "点［点～］": "点单，订购",
    "肘回国": "临时回国",
    "助［助］": "协助，合作",
    "焦売": "焦急",
    "放": "放弃",
    "律": "律师",
    "目杯": "目标",
    "很棒的": "很棒的",
    "以況": "遇见",
    "i真的": "认真的",
    "交往【交往］": "交往",
    "辺": "痛苦，难受",
    "蜡独": "蜡烛",
    "想象【想象］": "想象",
    "互相": "互相",
    "対方": "对方",
    "求婚【求婚】": "求婚",
    "最小的~": "最小的孩子",
    "世同": "社会，世间",
    "常沢": "常识",
    "生的事": "发生的事",
    "准": "标准",
    "自": "自信",
    "依附": "附着，获得",
    "表兄弟妹、堂表兄弟姐妹": "堂表兄弟姐妹",
    "有銭人": "有钱人",
    "交住": "交往",
    "困雅": "困难，痛苦",
    "痛者": "痛苦",
    "用": "甩掉，抛弃",
    "活説": "那么，接下来",
    "致詞【致詞］": "演讲，致辞",
    "会～我": "给我",
    "感謝感謝］": "感谢",
    "f学［学］": "升学",
    "建筑【建］": "建筑",
    "等級": "等级，水平",
    "流物": "流利",
    "器": "乐器",
    "※【易］": "贸易",
    "企y": "企业",
    "就取［明］": "就业",
    "相倉": "信任，信用",
    "笠名【袋名］": "签名",
    "終子": "终于",
    "手練［手練］": "手续",
    "菌口": "窗口",
    "接受": "受理，接受",
    "保隘": "保险",
}

MANUAL_VOCAB = {
    1499: ["1499", "エンジニア", "", "名", "工程师"],
    1515: ["1515", "きつい", "", "イ形", "辛苦的，严厉的"],
    1523: ["1523", "月末", "げつまつ", "名", "月底，月末"],
    1529: ["1529", "事務", "じむ", "名", "事务工作，文职"],
    1530: ["1530", "アピールする", "", "名・動3他", "展示，强调"],
    1531: ["1531", "新型", "しんがた", "名", "新型"],
    1541: ["1541", "積もる", "つもる", "動1自", "积累，堆积"],
    1547: ["1547", "まあまあな", "", "ナ形", "还可以的，过得去的"],
    1550: ["1550", "会員", "かいいん", "名", "会员"],
    1565: ["1565", "問い合わせる", "といあわせる", "動2他", "咨询，询问"],
    1576: ["1576", "名刺", "めいし", "名", "名片"],
    1603: ["1603", "独身", "どくしん", "名", "单身"],
    1612: ["1612", "悩み", "なやみ", "名", "烦恼"],
    1617: ["1617", "様子", "ようす", "名", "样子，情况"],
    1624: ["1624", "そのため", "", "接続", "因此，所以"],
    1625: ["1625", "キスする", "", "名・動3自", "接吻"],
    1627: ["1627", "ろうそく", "", "名", "蜡烛"],
    1639: ["1639", "たとえ", "", "副", "即使，哪怕"],
    1651: ["1651", "資格", "しかく", "名", "资格，证书"],
    1663: ["1663", "いとこ", "", "名", "堂表兄弟姐妹"],
    1664: ["1664", "お金持ち", "おかねもち", "名", "有钱人"],
    1666: ["1666", "しかし", "", "接続", "但是，然而"],
    1670: ["1670", "さて", "", "接続", "那么，接下来"],
    1698: ["1698", "年下", "としした", "名", "年纪小的人"],
    1699: ["1699", "信用する", "しんよう", "名・動3他", "信任，信用"],
    1702: ["1702", "とうとう", "", "副", "终于，到底"],
    1703: ["1703", "はんこ", "", "名", "印章"],
}

JP_CN = {
    282: ("洗衣店和酒店前台", ["妹は平日はクリーニング屋、週末はホテルのフロントでアルバイトをしている。いつも寝不足で、なかなか体を休めることができない。"], "妹妹平日在洗衣店打工，周末在酒店前台打工。她总是睡眠不足，身体很难好好休息。"),
    283: ("孩子想做的职业", ["子どもたちがなりたい職業について、かつてはエンジニアが上位だった。しかし、最近の1位は意外にもサラリーマンである。"], "关于孩子们将来想从事的职业，以前工程师排在前面。可是最近排第一的，意外地是公司职员。"),
    284: ("研修期间的工资", ["彼女は先々月から仕事を始めたが、研修期間も給料がもらえるらしい。"], "她从上上个月开始工作，听说研修期间也能拿到工资。"),
    285: ("给新员工的建议", ["新入社員には、いつも「単純で機械的な作業であっても、繰り返すことが大切だ」というアドバイスを送っている。"], "我总是建议新员工：即使是单纯、机械的工作，反复练习也很重要。"),
    286: ("加油站兼职", ["ガソリンスタンドでのアルバイトはきつく、まったく座ることができないので、腰を痛めてしまい、半年で辞めてしまった。"], "在加油站打工很辛苦，完全不能坐下，所以伤了腰，半年后就辞职了。"),
    287: ("向店长提出辞职", ["店長の態度が悪く、その上休憩時間も短い。無理を承知で、月末で辞めることを伝えたら、うまくいった。"], "店长态度不好，而且休息时间也短。我明知道可能不容易，还是告诉他月底要辞职，结果顺利解决了。"),
    288: ("出版社面试", ["ある出版社の副社長と面接することになった。特技は事務だとアピールしたら、見事に受かった。"], "我和一家出版社的副社长进行了面试。我强调自己的特长是事务工作，结果顺利通过了。"),
    289: ("失业原因", ["この月に失業した人の約7割が新型コロナウイルスの影響によるものである。"], "这个月失业的人中，大约七成是受新型冠状病毒影响。"),
    290: ("销售高级商品", ["彼は営業の仕事をしているが、扱っている商品が高級な物のため、めったに売れずに苦労している。"], "他做销售工作，但负责的商品是高档品，很少卖出去，所以很辛苦。"),
    291: ("积累职场经验", ["新しい職場は大変だと思うが、しっかり経験を積んで、力をつけてもらいたい。コミュニケーション能力が高い彼女なら、きっとできるはずだ。"], "新职场应该会很辛苦，但我希望她踏实积累经验、提升实力。她沟通能力强，一定能做到。"),
    292: ("兼职五年", ["パートとして働いているが、時給がまあまあなので長く続けられており、今月末で5年になる。"], "我在做兼职，因为时薪还不错，所以一直做了很久，到这个月底就满五年了。"),
    293: ("会员活动手册", ["会員のイベントは会員限定なので、会員に向けた参加マニュアルを作成する必要がある。"], "会员活动只限会员参加，所以需要制作一份面向会员的参加手册。"),
    294: ("临时招聘", ["あの店は新年とお盆の時期に混雑するので、半年に一度臨時でアルバイトを募集する。"], "那家店在新年和盂兰盆节期间会很拥挤，所以每半年临时招聘一次兼职。"),
    295: ("驾驶员的义务", ["運転手にとって周りの人や車に気を配り、注意を注ぐことは義務である。事故を起こしたら、二度とハンドルを握れなくなる。"], "对驾驶员来说，留意周围的人和车辆、集中注意力是义务。一旦发生事故，可能就再也不能开车了。"),
    296: ("速递履历书", ["会社に問い合わせたところ、今日中に速達で履歴書を提出すれば大丈夫だった。時間がないので、宛名などを書き忘れないようにしなければならない。"], "向公司咨询后得知，只要今天之内用速递提交履历书就可以。因为时间不多，必须注意不要忘记写收件人等信息。"),
    297: ("面试会场集合", ["指定された場所に集合して、みんなで一緒に面接会場に行った。"], "大家在指定地点集合，然后一起去了面试会场。"),
    298: ("交换名片", ["国際会議場でたまたま知り合いに会った。久しぶりだったので、名刺を交換して、食事会の日程調整を行った。"], "我在国际会议场偶然遇到熟人。因为很久没见，我们交换了名片，并调整了聚餐日程。"),
    299: ("职业介绍所", ["ハローワークで工業、サービス業などの希望条件から順に質問された。良い仕事かどうかがなかなか判断できなかった。"], "在公共职业介绍所，对方按顺序询问了我对工业、服务业等工作的希望条件。我一时很难判断是不是好工作。"),
    300: ("收银员的名牌", ["レストランで食事をして、会計のとき、レジの人の名札を見ると高校時代の恋人だった。久しぶりに会って驚いたため、クレジットカードのサインを間違えてしまった。"], "在餐厅吃饭结账时，我看到收银员的名牌，发现她是高中时代的恋人。太久没见让我很惊讶，结果把信用卡签名写错了。"),
    301: ("制造业经营", ["製造業はどこも経営が厳しい。ある人の話では、個人経営の会社はもうからないらしい。"], "制造业各处经营都很艰难。听人说，个人经营的公司似乎赚不到钱。"),
    302: ("办公室留守", ["オフィスに誰もいないのは危ないから、留守番しておいて。正午までに戻ってくるから、それまでに部屋の整理もやっておいてね。"], "办公室里一个人都没有很不安全，你先留守一下。我中午前会回来，在那之前也把房间整理一下。"),
    303: ("居酒屋厨房", ["居酒屋のキッチンで働いているが、看板メニューを作ることを上司に命令された。"], "我在居酒屋厨房工作，上司命令我做出招牌菜。"),
    304: ("送别会点酒", ["送別会でビールを10本注文すべきだったのに、間違えて10ダース注文してしまった。一時はどうなるかと思ったが、いろんな人が協力してくれたおかげで、何とかなりほっとしている。"], "送别会上本来应该点10瓶啤酒，我却误点成10打。一度不知道该怎么办，多亏许多人帮忙，总算解决了，我松了一口气。"),
    305: ("无职与单身", ["私は無職で独身だ。焦ったり、不安になったりすることもある。だが、可能な限り、仕事も恋愛も諦めないでがんばるつもりだ。"], "我没有工作，也还是单身。有时会着急，也会不安。但我打算尽可能不放弃工作和恋爱，继续努力。"),
    306: ("想当律师的孙子", ["孫は悩んでいる人を助けるため、弁護士になることを目指している。人の倍は努力している様子だ。"], "孙子为了帮助有烦恼的人，正以成为律师为目标。看起来他付出了别人两倍的努力。"),
    307: ("认真的交往", ["同僚は素敵な女性に出会い、真剣に交際している。そのため、まだキスもしていないようだ。"], "同事遇到了一位很棒的女性，正在认真交往。因此，他们似乎还没有接吻。"),
    308: ("葬礼上的想象", ["親友の葬式で、ろうそくを見つめながら、彼女がいないこれからの人生を想像した。つらくなった。"], "在好友的葬礼上，我凝视着蜡烛，想象今后没有她的人生，心里变得很难受。"),
    309: ("理想的父母", ["両親は理想的な夫婦だ。お互いに相手を大切にしている。母が父にプロポーズしたらしい。"], "我的父母是理想的夫妻，彼此都很珍惜对方。听说是母亲向父亲求婚的。"),
    310: ("不改姓的女儿", ["末っ子の娘は、たとえ結婚しても絶対に姓は変えたくないと言っている。世の中の常識に縛られたくないらしい。"], "小女儿说，即使结婚也绝对不想改姓。她似乎不想被社会常识束缚。"),
    311: ("夸大其词的朋友", ["ある友人は、周囲の人に小さな出来事を大げさに話すので、聞いていていらいらする。"], "有个朋友总是把小事夸大其词地讲给周围的人听，我听着就很烦躁。"),
    312: ("资格讲座", ["公務員試験のために自分で勉強するだけではなく、日本語教師の資格講座も最前列で受けている。標準的な問題は分かるが、難しい問題が多い。なかなか自信が付かない。"], "为了公务员考试，我不只自己学习，还坐在最前排听日语教师资格讲座。标准题能看懂，但难题很多，一直没什么自信。"),
    313: ("延长出差", ["出張で大阪に行った。大阪で新しく重要な会議が入ったので、戻る日にちを延ばす方向で話し合っている。"], "我出差去了大阪。因为在大阪又安排了新的重要会议，所以正在商量把返回日期延后。"),
    314: ("甩掉有钱男友", ["いとこはお金持ちの男性と付き合っていた。しかし、彼の会社の経営が苦しくなり、お金がなくなると、彼を振った。"], "表亲曾和一位有钱男性交往。但他的公司经营变困难、钱没了以后，她就甩了他。"),
    315: ("感谢演讲的邮件", ["＜メールの文章＞山田さん、おはようございます。林です。今日も暑いですね。さて、先日のパーティーではスピーチをしてくださり、ありがとうございました。感謝しています。パーティーの感想も聞かせてください。"], "＜邮件正文＞山田先生/女士，早上好。我是林。今天也很热呢。前几天的聚会上，感谢您为我们演讲，我非常感激。也请告诉我您对聚会的感想。"),
    316: ("升学与日语能力", ["大学院に進学し、建築について勉強したい。また、日本語のレベルを上げ、ぺらぺらと話せる能力をつけたい。"], "我想升入研究生院学习建筑。另外，我也想提高日语水平，培养能流利表达的能力。"),
    317: ("想当歌手的姐妹", ["隣の家の姉妹は歌手になりたいらしい。最近は早起きし、夢中で楽器を演奏している。うるさくて目が覚める。"], "邻居家的姐妹似乎想当歌手。最近她们早起，沉迷地演奏乐器，吵得我醒了。"),
    318: ("多国籍企业就业", ["大学生のとき、貿易を行う多国籍企業への就職を希望していた。今、実際に働いている。"], "大学时，我希望进入从事贸易的跨国企业工作。现在，我真的在那里工作。"),
    319: ("轻信签名", ["妻は年上の友人から、「私を信用して署名してください」と何度も頼まれた。素直な妻はとうとうはんこを押してしまった。"], "妻子多次被年长的朋友拜托：“请相信我并签名。”单纯的妻子最后还是盖了章。"),
    320: ("领取年金手续", ["年金をもらうための手続きを教えてもらった。市役所の窓口で受け付けていて、印鑑と保険証が必要だそうだ。"], "别人教了我领取年金所需的手续。听说市役所窗口可以受理，需要印章和保险证。"),
}


POS_RE = re.compile(r"(名|動|副|接尾|接頭|接続|ナ|イ|感)")
KANA_RE = re.compile(r"^[ぁ-ゖー〜～・]+$")


def raw_lines(story: dict) -> list[str]:
    raw = story.get("vocabRaw") or []
    if isinstance(raw, str):
        return [line.strip() for line in raw.splitlines() if line.strip()]
    return [str(line).strip() for line in raw if str(line).strip()]


def normalize_meaning(raw: str) -> str:
    parts = raw.replace("【", "[").replace("】", "]").split("/")
    if len(parts) >= 2:
        meaning = parts[1]
    else:
        meaning = raw
    meaning = meaning.strip(" []［］「」")
    return MEANING_FIXES.get(meaning, meaning) or "待校正"


def clean_token(text: str) -> str:
    text = text.replace("［", "[").replace("］", "]").replace("＋", "+")
    return re.sub(r"\s+", "", text).strip()


def number_from_token(token: str, min_no: int, max_no: int) -> int | None:
    if not token.isdigit():
        return None
    no = int(token)
    if min_no <= no <= max_no:
        return no
    if 100 <= no <= 999 and min_no <= no + 1000 <= max_no:
        return no + 1000
    return None


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


def parse_vocab(story: dict, min_no: int, max_no: int) -> list[list[str]]:
    lines = raw_lines(story)
    indexes = []
    for i, item in enumerate(lines):
        no = number_from_token(item, min_no, max_no)
        if no is not None:
            indexes.append((no, i))
    rows = []
    seen = set()
    for idx, (no, start) in enumerate(indexes):
        if no in seen:
            continue
        end = indexes[idx + 1][1] if idx + 1 < len(indexes) else len(lines)
        row = parse_vocab_block(no, lines[start + 1 : end])
        if row[1] != "未確認":
            rows.append(row)
            seen.add(no)
    for no, row in MANUAL_VOCAB.items():
        if min_no <= no <= max_no and row_belongs_to_story(no, story["id"]):
            rows = [existing for existing in rows if existing[0] != str(no)]
            rows.append(row)
    rows.sort(key=lambda row: int(row[0]))
    return rows


def row_belongs_to_story(no: int, story_id: int) -> bool:
    return {
        **{n: 282 for n in range(1493, 1498)},
        **{n: 283 for n in range(1498, 1504)},
        **{n: 284 for n in range(1504, 1508)},
        **{n: 285 for n in range(1508, 1514)},
        **{n: 286 for n in range(1514, 1518)},
        **{n: 287 for n in range(1518, 1524)},
        **{n: 288 for n in range(1524, 1531)},
        **{n: 289 for n in range(1531, 1535)},
        **{n: 290 for n in range(1535, 1539)},
        **{n: 291 for n in range(1539, 1544)},
        **{n: 292 for n in range(1544, 1549)},
        **{n: 293 for n in range(1549, 1555)},
        **{n: 294 for n in range(1555, 1560)},
        **{n: 295 for n in range(1560, 1565)},
        **{n: 296 for n in range(1565, 1571)},
        **{n: 297 for n in range(1571, 1575)},
        **{n: 298 for n in range(1575, 1578)},
        **{n: 299 for n in range(1578, 1582)},
        **{n: 300 for n in range(1582, 1585)},
        **{n: 301 for n in range(1585, 1588)},
        **{n: 302 for n in range(1588, 1592)},
        **{n: 303 for n in range(1592, 1596)},
        **{n: 304 for n in range(1596, 1602)},
        **{n: 305 for n in range(1602, 1610)},
        **{n: 306 for n in range(1610, 1618)},
        **{n: 307 for n in range(1618, 1626)},
        **{n: 308 for n in range(1626, 1632)},
        **{n: 309 for n in range(1632, 1638)},
        **{n: 310 for n in range(1638, 1645)},
        **{n: 311 for n in range(1645, 1650)},
        **{n: 312 for n in range(1650, 1657)},
        **{n: 313 for n in range(1657, 1663)},
        **{n: 314 for n in range(1663, 1670)},
        **{n: 315 for n in range(1670, 1675)},
        **{n: 316 for n in range(1675, 1682)},
        **{n: 317 for n in range(1682, 1690)},
        **{n: 318 for n in range(1690, 1697)},
        **{n: 319 for n in range(1697, 1704)},
        **{n: 320 for n in range(1704, 1710)},
    }.get(no) == story_id


def story_topic(story_id: int) -> int | None:
    for topic_id, story_range in TOPIC_RANGES.items():
        if story_id in story_range:
            return topic_id
    return None


def line(text: str) -> dict:
    return {"text": text}


def assert_complete(by_id: dict[int, dict]) -> None:
    expected = {
        14: set(range(1493, 1602)),
        15: set(range(1602, 1710)),
    }
    actual = {14: set(), 15: set()}
    for topic_id, story_range in TOPIC_RANGES.items():
        for story_id in story_range:
            story = by_id[story_id]
            for row in story.get("vocab", []):
                if len(row) != 5:
                    raise SystemExit(f"T{story_id:03d} malformed vocab: {row}")
                if not row[4]:
                    raise SystemExit(f"T{story_id:03d} empty meaning: {row}")
                actual[topic_id].add(int(row[0]))
    for topic_id, numbers in expected.items():
        missing = sorted(numbers - actual[topic_id])
        extra = sorted(actual[topic_id] - numbers)
        if missing or extra:
            raise SystemExit(f"Topic {topic_id} vocab mismatch missing={missing} extra={extra}")


def main() -> None:
    text = DATA.read_text(encoding="utf-8")
    prefix, raw = text.split("=", 1)
    data = json.loads(raw.strip().rstrip(";"))
    by_id = {story["id"]: story for story in data["stories"]}

    for story_id in range(282, 321):
        story = by_id[story_id]
        topic_id = story_topic(story_id)
        if topic_id is None:
            continue
        title, japanese, chinese = JP_CN[story_id]
        story["topicId"] = topic_id
        story["title"] = title
        story["japanese"] = [line(item) for item in japanese]
        story["naturalChinese"] = [chinese]
        story["originalChinese"] = [chinese]
        story["reviewStatus"] = "已校对"
        if story_id in IMAGE_OVERRIDES:
            story["images"] = IMAGE_OVERRIDES[story_id]
        if topic_id == 14:
            story["vocab"] = parse_vocab(story, 1493, 1601)
        elif topic_id == 15:
            story["vocab"] = parse_vocab(story, 1602, 1709)

    for story_id, topic_id in ROUTE_ONLY.items():
        story = by_id[story_id]
        story["topicId"] = topic_id
        story["reviewStatus"] = "OCR未校对"

    assert_complete(by_id)

    DATA.write_text(prefix + "= " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("patched Topics 14-15 and routed T321-T325 to Topic 16")


if __name__ == "__main__":
    main()
