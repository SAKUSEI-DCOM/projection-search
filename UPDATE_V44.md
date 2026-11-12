# v44: X投稿の巡回漏れを修正・Wiki画像の権利確認を追加

## X投稿本文の取得
- X公式APIのBearer Tokenがある場合、登録アカウントを8名ずつまとめて検索します。
- **従来は毎時先頭16名だけを検索していたため、残りのライバーが恒常的に対象外でした。** 今回は `data/x_query_cursor.json` に次の検索位置を保存し、毎時対象を順送りにします。
- 1時間に2クエリ（16名）なら142名を一巡するのに約9時間かかります。**各ライバーを毎時監視できるわけではありません。** X APIの直近検索の取得可能期間を超えた投稿は取り逃す可能性があります。
- `X_MAX_QUERIES_PER_RUN` を増やすとAPI利用料が増える可能性があります。APIキーなしの場合、X本文取得はできません。
- 取得結果は `data/collection_status.json`、巡回位置は `data/x_query_cursor.json` に保存されます。

## ライバー画像
- Wikiの個人ページから明示的に「立ち絵」「全身」等と書かれた画像を抽出し、`data/wiki_portrait_report.json` の `candidates` に画像URLと出典を保存します。
- **第三者画像の公開埋め込みは、Wikiにあるという理由だけでは許可されません。** 初期状態は画像候補の収集のみで、ライバー一覧には自動表示しません。
- 画像権利者から利用許可を得ている場合、GitHub Actionsの `sync_wiki_portraits.py` 実行ステップに `WIKI_PORTRAIT_EMBED_APPROVED: 'true'` を設定すると、明確な画像候補のみ反映できます。設定者が権利を確認する必要があります。
- 既存画像を勝手に上書きしません。

## 導入
ZIPを展開してリポジトリ直下へアップロードし、GitHub Actionsを実行。`data/collection_status.json` と `data/wiki_portrait_report.json` を確認してください。実サイトへのアップロード・本番API取得は未実施です。
