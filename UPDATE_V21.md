# v21: 無料の自動取得ルートを追加

- `scripts/collect_free_feeds.py` が許可済みの公開RSS/Atomを毎時巡回し、配信告知を `candidates.json` に自動登録します。
- `data/free_feeds.json` に配信者本人や許可を得た公開フィードのURLを追加します。空のままではX投稿は取得できません。
- `data/free_feed_status.json` に取得成功・失敗・新規件数を記録します。
- 取得した本文は既存の `auto_publish.py` で解析します。本人Xアカウントとの照合には `livers.json` の `x` URLが必要です。

## 設定例（実在するURL・許可確認後に置き換える）

```json
[
  {
    "name": "配信者本人の告知フィード",
    "url": "https://example.org/authorized-announcements.xml",
    "x_handle": "example_account",
    "author_verified": true
  }
]
```

`author_verified: true` は**本人が管理するフィードなどで投稿者の同一性を確認した場合だけ**設定してください。検索結果RSSや第三者のまとめRSSでは `false` にしてください。後者は自動掲載せず候補として保留します。

**制限**: Xの投稿を無料・網羅的・無人で取得する方法を実証できたわけではありません。X公式APIは利用権限・料金が必要になる場合があります。スクレイピングや規約回避は実装していません。GitHub Actionsは毎時起動設定ですが、遅延・停止があり得ます。
