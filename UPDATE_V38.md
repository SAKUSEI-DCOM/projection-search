# v38 毎時監視の実行基盤と可視化

- 既存のGitHub Actions `23 * * * *`（毎時23分）を維持。実行遅延はあり得ます。
- `scripts/hourly_monitor.py` を追加。ライバーのXプロフィール登録数・監視対象ID・RSS取得成功数・X API設定状況をレポート化。
- `monitor.html` を追加。サイト上で各ライバーのX URL登録状況とデータ取得元の稼働状況を確認可能。
- GitHub Actionsで毎時レポート生成・コミット。
- `scripts/test_hourly_monitor.py` でURL正規化と誤認表示防止をテスト。

## 公開方法
ZIPの内容をリポジトリルートへアップロードし、`.github/workflows/collect.yml` を含めて上書きします。GitHub Actionsの書き込み権限を有効にし、Actions画面から `Refresh Wiki roster and announcements` を手動実行して初回レポートを生成してください。公開後は `monitor.html` から確認できます。

## 制限
**Xプロフィールを登録しただけで投稿が読めるわけではありません。** X公式APIの利用可能な権限がない場合、X投稿の自動取得はできません。RSSも許可された公開フィードが登録されている場合のみ取得します。ライバー本人の投稿を取得できたと誤認させない表示にしています。GitHub Issuesによる情報提供はv37の仕組みを維持します。
