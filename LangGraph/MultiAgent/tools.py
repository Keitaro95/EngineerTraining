from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from typing import Annotated


tavily_tool = TavilySearchResults(max_results=5)
repl = PythonREPL()


# str をinputして実行結果を返す
@tool
def python_repl(code: Annotated[str, "チャートを生成するために実行する Python コード"]):
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"


tools = [tavily_tool, python_repl]
