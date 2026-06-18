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
        "ping": "affiche le ping du bot.",
        "userinfo": "montre les infos d’un utilisateur.",
        "help": "liste toutes les commandes."
    })

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # ton token de bot
API_KEY = os.getenv("API_KEY")  # clé secrète API
OWNER_ID = 1067745915915481098



# Init Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ oibot. API en ligne. utilise /status pour vérifier l'état du bot. oibot."

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

@bot.tree.command(name="help", description="📖 affiche le menu d'aide")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 menu d'aide.",
        description="voici la liste des commandes disponibles :",
        color=discord.Color.blue()
    )
    embed.add_field(name="/commandes", value="montre la liste des commandes", inline=False)
    embed.add_field(name=" plus de commandes d'aides arrivent ultérieurement", value="", inline=False)

    await interaction.response.send_message(embed=embed)
    
# On sépare les commandes en pages
pages = []

# Page 1 : Commandes staff
embed1 = discord.Embed(
    title="💻 menu des commandes page 1/2",
    description="commandes réservées au staff 🛠️:",
    color=discord.Color.green()
)
embed1.add_field(name="/delete [nombre de messages]", value="supprime le nombre de messages donné", inline=False)
embed1.add_field(name="/ban [user]", value="bannir un membre, et ne pourra pas revenir dans le serveur.", inline=False)
embed1.add_field(name="/kick [user]", value="expulse un membre, mais peut revenir dans le serveur", inline=False)
embed1.add_field(name="/mute [user] [duration]", value="mettre un membre en sourdine pendant un temps donné", inline=False)
embed1.add_field(name="/unmute [user]", value="retirer le mute d'un membre", inline=False)
embed1.add_field(name="/timeout [user] [duration]", value="mettre un membre en timeout pendant une durée", inline=False)
embed1.add_field(name="/untimeout [user]", value="permet à un membre de parler après un timeout", inline=False)
embed1.add_field(name="/warn", value="avertis un membre d'un comportement inapproprié", inline=False)
embed1.add_field(name="/poll", value="crée un sondage pour le serveur", inline=False)
pages.append(embed1)

# Page 3 : Commandes pour tous les membres
embed2 = discord.Embed(
    title="💻 menu des commandes page 2/2",
    description="Commandes pour tous les membres :",
    color=discord.Color.green()
)
embed2.add_field(name="/userinfo [user]", value="obtenir les infos d'un utilisateur", inline=False)
embed2.add_field(name="/serverinfo", value="donne les infos du serveur", inline=False)
pages.append(embed2)

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
@bot.tree.command(name="commandes", description="💻 liste toutes les commandes disponibles")
async def commandes(interaction: discord.Interaction):
    await interaction.response.send_message(embed=pages[0], view=Paginator(pages))
    
    
    
# Vérifie si la personne est admin OU a le rôle STAFF 🛠️ (pour ctx commands)
def is_staff():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        staff_role = discord.utils.get(ctx.guild.roles, name="[ staff. ] ")
        if staff_role in ctx.author.roles:
            return True
        return False
    return commands.check(predicate)

# Vérifie si la personne est admin OU a le rôle STAFF 🛠️ (pour slash commands)
def is_staff_interaction(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    staff_role = discord.utils.get(interaction.guild.roles, name="[ staff. ] ")
    if staff_role in interaction.user.roles:
        return True
    return False


# -------------------------
# Commande purge
# -------------------------
@bot.tree.command(name="delete", description="supprime un nombre de messages.")
async def delete(interaction: discord.Interaction, amount: int = 3):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions nécéssaires pour cette commande.", ephemeral=True)
        return
    await interaction.response.defer()
    await interaction.channel.purge(limit=amount + 1)
    await interaction.followup.send(f"{amount} message(s) supprimé(s)!")

# -------------------------
# Commande kick
# -------------------------
@bot.tree.command(name="kick", description="expulse un membre du serveur.")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "aucune raison fournie."):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'as pas les permissions requises pour cette commande.", ephemeral=True)
        return
    try:
        await member.send(f"aïe, tu a été **expulsé** du serveur **{interaction.guild.name}** car {reason}. mais tu peut toujours revenir **en respectant les règles**!")
    except:
        pass
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} a été éxpulsé du serveur car {reason}. mais il peut tout de même revenir dans le serveur !")


# -------------------------
# Commande ban
# -------------------------
@bot.tree.command(name="ban", description="bannit un membre du serveur.")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "aucune raison fournie."):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions pour cette commande.", ephemeral=True)
        return
    try:
        await member.send(f"tu a été **banni** du serveur **{interaction.guild.name}** car {reason}")
    except:
        pass
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} a été banni du serveur car {reason}")


# -------------------------
# Commande mute
# -------------------------
@bot.tree.command(name="mute", description="mute un membre.")
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "aucune raison fournie."):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions pour cette commande.", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not role:
        role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)

    await member.add_roles(role, reason=reason)

    try:
        await member.send(f"chut! tu a été **mute** sur **{interaction.guild.name}** car {reason}")
    except:
        pass

    await interaction.response.send_message(f"{member.mention} a été mute car {reason}")


