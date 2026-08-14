# BERT で2値分類 — 学習からモデルを動かすまで

日本語 BERT をファインチューニングして、テキストの2値分類器を作る手順。
このリポジトリでは「メッセージが好意シグナルか否か」を題材にしているが、
データを差し替えれば任意の2値分類（文字起こしのトラブル判定など）に使える。

## 全体像

```
 ① データ準備          data/labeled_messages.jsonl   {"text": "...", "label": 0/1}
       ↓
 ② トークナイズ        文 → BERT が読める数値ID列    bert/dataset.py
       ↓
 ③ ファインチューニング  事前学習済みBERT + 分類ヘッド  bert/train.py
       ↓
 ④ 評価                検証セットで F1 を測る
       ↓
 ⑤ 保存                models/affinity-bert/          重み + tokenizer + 設定
       ↓
 ⑥ 推論                保存したモデルを読んで判定     bert/predict.py
```

**重要**: ③で学習するのは「分類ヘッド（最終層）」だけではなく BERT 本体の重みも含む。
だから「ファインチューニング（追加学習）」と呼ぶ。ゼロから学習するわけではないので、
数百件のデータでも動く。

---

## ① 環境構築

このマシンでは共有環境 `~/.venvs/ml` にリンクを張る方式を使う。

```bash
cd ~/Documents/Code/エンジニアトレーニング/ML
uv venv --python 3.14        # ← 3.14 の明示が必須
ml-link
```

`uv venv` は引数なしだと 3.12 を拾うことがあり、その場合リンクが弾かれる（正しい挙動）。

```
ERROR: 共有環境は Python 3.14、対象 venv は 3.12。ABI が違うため張れません
```

共有環境にはこの作業で以下を追加済み。**リンク済みの全プロジェクトに反映されている。**

```bash
uv pip install --python ~/.venvs/ml/bin/python fugashi unidic-lite scikit-learn
```

| パッケージ | 用途 |
|---|---|
| `fugashi` | MeCab の Python バインディング。日本語BERTの前段の分かち書きに必須 |
| `unidic-lite` | fugashi が使う辞書。**`ipadic` ではない**（後述） |
| `scikit-learn` | 評価指標の比較用（本体の学習には不要） |

`torch` 2.13.0 / `transformers` 5.5.3 は元から入っている。`datasets` と `accelerate` は
**使わない実装にしたので不要**。

---

## ② データを用意する

JSONL（1行1件）。これだけ。

```json
{"text": "また今度ゆっくり話したいです", "label": 1}
{"text": "また今度で", "label": 0}
{"text": "忙しいけど時間作りますね", "label": 1}
{"text": "忙しいので難しいです", "label": 0}
```

このデータの作り方が精度を決める。**特に、表面的な単語が同じで意味が逆になるペアを
意図的に入れる**こと。BERT を使う理由がまさにそこにあるため。

| 表層 | label 1 | label 0 |
|---|---|---|
| また今度 | また今度ゆっくり話したいです | また今度で |
| 忙しい | 忙しいけど時間作りますね | 忙しいので難しいです |
| 好き | 好きなタイプはあなたみたいな人です | 好きな食べ物はラーメンです |
| 問題 | 問題ないです、むしろ嬉しいです | 問題があるので考え直したいです |

TF-IDF は単語の出現しか見ないので、この区別は**原理的に不可能**。前回作った
ルールベースの `affinity/lexicon.py` も、「また今度」に否定の重みを付けたせいで
「また今度ゆっくり話したいです」を誤検出し、正規表現の否定先読みで手当てした。
BERT ならこれを辞書のメンテなしで扱える。

同梱のデモデータは 134 件（`data/labeled_messages.jsonl`）。**実運用には全く足りない**
（後述）。

---

## ③④⑤ 学習する

```bash
.venv/bin/python -m bert.train --data data/labeled_messages.jsonl --out models/affinity-bert
```

実際の出力:

