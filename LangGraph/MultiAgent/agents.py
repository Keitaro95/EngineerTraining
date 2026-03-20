from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools import tavily_tool, python_repl

llm = ChatOpenAI(model="gpt-4o")

research_agent = create_react_agent(
    model=llm,
    tools=[tavily_tool],
    prompt="あなたはリサーチアシスタントです。Tavily検索を使って正確なデータを収集してください。",
    name="Researcher",
)

chart_agent = create_react_agent(
    model=llm,
    tools=[python_repl],
    prompt="あなたはチャート生成アシスタントです。Pythonコードを使ってグラフを作成してください。",
    name="Chart Generator",
)
