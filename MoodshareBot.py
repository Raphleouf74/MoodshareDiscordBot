import os
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from flask import Flask, jsonify, request, abort
from threading import Thread


API_KEY = os.getenv("API_KEY", "2JX9F7bN1kL0aYQp")  # déjà mis
app = Flask(__name__)

def check_key():
    key = request.args.get("key")
    if key != API_KEY:
        abort(403)

@app.route("/status")
def status():
    check_key()
    return jsonify({
        "status": "online" if bot.is_ready() else "starting",
        "bot": str(bot.user) if bot.user else "starting...",
        "servers": len(bot.guilds),
        "users": sum(g.member_count for g in bot.guilds)
    })

@app.route("/servers")
def servers():
    check_key()
    return jsonify([
        {"id": str(g.id), "name": g.name, "members": g.member_count}
        for g in bot.guilds
    ])
    
@app.route("/commands")
def list_commands():
    check_key()
    return jsonify({
        "ping": "Affiche le ping du bot",
        "userinfo": "Montre les infos d’un utilisateur",
        "help": "Liste toutes les commandes"
    })

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # ton token de bot
API_KEY = os.getenv("API_KEY")  # clé secrète API
OWNER_ID = 1067745915915481098



# Init Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ SmartBot API est en ligne. Utilise /status pour vérifier l'état du bot. Bienvenue sur MoodshareBot ⃞⃝!"

@app.route("/status")
def status():
    key = request.args.get("key")
    if key != API_KEY:
        abort(403)  # accès refusé

    return jsonify({
        "status": "running",
        "bot": str(bot.user) if bot.user else "starting...",
        "servers": len(bot.guilds),
        "users": sum(g.member_count for g in bot.guilds)
    })

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render fournit PORT automatiquement
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()




# -------------------------
# Configuration des intents
# -------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")
warns = {}

@bot.tree.command(name="help", description="📖 Affiche le menu d'aide")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Menu d'aide",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.blue()
    )
    embed.add_field(name="/commandes", value="Montre la liste des commandes", inline=False)
    embed.add_field(name=" Plus de commandes d'aides ultérieurement", value="", inline=False)

    await interaction.response.send_message(embed=embed)
    
# On sépare les commandes en pages
pages = []

# Page 1 : Commandes staff
embed1 = discord.Embed(
    title="💻 Menu des commandes (Page 1/3)",
    description="Commandes réservées au staff 🛠️:",
    color=discord.Color.green()
)
embed1.add_field(name="/delete [nombre de messages]", value="Supprime le nombre de messages donné", inline=False)
embed1.add_field(name="/ban [user]", value="Bannir un membre, il ne pourra pas revenir dans le serveur.", inline=False)
embed1.add_field(name="/kick [user]", value="Expulser un membre, mais il peut revenir dans le serveur", inline=False)
embed1.add_field(name="/mute [user] [duration]", value="Mettre un membre en sourdine pendant un temps donné", inline=False)
embed1.add_field(name="/unmute [user]", value="Retirer l'action mute d'un membre", inline=False)
embed1.add_field(name="/timeout [user] [duration]", value="Mettre un membre en timeout pendant une durée", inline=False)
embed1.add_field(name="/untimeout [user]", value="Permet à un membre de parler après un timeout", inline=False)
embed1.add_field(name="/warn", value="Avertis un membre d'un comportement inapproprié", inline=False)
embed1.add_field(name="/poll", value="Crée un sondage pour le serveur", inline=False)
pages.append(embed1)

# Page 2 : Commandes administrateur
embed2 = discord.Embed(
    title="💻 Menu des commandes (Page 2/3)",
    description="Commandes réservées à l'administrateur du serveur 💻",
    color=discord.Color.green()
)
embed2.add_field(name="/shutdown", value="Éteins le bot", inline=False)
embed2.add_field(name="/ping", value="Annonce le ping du bot", inline=False)
pages.append(embed2)

# Page 3 : Commandes pour tous les membres
embed3 = discord.Embed(
    title="💻 Menu des commandes (Page 3/3)",
    description="Commandes pour tous les membres :",
    color=discord.Color.green()
)
embed3.add_field(name="/userinfo [user]", value="Obtenir les infos d'un utilisateur", inline=False)
embed3.add_field(name="/serverinfo", value="Donne les infos du serveur", inline=False)
pages.append(embed3)

