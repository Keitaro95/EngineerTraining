# Hypermodern Python OCR ノート

画像ファイルを降順（IMG_0485 → IMG_0464）でOCRした内容です。

---

## IMG_0485.JPG (p.153)

### 例6-14 fetch()関数をhttpxで書き換える

```python
import httpx

from importlib.metadata import metadata

USER_AGENT = "{Name}/{Version} (Contact: {Author-email})"

def fetch(url):
    fields = metadata("random-wikipedia-article")
    headers = {"User-Agent": USER_AGENT.format_map(fields)}
    with httpx.Client(headers=headers, http2=True) as client:
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()
        data = response.json()

    return Article(data["title"], data["extract"])
```

### 6.6 プラグインによるpytestの拡張

「3.11.5 エントリポイント」で説明した通り、誰でもpytestプラグインを作成して内部に公開できます。次に、pytestの出力を強化して、プログレスバーを追加するpytest-sugarプラグインを紹介します。本節では、pytestプラグインを詳しく扱います。

### 6.6.1 pytest-httpserverプラグイン

pytest-httpserver（https://oreil.ly/E5eH5）プラグインには、例6-10よりも再利用性が高く、広く使われているhttpserverフィクスチャがあります。

まず、テストの依存関係にpytest-httpserverを追加します。次に、私たちが実装したhttpserverフィクスチャをテストモジュールから削除します。そして、serveフィクスチャを修正して、pytest-httpserverのhttpserverフィクスチャを利用します（例6-15）。

### 例6-15 pytest-httpserverを使ってserveフィクスチャを修正する

```python
@pytest.fixture
def serve(httpserver):
    def f(article):
        json = {"title": article.title, "extract": article.summary}
        httpserver.expect_request("/").respond_with_json(json)
        return httpserver.url_for("/")
    return f
```

---

## IMG_0484.JPG (p.152)

### 例6-11 fetch()関数のテスト（バージョン2）

```python
def test_fetch(article):
    def serve(article):
        httpserver.article = article
        return f"http://localhost:{httpserver.server_port}"
    assert article == fetch(serve(article))
```

❶ サーバにArticleを保存して、リクエストハンドラがそれにアクセスできるようにする。

serve()関数はコンテキストマネージャを返さなくなり、単なるURLの文字列を返すようになりました。serve()関数はフィクスチャが準備からクリーンアップまですべて処理します。しかし、改善企業はまだあります。fetch()関数に関するテストを含め、関数がネストしているのでテストが複雑になっています。ここで、serve()を独自のフィクスチャ内で定義しましょう。フィクスチャは関数を含む任意のオブジェクトを返せます（例6-12）。

### 例6-12 serveフィクスチャ

```python
@pytest.fixture
def serve(httpserver):  ❶
    def f(article):  ❷
        httpserver.article = article
        return f"http://localhost:{httpserver.server_port}"
    return f
```

❶ 外側の関数はhttpserverに依存するserveフィクスチャを定義する。
❷ 内側の関数は、外側で呼び出すserve関数。

このようにserveフィクスチャを定義すると、各テストは1行に収まります（例6-13）。また、セッションごとにHTTPサーバが起動および停止するので、最初の実装よりも高速になります。

### 例6-13 fetch()関数のテスト（バージョン3）

```python
def test_fetch(article, serve):
    assert article == fetch(serve(article))
```

テストは特定のHTTPクライアントライブラリに依存していません。fetch()関数をhttpxで書き換えることができます。モンキーパッチを使っていたならば、テストは壊れていたでしょう。しかし、私たちのテストは問題ありません。

---

## IMG_0483.JPG (p.151)

### フィクスチャのスコープ（上級テクニック）

テストのたびにHTTPサーバを起動するのはコストがかかります。そもそも、HTTPサーバをフィクスチャに依存するには存在するのでしょうか。確かに、このままでは問題はありません。fixture のscope引数に"session"を渡します。

```python
@pytest.fixture(scope="session")
def httpserver():
    ...
```

テスト単位で都度HTTPサーバを起動して停止するよりは良さそうですが、テストが終了した後のサーバオブジェクトを準備しても返す方法がありません。つまり、return文の後に続くコードは実行できません。しかし、yield文の後に続くコードは実行できます。つまり、フィクスチャは通常の関数ではなくジェネレータ関数として定義すればよいのです。

**ジェネレータフィクスチャ**は、テストオブジェクトを準備して、それをyieldし、最後にリソースをクリーンアップするフィクスチャです。この動きはコンテキストマネージャと良く似ています。pytestは、実装で準備とクリーンアップフェーズを行い、yieldされた値をテスト関数の実引数として渡します。

例6-10では、ジェネレータフィクスチャでhttpserverを実装しています。

