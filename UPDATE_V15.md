# v15 更新内容
- 立ち絵の一括CSV確認・反映ページ `portrait_bulk.html` を追加。
- ライバーIDまたは重複しない名前で照合。重複行・不明な名前は除外。
- `permission_confirmed=yes` と `complete_confirmed=yes` の両方がある場合のみ、X投稿URLと直接画像URLを検証して登録。
- 登録結果を `livers.json` としてダウンロード可能。公開反映はGitHubへのアップロードが必要。
- Xからの自動画像取得や掲載許可の自動判断は行わない。
- ローカルのfile://ではfetchが動作しない場合があるため、GitHub Pages上で操作する。
