# v37 リスナーからのX投稿情報提供方式

## できること
- `submit.html` で公開X投稿URL、投稿者ID、投稿日時（JST）、投稿本文を入力。URLからIDを補完し、各欄をコピーできます。
- GitHub Issueの「配信告知」テンプレートへ投稿します。**GitHubアカウントが必要**です。
- 管理者が元投稿を目視確認してIssueに `掲載承認` ラベルを付けると、GitHub Actionsが自動起動し、告知候補を取り込みます。
- 既存の日時解析で予定を仮登録し、元投稿へのリンクを残します。ライバー登録済みのX IDとの一致が必要です。
- 定期実行も承認済みIssueを取得します。承認時の初回内容を保存し、後からの編集で承認済みデータを上書きしません。

## 導入手順
1. ZIPを展開し、内容を `SAKUSEI-DCOM/projection-search` リポジトリのルートにアップロード。`.github` フォルダーも必要。
2. GitHubのSettings → Actions → Generalで、Actionsにリポジトリへの書き込み権限（Read and write permissions）を付与。
3. GitHub Issuesを有効化し、Issueラベル `配信告知` と `掲載承認` を作成。
4. Pagesで `submit.html` を開き、テスト投稿を作成。運営者が投稿内容・本人のXアカウント・投稿日時を確認後 `掲載承認` ラベルを付ける。
5. Actionsの `Import trusted stream announcement issue` 実行結果、`data/inbox_report.json`、`data/auto_publish_report.json`、`schedules.json` を確認。

## 制限・注意
- **X投稿の自動監視や本文の自動取得はしません。** 情報提供がなければ新しい投稿を発見できません。
- 情報提供者は投稿内容を手入力します。投稿本文・日時の真偽は自動では検証できないため、**掲載承認は運営者の目視確認が前提**です。
- 相対日時はX投稿の正しい投稿日が必要です。曖昧な告知は自動登録されません。
- GitHub Issueの編集後に再承認した場合、すでに取り込んだ内容は上書きされません。訂正は新規Issueまたは管理者がデータを修正してください。
- GitHub Pagesは静的サイトのため、GitHubアカウント不要の直接送信フォームではありません。
- GitHub Actionsの無料枠・ポリシーはリポジトリの公開設定等によります。
