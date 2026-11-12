# v39: Projection非公式WikiのXリンクを監視対象へ同期

参照元: https://wikiwiki.jp/projecti0n/

- Wikiトップのライバー名と隣接するXプロフィールリンクを照合し、未登録のX URLを `livers.json` に追加します。
- 既存のX URLとWiki掲載URLが異なる場合、無断上書きせず `data/wiki_x_link_report.json` に確認候補として記録します。
- リンクが消えても直ちに引退判定しません。Wikiが明示的に引退者へ分類したか、Xアカウントが存在しないことを別途確認する必要があります。
- 毎時23分のGitHub ActionsでWikiリンク同期→Xハンドル一覧更新→既存の告知収集処理を実行します。
- **Xの投稿本文を取得する機能は追加していません。** 投稿の自動取得には正規のAPIや許可された情報源が必要です。

## 導入
ZIPを展開し、`.github` を含めて既存リポジトリへ上書きアップロードしてください。GitHub Actionsの `Refresh Wiki roster and announcements` を手動実行すると、レポートが生成されます。

## 検証
ローカルではネットワークが制限されているため、Wiki本番HTMLを使った同期は未検証です。実行後は `data/wiki_x_link_report.json` の `matched` と `newly_linked` を確認してください。Wiki側のHTML構造によっては抽出処理の調整が必要です。