# -------------------------
# Commande unmute
# -------------------------
@bot.tree.command(name="unmute", description="autorise un membre à parler.")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions pour cette commande.", ephemeral=True)
        return
    role = discord.utils.get(interaction.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        try:
            await member.send(f"horra! tu peut désormais **parler** sur **{interaction.guild.name}** mais fais tourner sept fois ta langue dans ta bouche avant de parler.")
        except:
            pass
        await interaction.response.send_message(f" {member.mention} est désormais autorisé à parler.")
    else:
        await interaction.response.send_message("❌ ce membre n'a pas reçu de sanction concernant le chat.")


@bot.tree.command(name="shutdown", description="éteint le bot.")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ petit malin tu ne m'éteindra pas comme ça. tu n'a pas le pouvoir. mouahahaha.", ephemeral=True)
        return

    await interaction.response.send_message("au revoir monde cruel...")
    await bot.close()


# -------------------------
# Système de mate
# -------------------------
class MateView(View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="oui!", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user == self.author:
            await interaction.response.send_message("❌ c'est tentant mais tu ne peut pas devenir ton propre mate, désolés ＼(ﾟｰﾟ＼)!", ephemeral=True)
            return
        await interaction.response.send_message(
            f"🎉 {interaction.user.mention} est maintenant le mate de {self.author.mention}."
        )
        self.stop()

    @discord.ui.button(label="❌ Non", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user == self.author:
            await interaction.response.send_message("❌ pourquoi essayer de te refuser ? de toute façon tu ne peut pas!", ephemeral=True)
            return
        await interaction.response.send_message(
            f"{interaction.user.mention} a malheureusement refusé d'être le mate de {self.author.mention}."
        )
        self.stop()


@bot.tree.command(name="timeout", description="met un membre en timeout")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "aucune raison fournie."):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions pour cette commande.", ephemeral=True)
        return
    duration = timedelta(minutes=minutes)

    try:
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} a été mis en timeout pendant {minutes} minutes car {reason}")
        await member.send(f"tu a été timeout de **{interaction.guild.name}** pendant {minutes} minutes car {reason}.")

    except Exception as e:
        await interaction.response.send_message(f"❌ impossible de mettre {member.mention} en timeout : {e}")
        
        
@bot.tree.command(name="untimeout", description="retire le timeout d'un membre!")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions pour cette commande.", ephemeral=True)
        return
    try:
        await member.timeout(None)
        await interaction.response.send_message(f"{member.mention} n'est plus en timeout.")
        await member.send(f"⚠️ tu n'est plus timeout de **{interaction.guild.name}**, merci de respecter les règles afin de ne pas être sanctionné dans le futur.")

    except Exception as e:
        await interaction.response.send_message(f"❌ impossible d'enlever le timeout : {e}")

@bot.tree.command(name="warn", description="avertit un membre.")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "aucune raison fournie."):
    if not is_staff_interaction(interaction):
        await interaction.response.send_message("❌ tu n'a pas les permissions pour cette commande.", ephemeral=True)
        return
    user_id = member.id
    warns[user_id] = warns.get(user_id, 0) + 1

    await interaction.response.send_message(f"{member.mention} a reçu un avertissement ! au total il en a: {warns[user_id]})")

    # Sanctions automatiques
    if warns[user_id] == 3:
        await member.timeout(timedelta(minutes=10), reason="3 warns accumulés")
        await interaction.followup.send(f"{member.mention} a été mis en timeout 10 minutes (3 warns).")
    elif warns[user_id] == 5:
        await interaction.guild.ban(member, reason="5 warns accumulés")
        await interaction.followup.send(f"{member.mention} a été banni (5 warns).")
        
@bot.tree.command(name="ping", description="ping du bot.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"tic tac {latency}ms")

@bot.tree.command(name="userinfo", description="affiche les infos d'un utilisateur.")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"Infos sur {member}", color=discord.Color.green())
    embed.add_field(name="id", value=member.id, inline=False)
    embed.add_field(name="pseudo", value=member.display_name, inline=False)
    embed.add_field(name="compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="à rejoint le serveur le", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="rôles", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]), inline=False)
    embed.add_field(name="compte oifeel.", value="_non implémenté pour le moment_", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="affiche les infos du serveur.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"infos du serveur : {guild.name}", color=discord.Color.purple())
    embed.add_field(name="id", value=guild.id, inline=False)
    embed.add_field(name="membres", value=guild.member_count, inline=False)
    embed.add_field(name="propriétaire", value=guild.owner, inline=False)
    embed.add_field(name="créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="nombre de rôles", value=len(guild.roles), inline=False)
    embed.add_field(name="nombre de bg dans le serveur", value=guild.member_count, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="crée un sondage")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="sondage", description=question, color=discord.Color.gold())
    poll_message = await interaction.response.send_message(embed=embed)
    await poll_message.add_reaction("✅")
    await poll_message.add_reaction("❌")
    
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Membre")
    if role:
        await member.add_roles(role)
        try:
            await member.send(f"bienvenue sur **{member.guild.name}**! tu as reçu automatiquement le rôle **{role.name}**.")
        except:
            pass
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="vérification")
    if channel:
        msg = await channel.send(f"👋 bienvenue {member.mention}! pour accéder au serveur, clique sur ✅.")
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
            await member.kick(reason="échec de la vérification captcha")
async def send_log(guild, message):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        await log_channel.send(message)

@bot.event
async def on_member_ban(guild, user):
    await send_log(guild, f"{user} a été banni.")

@bot.event
async def on_member_remove(member):
    await send_log(member.guild, f"{member} a quitté ou a été expulsé du serveur.")

@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        await send_log(message.guild, f"message supprimé de {message.author}: {message.content}")


# ------------------------- 
# Quand le bot est prêt 
# ------------------------- 
@bot.event 
async def on_ready(): 
    latency = round(bot.latency * 1000) 
    print(f"oibot. connecté. id: {bot.user}") 
    print(f"ping: {latency}ms") 
    print(f"oibot.")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commandes synchronisées !")
    except Exception as e:
        print(f"❌ erreur lors de la synchronisation des commandes : {e}")
    
# ------------------------- 
# Lancer le bot 
# ------------------------- 
if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)