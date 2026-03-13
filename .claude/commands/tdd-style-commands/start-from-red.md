---
name: start-from-red
description: skill @.claude/skills/tdd-integration-new/skill.md を起動します。起動後は、REDテストの仕様書mdおよびRED CODE品質の基準となるmdを要求します。ユーザー送信後、skill内容で進めます。
---

# /commands/start-from-red
skill @.claude/skills/tdd-integration-new/skill.md を起動します。

起動後は
REDテストの仕様書mdおよび
RED CODE品質の基準となるmdを
Claude が要求します。
要求の際は下記のtemplate文を送りなさい。

never read entire directry
ファイル全体の構造を読み込まないでください。
コンテキスト削減のために。

下記のテンプレートを送信してユーザーから明示的に回答を得てください。

ユーザーがこれらを送信後、skill内容の通り進めます。


```bash
TDDをスタートするにあたって以下の2点をお送りください。

REDテストの仕様書となるmdファイル。これはdocs配下にあります。：

REDCODE品質の基準となるmdファイル。これは、subagentファイルとして .claude/agents　配下に用意してあります。：

下記のものをコピー&ペーストして、該当ファイルを指定して送ってください
REDテストの仕様書： @~
REDCODE品質基準ファイル： @~
```