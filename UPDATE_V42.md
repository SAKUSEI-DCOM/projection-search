# v42：Wiki個別プロフィール同期の実行漏れを修正

## 修正した問題
v41には `scripts/sync_wiki_profile_x.py` が含まれていましたが、GitHub Actionsの定期実行手順から呼び出されていませんでした。このため、毎時12件の個別プロフィール確認は実際には走りませんでした。v42ではワークフローに組み込みました。

## 変更点
- 毎時23分のワークフローで `sync_wiki_profile_x.py` を実行。
- `data/wiki_profile_cursor.json` と `data/wiki_profile_x_report.json` をコミット対象に追加。次回の巡回位置を保持。
- `data/hourly_monitor_status.json` に `wiki_profile_sync` を追加し、取得件数・追加・衝突・エラーを確認可能に。
- ワークフローの登録漏れを防ぐ回帰テストを追加。

## 導入
1. ZIPを展開し、隠しフォルダー `.github` も含めて `SAKUSEI-DCOM/projection-search` のルートに上書きアップロード。
2. GitHub Actionsの `Refresh Wiki roster and announcements` を手動実行。
3. `data/wiki_profile_x_report.json` を開き `checked`, `added`, `errors`, `multiple`, `conflicts` を確認。
4. `data/wiki_profile_cursor.json` の `cursor` が進むことを確認。

## 現状と制約
GitHubへのアップロードやGitHub Actions本番実行は未実施です。Wikiがアクセスを拒否する場合、取得は失敗しエラーが記録されます。X投稿本文の自動取得は引き続き未接続です。Xリンクの登録のみでは配信告知の取得はできません。