### 例6-10 httpserverフィクスチャ

```python
@pytest.fixture(scope="session")
def httpserver():
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            article = self.server.article  ❶
            data = {"title": article.title, "extract": article.summary}
            body = json.dumps(data).encode()
            ... # 以下同様

    with http.server.HTTPServer(("localhost", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield server
        server.shutdown()
        thread.join()
```

❶ 例6-9とは異なり、スコープ内にarticleが存在しない。その代わり、リクエストハンドラはサーバのarticle属性からそれにアクセスする（例6-11参照）。

まだ終わりではありません。serve()関数を定義する必要があります。serve()関数はhttpserver

---

## IMG_0482.JPG (p.150)

### serve()関数の実装（コンテキストマネージャ）

ジャとは、簡的にはwithブロックで使用するためのオブジェクトです。コンテキストマネージャを使うことで、withブロックを抜けた際にサーバを自動的に停止できます。

```python
from contextlib import contextmanager

@contextmanager
def serve(article):
    ... # サーバ起動
    yield f"http://localhost:{server.server_port}"
    ... # サーバ停止
```

serve()関数は、標準ライブラリのhttp.serverモジュールを使えば実装できます（例6-9）。ただし、実装の詳細については意識する必要はありません。本章の後半でpytest-httpserverプラグインを紹介します。実際のプロジェクトではpytest-httpserverを採用すべきでしょう。

### 例6-9 serve()関数の実装

```python
import http.server
import json
import threading

@contextmanager
def serve(article):
    data = {"title": article.title, "extract": article.summary}
    body = json.dumps(data).encode()

    class Handler(http.server.BaseHTTPRequestHandler):  ❶
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with http.server.HTTPServer(("localhost", 0), Handler) as server:  ❷
        thread = threading.Thread(target=server.serve_forever, daemon=True)  ❸
        thread.start()
        yield f"http://localhost:{server.server_port}"
        server.shutdown()
        thread.join()
```

❶ リクエストハンドラは、GETリクエストに対してArticleに関する情報をUTF-8エンコードされたJSON表現で返す。
❷ HTTPサーバはローカル接続のみを受け入れる。オペレーティングシステムはポート番号をランダムに割り当てる。
❸ HTTPサーバはバックグラ...

---

## IMG_0481.JPG (p.148-149)

### unittestとpytestの比較

- テストをクラス内部に記述するので、関数ベースのpytestよりも読みにくい。
- assert\*メソッドは表現力と柔軟性に欠ける。チェックする項目ごとに専用のメソッドが必要となる。例えば、assertEqualやassertInは存在するが、assertStartsWithは存在しない。

> 既にunittestで書かれたテストスイートがある場合、それをpytestスタイルに書き直す必要はありません。pytestもunittestのテスト構造を知っているからです。つまり、unittestのスタイルのままpytestをテストランナーとして使えますし、段階的にpytestのスタイルに書き換えることもできます。

### 6.5 フィクスチャの上級テクニック

fetch()関数をテストする場合、ローカルにHTTPサーバを立てて、ラウンドトリップ形式でテストできます。つまり、Articleに関する情報から生成したフィクスチャと、fetch()関数を使ってHTTP経由で取得したArticleが一致するかどうかをチェックします。この動きを実装したのが例6-8です。

### 例6-8 fetch()関数のテスト（バージョン1）

```python
def test_fetch(article):
    with serve(article) as url:
        assert article == fetch(url)
```

次のserve()ヘルパ関数は、Articleインスタンスを受けて、その記事を取得するためのURLを返す関数です。より正確には、URLをコンテキストマネージャでラップします。コンテキストマネージャ

---

## IMG_0480.JPG (p.148)

### パラメタライズフィクスチャの利点

パラメタライズフィクスチャの利点は何でしょうか。1つは、各テストに`@pytest.mark.parametrize`デコレータを付ける必要がなくなったことです。テストが複数のモジュールにまたがる場合には、もう1つ利点があります。それはフィクスチャをconftest.pyに記述すれば、インポートせずにフィクスチャをテストスイート全体で利用できることです。

パラメタライズフィクスチャの構文はやや難解です。シンプルにするために、筆者の好みは以下のようなヘルパ関数を定義することです。

```python
def parametrized_fixture(*params):
    return pytest.fixture(params=params)(lambda request: request.param)
```

このヘルパ関数を使えば、例6-7のフィクスチャを簡潔に記述できます。また、例6-6のarticles変数をインライン化することもできます。

```python
article = parametrized_fixture(Article(), Article("test"), ...)
```

### unittestフレームワーク

Pythonの標準ライブラリにはunittestテストフレームワークがあります。これはテスト駆動開発の初期に登場したJavaのテストライブラリであるJUnitにインスパイアされたものです。本書ではunittestで書いたテストをpytestによるテストと比較してみましょう。

