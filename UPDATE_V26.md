# Projection v26 — 無料の公開プロフィール監査

- `scripts/profile_link_audit.py`: 公開Wikiのライバー個別ページを毎時最大15件ずつ確認し、掲載されたXプロフィールリンクを候補として保存。約142人なら約10回の成功実行で一巡します。
- `profile_audit.html`: 候補1件・複数・なし・取得エラー・登録済みを検索・確認できます。
- `.github/workflows/collect.yml`: 監査を定期実行し、`data/profile_link_audit.json` を保存。
- **安全性**: XのWebページにアクセスせず、Xログイン・Playwrightスクレイピングを行いません。複数候補はもちろん単一候補も自動確定しません。Wikiのリンクが本人のものか人が確認してください。
- **制限**: X投稿自体の自動取得は未実現。WikiページにXリンクがなければ発見できません。GitHub Actionsの実行には公開リポジトリへの反映が必要です。

## 公開方法
ZIPを展開してGitHubの `projection-search` に上書きアップロードし、Actionsの `Refresh Wiki roster and announcements` を手動実行。`profile_audit.html` を開いて候補を確認してください。
