import os
import random
import asyncio
from datetime import datetime
from threading import Thread
from flask import Flask
import discord
from discord import app_commands

# --- 1. Render向けWebサーバーの設定 (スリープ防止用) ---
app = Flask('')

@app.route('/')
def home():
    return "1024BoT is running!"

def run_web_server():
    # Renderは自動的にPORT環境変数を割り当てます
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. Discord Botの設定 ---
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # メンバー管理コマンドに必要
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # コマンドをDiscordに同期（グローバル同期）
        await self.tree.sync()

bot = MyBot()
start_time = datetime.now()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="/help | 1024BoT"))

# ==========================================
# ⚙️ サーバー管理コマンド (5個)
# ==========================================

@bot.tree.command(name="ban", description="指定したユーザーをサーバーから永久追放します。")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "理由なし"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🚨 {member.mention} をBANしました。理由: {reason}")

@bot.tree.command(name="kick", description="指定したユーザーをサーバーからキックします。")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "理由なし"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} をキックしました。理由: {reason}")

@bot.tree.command(name="mute", description="指定したユーザーを一定時間タイムアウト（ミュート）します。")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "理由なし"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🤫 {member.mention} を {minutes} 分間ミュートしました。理由: {reason}")

@bot.tree.command(name="clear", description="メッセージを指定件数一括削除します。")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        return await interaction.response.send_message("1〜100の範囲で指定してください。", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ {len(deleted)} 件のメッセージを削除しました。")

@bot.tree.command(name="slowmode", description="チャンネルの低速モードを設定します(0秒で解除)。")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱️ このチャンネルの低速モードを {seconds} 秒に設定しました。")

# ==========================================
# 🛠️ ユーティリティコマンド (5個)
# ==========================================

@bot.tree.command(name="userinfo", description="ユーザーの詳細情報を表示します。")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"{member.name} の情報", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="アカウント作成日", value=member.created_at.strftime('%Y/%m/%d'), inline=True)
    embed.add_field(name="サーバー参加日", value=member.joined_at.strftime('%Y/%m/%d'), inline=True)
    embed.add_field(name="最上位ロール", value=member.top_role.mention, inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="サーバーの統計情報を表示します。")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"{guild.name} の情報", color=discord.Color.green())
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="開設日", value=guild.created_at.strftime('%Y/%m/%d'), inline=True)
    embed.add_field(name="メンバー数", value=f"{guild.member_count} 人", inline=True)
    embed.add_field(name="ロール数", value=f"{len(guild.roles)}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="簡易的な2択投票を作成します。")
async def poll(interaction: discord.Interaction, question: str, choice1: str, choice2: str):
    embed = discord.Embed(title="📊 投票", description=question, color=discord.Color.orange())
    embed.add_field(name="1️⃣", value=choice1, inline=False)
    embed.add_field(name="2️⃣", value=choice2, inline=False)
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")

@bot.tree.command(name="timer", description="指定分後にメンションで通知します。")
async def timer(interaction: discord.Interaction, minutes: int, message: str = "時間です！"):
    await interaction.response.send_message(f"⏰ {minutes}分間のタイマーをセットしました。")
    await asyncio.sleep(minutes * 60)
    await interaction.channel.send(f"🔔 {interaction.user.mention} {message}")

@bot.tree.command(name="avatar", description="ユーザーのアバター画像を拡大表示します。")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"{member.name} のアバター")
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ==========================================
# 🎮 エンタメ・便利コマンド (5個)
# ==========================================

@bot.tree.command(name="dice", description="サイコロを振ります。")
async def dice(interaction: discord.Interaction, count: int = 1, sides: int = 6):
    if count > 10: return await interaction.response.send_message("ダイスは一度に10個までです。", ephemeral=True)
    results = [random.randint(1, sides) for _ in range(count)]
    await interaction.response.send_message(f"🎲 ダイス結果 ({count}d{sides}): **{results}** (合計: {sum(results)})")

