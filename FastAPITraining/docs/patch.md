5. PATCHメソッドと部分更新（Partial Updates）のロジック
REST APIにおいて、リソースの一部のみを更新するPATCHメソッドの実装は、PUT（全置換）と比較して複雑である。クライアントが「値を更新したい」のか、「値を変更したくない（送信していない）」のか、あるいは「値を明示的にnullにしたい」のかを区別する必要があるためである。
5.1 exclude_unset の重要性と動作原理
Pydanticモデルの.model_dump(exclude_unset=True)メソッドは、この問題を解決するための鍵となる機能である。これは、ユーザーが明示的に送信したフィールドのみを含む辞書を生成する。

Python


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item_in: ItemUpdate):
    # 1. DBから既存データを取得
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    
    # 2. 入力データから「送信された値」のみを抽出
    # クライアントが {"price": 10.5} だけ送ってきた場合、
    # nameやdescriptionは除外される（Noneで上書きされない）
    update_data = item_in.model_dump(exclude_unset=True)
    
    # 3. 既存モデルに入力データを上書きコピー
    updated_item = stored_item_model.model_copy(update=update_data)
    
    # 4. DBへの保存と返却
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


ロジックの詳細解説
もしexclude_unset=Trueを使用せず、単にitem_in.dict()を使用した場合、送信されなかったフィールド（例：name）はデフォルト値のNoneとして辞書に含まれてしまう。これをそのまま更新に使用すると、DB上の既存のnameがNoneで上書きされ、データが消失する事故につながる。exclude_unsetは、「値が送信されなかった＝変更の意思がない」と解釈し、既存の値を維持するために不可欠なフラグである。
