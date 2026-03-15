from typing import Any
from langchain_core.prompts import ChatPromptTemplate

ROLES = {
    "1": {
        "name": "一般知識エキスパート",
        "description": "幅広い分野の一般的な質問に答える",
        "details": "幅広い分野の一般的な質問に対して、正確でわかりやすい回答を提供してください。"
    },
    "2" : {
        "name": "生成AIエキスパート",
        "description": "生成AIや関連製品、技術に関する専門的な質問に答える",
        "details": "生成AIや関連製品、技術に関する専門的な質問に対して、最新の情報と深い洞察を提供してください。"
    },
    "3" : {
        "name": "カウンセラー",
        "description": "個人的な悩みや心理的な問題に対してサポートを提供する",
        "details": "個人的な悩みや心理的な問題に対して、共感的で支援的な回答を提供し、可能であれば適切なアドバイスも行ってください。"
    }
}

llm = ChatOpenAI(model="gpt-4.1", temperature=0.0)
llm = llm.configurable_fields(max_tokens=ConfigurableField(id="max_tokens"))

def selection_node(state: State)-> dict[str, Any]:
    query = state.query
    role_options = "\n".join([f'{k}.{v["name"]}: {v["description"]}' for k, v in ROLES.items()])
    prompt = ChatPromptTemplate.from_template(
        """質問を分析し、最も適切な回答担当ロールを選択してください。

        選択肢:
        {role_options}

        回答は選択肢の番号（1、2、または3）のみを返してください。

        質問: {query}
        """.strip()
    )
    # 出力を 1,2,3 どれか1tokenだけに強制
    chain = prompt | llm.with_config(configurable=dict(max_tokens=1)) | StrOutputParser()
    # プロンプトにfstringをわたつ
    role_number = chain.invoke({"role_options": role_options, "query": query})
    # role_numberをchainが引き当ててくれたので、その番号のnameを取り出す
    selected_role = ROLES[role_number.strip()]["name"]
    # Stateの current_roleが更新される
    return {"current_role": selected_role}
