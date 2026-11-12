# v45 更新内容

- Wiki画像候補を `data/wiki_portrait_candidates.json` に累積保存。毎時のレポート上書きで以前の候補が消える問題を解消。
- `wiki_portrait_review.html` を追加。候補の名前・出典・画像URLを確認できる。権利確認前の画像は表示しない。
- X APIの状態を `data/collection_status.json` に明示（未設定、APIエラー、部分巡回、巡回済み）。
- 既存の配信告知・プロフィール・GitHub Actionsは維持。

## 注意
X APIトークン未設定ではX本文は取得できません。無料で142名の投稿を毎時取得できると保証するものではありません。Wiki画像の別サイトでの表示には利用許可を確認してください。

## 導入
ZIPを解凍しGitHubリポジトリのルートへアップロードしてください。Actionsを実行後、`wiki_portrait_review.html` と `data/collection_status.json` を確認してください。GitHubへの反映と本番取得は未実施です。