@bot.tree.command(name="choice", description="複数の選択肢から1つを選びます（スペース区切り）。")
async def choice(interaction: discord.Interaction, options: str):
    opt_list = options.split()
    chosen = random.choice(opt_list)
    await interaction.response.send_message(f"🤖 厳正なる抽選の結果... **【{chosen}】** を選びました！")

@bot.tree.command(name="fortune", description="今日の運勢を占います。")
async def fortune(interaction: discord.Interaction):
    fortunes = ["大吉 🌟", "吉 ✨", "中吉 👍", "小吉 🙂", "末吉 😐", "凶 👻", "大凶 💀"]
    items = ["キーボード", "1024のデータ", "エナジードリンク", "LANケーブル", "青いペン"]
    await interaction.response.send_message(f"🔮 {interaction.user.mention} さんの今日の運勢は **{random.choice(fortunes)}** ！\nラッキーアイテム: `{random.choice(items)}`")

@bot.tree.command(name="janken", description="Botとじゃんけん勝負をします。")
async def janken(interaction: discord.Interaction, hand: str):
    bot_hands = ["グー", "チョキ", "パー"]
    if hand not in bot_hands:
        return await interaction.response.send_message("「グー」「チョキ」「パー」のいずれかを入力してください。", ephemeral=True)
    bot_hand = random.choice(bot_hands)
    if hand == bot_hand: result = "引き分け！"
    elif (hand == "グー" and bot_hand == "チョキ") or (hand == "チョキ" and bot_hand == "パー") or (hand == "パー" and bot_hand == "グー"):
        result = "あなたの勝ち！🎉"
    else: result = "私の勝ち！🤖"
    await interaction.response.send_message(f"あなた: {hand} vs Bot: {bot_hand}\n結果: **{result}**")

@bot.tree.command(name="calc", description="簡単な数式を計算します。")
async def calc(interaction: discord.Interaction, expr: str):
    try:
        # 安全な評価のため、許可する文字を制限（簡易版）
        if not all(c in "0123456789+-*/(). " for c in expr): raise ValueError()
        res = eval(expr)
        await interaction.response.send_message(f"🧮 計算結果:\n`{expr}` = **{res}**")
    except:
        await interaction.response.send_message("❌ 正しい数式を入力してください。(例: 2+3*4)", ephemeral=True)

# ==========================================
# 🤖 1024BoT 専用・お遊びコマンド (4個)
# ==========================================

@bot.tree.command(name="1024", description="Botが全力で叫びます。")
async def call_1024(interaction: discord.Interaction):
    rand = random.random()
    if rand < 0.05: text = "⚡ 1023 (バグが発生しました！！)"
    elif rand < 0.10: text = "🚀 2048 (限界突破！！)"
    else: text = "🔥 1024！！！"
    await interaction.response.send_message(text)

@bot.tree.command(name="binary", description="文字列を2進数に変換します。")
async def binary(interaction: discord.Interaction, text: str):
    bin_str = ' '.join(format(ord(c), '08b') for c in text)
    if len(bin_str) > 1900: bin_str = bin_str[:1900] + "...(長すぎるため省略)"
    await interaction.response.send_message(f"💻 「{text}」のバイナリ表現:\n`{bin_str}`")

@bot.tree.command(name="ping", description="Botの応答速度を計測します。")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! 遅延時間: **{latency}ms**")

@bot.tree.command(name="status", description="Botの稼働状態を表示します。")
async def status(interaction: discord.Interaction):
    uptime = datetime.now() - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    await interaction.response.send_message(f"📊 **1024BoT ステータス**\n🟢 稼働時間: {hours}時間{minutes}分\n📡 参加サーバー数: {len(bot.guilds)}")

# --- エラーハンドリング (権限不足などのエラーをキャッチ) ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ このコマンドを実行する権限がありません。", ephemeral=True)
    else:
        await interaction.response.send_message("❌ コマンドの実行中にエラーが発生しました。", ephemeral=True)

# --- メイン処理の起動 ---
if __name__ == "__main__":
    # Webサーバーを別スレッドで起動
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    # Discord Botの起動 (環境変数からトークンを取得)
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("エラー: 環境変数 'DISCORD_TOKEN' が設定されていません。")
