<!--
=============================================================
  Tailwind CSS サンプルコード 解説版
  ※ class="" の中のコメントは読みやすさのため外に出しています
=============================================================
-->

<!--
  ★ Tailwindの基本ルール（読む前に覚えておくと楽）

  【サイズの単位】
    数字は基本的に × 4px
    例: p-2 = 8px,  p-10 = 40px,  h-6 = 24px

  【色の濃さ】
    数字が大きいほど濃い
    例: gray-100(薄い) 〜 gray-950(ほぼ黒)

  【方向の省略形】
    p  = padding（全方向）
    m  = margin（全方向）
    pt = padding-top    pb = padding-bottom
    pl = padding-left   pr = padding-right
    mt = margin-top     mb = margin-bottom
    ml = margin-left    mr = margin-right

  【条件プレフィックス】
    dark:クラス名    → ダークモード時だけ適用
    hover:クラス名   → マウスオーバー時だけ適用
    sm: md: lg:      → 画面サイズによるレスポンシブ対応
=============================================================
-->


<!-- ===== 外側の大きなコンテナ ===== -->
<div class="
  relative                         /* position: relative（子要素の基準点になる） */
  grid                             /* display: grid（グリッドレイアウトを使う） */
  min-h-screen                     /* min-height: 100vh（画面の高さいっぱいに広がる） */

  grid-cols-[1fr_2.5rem_auto_2.5rem_1fr]
  /*
    列を5つ定義する（_はスペースの代わり）
    列1: 1fr      → 残りスペースを均等に使う（左の余白）
    列2: 2.5rem   → 固定幅10px（左のストライプ柄の帯）
    列3: auto     → 中身の幅に合わせる（コンテンツ本体）
    列4: 2.5rem   → 固定幅10px（右のストライプ柄の帯）
    列5: 1fr      → 残りスペースを均等に使う（右の余白）
  */

  grid-rows-[1fr_1px_auto_1px_1fr]
  /*
    行を5つ定義する
    行1: 1fr  → 残りスペースを均等に使う（上の余白）
    行2: 1px  → 1pxの細い線（上の区切り線）
    行3: auto → 中身の高さに合わせる（コンテンツ本体）
    行4: 1px  → 1pxの細い線（下の区切り線）
    行5: 1fr  → 残りスペースを均等に使う（下の余白）
  */

  bg-white                         /* background-color: white（ライトモード時の背景色） */

  [--pattern-fg:var(--color-gray-950)]/5
  /*
    カスタムCSS変数 --pattern-fg を定義している（Tailwind v4の書き方）
    var(--color-gray-950) = ほぼ黒色 を 5%の透明度で設定
    → ストライプ柄の色として使い回す
  */

  dark:bg-gray-950                 /* ダークモード時: 背景をほぼ黒に変える */
  dark:[--pattern-fg:var(--color-white)]/10
  /*
    ダークモード時: --pattern-fg を 白色10%透明度 に変える
    → 暗い背景にうっすら白いストライプが見える
  */