```python
import unittest
```

---

## IMG_0479.JPG (p.147)

### フィクスチャを使用するように書き換えた場合の注意

フィクスチャを使用するように書き換えた場合、テスト関数の仮引数に`write`というわかりにくいエラーが発生します。`file`という名前がスコープ内に存在しないのに、フィクスチャ関数を呼び出そうとしているため、これはPytestにはわかりにくいエラーになるからです。その方法は、`@pytest.fixture(name="file")`のように、`"file"`のように、この章のテクニックを使用して、フィクスチャ関数の名前をfile()のように変更することです。

テストデータとして型空の場合でもプログラムがクラッシュしないようにしたいと考えています。例えば、記事のタイトルが空の場合でもプログラムがクラッシュしないようにしたいと考えています。例6-6では`@pytest.mark.parametrize`デコレータ＊³を使用して、複数パターンに対してテストします。

### 例6-6 記事のパターンを考慮したテスト

```python
articles = [
    Article(),
    Article("test"),
    Article("Lorem Ipsum", "Lorem ipsum dolor sit amet."),
    Article(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "Nulla mattis volutpat sapien, at dapibus ipsum accumsan eu."
    ),
]

@pytest.mark.parametrize("article", articles)
def test_final_newline(article, file):
    show(article, file)
    assert file.getvalue().endswith("\n")
```

テスト間で同じ方法でパラメタライズテストをする場合は、複数の値を持つフィクスチャであるパラメタライズフィクスチャを定義します（**例6-7**）。以下のコードを実行すると、pytestはarticlesの各記事に対して1回ずつテストします。

### 例6-7 パラメタライズフィクスチャで複数の記事に対してテストする

```python
@pytest.fixture(params=articles)
def article(request):
    return request.param

def test_final_newline(article, file):
    show(article, file)
    assert file.getvalue().endswith("\n")
```

＊³ デコレータ名がparameterizeではなくparametrizeであることに注意すること。

---

## IMG_0478.PNG（スマートフォンメモ）

### → だから実装をRichに変えてもテストは壊れない

### pytest が何をしているか（魔法の正体）

```python
def test_final_newline(file):
    article = Article(...)
    show(article, file)
    assert file.getvalue().endswith("\n")
```

### pytest 内部ではこうなってる

1. test_final_newline(file) を見つける
2. 「file という fixture があるな？」
3. file() を呼ぶ
4. 戻り値（StringIO）を引数に渡す

```python
file = file()  # ← pytestが勝手にやる
test_final_newline(file)
```

### かぜフィクスチャを使うの？

---

## IMG_0477.JPG (p.146)

### 例6-5 show()関数の実装を入れ替える

```python
from rich.console import Console

def show(article, file):
    console = Console(file=file, width=72, highlight=False)
    console.print(article.title, style="bold", end="\n\n")
    console.print(article.summary)
```

実際、テストの本来の目的はこのような変更を加えた後でもプログラムが正常に動作することを保するためです。一方で、モックやモンキーパッチは脆弱です。テストと実装の詳細を結び付けてしまうので、プログラムの変更が徐々に難しくなってしまうのです。

### 6.4 フィクスチャとパラメタライズテスト

show()関数でテストすべき項目として、以下の3点が挙げられます。

- タイトルと要約がすべて表示されること
- タイトルの後に空行があること
- 要約の1行の長さが72文字を超えないこと

フィクスチャを使えば重複を取り除けます。**フィクスチャ**とは、`@pytest.fixture`デコレータでデコレートされた関数です。

```python
@pytest.fixture
def file():
    return io.StringIO()
```

テスト（およびフィクスチャ）は、フィクスチャと同じ名前の仮引数を含めることにより、そのフィクスチャを利用できます。pytestがテスト関数を呼び出す寸前に、その実引数としてフィクスチャの返り値を渡します。フィクスチャを使って例6-4を書き換えてみましょう。

```python
def test_final_newline(file):
    article = Article("Lorem Ipsum", "Lorem ipsum dolor sit amet.")
    show(article, file)
    assert file.getvalue().endswith("\n")
```

＊² 「4.2 プロジェクトの依存関係の指定」で説明した通り、Richをプロジェクトの依存関係に追加すること、Poetryを使っている場合は「6.3 依存関係の管理」を参照すること。

---

## IMG_0476.JPG (p.145)

### 例6-3 テストをしやすくするためのリファクタリング

```python
import sys  ❶
from dataclasses import dataclass

@dataclass
class Article:
    title: str = ""
    summary: str = ""

def fetch(url):
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    return Article(data["title"], data["extract"])

def show(article, file):
    summary = textwrap.fill(article.summary)
    file.write(f"{article.title}\n\n{summary}\n")

def main():
    article = fetch(API_URL)
    show(article, sys.stdout)
```

