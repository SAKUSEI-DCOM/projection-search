# v43: X投稿取得の安全設定とWiki画像の自動補完

- X公式APIの投稿本文取得は以前から `scripts/collect.py` に実装されています。`X_BEARER_TOKEN` が必要で、X APIは従量課金です。無料・無制限の自動収集ではありません。
- 誤課金を避けるため `X_MAX_QUERIES_PER_RUN` の初期値を2に制限。1回の実行で最大16アカウントを問い合わせます。全アカウントを毎時確認するには値の変更と予算確認が必要です。
- Xから取得した投稿はキーワードを含むものを `candidates.json` に保存し、誤告知防止のため自動公開は既存の確認処理に従います。
- Wikiの個人ページから画像のalt/titleに「立ち絵」「全身」「キービジュアル」等が明示されている画像のみ、ライバー画像としてURLを補完する `scripts/sync_wiki_portraits.py` を追加。
- Wiki画像をダウンロード・再配布せず、外部画像URLを参照します。画像の転載・埋め込み許諾を保証するものではないため、公開運用前にWikiや権利者の利用条件を確認してください。
- 曖昧な画像、無関係画像、既存画像は自動上書きしません。画像がないページは空欄のままです。
- 毎時のActionsワークフローに追加。`data/wiki_portrait_report.json` で結果を確認できます。

## 導入
1. ZIPの中身をGitHubリポジトリ直下へ配置（`.github` フォルダーを含む）。
2. GitHub Actionsで `Refresh Wiki roster and announcements` を手動実行。
3. X APIを使う場合のみGitHub Secretsに `X_BEARER_TOKEN` を設定。Xの開発者コンソールで課金上限を設定。
4. `data/collection_status.json` と `data/wiki_portrait_report.json` を確認。

## 未完了・制約
- 本番Wikiへの画像取得テストおよびGitHub反映は未実施。
- Wikiの画像に明確な説明がない場合は埋めません。Wikiの画像が表示禁止・権利上不適切な場合も使用できません。
- XのAPIキーがない状態では投稿本文の自動取得は動きません。142名全員の毎時取得を無料で保証できません。
