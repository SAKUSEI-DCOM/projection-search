# Projection v25 — X監視対象の自動同期

## 追加したこと
- `scripts/sync_x_accounts.py` を新設。`livers.json` の公開XプロフィールURLから、正しい形式のハンドルのみを抽出。
- `data/x_accounts.json` の `manual_handles` を保持し、重複なく `handles` を自動更新。従来の `handles` は初回実行時に手動登録分として引き継ぐ。
- GitHub ActionsでWikiプロフィール補完の直後に自動同期を実行。X APIを利用できる場合、同期されたハンドルが次の取得処理で使われる。
- `data/x_account_sync_report.json` に登録件数、不正URL、重複プロフィールを記録。
- `automation.html` から同期結果を確認可能。

## 無料運用
Windows PCの常時起動不要。GitHub Actionsの無料枠で実行できます。ただしXの投稿を無料で取得する経路はまだ確保していません。X APIの利用には公式の認証情報と該当権限が必要です。Xログイン済みセッションのスクレイピングは行いません。

## 反映手順
1. ZIPを展開し、GitHub `projection-search` リポジトリへ既存ファイルを上書きアップロード。
2. Actionsの `Refresh Wiki roster and announcements` を手動実行。
3. `automation.html` と `data/x_account_sync_report.json` で対象数を確認。
4. 新しいライバーのXプロフィールがWikiに掲載されると、巡回後に監視対象へ反映されます（自動抽出は一意のURLに限る）。

**注意**: この更新は監視対象リストの自動整備です。142名のX投稿の完全自動収集を実現したものではありません。GitHubへのデプロイは未実施です。
