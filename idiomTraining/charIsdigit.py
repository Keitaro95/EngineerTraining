import uuid
import functools

# token = str(uuid.uuid4())
token = "aaaabbbb"


# funcにはv2(token)が渡される
def getSelfFunctionName(func):
    @functools.wraps(func)
    # wrapper(token)が実行される
    def wrapper(*args, **kwargs):
        """wrapper関数は、任意のarg, kwargsを受け取って,
        funcで受け取った関数自身をprintする関数"""
        # v2関数が実行される。つまりv2(token)が行われる
        result = func(*args, **kwargs)
        # func.__name__はv2
        print(f"You called {func.__name__} function. Validation finished")
        return result
    return wrapper # 内部で定義したwrapper関数を提供
    

def v1(token: str):
    # v1
    hasDigit = False

    for char in token:
        if char.isdigit():
            hasDigit = True
            print(f"Token: {token} is valid")
            break

    if not hasDigit:
        print(ValueError("Token must contain a digit"))
    print("Validation finished")

@getSelfFunctionName
def v2(token: str):
    if not any(char.isdigit() for char in token):
        print(ValueError("Token must contain a digit"))
    else:
        print(f"Token: {token} is valid")
    
@getSelfFunctionName
def v3(token: str):
    if "token" and not any(char.isdigit() for char in token):
        print(ValueError("Token must contain a digit"))
    else:
        print(f"Token: {token} is valid")


if __name__ == "__main__":
    # v1(token)
    v2(token)
    v3(token)