">


  <!-- ===== 中央のカードを包むグレーの枠 ===== -->
  <div class="
    col-start-3                    /* グリッドの3列目から始める（＝中央列） */
    row-start-3                    /* グリッドの3行目から始める（＝中央行） */
    flex                           /* display: flex（子要素を並べる） */
    max-w-lg                       /* max-width: 32rem = 512px（最大幅を制限） */
    flex-col                       /* flex-direction: column（子要素を縦に並べる） */
    bg-gray-100                    /* background-color: 薄いグレー（ライトモード） */
    p-2                            /* padding: 8px（全方向の内側余白） */
    dark:bg-white/10               /* ダークモード時: 白色を10%透明度で重ねた背景 */
  ">


    <!-- ===== 白いカード本体 ===== -->
    <div class="
      rounded-xl                   /* border-radius: 12px（角を丸くする） */
      bg-white                     /* background-color: white */
      p-10                         /* padding: 40px（全方向の内側余白） */
      text-sm/7                    /* font-size: small（0.875rem）/ line-height: 28px */
      text-gray-700                /* color: 濃いグレー（文字色） */
      dark:bg-gray-950             /* ダークモード時: 背景をほぼ黒に */
      dark:text-gray-300           /* ダークモード時: 文字色を薄いグレーに */
    ">

      <!-- ロゴ画像（ライトモード用） -->
      <img
        src="/img/logo.svg"
        class="
          mb-11.5                  /* margin-bottom: 46px（下の余白） */
          h-6                      /* height: 24px */
          dark:hidden              /* ダークモード時: display:none（非表示になる） */
        "
        alt="Tailwind Play"
      />

      <!-- ロゴ画像（ダークモード用） -->
      <img
        src="/img/logo-dark.svg"
        class="
          mb-11.5                  /* margin-bottom: 46px */
          h-6                      /* height: 24px */
          not-dark:hidden          /* ライトモード時: 非表示（dark:hiddenの逆） */
        "
        alt="Tailwind Play"
      />


      <!-- ===== テキストコンテンツのまとまり ===== -->
      <div class="space-y-6">
      <!--
        space-y-6:
        直接の子要素の間に margin-top: 24px を入れる
        「子要素同士の縦の隙間を均等に開ける」便利クラス
      -->

        <p>An advanced online playground for Tailwind CSS, including support for things like:</p>

        <!-- ===== リスト ===== -->
        <ul class="space-y-3">
        <!-- space-y-3: リストアイテム間に margin-top: 12px -->

          <!-- リストアイテム（4つとも同じ構造なので1つだけ詳しく解説） -->
          <li class="flex">
          <!-- flex: アイコン（SVG）とテキストを横並びにする -->

            <!-- チェックマークアイコン -->
            <svg
              class="
                h-[1lh]            /* height: 1lh = 現在の行の高さと同じ（テキストとアイコンの高さを揃える） */
                w-5.5              /* width: 22px */
                shrink-0           /* flex-shrink: 0（flex内でアイコンが縮まないようにする） */
              "
              viewBox="0 0 22 22" fill="none" stroke-linecap="square"
            >
              <!-- 薄い水色の円（背景） -->
              <circle cx="11" cy="11" r="11" class="fill-sky-400/25" />
              <!--
                fill-sky-400/25:
                fill（塗りつぶし色）= sky-400（水色）を 25%透明度で
              -->

              <!-- 水色の円の枠線 -->
              <circle cx="11" cy="11" r="10.5" class="stroke-sky-400/25" />
              <!--
                stroke-sky-400/25:
                stroke（線の色）= sky-400（水色）を 25%透明度で
              -->

              <!-- チェックマーク本体（パス） -->
              <path
                d="M8 11.5L10.5 14L14 8"
                class="
                  stroke-sky-800       /* ライトモード: 濃い水色の線 */
                  dark:stroke-sky-300  /* ダークモード: 薄い水色の線 */
                "
              />
            </svg>

            <p class="ml-3">
            <!-- ml-3: margin-left: 12px（アイコンとテキストの隙間） -->
              Customizing your theme with
              <code class="
                font-mono            /* font-family: monospace（等幅フォント） */
                font-medium          /* font-weight: 500 */
                text-gray-950        /* color: ほぼ黒 */
                dark:text-white      /* ダークモード時: 白文字に */
              ">@theme</code>
            </p>
          </li>

          <!-- 以下3つのリストアイテムは上と同じ構造のため省略コメントのみ -->
          <li class="flex">
            <!-- SVG・pの構造は上と全く同じ -->
            <svg class="h-[1lh] w-5.5 shrink-0" viewBox="0 0 22 22" fill="none" stroke-linecap="square">
              <circle cx="11" cy="11" r="11" class="fill-sky-400/25" />
              <circle cx="11" cy="11" r="10.5" class="stroke-sky-400/25" />
              <path d="M8 11.5L10.5 14L14 8" class="stroke-sky-800 dark:stroke-sky-300" />
            </svg>
            <p class="ml-3">
              Adding custom utilities with
              <code class="font-mono font-medium text-gray-950 dark:text-white">@utility</code>
            </p>
          </li>

          <li class="flex">
            <svg class="h-[1lh] w-5.5 shrink-0" viewBox="0 0 22 22" fill="none" stroke-linecap="square">
              <circle cx="11" cy="11" r="11" class="fill-sky-400/25" />
              <circle cx="11" cy="11" r="10.5" class="stroke-sky-400/25" />
              <path d="M8 11.5L10.5 14L14 8" class="stroke-sky-800 dark:stroke-sky-300" />
            </svg>
            <p class="ml-3">
              Adding custom variants with
              <code class="font-mono font-medium text-gray-950 dark:text-white">@variant</code>
            </p>
          </li>

          <li class="flex">
            <svg class="h-[1lh] w-5.5 shrink-0" viewBox="0 0 22 22" fill="none" stroke-linecap="square">
              <circle cx="11" cy="11" r="11" class="fill-sky-400/25" />
              <circle cx="11" cy="11" r="10.5" class="stroke-sky-400/25" />
              <path d="M8 11.5L10.5 14L14 8" class="stroke-sky-800 dark:stroke-sky-300" />
            </svg>
            <p class="ml-3">Code completion with instant preview</p>
          </li>

        </ul><!-- /ul.space-y-3 -->

        <p>Perfect for learning how the framework works, prototyping a new idea, or creating a demo to share online.</p>

      </div><!-- /div.space-y-6 -->


      <!-- 区切り線 -->
      <hr class="
        my-6                       /* margin-top + margin-bottom: 24px（上下の余白） */
        w-full                     /* width: 100% */
        border-(--pattern-fg)      /* border-color: CSS変数 --pattern-fg の色を使う */
      " />

      <p class="mb-3">
      <!-- mb-3: margin-bottom: 12px -->
        Want to dig deeper into Tailwind?
      </p>

      <p class="font-semibold">
      <!-- font-semibold: font-weight: 600 -->

        <a
          href="https://tailwindcss.com/docs"
          class="
            text-gray-950            /* 文字色: ほぼ黒 */
            underline                /* text-decoration: underline（下線） */
            decoration-sky-400       /* 下線の色: 水色 */
            underline-offset-3       /* 下線とテキストの隙間: 3px */
            hover:decoration-2       /* ホバー時: 下線の太さを 2px に変える */
            dark:text-white          /* ダークモード時: 白文字に */
          "
        >Read the docs &rarr;</a>
      </p>

    </div><!-- /div.rounded-xl (白いカード本体) -->
  </div><!-- /div.col-start-3 (グレーの枠) -->


  <!-- ===== 左のストライプ柄の帯 ===== -->
  <div class="
    relative                       /* position: relative */
    -right-px                      /* right: -1px（1pxはみ出させて境界線をぴったり合わせる） */
    col-start-2                    /* グリッド2列目（左の帯の列） */
    row-span-full                  /* 全行にまたがる（画面の上から下まで） */
    row-start-1                    /* 1行目から始める */
    border-x                       /* 左右に border を引く */
    border-x-(--pattern-fg)        /* border の色を --pattern-fg 変数で指定 */
    bg-[image:repeating-linear-gradient(315deg,_var(--pattern-fg)_0,_var(--pattern-fg)_1px,_transparent_0,_transparent_50%)]
    /*
      background-image に斜めのストライプを描く
      repeating-linear-gradient: 繰り返しグラデーション
      315deg: 斜め45度方向
      0〜1px: --pattern-fg色の線
      transparent: 透明部分（線の間）
    */
    bg-[size:10px_10px]            /* background-size: 10px × 10px（ストライプの間隔） */
    bg-fixed                       /* background-attachment: fixed（スクロールしても背景は固定） */
  "></div>

  <!-- ===== 右のストライプ柄の帯（左と対称） ===== -->
  <div class="
    relative
    -left-px                       /* left: -1px（左と逆方向に1pxはみ出す） */
    col-start-4                    /* グリッド4列目（右の帯の列） */
    row-span-full
    row-start-1
    border-x
    border-x-(--pattern-fg)
    bg-[image:repeating-linear-gradient(315deg,_var(--pattern-fg)_0,_var(--pattern-fg)_1px,_transparent_0,_transparent_50%)]
    bg-[size:10px_10px]
    bg-fixed
  "></div>

  <!-- ===== 上の区切り線（1px） ===== -->
  <div class="
    relative
    -bottom-px                     /* bottom: -1px（1pxずらして線をぴったり合わせる） */
    col-span-full                  /* 全列にまたがる（横幅いっぱい） */
    col-start-1                    /* 1列目から始める */
    row-start-2                    /* グリッド2行目（上の1px行） */
    h-px                           /* height: 1px（細い線） */
    bg-(--pattern-fg)              /* background-color: --pattern-fg の色 */
  "></div>

  <!-- ===== 下の区切り線（1px） ===== -->
  <div class="
    relative
    -top-px                        /* top: -1px */
    col-span-full
    col-start-1
    row-start-4                    /* グリッド4行目（下の1px行） */
    h-px                           /* height: 1px */
    bg-(--pattern-fg)
  "></div>

</div><!-- /div.relative.grid (外側の大きなコンテナ) -->