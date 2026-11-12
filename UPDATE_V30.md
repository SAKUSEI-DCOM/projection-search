# v30 更新内容：無料のGitHub告知収集を実際の定期処理に接続

- GitHubの公開Issue APIから「配信告知」ラベル付きIssueを定期取得する `scripts/collect_github_issues.py` を追加。
- **リポジトリのOWNER/MEMBER/COLLABORATORのみ**自動取り込み。一般ユーザーの投稿は承認なしで公開されません。
- 取得したIssueは既存の厳格なURL・投稿者・タイムゾーン検証を通し、`data/incoming/` → `candidates.json` → 日時解析へ接続。
- `collect.yml` に組み込み、PCなしで毎時実行（GitHub Actionsの遅延・停止はあり得ます）。
- `data/github_issue_collection.json` に取得件数・拒否件数・APIエラーを記録。
- `scripts/test_github_issues.py` で権限検査と入力解析をテスト。

## 実際に動かすには
1. v30一式をGitHubの `projection-search` リポジトリへアップロード。
2. GitHub Actionsが有効で、ワークフローに `contents: write` 権限があることを確認。
3. 共同編集者が「配信告知」Issueフォームに投稿URL・本文・投稿日時を入力。
4. Issueイベント、または毎時の定期実行で取り込み。`data/github_issue_collection.json` を確認。

## 限界
- **Xの投稿そのものは取得しません**。信頼できる人から提供された投稿内容を自動取り込みする機能です。
- 取得対象の公開Issueが0件なら、配信予定は増えません。
- 投稿者が本当にX投稿の内容を正しく転記したかは自動検証できません。公開時は「要確認」扱いです。
- GitHubへのデプロイ・本番のAPI接続は未実施です。
