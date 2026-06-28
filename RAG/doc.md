
## RAGの精度を高める
agentic RAG（エージェント型RAG）のSelf-Reflective RAG（自己反省型RAG）
 
user : クエリ x
↓
system: RAG検索
↓
system: 近いドキュメントが見つかる
↓
system: このdocは xに対して確かな回答? 

correct ならば docを分解・再構成して返答
ambiguous 
incorrect ならば x をクエリ言い換えして x'　を作り出して　再びrag検索