❶ 簡潔にするために、本章のコード例では初出時のみimport文を表示する。

例6-3のリファクタリングでは、main()関数からfetch()関数とshow()関数を抽出しています。また、fetch()関数とshow()関数に共通する要素としてArticleクラスを定義しています。このリファクタリングで、プログラムの各部分を個別に、かつ再利用性のある方法でテストできるようになったことに注目しましょう。

show()関数は引数としてArticleインスタンスとファイルオブジェクトを受け取ります。main()ではファイルオブジェクトとしてsys.stdoutを渡していますが、テストでは出力をメモリに保存するためにio.StringIO()インスタンスを渡します。show()関数はファイルの末尾が必ず改行であるかを確認します（例6-4）。出力の末尾に必ず改行が入ることで、出力とシェルプロンプトが別の行になるようにしています。

### 例6-4 show()関数のテスト

```python
import io
from random_wikipedia_article import Article, show

def test_final_newline():
    article = Article("Lorem Ipsum", "Lorem ipsum dolor sit amet.")
    file = io.StringIO()
    show(article, file)
    assert file.getvalue().endswith("\n")
```

---

## IMG_0475.JPG (p.143)

### プロジェクト構造

```
random-wikipedia-article
├── pyproject.toml
└── src
    └── random_wikipedia_article
        ├── __init__.py
        └── __main__.py
    tests
    ├── __init__.py
    └── test_main.py
```

### 6.2 テストの依存関係

テストをする際にプロジェクトとその依存関係をインポートできるようにするには、プロジェクト環境にpytestをインストールする必要があります。例えば、次のようにtestsエクストラを追加します。

```toml
[project.optional-dependencies]
tests = ["pytest>=8.1.1"]
```

これでプロジェクト環境にpytestをインストールできます。

```sh
$ uv pip install -e ".[tests]"
```

または、requirementsファイルをコンパイルして環境と同期することもできます。

```sh
$ uv pip compile --extra=tests pyproject.toml -o dev-requirements.txt
$ uv pip sync dev-requirements.txt
$ uv pip install -e . --no-deps
```

Poetryを使っている場合は、poetry addでpytestを追加することも可能です。

```sh
$ poetry add --group=tests "pytest>=8.1.1"
```

本章の後半でテストの依存関係を更新するように求められた場合は、上記の手順を参照してください。

最後に、テストを実行してみましょう。Windowsの場合は、以下のコマンドを実行する前に仮想環境をアクティベートしてください。

```sh
$ py -m pytest
========================== test session starts ==========================
platform darwin -- Python 3.12.2, pytest-8.1.1, pluggy-1.4.0
rootdir: ...
collected 1 item

tests/test_main.py .                                              [100%]

========================== 1 passed in 0.01s ==========================
```

---

## IMG_0474.JPG (p.143 - 構造図拡大)

### プロジェクト構造（拡大表示）

```
random-wikipedia-article
├── pyproject.toml
└── src
    └── random_wikipedia_article
        ├── __init__.py
        └── __main__.py
    tests
    ├── __init__.py
    └── test_main.py
```

### 6.2 テストの依存関係（冒頭）

テストをする際にプロジェクトとその依存関係をインポートできるようにするには、プロジェクト環境にpytestをインストールする必要があります。

---

## IMG_0473.JPG (p.142)

### 6.1 テストを書く

「3章 Pythonパッケージ」で使った例を例6-1として再び取り上げます。プログラムは限りなくシンプルですが、そのテストの書き方はそれほど明確ではありません。main()関数には引数も返り値がなく、標準出力への書き込みなどの副作用しか存在しません。このような関数をどのようにテストすればよいでしょうか。

### 例6-1 random-wikipedia-articleのmain()関数

```python
def main():
    with urllib.request.urlopen(API_URL) as response:
        data = json.load(response)

    print(data["title"], end="\n\n")
    print(textwrap.fill(data["extract"]))
```

プログラムをサブプロセスで実行して、出力が空でない状態で完了することを検証するエンドツーエンドテストを書いてみましょう。エンドツーエンドテストとは、エンドユーザと同じ方法でプログラム全体を実行してテストする手法です。具体的には、**例6-2**のようにします。

### 例6-2 random-wikipedia-articleのテスト

```python
import subprocess
import sys

def test_output():
    args = [sys.executable, "-m", "random_wikipedia_article"]
    process = subprocess.run(args, capture_output=True, check=True)
    assert process.stdout
```

