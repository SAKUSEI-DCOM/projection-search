# v40：Wiki Xリンク同期の安定化・初回実行診断

## 更新内容
- Wikiの表（`tr`）や箇条書き（`li`）の構造から、同じ行にあるライバー名とXリンクを対応付けるよう改良。
- 別のライバーの行にあるXリンクを誤登録しないように変更。
- Xリンクが複数ある場合や既存の登録と食い違う場合は、勝手に上書きせず確認レポートへ記録。
- Wikiへの接続失敗時・抽出0件時も `data/wiki_x_link_report.json` に失敗理由を保存。既存登録は維持。
- **WikiにXリンクがないことや一時的なエラーだけで引退と判定しない。**
- 追加テスト6件、既存含む35件のテスト成功。

## 公開・初回確認
1. ZIPを解凍してGitHubの `SAKUSEI-DCOM/projection-search` に `.github` を含むファイルをアップロード。
2. GitHub → Actions → `Refresh Wiki roster and announcements` → `Run workflow`。
3. 実行後、`data/wiki_x_link_report.json` の `status` / `matched` / `newly_linked` / `changed_needs_review` を確認。
4. `status=fetch_error` はWiki接続失敗、`status=no_matches` はHTMLから照合できなかったことを意味します。どちらも引退者の判定には使いません。

## 制約
Xの新着ポストを自動取得する機能はまだありません。1時間ごとのActions実行はできますが、X公式APIの認証・利用権限または許可されたフィードがない場合、ポストは収集されません。
実際のWiki本番データでの同期とGitHubへの公開は未実施です。