```
デバイス: mps
データ: 全 134 件 -> 学習 107 / 検証 27
  クラス分布(全体): {0: 67, 1: 67}
事前学習モデル: tohoku-nlp/bert-base-japanese-v3
epoch 1/4 | train_loss 0.7095 | val_loss 0.6590 | acc 0.654 | P 0.591 R 1.000 F1 0.743
  -> 保存しました（F1 更新）: models/affinity-bert
epoch 2/4 | train_loss 0.6174 | val_loss 0.6332 | acc 0.731 | P 0.750 R 0.692 F1 0.720
epoch 3/4 | train_loss 0.5321 | val_loss 0.5868 | acc 0.769 | P 0.769 R 0.769 F1 0.769
  -> 保存しました（F1 更新）: models/affinity-bert
epoch 4/4 | train_loss 0.5164 | val_loss 0.5748 | acc 0.731 | P 0.750 R 0.692 F1 0.720

学習完了。最良 F1 = 0.769
```

起動時に出る `MISSING: classifier.weight / classifier.bias` は**正常**。
事前学習モデルには分類ヘッドが無く、新規にランダム初期化されたという意味。
これから学習するのがまさにその層なので、警告ではあるがエラーではない。

### 主なオプション

```bash
--epochs 4          # 学習回数
--batch-size 16     # 一度に処理する件数。メモリ不足なら下げる
--lr 2e-5           # 学習率。1e-5 〜 5e-5 の範囲を出ないこと
--max-length 128    # 何トークンで切るか。長文なら 256 / 512
--device cpu        # 既定は cuda > mps > cpu の自動選択
```

### 学習ループの中身

`bert/train.py` の核心はこの6行だけ。これがファインチューニングの全て。

```python
outputs = model(**batch)      # 順伝播。labels を渡すと loss も一緒に返る
loss = outputs.loss
loss.backward()               # 逆伝播で、各重みをどちらに動かすべきか計算
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # 勾配の暴走を抑える
optimizer.step()              # 重みを実際に更新
scheduler.step()              # 学習率を少しずつ下げる
optimizer.zero_grad()         # 勾配をリセット（忘れると累積してバグる）
```

**学習率 `2e-5` の小ささが本質。** 事前学習で獲得済みの日本語の知識を壊さずに、
タスクに合わせて微調整するための値。ここを `1e-3` のような通常のNNの値にすると、
学習済みの重みが吹き飛んで性能が出ない。

### Trainer を使わない理由

記事のコードは `Trainer` を使っているが、ここでは素の PyTorch ループにした。

1. **依存が減る** — `datasets` と `accelerate` が不要になる
2. **API 変更に強い** — transformers v5 で `evaluation_strategy` は `eval_strategy` に
   改名された。v4 時代のチュートリアルは v5 でそのまま動かない
3. **何をしているか見える** — 上の6行が隠れない

`Trainer` は分散学習・勾配累積・混合精度などを自動でやってくれるので、
データが大きくなったら乗り換える価値はある。

---

## 評価の読み方

**Accuracy だけを見ないこと。** クラスが偏っているとき、全部を多数派クラスと
答えるだけで高い accuracy が出る。

| 指標 | 意味 | 気にすべき場面 |
|---|---|---|
| Precision | 「好意あり」と判定したうち、実際に好意だった割合 | 誤検出を避けたい（ぬか喜びしたくない） |
| Recall | 実際の好意のうち、拾えた割合 | 見逃しを避けたい |
| F1 | 上2つの調和平均 | 総合。モデル選択はこれで行う |

上のログの epoch 1 が典型例で、**R 1.000 と一見完璧だが P 0.591**。
これは「ほぼ全部を好意ありと答えた」だけで、分類器として機能していない。
F1 で見れば 0.743 と正体が分かる。

`train_loss` が下がるのに `val_loss` が上がり始めたら過学習。そこで打ち切る。

---

## ⑥ モデルを動かす

保存済みモデルを読んで判定する。**学習時と同じ tokenizer を使う必要がある**ため、
tokenizer もモデルと同じディレクトリから読んでいる。ここを取り違えると、
エラーは出ないまま静かに精度が落ちる。

```bash
.venv/bin/python -m bert.predict models/affinity-bert \
  "また今度ゆっくり話したいです" "また今度で" \
  "忙しいけど時間作りますね" "忙しいので難しいです" "了解しました"
```

実際の出力:

```
████████████░░░░░░░░ P(好意)=0.624  「また今度ゆっくり話したいです」
█████░░░░░░░░░░░░░░░ P(好意)=0.270  「また今度で」
██████████░░░░░░░░░░ P(好意)=0.516  「忙しいけど時間作りますね」
█████░░░░░░░░░░░░░░░ P(好意)=0.286  「忙しいので難しいです」
███████░░░░░░░░░░░░░ P(好意)=0.366  「了解しました」

文面スコア（[-1,1] 換算）: -0.091
```

