app.dependency\_overrides  
[https://fastapi.tiangolo.com/advanced/testing-dependencies/\#overriding-dependencies-during-testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/#overriding-dependencies-during-testing)

**Aスタブデータとかモックデータ使う用の関数**  
async def **override\_dependency**(q: str | None \= None):  
    return {"q": q, "skip": 5, "limit": 10}  
**↓依存関係をオーバーライド**  
**B元々DIで注入されるはずの関数**  
async def common\_parameters(q: str | None \= None, skip: int \= 0, limit: int \= 100):  
    return {"q": q, "skip": skip, "limit": limit}

テストの開始時 (テスト関数内) にオーバーライドを設定

app.dependency\_overrides\[B\] \= A　\# 依存関係をオーバーライド

@app.get("/items/")  
async def read\_items(commons: Annotated\[dict, **Depends(common\_parameters)\]):**  
    return {"message": "Hello Items\!", "params": commons}

ここでオーバーライドが走る  
**app.dependency\_overrides\[common\_parameters\] \= override\_dependency(関数名)**

**client \= TestClient(app)**

def test\_override\_in\_items\_with\_q():  
    **response \= client.get("/items/?q=foo")**  
    assert response.status\_code \== 200  
    assert response.json() \== {  
        "message": "Hello Items\!",  
        "params": {"q": "foo", "skip": 5, "limit": 10},  
    }  
終了時 (テスト関数の終了時) にリセットすることができます。  
**app.dependency\_overrides \= {}  \# リセット**

Depends  
[https://fastapi.tiangolo.com/reference/dependencies/](https://fastapi.tiangolo.com/reference/dependencies/)