# Classe de pagination
class Paginator(View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0
        self.prev_button.disabled = True
        if len(pages) == 1:
            self.next_button.disabled = True

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current -= 1
        if self.current == 0:
            button.disabled = True
        self.next_button.disabled = False
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current += 1
        if self.current == len(self.pages) - 1:
            button.disabled = True
        self.prev_button.disabled = False
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

# Commande pour afficher les embeds paginés
@bot.tree.command(name="commandes", description="💻 Liste toutes les commandes disponibles")
async def commandes(interaction: discord.Interaction):
    await interaction.response.send_message(embed=pages[0], view=Paginator(pages))
    
    
    
# Vérifie si la personne est admin OU a le rôle STAFF 🛠️ (pour ctx commands)
def is_staff():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        staff_role = discord.utils.get(ctx.guild.roles, name="[ 🛠️ Staff ] ")
        if staff_role in ctx.author.roles:
            return True
        return False
    return commands.check(predicate)

# Vérifie si la personne est admin OU a le rôle STAFF 🛠️ (pour slash commands)
def is_staff_interaction(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    staff_role = discord.utils.get(interaction.guild.roles, name="[ 🛠️ Staff ] ")
    if staff_role in interaction.user.roles:
        return True
    return False


# -------------------------
# Commande purge
# -------------------------
@bot.tree.command(name="delete", description="🧹 Supprime un nombre de messages")
async def delete(interaction: discord.Interaction, amount: int = 3):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    await interaction.response.defer()
    await interaction.channel.purge(limit=amount + 1)
    await interaction.followup.send(f"🧹 {amount} message(s) supprimé(s) avec succès !")

# -------------------------
# Commande kick
# -------------------------
@bot.tree.command(name="kick", description="👢 Expulse un membre du serveur")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    try:
        await member.send(f"👢 Vous avez été **expulsé** du serveur **{interaction.guild.name}** car {reason}. Mais revenir dans le serveur est toujours possible !")
    except:
        pass
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} a été éxpulsé du serveur car {reason}. Mais ils peuvent tout de même revenir dans le serveur !")


# -------------------------
# Commande ban
# -------------------------
@bot.tree.command(name="ban", description="🔨 Bannit un membre du serveur")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    try:
        await member.send(f"🔨 Vous avez été **banni** du serveur **{interaction.guild.name}** car {reason}")
    except:
        pass
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member.mention} a été banni du serveur car {reason}")


# -------------------------
# Commande mute
# -------------------------
@bot.tree.command(name="mute", description="🔇 Rend un membre muet")
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not role:
        role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)

    await member.add_roles(role, reason=reason)

    try:
        await member.send(f"🔇 Vous avez été **Mis en silencieux** sur **{interaction.guild.name}** car {reason}")
    except:
        pass

    await interaction.response.send_message(f"🔇 {member.mention} a été mis en silencieux car {reason}")


# -------------------------
# Commande unmute
# -------------------------
@bot.tree.command(name="unmute", description="🔊 Autorise un membre à parler")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        try:
            await member.send(f"🔊 Vous pouvez désormais **parler** sur **{interaction.guild.name}**.")
        except:
            pass
        await interaction.response.send_message(f"🔊 {member.mention} est désormais autorisé à parler ✅")
    else:
        await interaction.response.send_message("❌ Ce membre n'a pas reçu de sanction concernant le chat.")


@bot.tree.command(name="shutdown", description="🛑 Eteint le bot (owner only)")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Impossible d'éffectuer cette commande. Vous ne disposez pas des droits pour le faire.", ephemeral=True)
        return

    await interaction.response.send_message("🛑 Le bot s'éteint...")
    await bot.close()


