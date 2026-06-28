
ステージングを解除
git restore --staged <ファイル名>

## git pull
```bash

git pull 
= git fetch ：最新コミット取得
+ git merge：現在のブランチに統合


git pull origin(リモートのオリジナル) dev(localのdevブランチ)

=

git fetch origin dev リモートのオリジナルにあるdevブランチから最新のコミット取得
+
git merge origin/dev originというリモート上にあるdevブランチに統合

```



詳しくいうと

git fetch origin(リモートrepo) dev (devブランチ)

`fetch`
1. リモート(リモート追跡ブランチ)にあるコミットハッシュとコミットしたコードを見る
2. もらったコミット差分を localのgit.objectsに保存する
3. localにある .git/refsはコミットハッシュを記録する　ここにdevの最新コミットハッシュを更新。
    「今最新のリモートはこうなっているよ、このハッシュだよ。」

つまり、リモートがどこを指しているかを localの .git/refs にメモしています


## git merge

```bash
git merge origin/dev

localで今いるブランチdevに対して リモートのorigin/devが指しているコミットを取り込みたい

```

### mergeのパターンA fast-forward 

---------------->| origin/dev 最新、進んでいる
local            |
------|--------->|
遅れている `merge` で追いつく

### マージのパターンB お互いコードを進めていて、枝分かれしている場合

        A---B---C
       /         \
......O           M   ← merge commit（親が C と E の2つ）
       \         /
        D---E---/


1. Baseライン（お互いに共通する祖先コミット）を見つける
2. Base Line + origin/dev + local　で 3つのmergeを試みる
3. 同じ行をぶつけていなければ、自動でマージして新しい merge commit（親が2つ＝CとEの両方を指すコミット）を作り、それを local dev の先頭にする
4. 同じ行をぶつけていたら（コンフリクト）、ファイルを手直ししてから git add → git commit