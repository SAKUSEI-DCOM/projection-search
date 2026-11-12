# v18 更新内容

- Octoparse無料版のCSV手動エクスポートを、既存の配信告知候補形式へ変換する `scripts/import_octoparse.py` を追加。
- CSV列名 `post_url,post_text,published_at,author` に対応（日本語等の別名も一部対応）。
- X投稿URL、投稿者一致、日時のタイムゾーン有無、重複を検査。
- 既存の `scripts/auto_publish.py` と連携し、相対日付の配信告知を要確認予定に変換。
- `octoparse_import.html` にWindows向けの導入手順を追加。
- **Octoparse無料版にはクラウド実行・スケジュール実行・API連携がありません。** 手動CSVエクスポートが必要です。
- X投稿を無許可でスクレイピングするコードは含みません。実際のX投稿収集やGitHub公開サイトへの反映は未実施。
