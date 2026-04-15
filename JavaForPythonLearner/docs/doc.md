https://runestone.academy/ns/books/published/java4python/Java4Python/javadatatypes.html#java-data-types



javac Hello.java** // コンパイル＝JavaコードをJava仮想マシン（JVM）が理解できる言語=バイトコードに変換する。バイトコードはコンピュータのネイティブ言語に非常に近いため、より高速に実行できる。さらにコンパイル時点でコンパイラエラーを発生させるのでエラーをこの時点で検出できる

ls -l Hello.*
java Hello // ファイル名で実行


## Javaのデータ型
https://runestone.academy/ns/books/published/java4python/Java4Python/javadatatypes.html#java-data-types

Pythonはどんなデータ型もObjectですが
Javaではprimitiveなdataはobjectではない
つまり primitive型に対する演算が高速

ただし、objectとobjectでないprimitiveがごっちゃだとプログラマがややこしいのでprimitive型もobject化されたバージョンを持つようになった


大文字の型宣言をするとObjectの宣言ということになる

```java
Double fahr;
Double cel; // ここをコメントアウトするとエラーが出る
Scanner in;
```

Primitive, Object
int, Integer
float, Float
double, Double
char, Char
boolean, Boolean

Primitive　→ 変換：Boxing → Object
Primitive　← 変換：UnBoxing ← Object
Java 5では、コンパイラが適切な変換タイミングを自動的に判断できるようになった。（オートボクシング）


## javaのimport
javacとjavaコマンドは存在しているclassを知らなければなりません
クラス名のfullnameを使います

そのためJavaは
- カレントディレクトリにある .java と .class ファイルで定義された全てのclassを知っています
- Javaがshipした全てのクラスを知っています
- CLASSPATH環境変数に含まれる全てのクラスを知っています。CLASSPATH環境変数は2つの構造をnameします
  - java クラスを保管する .jar
  - javaクラスファイルを保管するディレクトリ


**javaのimportは階層的である**
java.util.Scanner
java.utilはパッケージ
Scannerはclass
**loaderがクラスをメモリにロードする**
import文での宣言ではなく
import文を書いたら
Java Class loaderがクラスをメモリにロードする

そのためimport文は、クラスの「完全修飾名（フルネーム）」を省略して書けるようにするための仕組みで
javaコードの中で Scannerを単一で使うためにコンパイラに「これからこのクラスを短い名前で呼ぶよ」と伝えているだけ。
試しに Scanner部分を　java.util.Scanner　と書いても伝わる

## 変数宣言
変数を宣言した時点でその変数とタイプは決定される
その変数を他のタイプで参照しようとするとエラーが出る
Javaの一般的なルールは、変数が参照するオブジェクトの種類を決定し、使用する前にその変数を宣言しなければならないということです。



https://runestone.academy/ns/books/published/java4python/Java4Python/javadatatypes.html#input-output-scanner

