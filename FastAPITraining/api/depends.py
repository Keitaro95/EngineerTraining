
# 1. app/FastAPIグローバル
#    ↓
# 2."The router dependencies are executed first, 最初にルーター
#  include_router時の依存関係
#    ↓
# 3. then the dependencies in the decorator, 　次にデコレーター
# @router.get(dependencies=[...]) デコレータ
#    ↓
# 4. and then the normal parameter dependencies."　その次にnomal
# 関数パラメータの Depends()
#    ↓
# 5. パスオペレーション関数の実行
