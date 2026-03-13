

```python
class MyClass:
    x = 10 

obj = MyClass()　# インスタンスを作る


obj.y = 20 # 新しいインスタンス変数
```

内部的には

A.__dict__ → {"x": 10}
obj.__dict__ → {"y": 20}