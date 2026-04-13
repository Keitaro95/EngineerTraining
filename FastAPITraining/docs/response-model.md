## **6\. レスポンスにおける response\_model と ORJSONResponse の使い分け**

FastAPIにおけるレスポンス生成には主に2つのアプローチが存在する。標準的な response\_model を使用する方法と、高パフォーマンスな ORJSONResponse を直接返す方法である。これらはトレードオフの関係にあり、現代のPython Web開発におけるデファクトスタンダードとして適切に使い分ける必要がある。

### **6.1 response\_model を使用する標準アプローチ**

デフォルトの JSONResponse とデコレータの response\_model 引数を組み合わせる方法である。

Python

@app.post("/orders", response\_model=OrderResponse)  
def create\_order(order: OrderDetail):  
    return order

* **仕組み**: 関数から返されたデータ（ORMオブジェクトやPydanticモデル）は、FastAPI内部の jsonable\_encoder によって一度Pythonの標準型（dict, list, strなど）に変換され、その後Pydanticによって response\_model のスキーマに従ってバリデーションとフィルタリングが行われ、最後に json.dumps でシリアライズされる 11。  
* **メリット**:  
  * **データのフィルタリング**: パスワードハッシュや内部IDなど、レスポンスモデルに含まれないフィールドを自動的に除去するセキュリティ上の利点がある。  
  * **ドキュメント生成**: Swagger UIなどのAPIドキュメントにレスポンススキーマが自動反映される。  
  * **型安全性**: クライアントに返すデータの整合性が保証される。  
* **デメリット**:  
  * **パフォーマンス**: 二重の変換（jsonable\_encoder \+ Pydantic validation）が発生するため、巨大なネストデータの場合、シリアライズ処理がボトルネックとなりうる。

### **6.2 ORJSONResponse による高速化**

orjson はRustで実装された超高速JSONライブラリであり、標準の json ライブラリと比較して数倍から数十倍の速度でシリアライズを行う 13。FastAPIでは ORJSONResponse クラスとして提供されている。

#### **パターンA: response\_class として指定する（推奨されるデファクト）**

Python

from fastapi.responses import ORJSONResponse

@app.post("/orders", response\_model=OrderResponse, response\_class=ORJSONResponse)  
def create\_order(order: OrderDetail):  
    return order

この方法では、データのバリデーションとフィルタリングは依然としてPydanticが行うが、最後のバイト列への変換（シリアライズ）を高速な orjson が担当する。これにより、安全性を維持しつつ、20%〜50%程度のパフォーマンス向上が見込める 13。**現代のFastAPI開発においては、これが最もバランスの取れたデファクトスタンダードである。**

#### **パターンB: ORJSONResponse を直接返す（最大パフォーマンス）**

Python

from fastapi.responses import ORJSONResponse

@app.get("/orders/bulk")  
def get\_bulk\_orders():  
    large\_data \= get\_large\_data\_from\_db() \# 既に辞書リスト形式など  
    return ORJSONResponse(content=large\_data)

この方法では、FastAPIの jsonable\_encoder およびPydanticのバリデーションプロセスを完全にバイパスする 11。

* **メリット**: **圧倒的な速度**。巨大なリスト（数万行のレコード）を返す場合、標準の方法と比べて桁違いに速い。  
* **デメリット**: Pydanticによるバリデーションやフィルタリングが行われないため、開発者がデータの整合性とセキュリティ（機密情報の除去など）を自前で担保する必要がある。また、APIドキュメントへのスキーマ反映も手動で行う必要がある。

### **6.3 比較と推奨戦略**

以下の表に、各アプローチの特性と推奨ユースケースをまとめる。

| 特性 | 標準 (JSONResponse) | response\_class=ORJSONResponse | ORJSONResponse 直接返却 |
| :---- | :---- | :---- | :---- |
| **シリアライザ** | 標準 json | **orjson (Rust)** | **orjson (Rust)** |
| **バリデーション** | あり (Pydantic) | あり (Pydantic) | **なし** (バイパス) |
| **データフィルタ** | あり (自動) | あり (自動) | なし (手動対応必須) |
| **速度** | 低 | 中 (標準比 1.2\~1.5倍) | **高 (標準比 10倍以上)** |
| **ドキュメント** | 自動生成 | 自動生成 | 手動定義が必要 |
| **推奨度** | 小規模なら可 | **基本はこれ (De Facto)** | 大量データ参照系のみ |

**結論として、5階層のような複雑でデータ量の多いAPIにおいては、基本設定として response\_class=ORJSONResponse を採用し、レポート出力や一覧取得などの重いエンドポイントにおいてのみ ORJSONResponse の直接返却を選択するアーキテクチャが推奨される。**