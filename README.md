# 世田谷1丁目住宅 Web内覧

QRコードから開く、物件のWeb内覧ページです。`site/` がそのまま公開されます（静的サイト・ビルド不要）。

公開中のページ: https://claude.ai/artifact/YY4Roxk8q1inrdeu5JMp7c
（`artifact/index.html` と `site/` の画像・動画・資料を claude.ai に公開したもの。QRコードは `qr/` にあります）

## 構成

| パス | 内容 |
| --- | --- |
| `site/index.html` | 公開ページ（`tools/build.py` で生成。Vercel などにそのまま置ける版） |
| `artifact/index.html` | 同じページの claude.ai 公開用（外枠のhtml/headを除いた版。同じく自動生成） |
| `site/img/` | 写真（WebP。`-l` 拡大表示用 / `-m` 見どころ用 / `-t` サムネイル） |
| `site/media/` | 浴室の動画（720p H.264）とポスター画像 |
| `site/docs/` | 設備資料PDF（圧縮済み） |
| `tools/plans.py` | 間取り図（SVG）。壁は元図面からトレース、建具・設備・部屋名は手描き |
| `tools/data.py` | 写真タイトル・並び順・ピン位置・資料・見どころの文言 |
| `tools/template.html` | ページのHTML/CSS/JS |
| `qr/` | 印刷用QRコード（SVG / PNG） |

## 更新のしかた

1. 文言や写真の並び順を変える → `tools/data.py`
2. 図面の部屋名・位置を変える → `tools/plans.py`
3. 見た目を変える → `tools/template.html`
4. `python3 tools/build.py` で `site/index.html` を再生成してコミット

写真を差し替えるときは、元写真（`0.JPG`〜`47.JPG`）のあるフォルダを指定して
`python3 tools/images.py <フォルダ>` を実行します（EXIF情報は削除されます）。

## 方針（プロの物件ページの作法に合わせた点）

- スマホ前提・軽量：写真は合計約6MB（元143MB）、外部CSS/JSなし
- 間取り図はベクター化して拡大しても鮮明。スマホでは北が上になるよう回転表示
- 撮影位置を間取り上のピンで表示し、写真ビューアからも「間取りで位置を見る」で戻れる
- 写真は玄関から歩く順番（動線順）に並べ、部屋名を明記
- 冒頭に物件の顔（外観）と要点、見どころ6点
- 大容量PDFにはサイズと「Wi-Fi推奨」を表示
