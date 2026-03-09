"""
request.jsonを
response.json
に書き換える
"""

import json

file_path = "target.json"

with open(file_path, "r", encoding="utf-8") as req_f:
    # json to obj
    request_data = json.load(req_f)
    # json.loads() はstrをjsonに変換するもの

# pythonでobjを書き換え


# 最後に
with open("response_data.json", "w", encoding="utf-8") as res_f:
    # dumpは ファイルへの書き出し
    json.dump(response_data, res_f, indent=4, ensure_ascii=False)


# json.dump()	ファイルに書き込む 
# json.load(req_f) json_file → jsondictObj
# json.dumps()	文字列として返す
# json.loads(some_str_obj) str　→ jsonDictObj