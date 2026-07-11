#!/usr/bin/env python3
from repair_utils import apply_topic_patch, dialogue


PATCHES = {
    17: {"title":"进店时受到欢迎","type":"dialogue","japanese":dialogue(("A","いらっしゃいませ。"),("B","どうも。")),"focus":["いらっしゃいませ"],"naturalChinese":["A：欢迎光临。","B：你好。"],"originalChinese":["A：欢迎光临。","B：你好。"],"vocab":[["27","いらっしゃいませ","","句","欢迎光临"]]},
    18: {"title":"招呼咖啡店店员","type":"dialogue","japanese":dialogue(("A","すみません。"),("B","はい。")),"focus":["すみません"],"naturalChinese":["A：不好意思。","B：好的。"],"originalChinese":["A：不好意思。","B：是。"],"vocab":[["28","すみません②","","句","不好意思"]]},
    19: {"title":"点一杯咖啡","type":"dialogue","japanese":dialogue(("A","コーヒー、ください。"),("B","コーヒーですね。")),"focus":["コーヒー","ください"],"naturalChinese":["A：请给我一杯咖啡。","B：一杯咖啡，对吧。"],"originalChinese":["A：请给我咖啡。","B：咖啡。好的。"],"vocab":[["29","コーヒー","","名","咖啡"],["30","ください","","句","请给我"]]},
    20: {"title":"看到草莓蛋糕","type":"dialogue","japanese":dialogue(("A","いちごのケーキです。"),("B","わあ。")),"focus":["いちご","ケーキ","わあ"],"naturalChinese":["A：这是草莓蛋糕。","B：哇！"],"originalChinese":["A：这是草莓蛋糕。","B：哇～。"],"vocab":[["31","いちご","","名","草莓"],["32","ケーキ","","名","蛋糕"],["33","わあ","","感","哇"]]},
    21: {"title":"端上咖喱饭","type":"dialogue","japanese":dialogue(("A","カレーライスです。どうぞ。"),("B","いただきます。")),"focus":["カレーライス","いただきます"],"naturalChinese":["A：您的咖喱饭，请慢用。","B：我开动了。"],"originalChinese":["A：这是咖喱饭。请慢用。","B：我要开动了。"],"vocab":[["34","カレー（ライス）","","名","咖喱饭"],["35","いただきます","","句","我开动了"]]},
    22: {"title":"向店员要水","type":"dialogue","japanese":dialogue(("A","あのー、水をください。"),("B","はい、どうぞ。")),"focus":["あのー","水","ください"],"naturalChinese":["A：那个，请给我水。","B：好的，请用。"],"originalChinese":["A：那个～请给我水。","B：好的，请用。"],"vocab":[["36","あのー","","感","那个"],["37","水","みず","名","水"]]},
    23: {"title":"用餐后离店致谢","type":"dialogue","japanese":dialogue(("A","ごちそうさまでした。"),("B","ありがとうございました。")),"focus":["ごちそうさまでした","ありがとうございました"],"naturalChinese":["A：多谢款待。","B：谢谢惠顾。"],"originalChinese":["A：多谢款待。","B：谢谢。"],"vocab":[["38","ごちそうさまでした","","句","多谢款待"],["39","ありがとうございました","","句","谢谢"]]},
}

if __name__ == "__main__":
    changed=apply_topic_patch(level="n5",topic_id=3,patches=PATCHES,source="N5 PDF pages 26-28 (printed pages 24-26)",reviewed_at="2026-07-12T00:40:00+09:00")
    print(f"patched {len(PATCHES)} N5 Topic 3 stories; logged {changed} field changes")