> pytestにおけるテストとは、名前がtestから始まる関数を指します。組み込みのassert文を使って期待する動きをするかどうかをチェックします。内部的な動きとして、pytestはテストが失敗した場合、エラーを報告するために内部言語構造を書き換えます。

例6-2にあるコードをtestsディレクトリの`__init__.py`を追加して`test_main.py`ファイルにコピーします。testsディレクトリに`__init__.py`を追加して、テストスイートをモジュールにします。このような構造とすることで、テスト対象のモジュールとテストスイートを同じ構造にでき、かつ、テスト用ユーティリティ関数もインポートできるようになります。この時点で、プロジェクトは以下のような構造になるはずです。

---

## IMG_0472.JPG (p.52-53)

### sys.path と仮想環境の設定

sys.pathの説明と仮想環境ディレクトリの構成：

```
/usr/local/lib/python3.12/site-packages/
/usr/local/lib/python3.12/
/usr/local/lib/python3.12/lib-dynload (exts)
```

### 2.4.7 初期化に備える

SiteConfigurationは、仮想環境のsys.pathをカスタマイズするディレクトリです。SiteConfigurationは、SiteConfigurationが、仮想環境を作成する際にPythonインタプリタが場所を指定する仮想環境の構成ファイルを読み込みます。

```sh
$ py -m site
USER_BASE: '/home/user/.local' (exists)
```

サイトモジュールは独自のパス変数を追加することによって、その関係の場所のカスタマイズに貢献します。SiteConfigurationは、venv.cfgの設定ファイルを使ってインストール先を指定します。

---

## IMG_0471.JPG (p.51)

### 2.4.5.2 PYTHONPATH 環境変数

環境変数PYTHONPATHでも、sys.pathの標準ライブラリの前に場所を追加することができます。PATH変数と同じ文法を使用します。ただし、カレントディレクトリの場合と同じ理由で、この方法は推奨されません。代わりに、仮想環境を使用するようにしてください。

### 2.4.5.3 標準ライブラリ

表2-6は、初期モジュールパスに残っているエントリを示します。これらのエントリは標準ライブラリに割り当てられています。場所にはインストールパスが付いており、プラットフォームによって詳細が異なることがあります。例えば、Fedoraは標準ライブラリをlibではなくlib64に配置します。

**表2-6 sys.path上の標準ライブラリ**

| Windows | Linux/macOS | 説明 |
|---------|-------------|------|
| python3x.zip | lib/python3x.zip | コンパクトにするため、標準ライブラリをzipアーカイブとしてインストールできる。この項目は、アーカイブが存在しない場合でも表示される（通常は存在しない）。 |
| Lib | lib/python3.x | ピュアPythonのモジュール |
| DLLs | lib/python3.x/lib-dynload | バイナリ拡張モジュール |

標準ライブラリの場所はインタプリタにハードコードされていません（「2.1.3 仮想環境」参照）。代わりに、Pythonは自身の実行可能ファイルへのパス上にあるランドマークファイルを探します。そして、ランドマークファイルを使って現在の環境（sys.prefix）とPythonインストール（sys.base_prefix）を特定します。このようなランドマークファイルの1つがpyvenv.cfgです。これは仮想環境を示し、homeキーはその環境の元となった環境を指します。また、標準モジュールosを含むファイルであるos.pyもランドマークです。Pythonはos.pyを使って仮想環境外でのプレフィックスを取得し、標準ライブラリの場所を特定します。

### 2.4.6 サイトパッケージ

インタプリタは初期化の早い段階で、比較的固定されたプロセスを使って初期のsys.pathを構築します。これに対して、sys.pathの残りの場所（サイトパッケージと呼ばれる部分）は柔軟にカスタマイズ可能です。カスタマイズにはPythonモジュールのsiteを使います。

次のパスエントリがファイルシステム上に存在する場合、siteモジュールで追加することができます。

**ユーザサイトパッケージ**

ユーザごとの環境から取得したサードパーティパッケージがある。位置はOSによって決まっている（例：「2.1.2 ユーザごとの環境」）。Fedoraなどの一部のシステムでは、Pythonモジュールと拡張モジュール用に2つのパスエントリがある。

---

## IMG_0470.JPG (p.50)

### 2章 Python環境（初期モジュールパスの構成）

この節では、インタプリタが標準ライブラリで初期モジュールパスをどのように構築するかを説明します。次の節では、siteモジュールがサイトパッケージを含むディレクトリを追加する方法を説明します。

> CPythonのソースコードには、sys.pathを構築するための組み込みロジックがModules/getpath.pyにあります。見た目は普通のモジュールですが、実装は異なります。Pythonをビルドする際、このコードはバイトコードに変換されて、実行可能ファイルに埋め込まれます。

初期モジュールパスの場所は、以下の3つのカテゴリに分類されます。これらは次の順序で発生します。

