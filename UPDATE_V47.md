# v47 更新内容

## Wikiライバー画像の候補検出を強化
- Wikiの遅延読み込み画像（`data-src`、`data-original`、`data-lazy-src`）に対応。
- `figure` 内の「立ち絵」「全身」などのキャプションを検出。
- 広告・バナー・外部ホスト画像を除外。
- 画像が曖昧になった場合、過去の候補を消さず「要再確認」と記録。
- 画像が見つからなくなった場合も履歴を保持して再確認可能に。

## X投稿本文について
現時点で無料・無人・全142アカウント毎時の取得は実現していません。既存のX API連携と許可済みRSS/Atom連携は維持しています。X API未設定の場合はX本文を取得しません。

## 導入
ZIPを展開し、GitHub `projection-search` リポジトリにファイルを反映して Actions を手動実行。`data/wiki_portrait_candidates.json` と `data/wiki_portrait_report.json` を確認してください。画像の公開には個別の利用許可確認が必要です。
