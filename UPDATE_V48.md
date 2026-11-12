# v48 更新内容

- 非公式Wiki個人ページで、画像のalt属性ではなく表のセルに「立ち絵」等が書かれている場合にも候補を検出します。無関係な画像を誤登録しないよう、同じセルに画像が1枚だけの場合に限定します。
- 画像候補の履歴で、ライバーIDが数値のときにも「再確認が必要」の状態が保存されるよう修正しました。
- `scripts/build_source_coverage.py` を追加。登録Xリンク数、許可済みフィード数、Wiki画像候補数、掲載済み画像数を `data/source_coverage.json` に出力します。Xリンクの登録と投稿本文取得を区別し、API未設定で取得済みと誤表示しません。
- GitHub Actionsに上記レポート生成を組み込みました。

## 注意
X投稿本文の無料・完全自動収集は未実現です。X APIなしで投稿本文を取得できると偽ることはしません。Wiki画像は掲載許可の確認が必要です。GitHubへのアップロードと本番Wikiでの動作確認は未実施です。

## 導入
ZIPを展開して `projection-search` リポジトリに上書きし、GitHub Actionsを手動実行。`data/source_coverage.json` と `data/wiki_portrait_candidates.json` を確認してください。
