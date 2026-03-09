

class Calculator:

    def __init__(self):
        pass

    def analyse_single(self, b, a):
        pass

    

def cate_by_cos(
    before_list: list[str],
    after_list: list[str],
    threshhold: float = 0.7,
) -> dict:
    calc = Calculator()
    result = {
        "changed": [],
        "removed": [],
        "added": []
    }

    all_pairs = []
    for b_idx in range(len(before_list)):
        for a_idx in range(len(after_list)):
            sim = round(calc.analyse_single(before_list[b_idx], after_list[a_idx]), 4)
            all_pairs.append((b_idx, a_idx, sim))

    # x[2]はsimに当たる。 sim高い順にsort 
    all_pairs.sort(key=lambda x: x[2], reverse=True)

    # 空の集合
    used_b = set()
    used_a = set()

    for b_idx, a_idx, sim in all_pairs:
        
        # 使用済み判定を喰らっているインデックスがあるなら通過
        if b_idx in used_b or a_idx in used_a:
            continue
        
        # sim = 1.0　のインデックスは使用済みに追加
        if sim == 1.0:
            used_b.add(b_idx)
            used_a.add(a_idx)

        # 0.7 <= sim < 1.0
        # changed に追加
        elif sim >= threshhold:
            result["changed"].append(
                {
                    "old": before_list[b_idx],
                    "new": after_list[a_idx]
                 }
            )
            # インデックスを使用済みに追加
            used_b.add(b_idx)
            used_a.add(a_idx)
        # sim < 0.7
        # 0.7のものだけは透過させていく
        else:
            continue
    
    # bの要素数の分だけ
    for b_idx in range(len(befor_list)):
        # 使用済みでないbインデックスのもののみ
        if b_idx not in used_b:
            result["removed"].append(
                {"old": before_list[a_idx],
                 "new": ""}
            )

    for a_idx in range(len(after_list)):
        if a_idx not in used_a:
            result["added"].append(
                {"old": "",
                 "new": after_list[a_idx]}
            )
    return result
            

