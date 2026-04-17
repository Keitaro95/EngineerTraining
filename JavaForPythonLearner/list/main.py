def main():
    # 0が10個入ったリストを作って
    count = [0]*10
    data = open('test.dat')

    # dataを展開→数値取り出し→整数に変換→リスト内の位置でインデックス+1取り出し
    for line in data:
        count[int(line)] = count[int(line)] + 1

    idx = 0
    # countリストからnumを展開
    for num in count:
        print(idx, " occurd ", num, " times.")
        idx += 1

main()