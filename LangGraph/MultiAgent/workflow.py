"""ワークフロー定義"""

from langgraph.prebuilt import create_supervisor
from langchain_openai import ChatOpenAI
from agents import research_agent, chart_agent

llm = ChatOpenAI(model="gpt-4o")

graph = create_supervisor(
    agents=[research_agent, chart_agent],
    model=llm,
    prompt=(
        "あなたはリサーチとチャート生成を管理するスーパーバイザーです。"
        "まずResearcherにデータ収集を依頼し、次にChart Generatorにグラフ作成を依頼してください。"
    ),
).compile()
