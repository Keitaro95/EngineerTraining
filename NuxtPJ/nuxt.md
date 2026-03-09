UIはこれ
https://element-plus.org/en-US/guide/quickstart#nuxt
https://element-plus.org/en-US/component/message
https://element-plus.org/en-US/component/notification　
https://element-plus.org/en-US/component/menu#top-bar







Element Plus = htmlタグ
el-input  = input
el-tag


これをrappingしている
機能拡張したい時
Element plusをラップしている
ソースコード
Propsがあったりなかったりする
あった方が綺麗になるならprops追加していい
EC2インスタンスで動いてる
Nuxtが動いてるNodeサーバーから backend APIに接続。
php, Laravel
db


今はmockサーバーを建てた段階で
画面のmockupをmockサーバーと繋いでる段階
↓
11月 Backend　API実装されて
それをFrontで繋ぎ合わせる作業。

typescriptのinterfaceとか
UI表示の整合性に時間を要する


UTは画面コンポーネントレベルのレベルのテストは不要で、関数のテストレベルでお願いします！

前橋さんデプロイ環境とLocalとの環境差異の原因究明
・husky導入検討
commit時にlint系
prettierを走らせてレビューコストを下げれる。品質が保持される。
・eslint-plugin-vuejs-accessibility導入検討
PR作成前に凡ミス実装を防げる(alt欠落、label/for不整合などなど)

9/17
バレルを使いまくると localの npm run dev　が遅い 40s以上
Localデプロイで注意必要
https://sopherre.slack.com/archives/C08VBR27JG1/p1759122549094269
maehashijunnoMacBook-Air:dw-joy-frontend maehashijun$ npm -v
11.5.1
maehashijunnoMacBook-Air:dw-joy-frontend maehashijun$ node -v
v22.19.0
Npm run dev　で一時的に起動できない問題発生
前橋さん
sconfig.jsonの設定がnuxt3以降向けの正しい状態じゃなかったようです
.nuxtディレクトリ再生成のタイミングでこのへんにズレが生じることがあるようで
extends: "./.nuxt/tsconfig.json"を追加することで：Nuxtが自動生成する全ての型定義を継承
#imports、#app、~、@などのパスエイリアスが正しく解決される
自動インポートされるAPIの型が全て利用可能になる

オートインポート系の問題に関しては、デフォルトで .nuxt/tsconfig.json を読み込んでくれないみたいなので、明記する必要があるらしいです
これで動作した

