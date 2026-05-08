<script setup lang="ts">
</script>

<template>
  <TheModuleBar />
  <div class="t-top-template__announce-container">
    <div class="t-top-template__maintainance-container">
      <div class="t-top-template__maintainance-title">【連絡】</div>
      <div class="t-top-template__maintainance-content">
        ・ｘｘ月ｘｘ日までにｘｘｘを入力して下さい。<br />
        ・ｘｘ月ｘｘ日はメンテナンスのため利用できません。
      </div>
    </div>

    <div class="t-top-template__img">ここにimageが入ります</div>
  </div>
</template>

<style lang="scss" scoped>
/* お知らせ全体を囲むコンテナのスタイル */
.t-top-template__announce-container {
  /* 親要素の80%の幅に設定し、左右に余白を作成 */
  width: 80%;
  /* 上部に24pxの内部余白を設定 */
  padding-top: 24px;
  /* 上下の外部余白を0、左右の外部余白を自動に設定して中央揃えにする */
  margin: 0 auto;
}

/* メンテナンス情報を囲むコンテナのスタイル */
.t-top-template__maintainance-container {
  /* 内側に16pxの余白を設定 */
  padding: 16px;
  /* 下部に24pxの外部余白を設定 */
  margin-bottom: 24px;
  /* フォントサイズを30pxに設定 */
  font-size: 30px;
  /* 1pxの黒い実線の枠を設定 */
  border: 1px solid var(--color-neutral-1000);
}

/* 画像コンテナのスタイル */
.t-top-template__img {
  /* テキストや画像を中央揃えにする */
  text-align: center;
}
</style>
