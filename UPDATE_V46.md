# v46 更新内容

## 画像候補が次回実行で消える不具合を修正
GitHub Actions のコミット対象に `data/wiki_portrait_candidates.json` が抜けていました。v46では保存対象に追加しました。

## ライバー画像の個別承認方式
`data/wiki_portrait_approvals.json` に、対象ライバーIDごとに許可を記録した場合のみ画像を表示できます。画像URLとWikiプロフィールURLが一致し、`rights_confirmed_by` が記載されている必要があります。旧来の `WIKI_PORTRAIT_EMBED_APPROVED=true` による一括承認は廃止しました。

例（実際の許可を確認してから記入）:
```json
{
  "実際のライバーID": {
    "approved": true,
    "image_url": "https://wikiwiki.jp/projecti0n/実際の画像URL",
    "source_url": "https://wikiwiki.jp/projecti0n/実際の個人ページ",
    "rights_confirmed_by": "権利確認した管理者の記録"
  }
}
```

`wiki_portrait_review.html` で候補を確認してください。画像を掲載する許可がない場合は承認ファイルを空のままにしてください。

## X投稿の自動取得について
X公式APIトークンが未設定なら投稿本文は取得されません。無料のX全文監視は実現していません。現在の設定は最大16アカウント/時で順次巡回する方式です。

## 導入
v46をGitHubの `projection-search` リポジトリにアップロードし、Actionsを手動実行してください。`data/wiki_portrait_candidates.json` と `data/wiki_portrait_report.json` が更新・コミットされるか確認します。既存サイトは維持します。GitHub本番への反映は未実施です。