1. カレントディレクトリまたはPythonスクリプトが含まれているディレクトリ（もしあれば）
2. PYTHONPATH環境変数に設定されている場所（もし設定されていれば）
3. 標準ライブラリの場所

それぞれを詳しく見てみましょう。

### 2.4.5.1 カレントディレクトリ、またはスクリプトを含むディレクトリ

sys.pathの最初の項目は、次のいずれかです。

- `py <script>`を実行した場合、スクリプトがあるディレクトリ。
- `py -m <module>`を実行した場合、カレントディレクトリ。
- それ以外の場合、空の文字列。これもカレントディレクトリを示す。

伝統的に、このメカニズムはアプリケーションを構成する便利な方法を提供しています。メインのエントリポイントのスクリプトとすべてのアプリケーションモジュールを同じディレクトリに配置します。開発中、このディレクトリ内からインタプリタを起動して対話型デバッグを行うと、インポートも正常に動作します。

残念ながら、作業ディレクトリがsys.pathに含まれていると非常に危険です。攻撃者が自身のPythonファイルを配置できる可能性があるからです。これを避けるために、被害者のディレクトリにアプリケーションやPYTHONSAFEPATH環境変数を使用して、カレントディレクトリをsys.pathから除外できます。Python 3.11以降では、-Pインタプリタオプションを使ってスクリプトで呼び出す場合、このオプションはスクリプトがあるディレクトリも除外します。

仮想環境にアプリケーションをインストールする方が柔軟であり、好ましいとされる方が、カレントディレクトリにモジュールを置くより安全です。これには「3章 Pythonパッケージ」で説明します。

---

## IMG_0469.JPG (p.49)

### Pythonモジュールの検索（ファインダとローダ）

- ビルトインモジュールには`importlib.machinery.BuiltinImporter`を使う。
- フローズンモジュールには`importlib.machinery.FrozenImporter`を使う。
- sys.path上のモジュールを検索するには`importlib.machinery.PathFinder`を使う。

PathFinderは、インポートメカニズムの主要部分です。インタプリタに組み込まれているモジュールabc.PathEntryFinderと呼ばれる2次的なファインダのオブジェクトを使用し、sys.pathの特定の場所のモジュールを見つけます。標準ライブラリには、sys.path_hooksに登録された2種類のパスエントリファインダが含まれています。

- zipimport.zipimporterを使ってZIPアーカイブからモジュールをインポートする。
- importlib.machinery.FileFinderを使ってディレクトリからモジュールをインポートする。

一般的に、モジュールはファイルシステム上のディレクトリに保存されます。そのため、PathFinderはその作業をFileFinderに移譲します。このFileFinderは、ディレクトリをスキャンして、ファイル拡張子を使って適切なローダを決定します。モジュールの種類に応じて、以下の3つのローダがあります。

- ピュアPythonモジュールには`importlib.machinery.SourceFileLoader`を使用する。
- バイトコードモジュールには`importlib.machinery.SourcelessFileLoader`を使用する。
- バイナリ拡張モジュールには`importlib.machinery.ExtensionFileLoader`を使用する。

zipimporterは同様に動作します。しかし、拡張モジュールはサポートしていません。これは、現在のオペレーティングシステムがZIPアーカイブからダイナミックライブラリを読み込むことを許可していないためです。

### 2.4.5 モジュールパス

プログラムが特定のモジュールを見つけられない場合や、間違ったバージョンのモジュールをインポートしてしまう場合、sys.path（モジュールパス）を確認するとよいでしょう。しかし、sys.pathのエントリはどこから来ているのでしょうか。その謎を解いてみましょう。

インタプリタが起動すると、モジュールパスを2段階で構築します。最初に、組み込みのロジックを使用して初期モジュールパスを作成します。最も重要なのは、この初期パスに標準ライブラリが含まれていることです。次に、インタプリタは標準ライブラリからsiteモジュールをインポートします。siteモジュールは、現在の環境からサイトパッケージを含むようにモジュールパスを拡張します。

＊14 パッケージ内のモジュールの場合、パッケージの`__path__`属性がsys.pathの代わりになる。

---

## IMG_0468.JPG (p.48)

### 2.4.3 モジュールスペック

Pythonでは、モジュールのインポートは概念的に2つのステップで行います。まず、モジュールスペックの完全修飾名をもとに、インポートシステムがモジュールスペック（importlib.machinery.ModuleSpec）を生成します。次に、インポートシステムがモジュールオブジェクトを作成し、モジュールのコードを実行します。モジュールスペックは、これら2つのステップをつなぐリンクです。モジュールスペックには、モジュールの名前や場所の適切なローダが含まれています。また、モジュールオブジェクトの特別な属性を使用して、モジュールスペックから大部分のメタデータにアクセスできます。

