# TOM TED TOD 公式サイト

地球を愛するエイリアン TOM TED TOD の公式サイト（https://swarmproject1.netlify.app）。
旧 CREATURE WORKS のデザイン（暗色背景・モノスペース・細い罫線・システムラベル）を引き継いで改修したもの。

## 構成

| パス | 内容 |
|---|---|
| `content/site.json` | HERO・ORIGIN・各ページ導入文などの共通文言 |
| `content/artworks/` | 作品（素体・カスタム作品）。1作品＝1ファイル |
| `content/artists/` | 参加作家（公開名義・匿名の扱い） |
| `content/events/` | 展示・協業（ENCOUNTERS）。`artworks` に作品IDを入れると、その作品ページの活動履歴に自動で載る |
| `content/logs/` | 地球滞在ログ（EARTH LOG） |
| `content/news/` | お知らせ（SIGNALS） |
| `images/` | 画像 |
| `src/assets/` | CSS・JS |
| `build.py` | `content/` から `dist/` に静的HTMLを生成（Netlify がデプロイ時に自動実行） |
| `admin/` | 管理画面（Decap CMS）の設定 |
| `legacy/` | 改修前の CREATURE WORKS 版（バックアップ。公開されません） |

## 更新のしかた

1. `content/` の該当フォルダに JSON を追加・編集する（GitHub 上で直接編集してOK）。
2. `status` を `public` にすると公開。`draft` は非表示、`sample` はプレビューでのみ表示（本番では出ない）。
3. main に反映すると Netlify が自動でビルド・公開する。

ローカル確認: `python3 build.py` → `dist/` をブラウザで開く。

## 運用ルール（改修指示書より）

- キャラクターの造形（角・顔・身体・背中の余白）は確定。画像の加工・AI再生成はしない。
- 未確認の情報は `[要確認]` のまま残し、実績・作家名・SNSを作らない。
- 「誰でも百貨店に出せる」「必ず展開される」などの保証表現は使わない。
- 特定ジャンルをプロジェクトの中心として書かない。
