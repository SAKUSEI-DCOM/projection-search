# v14 更新内容

- トップページの編集・保存時に `portrait_source_url`、`portrait_status`、`portrait_reviewed_at`、`image_source`、`image_permission` が消える不具合を修正。
- `portrait_gallery.html` を追加。登録142名の画像掲載状況と、承認済み画像の出典を一覧表示。
- 画像登録時に `image_source` と `image_permission` を記録し、既存の品質検査と連携。
- 掲載取り消し時に出典・権利確認メタデータも消去。
- X投稿URLを画像URL欄に誤入力するケースを検出。
- 未確認の画像候補は自動掲載しない。

**注意**: X画像の実収集・転載許可の自動確認は行っていません。現時点で新たに画像を取得したわけではありません。GitHubには未反映です。