**表2-5 モジュールスペックとモジュールオブジェクトの属性**

| スペック属性 | モジュール属性 | 説明 |
|------------|--------------|------|
| name | `__name__` | モジュールの完全修飾名 |
| loader | `__loader__` | モジュールのコードを実行する方法が記述されているローダオブジェクト |
| origin | `__file__` | モジュールの位置 |
| submodule_search_locations | `__path__` | パッケージであるモジュールのサブモジュールを検索する場所 |
| cached | `__cached__` | モジュールのコンパイル後のバイトコードの場所 |
| parent | `__package__` | 含まれているパッケージの完全修飾名 |

モジュールの`__file__`属性は通常、PythonモジュールのファイルPasを保持します。特殊な場合、固定文字列を保持します。例えば、ビルトインモジュールの場合は"builtin"、名前空間パッケージの場合はNoneです。名前空間パッケージは単一の場所を持ちません。

### 2.4.4 ファインダとローダ

インポートシステムは、2種類のオブジェクトを使ってモジュールを見つけ、読み込みます。ファインダ（importlib.abc.MetaPathFinder）は、完全修飾名に基づいてモジュールを探します。成功すると、find_specメソッドがローダ付きのモジュールスペックを返します。失敗すると、Noneを返します。ローダ（importlib.abc.Loader）は、exec_module関数を持つオブジェクトで、モジュールのコードを読み込み、実行します。この関数は、モジュールオブジェクトを引数に取り、それを初期化してインポーターと呼ばれます。

ファインダはsys.meta_path変数に登録します。インポートシステムは順番に各ファインダをモジュールオブジェクトを持ったモジュールスペックを返した場合、インポートシステムはそのモジュールオブジェクトを作成し、初期化します。その後、実行のためにローダに渡します。デフォルトでは、sys.meta_path変数には3つのファインダが含まれています。これらのファインダは異なる種類のモジュールを扱います（「2.1.1.2 Pythonモジュール」参照）。

---

## IMG_0467.JPG (p.47)

### Pythonモジュールの検索（コード実行と属性）

```python
exec(code, module.__dict__)
```

さらに、モジュールオブジェクトには特別な属性があります。例えば、`__name__`属性はモジュールの完全修飾名を持ちます。例えばemail.messageといった値です。`__spec__`モジュールはモジュールスペックを保持します。詳しくは後ほど説明します。パッケージにも`__path__`属性があります。`__path__`属性には、サブモジュールを検索する場所が含まれています。

> ほとんどの場合、パッケージの`__path__`属性には単一のエントリが含まれています。それは`__init__.py`ファイルを持つトップディレクトリです。一方で、名前空間パッケージは複数のディレクトリに分けて置かれます。

### 2.4.2 モジュールキャッシュ

モジュールを初めてインポートすると、インポートシステムはモジュールオブジェクトをsys.modules辞書に完全修飾名をキーとして格納します。次回以降のインポートでは、sys.modulesから直接モジュールオブジェクトが返されます。このメカニズムにはいくつかの利点があります。

**パフォーマンス**

インポートは高コストです。インポートシステムはほとんどのモジュールをディスクからロードするためです。モジュールをインポートすることはそのコードを実行することも意味します。これにより、起動時間がさらに増加する場合があります。sys.modules辞書はキャッシュとして機能し、処理が速くなります。

**冪等性**

モジュールをインポートすると副作用が生じることがあります。例えば、モジュールレベルのステートメントを実行するときです。sys.modulesにモジュールをキャッシュすることで、これらの副作用が一度だけ発生するようにします。インポートシステムはロックも使用して、複数のスレッドが同じモジュールを安全にインポートできるようにします。

**再帰**

モジュールが自分自身を再帰的にインポートすることがあります。一般的なケースは循環インポートです。例えば、モジュールaがモジュールbをインポートし、bがaをインポートする場合です。インポートシステムはモジュールを実行する前にsys.modulesに追加することでこれに対応します。bがaをインポートするとき、インポートシステムはsys.modules辞書から（部分的に初期化された）モジュールaを返します。これにより無限ループを回避します。

---

## IMG_0466.JPG (p.31)

### 2.1.3.1 パッケージのインストール

パッケージをインストールする手段として、仮想環境にはpipが用意されています。仮想環境を作成してhttpx（HTTPクライアントライブラリ）をインストールし、対話型セッションを起動してみましょう。

Windowsでは、以下のコマンドを実行します。

```sh
> py -m venv .venv
> .venv\Scripts\python -m pip install httpx
> .venv\Scripts\python
```

Linux/macOSでは、以下のコマンドを実行します。環境名としてよく使われるPython Launcher for Unixはデフォルトで適切なインタプリタを選択するため、パスを明示する必要はありません。

