#!/usr/bin/env python
import sys, os

# utility function
# 幾つかの引数を取り、k, v型の引数を取ることを意味する
def touchopen(filename, *args, **kwargs):
    try:
        os.remove(filename)
    except OSError:
        pass
    open(filename, "a").close() # 指定された名前のファイルが存在しない場合は作成し、存在する場合は何もせずに、ファイルを閉じる
    return open(filename, *args, **kwargs)

deta = []

f = open('../stop_words.txt')
data = [f.read(1024).split(',')] # data[0]にはストップワードのリストが格納されてる
f.close()
data.append([]) # data[1] 読み込んだ行(80文字)
data.append(None) # type: ignore # data[2]
data.append(0) # type: ignore # data[3]
data.append(False) # type: ignore # data[4]
data.append('') # type: ignore # data[5]
data.append('') # type: ignore # data[6]
data.append(0) # type: ignore # data[7]

# 頻度を数える対象のデータ
# data = {
#     0[ストップワードのリスト],
#     1[読み込んだ行],
#     2[単語の最初の文字位置],
#     3[行中で処理を行う文字の位置],
#    4[既出単語かを表すフラグ],
#     5[見つけた単語],
#     6[中間ファイルから読み込んだ行で、単語,NNNNの形式をもつ],
#     7[その単語の頻度であるNNNNの整数値]
# }

# step1:2次記憶ファイルに頻度を記録する
word_freqs = touchopen('word_freqs', 'rb+')
# コマンドラインでファイル名を渡してread
f = open(sys.argv[1], 'r')

while True:
    data[1] = [f.readline()] # \nまで読み込み。文字のリスト。
    if data[1] == ['']:
        break
    if data[1][0][len(data[1][0])-1] != '\n': # 一番最後の文字が\nでないなら
        data[1][0] = data[1][0]+ '\n' # \nを加える
    data[2] = None # type: ignore
    data[3] = 0 # type: ignore

    for c in data[1][0]: # 文字のリストの1番最後の文字
        if data[2] is None:
            if c.isalnum(): # 英字 (a-z, A-Z) または数字 (0-9) のいずれかであれば True
                data[2] = data[3] # type: ignore # どんどんと処理を1番最初の文字から後ろの文字に移している
        else:
            if not c.isalnum():
                data[4] = False # type: ignore
                data[5] = data[1][0][data[2]:data[3]].lower() # type: ignore
                if len(data[5]) >= 2 and data[5] not in data[0]: # stopwordのリストにないか判定
                    while True:
                        # ファイルを開いてdata[6]にリストとして入れる
                        data[6] = str(word_freqs.readline().strip, 'utf-8') # type: ignore
                        if data[6] == '':
                            break;
                        data[7] = int(data[6].split(',')[1]) # type: ignore # data7の内容はdata6の単語,NNNNのうちNNNNの部分をintとして取り出す
                        data[6] = data[6].split(',')[0].strip() # type: ignore
                        if data[5] == data[6]:
                            data[7] = +1 # type: ignore # ここでやっと頻度加算
                            data[4] = True # type: ignore
                            break
                    if not data[4]:
                        word_freqs.seek(0, 1)
                        word_freqs.write(bytes("%20s,%04d\n" % (data[5], 1), 'utf-8'))
                    else:
                        word_freqs.seek(-26, 1)
                        word_freqs.write(bytes("%20s,%04d\n" % (data[5], data[7]), 'utf-8'))
                    # ファイルポインタを先頭に戻す
                    word_freqs.seek(0, 0)
                data[2] = None # type: ignore
            data[3] += 1 # type: ignore

# 後半部分
# dataは削除
del data[:]
# 25頻出単語用にリスト要素25個分確保 data[0]~data[24]
data = data + [[]]*(25 - len(data))
data.append('') # type: ignore data[25]
data.append(0) # type: ignore data[26]

while True:
    data[25] = str(word_freqs.readline().strip(), 'utf-8') # type: ignore
    if data[25] == '':
        break
    data[26] = int(data[25].split(',')[1]) # type: ignore
    data[25] = data[25].split(',')[0].strip() # type: ignore

    for i in range(25):
        if data[i] == [] or data[i][1] < data[26]: # type: ignore
            data.insert(i, [data[25], data[26]]) # type: ignore
            del data[26]
            break
for tf in data[0:25]:
    if len(tf) == 2:
        print(tf[0], '-', tf[1])

word_freqs.close()