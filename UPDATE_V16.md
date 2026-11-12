# v16 更新内容

- 立ち絵候補を名前で検索・状態別に絞り込み、元投稿を開いて確認できる審査ページ `portrait_review.html` を追加。
- 本人確認・全身完成版確認・掲載許可の3条件を満たす場合のみ、直接画像URLを `livers.json` に反映可能。
- 候補の承認・却下・保留とメモを `portrait_candidates.json` に書き出し可能。
- X投稿画像の自動取得は未対応。画像の確認とURL登録は手動。
- ブラウザの編集内容は自動的にはGitHubへ保存されません。2つのJSONをダウンロードし、`livers.json` と `data/portrait_candidates.json` に上書きアップロードしてください。
