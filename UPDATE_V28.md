# v28 更新内容

- 公開WikiプロフィールからRSS/Atom/iCalendarのURLを探す定期収集処理を追加。
- GitHub Actionsで1回最大10名を巡回し、候補を `data/feed_discovery.json` に保存。
- `feed_candidates.html` で候補と元リンクを確認可能。
- 候補は **自動で信用・登録しない**。情報提供の許可や本人との対応を確認した後、`data/free_feeds.json` またはカレンダー設定へ登録する。
- 既存のX収集制限は変わらず、X投稿の無料完全自動取得は未実現。
- GitHub Actionsの実行はGitHub上にv28をアップロード後に有効になる。

## テスト

`python -m unittest discover_feeds_test.py`
