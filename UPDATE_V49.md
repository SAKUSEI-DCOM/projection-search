# v49 更新内容

- GitHub Actionsに手動実行できる **Full Wiki profile audit (manual)** を追加しました。通常の1時間ごとの12名ずつではなく、登録済みの対象ライバー（最大200名）のWiki個人ページを1回で調べ、Xリンクと画像候補を記録します。
- `sync_wiki_profile_x.py` が環境変数 `WIKI_PROFILE_BATCH` を受け取れるようにしました。
- X APIキーの有無だけで「投稿取得済み」と判断してしまうカバレッジ表示を修正しました。
- 定期ワークフローのカバレッジ生成処理にもAPI設定の有無を渡します。

## 操作
1. ZIPを展開し、GitHubの `projection-search` リポジトリにファイルと `.github/workflows/wiki-full-audit.yml` をアップロード。
2. GitHub → Actions → **Full Wiki profile audit (manual)** → Run workflow。
3. 完了後、`data/wiki_profile_x_report.json`、`data/wiki_portrait_report.json`、`data/wiki_portrait_candidates.json`、`data/source_coverage.json` を確認。

## 制約
- 実際のWiki取得結果はGitHubでの実行後に確定します。ネットワークにアクセスできない環境では本番テスト未実施です。
- X投稿本文はX公式API等の適法な情報源が接続されない限り取得できません。
- Wiki画像の利用許可は別途確認が必要で、自動掲載は許可済み画像に限定しています。
