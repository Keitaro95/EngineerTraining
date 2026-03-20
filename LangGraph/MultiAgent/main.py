import sys
sys.path.append("..")
from settings import Settings
from langchain_core.messages import HumanMessage
from workflow import graph

Settings()

if __name__ == "__main__":
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="過去5年の日本のGDPを調査してください。"
                    " 次に折れ線グラフを描きます。"
                    " コード化したら完了です。"
                )
            ],
        },
        {"recursion_limit": 100},
    ):
        print(s)
        print("----")
