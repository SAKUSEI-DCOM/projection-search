# v29 更新内容

- **実際に収集を開始するための設定作成ツール** `feed_setup.html` を追加。
- 既存の `data/free_feeds.json` / `data/calendar_feeds.json` を読み込み、情報源を追加し、JSONをダウンロード可能。
- 取得元の許可確認、HTTPS、重複URL、Xユーザー名の形式を入力時に検査。
- 設定はブラウザ内だけで処理し、勝手に外部送信しない。GitHubへの手動アップロードが必要。
- 既存の `collect_free_feeds.py` と `collect_calendars.py` がGitHub Actionsの定期処理で設定を使用する。

## 重要な制限

- 公開RSS/Atom/iCalendarの**実在するURLはまだ登録されていません**。今回の追加だけではX投稿を収集できません。
- Xのログイン済みセッションを用いた無許可スクレイピングは採用しません。
- GitHubへのアップロード・公開サイトへのデプロイは未実施です。
- 情報源が許可する利用範囲を必ず確認してください。

## 操作

1. `feed_setup.html` を開く。
2. 公開設定を読み込むか既存JSONを指定する。
3. 許可された公開フィードのURLとライバー名を入力。
4. JSONをダウンロードし、GitHubリポジトリの `data/` に同名でアップロード。
5. GitHub Actionsの `Refresh Wiki roster and announcements` を手動実行するか定期実行を待つ。
6. `automation.html` で取得結果を確認。
