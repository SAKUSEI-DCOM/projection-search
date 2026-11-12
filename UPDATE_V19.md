# v19：無料の投稿取り込み自動化

- GitHub Actions（毎時）で `data/incoming/*.csv` と承認済みIssueを取り込み、既存の日時解析器で予定を生成。
- GitHub Issuesの「配信告知」フォームから、リポジトリのOWNER/MEMBER/COLLABORATORによる投稿を即時処理。一般ユーザーのIssueは自動登録しない。
- X投稿を無断スクレイピングする仕組みは含めない。X APIが設定されれば既存のAPI収集も利用可能（従量課金）。
- AIは必須ではない。曖昧な画像告知のAI解析は人による確認を経て追加する構想。

## 無料運用の手順
1. このZIPの中身をGitHubリポジトリ直下に配置し、Actionsの書込権限を有効化。
2. 本人または共同編集者がIssues → New issue → 配信告知の取り込み依頼にURL・本文・投稿日時・アカウントを入力すると、Actionが自動起動。
3. CSVでまとめて登録する場合は `data/incoming/` にCSVを追加し、毎時Actionまたは手動実行を待つ。
4. Xの投稿を自動で見つける部分はX API契約・許諾済みRSS・本人提供フィードなど、利用条件に合う入力元が必要。

CSV列：`post_url,post_text,published_at,author`。相対日時の基準となる投稿日時にはタイムゾーンを付ける。
注意：`livers.json` の各ライバーに正しいX URLがない場合、名前で一意に照合できない投稿は登録されません。
