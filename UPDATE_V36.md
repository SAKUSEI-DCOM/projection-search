# v36 無料・PC不要の公式API自動収集

## 実装
- Bluesky公式公開API `app.bsky.feed.getAuthorFeed` から投稿を取得する `scripts/collect_bluesky.py` を追加。認証・課金不要（利用制限はあり）。
- GitHub Actionsの既存の定期収集処理に接続。投稿の本文、投稿時刻、元投稿URLを `candidates.json` に記録。
- リポスト、他人の投稿、日時のない投稿、告知と無関係な投稿を除外。
- `data/bluesky_collection_status.json` にアカウント別の取得成否と新規件数を記録。
- `data/bluesky_accounts.json` で対象アカウントを設定。初期状態は空配列。既存Xアカウントとの照合が成立し、管理者が `verified_mapping:true` に設定した場合のみ配信予定の自動仮登録が可能。

## 設定例
`data/bluesky_accounts.json` に以下の形式で登録する（実在アカウント名に置き換える）。
```json
[
  {
    "actor": "example.bsky.social",
    "x_handle": "example_x_handle",
    "verified_mapping": true
  }
]
```
`x_handle` は `livers.json` の本人Xプロフィールと一致する必要がある。`verified_mapping` は同一人物だと確認した場合にのみ true にする。未確認は false にして、告知候補としてのみ収集する。

## 運用
ZIP内のファイルを GitHub リポジトリへアップロードし、Actionsを有効化。ワークフロー `collect.yml` を手動実行して `data/bluesky_collection_status.json` を確認する。GitHub Pagesは静的公開先で、収集処理はGitHub Actions側で動作する。

## 重要な限界
- **X投稿は取得しない。** Blueskyに同じライバー本人が告知を投稿している場合に限り収集できる。
- `bluesky_accounts.json` は現在0件。したがって本番での告知取得はまだ始まらない。
- 今回はサンプルデータによるユニットテストのみ実施。実アカウントへのAPIアクセス、GitHub上での動作は未検証。
- 公式APIのレート制限、投稿削除、サーバー停止により取得できない場合がある。
- 投稿の全文をそのままサイトに再掲載する設計ではなく、予定・元投稿リンクの表示を優先する。
