Renderへのデプロイ手順
GitHubにアップロード

上記3つのファイルをGitHubの新しいプライベート（非公開）リポジトリにアップロードします。

Renderを開く

Renderのダッシュボードで New + ＞ Blueprint を選択し、先ほどのGitHubリポジトリを連携します。

もしくは Web Service を選択して手動で設定しても構いません。（Language: Python, Build Command: pip install -r requirements.txt, Start Command: python main.py）

環境変数（Environment Variables）の設定

Renderの管理画面の「Environment」タブを開き、以下を追加します。

Key: DISCORD_TOKEN

Value: (Discord Developer Portalで取得したBotのトークン)

デプロイ完了！

自動的にビルドが始まり、Logged in as 1024BoT とログに表示されれば成功です！

💡 無料プランの注意点
Renderの無料Webサービスは、15分間外部からのアクセス（Webページへの閲覧）がないと自動的にスリープ状態になります。24時間完全に起こし続けたい場合は、**「UptimeRobot」**などの無料監視サービスを使い、Renderが発行したURL（https://〜.onrender.com）に5分おきにピン（アクセス）を飛ばすように設定すると、無料で常時稼働を維持できます
BOT名は必ず1024botにしてください
