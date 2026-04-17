def main():
    data = open('alice30.txt')
    # spaceで分割したリスト
    wordList = data.read().split()
    count = {}

    for w in wordList:
        w = w.lower()
        # 単語 w の登場回数を登録
        count[w] = count.get(w,0) + 1

    keyList = sorted(count.keys())

    for k in keyList:
        # print文のフォーマッター
        # %-20s — キー名を左揃えで20文字幅に固定
        # %4d — 出現回数を右揃えで4桁に固定
        print("%-20s occurred %4d times" % (k, count[k]))

main()