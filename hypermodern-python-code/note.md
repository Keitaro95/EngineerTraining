

homebrewでpythonをインストールしてる

Python Launcher for Unixでpyコマンド
これでよしなにインタープリタを探してくれる
仮想環境ならその仮想環境の

```sh
py  hello.py
py -m hello
py -m pip install some-package
pip --python=some-env install some-pachage
```

importlibでモジュールの場所を確認できる

## シバンでインタープリタの場所を確認する

```
#!/usr/local/bin/python3.12
```

## 仮想環境

win
```sh
py -m venv .venv
.venv\Scripts\activate
```
mac
source .venv/bin/activate

pipxを使うと、仮想環境にinstallした
pythonアプリケーションをよしなに使いまわせる

pipx run some-app でinstallせずrunできる


## python moduleとは
インタプリタはsys.pathを見に行く
↓
標準ライブラリの場所
↓
site-packagesディレクトリの場所（仮想環境）


## python プロジェクトをパッケージングする
tomlファイルを作るとpythonプロジェクトとして使いまわせるようになる

buildはパッケージ　ビルドフロントエンドで
ビルドプロセスをオーケストレーションする。
ビルドバックエンドはhatchlingでこれはtomlにそれを使うように明示してある。
ビルドすると
dist/sdist
dist/wheel
2つのバイナリができる

pipx run build