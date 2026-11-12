# Projection v24 — 無料クラウド更新の信頼性改善

- 許可済み公開ICSカレンダーについて、同一UIDの日時・タイトル変更を既存予定へ反映。
- ICSの `STATUS:CANCELLED` がある場合、予定を `cancelled` に更新。未掲載の中止イベントは追加しない。
- カレンダーの一時的な取得失敗や掲載期間外への移動を「中止」と誤認しないよう、フィードから消えたイベントは自動削除しない。
- `data/calendar_feed_status.json` に新規・変更・中止件数を記録。
- 自動取得管理画面に実際の対応範囲を明記。
- GitHub Actionsは毎時23分（UTC）に実行する設定。PC常時起動不要。ただし実行遅延・欠落の可能性あり。

## 初回設定
1. GitHubリポジトリの既存ファイルをv24で更新。
2. `source_setup.html` で本人の許可があるRSS/ICSの登録用JSONを作り、`data/sources.json` / `data/calendar_feeds.json` に設定。
3. GitHub Actionsの `Refresh Wiki roster and announcements` を手動実行して動作確認。
4. `automation.html` と `data/calendar_feed_status.json` を確認。

**制限:** Xの投稿を直接無料取得する機能は未実装です。未設定の公開フィードから投稿を取得することはできません。GitHubへのデプロイは行っていません。
