# Projection v27 — Xアカウント候補の人手確認と安全な登録

- `profile_approve.html` でWiki候補を開いて確認し、確認済みのライバー名とXプロフィールURLを登録できます。
- `verified_x_profiles.json` をダウンロードして、GitHubリポジトリの `data/verified_x_profiles.json` にアップロードしてください。
- GitHub Actionsは `apply_verified_profiles.py` → `sync_x_accounts.py` の順で実行し、承認済みアカウントを監視対象に追加します。
- 不正なURL、存在しないライバー名、同一Xアカウントの重複、既存アカウントとの不一致は拒否します。拒否時はActionsを失敗させ、確認を促します。
- Xへのログイン・スクレイピング・無許可の投稿収集は行いません。投稿の完全自動取得は未実現です。

## 導入
ZIPを展開し、GitHubの `projection-search` リポジトリにファイルを反映してください。`profile_approve.html` をGitHub Pagesで開き、候補を確認し、JSONを保存して `data/verified_x_profiles.json` にアップロードします。Actionsを実行後、`data/verified_x_apply_report.json` を確認してください。