```sh
$ py -m venv .venv
$ py -m pip install httpx
$ py
```

対話型セッションでは、httpx.getを使ってGETリクエストを送信します。

```python
>>> import httpx
>>> httpx.get("https://example.com/")
<Response [200 OK]>
```

仮想環境には、使用するバージョンのPythonがリリースされた時点の...

＊9 Fedoraはlibの代わりにlib64配下にサードパーティの拡張モジュールを配置する。
＊10 Windowsでも--symlinkを指定することでシンボリックリンクを作成することもできますが、つのコマンドの違いがあり、このオプションの使用は難しくなります...

---

## IMG_0465.JPG (p.32)

### 2章 Python環境 - モジュールの種類

**シンプルモジュール**
通常、PythonのソースコードがあるファイルはモジュールとしてOKです。例えば、`import string`文は、string.pyファイルを読み込みます。それをローカルスコープのstringという名前に関連付けます。

**パッケージ**
`__init__.py`ファイルがあるディレクトリはパッケージです。`import email.message`は、emailパッケージからmessageモジュールを読み込みます。

**名前空間パッケージ**
モジュールを含んでいるものの`__init__.py`がないディレクトリは、名前空間パッケージです。会社名などの共通の名前空間（例えばacme.unicycleやacme.rocketsled）でモジュールを整備するために使われます。通常のパッケージとは異なり、名前空間パッケージ配下に置かれることを想定している各モジュールは、個別に配布できます。

**拡張モジュール**
本書で取り上げるmathモジュールのような拡張モジュールには、Cなどの低レベルな言語で書かれ、コンパイルされたネイティブコードが含んでいることがあります。拡張モジュールは共有ライブラリであり、PythonからモジュールとしてOKするための特別なエントリポイントを持ちます＊4。パフォーマンス上の理由や、既存のCライブラリをPythonモジュールとして利用する目的で使用されます。また、共有ライブラリのファイル名の拡張子は、Windowsでは.pyd、macOSでは.dylib、Linuxでは.soです。

**ビルトインモジュール**
sysやbuiltinsモジュールなど、標準ライブラリの中にはインタプリタにコンパイルされるものがあります。変数`sys.builtin_module_names`は、これらのモジュール名のタプルです。

**フローズンモジュール**
標準ライブラリのいくつかのモジュールはPythonで書かれていますが、そのバイトコードがインタプリタに埋め込まれているものがあります。もともと、importlibの中心部分だけがフローズンモジュールとして扱われていました。最近のPythonのバージョンでは、osやioなどインタプリタの起動時にインポートされるモジュールはすべてフローズンモジュールとして扱われます。

> Pythonにおける「パッケージ」という用語の定義は曖昧です。これはモジュールと、モジュールがない限り、「パッケージ」を「配布物」の同義語としても使われることがあります。本書では特に...

＊4 共有ライブラリとは、複数のプログラムが実行時に利用できるようにしたバイナリファイルで、1つだけメモリ上にコピーされ...

---

## IMG_0464.JPG (p.31)

### 2.1 早わかりPython環境

dtg8T)や、GraalVMを用いてJavaとの相互運用性を高パフォーマンスのGraalPy（https://oreil.ly/ctx6J）など、多くの代替実装も利用可能です。ビルドは、CPUアーキテクチャ（例えば32ビットや64ビット、IntelやAppleシリコン）と、コンパイル時の最適化やインストールのレイアウトなどを決定するビルド構成によって異なります。

### インタプリタで取得できるPython環境についての情報

対話型セッションでsysモジュールをインポートして、以下の属性を確認してみましょう。

**sys.version_info**
Pythonのバージョンであり、メジャー、マイナー、マイクロバージョンと、リリースレベル、プレリリースのシリアルナンバーといった情報を名前付きタプルとして提供する。

**sys.implementation.name**
"cpython"や"pypy"のようなPythonの実装を表す文字列。

**sys.implementation.version**
実装のバージョンであり、CPythonのsys.version_infoと同じ。

**sys.executable**
Pythonインタプリタのパス。

**sys.prefix**
Python環境のパス。

**sys.path**
Pythonがモジュールをインポートする際に、検索するディレクトリの一覧。

`py -m sysconfig`は、CPUの命令セットアーキテクチャ、ビルド構成、インストールレイアウトなど、Pythonインタプリタのコンパイル時の多くのメタデータを表示します。

### 2.1.1.2 Pythonモジュール

モジュールはPythonオブジェクトのコンテナで、import文で読み込みます。モジュールは、WindowsではLib、Linux/macOSではlib/python3.xの下に配置されます。サードパーティパッケージはsite-packagesというサブディレクトリに配置されます。