# -------------------------
# Système de mate
# -------------------------
class MateView(View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="✅ Oui", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user == self.author:
            await interaction.response.send_message("❌ C'est tentant mais tu ne peut pas devenir ton propre mate, c'est dommage !", ephemeral=True)
            return
        await interaction.response.send_message(
            f"🎉 {interaction.user.mention} est maintenant le mate de {self.author.mention} ❤️"
        )
        self.stop()

    @discord.ui.button(label="❌ Non", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user == self.author:
            await interaction.response.send_message("❌ Pourquoi essayer de te refuser ? De toute façon tu ne peut pas !", ephemeral=True)
            return
        await interaction.response.send_message(
            f"{interaction.user.mention} a malheureusement refusé d'être le mate de {self.author.mention} 😢"
        )
        self.stop()


@bot.tree.command(name="timeout", description="⏳ Met un membre en timeout")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Aucune raison fournie"):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    duration = timedelta(minutes=minutes)

    try:
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} a été mis en timeout pendant {minutes} minutes car {reason}")
        await member.send(f"⚠️ Vous avez été timeout de **{interaction.guild.name}**pendant {minutes} minutes car {reason}.")

    except Exception as e:
        await interaction.response.send_message(f"❌ Impossible de mettre {member.mention} en timeout : {e}")
        
        
@bot.tree.command(name="untimeout", description="✅ Retire le timeout d'un membre")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    try:
        await member.timeout(None)
        await interaction.response.send_message(f"✅ {member.mention} n'est plus en timeout.")
        await member.send(f"⚠️ Vous n'êtes plus timeout de **{interaction.guild.name}**, merci de respecter les règles afin de ne pas être sanctionné dans le futur.")

    except Exception as e:
        await interaction.response.send_message(f"❌ Impossible d'enlever le timeout : {e}")

@bot.tree.command(name="warn", description="⚠️ Avertit un membre")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas les permissions pour cette commande.", ephemeral=True)
        return
    user_id = member.id
    warns[user_id] = warns.get(user_id, 0) + 1

    await interaction.response.send_message(f"⚠️ {member.mention} a reçu un avertissement ! (Total: {warns[user_id]})")

    # Sanctions automatiques
    if warns[user_id] == 3:
        await member.timeout(timedelta(minutes=10), reason="3 warns accumulés")
        await interaction.followup.send(f"⏳ {member.mention} a été mis en timeout 10 minutes (3 warns).")
    elif warns[user_id] == 5:
        await interaction.guild.ban(member, reason="5 warns accumulés")
        await interaction.followup.send(f"🔨 {member.mention} a été banni (5 warns).")
        
@bot.tree.command(name="ping", description="🏓 Affiche le ping du bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Ping du bot: {latency}ms")

@bot.tree.command(name="userinfo", description="👤 Affiche les infos d'un utilisateur")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"Infos sur {member}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Pseudo", value=member.display_name, inline=False)
    embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="A rejoint le serveur le", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Rôles", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="📊 Affiche les infos du serveur")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Infos du serveur : {guild.name}", color=discord.Color.purple())
    embed.add_field(name="ID", value=guild.id, inline=False)
    embed.add_field(name="Membres", value=guild.member_count, inline=False)
    embed.add_field(name="Propriétaire", value=guild.owner, inline=False)
    embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Nombre de rôles", value=len(guild.roles), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="📊 Crée un sondage")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Sondage", description=question, color=discord.Color.gold())
    poll_message = await interaction.response.send_message(embed=embed)
    await poll_message.add_reaction("✅")
    await poll_message.add_reaction("❌")
    
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Membre")
    if role:
        await member.add_roles(role)
        try:
            await member.send(f"👋 Bienvenue sur **{member.guild.name}** ! Tu as reçu automatiquement le rôle **{role.name}**.")
        except:
            pass
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="vérification")
    if channel:
        msg = await channel.send(f"👋 Bienvenue {member.mention} ! Pour accéder au serveur, clique sur ✅.")
        await msg.add_reaction("✅")

        def check(reaction, user):
            return user == member and str(reaction.emoji) == "✅" and reaction.message.id == msg.id

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=300.0, check=check)  # 5 min
            role = discord.utils.get(member.guild.roles, name="Membre")
            if role:
                await member.add_roles(role)
                await channel.send(f"✅ {member.mention} a passé la vérification !")
        except:
            await member.kick(reason="Échec de la vérification captcha")
async def send_log(guild, message):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        await log_channel.send(message)

@bot.event
async def on_member_ban(guild, user):
    await send_log(guild, f"🔨 {user} a été banni.")

@bot.event
async def on_member_remove(member):
    await send_log(member.guild, f"👢 {member} a quitté ou a été expulsé.")

@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        await send_log(message.guild, f"🗑️ Message supprimé de {message.author}: {message.content}")


# ------------------------- 
# Quand le bot est prêt 
# ------------------------- 
@bot.event 
async def on_ready(): 
    latency = round(bot.latency * 1000) 
    print(f"✅ Bot connecté. ID: {bot.user}") 
    print(f" Ping: {latency}ms") 
    print(f"Bienvenue sur MoodshareBot ⃞⃝!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes slash synchronisées !")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes : {e}")
    
# ------------------------- 
# Lancer le bot 
# ------------------------- 
if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)