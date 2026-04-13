


## 手法A：ドット記法によるオブジェクトアクセス（推奨）
FastAPIがリクエストを受け取った時点で、order 変数は既にバリデーション済みの OrderDetail クラスのインスタンスである。したがって、Pythonの属性アクセス（ドット記法）を使用するのが最も型安全で、IDEの補完機能も効くため推奨される。

Python


def extract_via_attributes(order: OrderDetail):
    """
    オブジェクト属性としてアクセスする例
    """
    extracted_data =

    # 第1階層へのアクセス
    print(f"注文ID: {order.order_id}")

    # ネストされたリストのループ処理
    for shipment in order.shipments:  # Level 2
        carrier = shipment.carrier_code
        
        for group in shipment.fulfillment_groups:  # Level 3
            warehouse = group.warehouse_id
            
            for item in group.line_items:  # Level 4
                sku = item.sku
                price = item.unit_price
                
                # 条件付きロジック：特定のSKUの場合のみ処理
                if sku.startswith("LTD-"):
                    print(f"限定商品検出: {sku}")

                # Level 5: コンポーネント情報の抽出
                # 内包表記を用いたフィルタリング
                engravings = [
                    comp.value 
                    for comp in item.components 
                    if comp.component_type == 'engraving'
                ]
                
                if engravings:
                    extracted_data.append({
                        "order_id": order.order_id,
                        "sku": sku,
                        "engraving_text": engravings,
                        "warehouse": warehouse
                    })

    return extracted_data


## 手法B：辞書形式への変換とアクセス（model_dump）
外部のAPIにデータをそのまま転送する場合や、NoSQLデータベース（MongoDB等）に保存する場合は、辞書形式への変換が必要となる。Pydantic V2では .dict() は非推奨となり、代わりに model_dump() を使用する 9。

Python


def extract_via_dict(order: OrderDetail):
    """
    辞書に変換してからアクセスする例
    """
    # mode='json'を指定することで、datetimeやUUIDなどの型をJSON互換の文字列に自動変換する
    order_dict = order.model_dump(mode='json', exclude_unset=True)

    try:
        # 深い階層への直接アクセス（インデックス指定）
        # ※ リストが空でないという保証がない場合はIndexErrorのリスクがあるため注意が必要
        first_sku = order_dict['shipments']['fulfillment_groups']['line_items']['sku']
        print(f"最初の明細SKU: {first_sku}")

        # 安全なアクセス方法（getメソッドチェーン）
        # 深い階層から安全に値を取り出すヘルパー関数の利用も検討すべき
        shipments = order_dict.get('shipments',)
        if shipments:
            groups = shipments.get('fulfillment_groups',)
            #... (以下同様にネスト)

    except (KeyError, IndexError) as e:
        print(f"データ構造が想定と異なります: {e}")

    # リスト内包表記によるフラット化（分析用データの作成などに便利）
    # 全ての明細行から「追加コスト」の合計を算出する
    total_additional_cost = sum([
        comp['additional_cost']
        for shipment in order_dict.get('shipments',)
        for group in shipment.get('fulfillment_groups',)
        for item in group.get('line_items',)
        for comp in item.get('components',)
    ])
    
    print(f"カスタマイズ追加料金合計: {total_additional_cost}")


## 手法C：Python 3.10+ パターンマッチング（構造的パターンマッチング）
Python 3.10以降で導入された match/case 文を使用すると、複雑なネストデータの抽出を宣言的かつ可読性高く記述できる。これはデータの形状に基づいて分岐処理を行う強力な手法である。

Python


def extract_via_pattern_matching(order: OrderDetail):
    """
    構造的パターンマッチングを用いた抽出例
    """
    # 特定の条件（例：YAMATO配送で、かつ刻印がある商品を含む注文）を抽出
    
    # 処理のために辞書化
    data = order.model_dump()

    match data:
        case {
            "shipments":,
                                    "sku": sku
                                },
                                *other_items
                            ]
                        },
                        *other_groups
                    ]
                },
                *other_shipments
            ]
        }:
            print(f"YAMATO配送の刻印商品を発見: SKU={sku}, メッセージ={msg}")
        
        case _:
            print("条件に合致するパターンは見つかりませんでした")