対比ペアの大小関係は正しく付いている（0.624 > 0.270、0.516 > 0.286）。
ただし **0.5 付近に寄っていて確信度が低い**。134 件では当然で、
ここが改善するかどうかはデータ量で決まる。

ファイルから一括で読むこともできる。

```bash
.venv/bin/python -m bert.predict models/affinity-bert --file messages.txt --json
```

### コードから使う

```python
from bert.predict import AffinityClassifier

clf = AffinityClassifier("models/affinity-bert")
results = clf.predict(["また今度ゆっくり話したいです"])
print(results[0]["p_positive"])        # 0.624

score = clf.affinity_score([...])      # [-1, 1] に正規化した文面スコア
```

---

## 既存のスコアラーへの組み込み

このリポジトリのルールベース判定（`affinity/`）とは、**置き換えではなく分業**になる。

| 層 | 実装 | BERT で置き換わるか |
|---|---|---|
| 文面スコア | `affinity/lexicon.py` の辞書 | **置き換わる**。`AffinityClassifier.affinity_score()` が同じ `[-1,1]` を返す |
| 行動指標 | `affinity/features.py` | **置き換わらない**。返信速度・会話開始率は言語モデルの領分ではない |
| 集計と判定 | `affinity/scoring.py` | そのまま |

`affinity_score()` の値域を `scoring.py` の `content_signal` と揃えてあるので差し替えられる。

**ただし、これで判定が「客観的」になるわけではない。** BERT はラベルを付けた人の
判断を学習するだけなので、文面側の主観性は消えない。むしろ BERT は辞書より柔軟に
丸暗記できるぶん、**主観をより忠実に再現する**。行動指標に重み 0.60 を置いた設計は
BERT を入れても変えるべきではない。

---

## 記事のコードから変えた点

よくあるチュートリアルのコードは、この環境ではそのまま動かないか、動いても
意図通りにならない箇所がある。

| 箇所 | よくある記述 | 実際に必要な対応 |
|---|---|---|
| モデル名 | `cl-tohoku/bert-base-japanese-v3` | `tohoku-nlp/...`（組織名が変更済み。旧名もリダイレクトはされる） |
| 辞書 | `pip install fugashi ipadic` | **v3 は `unidic-lite`**。`ipadic` は v1/v2 用で、v3 に使うと分割が変わる |
| 評価設定 | `evaluation_strategy="epoch"` | transformers v5 で削除。`eval_strategy` に改名 |
| パディング | `padding="max_length"` | バッチ内最長に合わせる動的パディング。短文が多いと計算量が数倍変わる |
| 評価 | `Trainer` に検証セットを渡していない | 検証セットなしでは過学習に気づけない。層化分割で分ける |
| 保存 | なし | `save_pretrained()` しないと学習結果がプロセス終了で消える |
| 高速化 | `fp16=torch.cuda.is_available()` | Mac は CUDA ではなく **MPS**。fp16 は効かず fp32 で動く |
| データ量 | サンプル6件 | 6件では学習にならない。丸暗記して終わる |

---

## データ量の目安

これが最大の制約。

| 件数 | 実態 |
|---|---|
| 〜50 | 学習にならない。丸暗記するだけで、検証スコアも当てにならない |
| 100〜300 | 動きはする。確信度が 0.5 付近に寄る（＝今の状態） |
| 500〜1000 | 実用の下限。ルールベースを明確に上回り始める |
| 3000〜 | BERT の本領。表現の揺れにも強くなる |

`bert/train.py` は 50 件未満のとき警告を出す。

なお、**ルールベースのスコアラーで自動ラベル付けして BERT を学習させるのは無意味**。
BERT がルールを再現するだけで、新しい情報は一切増えない（蒸留にはなるが精度は上がらない）。

---

## 実行コマンドまとめ

```bash
# 環境
cd ~/Documents/Code/エンジニアトレーニング/ML
uv venv --python 3.14 && ml-link

# 学習
.venv/bin/python -m bert.train --data data/labeled_messages.jsonl --out models/affinity-bert

# 推論
.venv/bin/python -m bert.predict models/affinity-bert "判定したい文"

# ルールベース版（BERT不要・学習不要）
.venv/bin/python main.py data/sample_messages.jsonl
```
