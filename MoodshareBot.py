import os
import subprocess
from datetime import timedelta

import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from flask import Flask, jsonify, request, abort
from threading import Thread



import subprocess
print(subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout)



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

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") # ton token de bot
API_KEY = os.getenv("API_KEY")  # clé secrète API
OWNER_ID = 1067745915915481098


# Init bot Discord
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

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
bot = commands.Bot(command_prefix="+", intents=intents)
bot.remove_command("help")
warns = {}

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📖 Menu d’aide",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.blue()
    )
    embed.add_field(name="+commandes", value="Montre la liste des commandes", inline=False)
    embed.add_field(name=" Plus de commandes d'aides ultérieurement", value="", inline=False)

    await ctx.send(embed=embed)
    
# On sépare les commandes en pages
pages = []

# Page 1 : Commandes staff
embed1 = discord.Embed(
    title="💻 Menu des commandes (Page 1/3)",
    description="Commandes réservées au staff 🛠️:",
    color=discord.Color.green()
)
embed1.add_field(name="+delete [nombre de messages]", value="Supprime le nombre de messages donné", inline=False)
embed1.add_field(name="+ban [user]", value="Bannir un membre, il ne pourra pas revenir dans le serveur.", inline=False)
embed1.add_field(name="+kick [user]", value="Expulser un membre, mais il peut revenir dans le serveur", inline=False)
embed1.add_field(name="+mute [user] [duration]", value="Mettre un membre en sourdine pendant un temps donné", inline=False)
embed1.add_field(name="+unmute [user]", value="Retirer l'action mute d'un membre", inline=False)
embed1.add_field(name="+timeout [user] [duration]", value="Mettre un membre en timeout pendant une durée", inline=False)
embed1.add_field(name="+untimeout [user]", value="Permet à un membre de parler après un timeout", inline=False)
embed1.add_field(name="+warn", value="Avertis un membre d'un comportement inapproprié", inline=False)
embed1.add_field(name="+poll", value="Crée un sondage pour le serveur", inline=False)
pages.append(embed1)

# Page 2 : Commandes administrateur
embed2 = discord.Embed(
    title="💻 Menu des commandes (Page 2/3)",
    description="Commandes réservées à l'administrateur du serveur 💻",
    color=discord.Color.green()
)
embed2.add_field(name="+shutdown", value="Éteins le bot", inline=False)
embed2.add_field(name="+givecoins [user] [amount]", value="Donne de l'argent à un user sans retrait d'argent.", inline=False)
embed2.add_field(name="+ping", value="Annonce le ping du bot", inline=False)
embed2.add_field(name="+start_tournoi", value="Lance le tournoi du jour", inline=False)
embed2.add_field(name="+end_tournoi", value="Termine le tournoi du jour", inline=False)
embed2.add_field(name="COMMANDES POUR LES TOURNOIS:", value="",inline=False)
embed2.add_field(name="+game [mode]", value="Choisit un jeu pour le tournoi (pfc, quiz, pendu ou random)", inline=False)
embed2.add_field(name="+pick", value="Tire au hasard deux joueurs pour un match", inline=False)
embed2.add_field(name="+victoire [user]", value="Déclare une victoire à un joueur (+3 points)", inline=False)
embed2.add_field(name="+defaite [user]", value="Déclare une défaite à un joueur (0 point)", inline=False)
embed2.add_field(name="+egalite [user1] [user2]", value="Déclare une égalité entre deux joueurs (+1 point chacun)", inline=False)
embed2.add_field(name="+panel", value="Affiche le panel du Chef de Tournoi", inline=False)
embed2.add_field(name="+addpoints [user] [points]", value="Ajoute des points à un user", inline=False)
pages.append(embed2)

# Page 3 : Commandes pour tous les membres
embed3 = discord.Embed(
    title="💻 Menu des commandes (Page 3/3)",
    description="Commandes pour tous les membres :",
    color=discord.Color.green()
)
embed3.add_field(name="+mate", value="Envoie une demande de partenaire de jeu aux autres membres", inline=False)
embed3.add_field(name="+userinfo [user]", value="Obtenir les infos d'un utilisateur", inline=False)
embed3.add_field(name="+serverinfo", value="Donne les infos du serveur", inline=False)
embed3.add_field(name="+remind [time]", value="Crée un rappel pour soi dans un temps donné", inline=False)
embed3.add_field(name="+pfc [pierre/feuille/ciseaux]", value="Joue au jeu Pierre-Feuille-Ciseaux contre le bot", inline=False)
embed3.add_field(name="+pendu", value="Démarre une partie de pendu", inline=False)
embed3.add_field(name="+lettre", value="Démarre un quiz", inline=False)
embed3.add_field(name="+quiz", value="Démarre un quiz", inline=False)
embed3.add_field(name="DURANT LES TOURNOIS:", value="", inline=False)
embed3.add_field(name="+join_tournoi", value="Rejoindre le tournoi du jour", inline=False)
embed3.add_field(name="+classement_jour", value="Afficher le classement du jour", inline=False)
embed3.add_field(name="+wiki [sujet]", value="Recherche un sujet sur Wikipédia et vous donne la description", inline=False)
embed3.add_field(name="+trad", value="Choisissez parmi les langues discponibles et traduisez ce que vous voulez", inline=False)
embed3.add_field(name="+money", value="Affiche votre solde de coins", inline=False)
embed3.add_field(name="+daily", value="Réclamez votre récompense quotidienne de coins", inline=False)
embed3.add_field(name="+pay [user] [amount]", value="Payez un autre utilisateur avec vos coins", inline=False)
embed3.add_field(name="+shop", value="Affiche la boutique où vous pouvez acheter des rôles avec vos coins", inline=False)
embed3.add_field(name="+buy [role]", value="Achetez un rôle dans la boutique avec vos coins", inline=False)
embed3.add_field(name="+coinflip [amount] [pile/face]", value="Jouez à pile ou face pour doubler vos coins", inline=False)
embed3.add_field(name="+slots [amount]", value="Jouez aux machines à sous pour gagner des coins", inline=False)
embed3.add_field(name="+blind", value="Participez à un blindtest (UNIQUEMENT DANS DES SALONS VOCAUX)", inline=False)
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
@bot.command()
async def commandes(ctx):
    await ctx.send(embed=pages[0], view=Paginator(pages))
    
    
    
# Vérifie si la personne est admin OU a le rôle STAFF 🛠️
def is_staff():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        staff_role = discord.utils.get(ctx.guild.roles, name="[ 🛠️ Staff ] ")
        if staff_role in ctx.author.roles:
            return True
        return False
    return commands.check(predicate)


# -------------------------
# Commande purge
# -------------------------
@bot.command()
@is_staff()
async def delete(ctx, amount: int = 3):
    await ctx.channel.purge(limit=amount + 1)  # +1 pour aussi supprimer la commande de l'utilisateur
    confirmation = await ctx.send(f"🧹 {amount} message(s) supprimé(s) avec succès !")
    await confirmation.delete(delay=5.0)  # Supprimer l’embed après 5 sec

# -------------------------
# Commande kick
# -------------------------
@bot.command()
@is_staff()
async def kick(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    try:
        await member.send(f"👢 Vous avez été **expulsé** du serveur **{ctx.guild.name}** car {reason}. Mais revenir dans le serveur est toujours possible !")
    except:
        pass
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} a été éxpulsé du serveur car {reason}. Mais ils peuvent tout de même revenir dans le serveur !")


# -------------------------
# Commande ban
# -------------------------
@bot.command()
@is_staff()
async def ban(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    try:
        await member.send(f"🔨 Vous avez été **banni** du serveur **{ctx.guild.name}** car {reason}")
    except:
        pass
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} a été banni du serveur car {reason}")


# -------------------------
# Commande mute
# -------------------------
@bot.command()
@is_staff()
async def mute(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        # Création du rôle si inexistant
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)

    await member.add_roles(role, reason=reason)

    try:
        await member.send(f"🔇 Vous avez été **Mis en silencieux** sur **{ctx.guild.name}** car {reason}")
    except:
        pass

    await ctx.send(f"🔇 {member.mention} a été mis en silencieux car {reason}")


# -------------------------
# Commande unmute
# -------------------------
@bot.command()
@is_staff()
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        try:
            await member.send(f"🔊 Vous pouvez désormais **parler** sur **{ctx.guild.name}**.")
        except:
            pass
        await ctx.send(f"🔊 {member.mention} est désormais autorisé à parler ✅")
    else:
        await ctx.send("❌ Ce membre n'a pas reçu de sanction concernant le chat.")


@bot.command()
async def shutdown(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Impossible d'éffectuer cette commande. Vous ne disposez pas des droits pour le faire.")
        return


    await ctx.send("🛑 Le bot s'éteint...")
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


@bot.command()
@is_staff()
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="Aucune raison fournie"):
    duration = timedelta(minutes=minutes)

    try:
        await member.timeout(duration, reason=reason)
        await ctx.send(f"⏳ {member.mention} a été mis en timeout pendant {minutes} minutes car {reason}")
        await member.send(f"⚠️ Vous avez été timeout de **{ctx.guild.name}**pendant {minutes} minutes car {reason}.")

    except Exception as e:
        await ctx.send(f"❌ Impossible de mettre {member.mention} en timeout : {e}")
        
        
@bot.command()
@is_staff()
async def untimeout(ctx, member: discord.Member):
    try:
        await member.timeout(None)  # Enlève le timeout
        await ctx.send(f"✅ {member.mention} n'est plus en timeout.")
        await member.send(f"⚠️ Vous n'êtes plus timeout de **{ctx.guild.name}**, merci de respecter les règles afin de ne pas être sanctionné dans le futur.")

    except Exception as e:
        await ctx.send(f"❌ Impossible d'enlever le timeout : {e}")

@bot.command()
@is_staff()
async def warn(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    user_id = member.id
    warns[user_id] = warns.get(user_id, 0) + 1

    await ctx.send(f"⚠️ {member.mention} a reçu un avertissement ! (Total: {warns[user_id]})")

    # Sanctions automatiques
    if warns[user_id] == 3:
        await member.timeout(timedelta(minutes=10), reason="3 warns accumulés")
        await ctx.send(f"⏳ {member.mention} a été mis en timeout 10 minutes (3 warns).")
    elif warns[user_id] == 5:
        await ctx.guild.ban(member, reason="5 warns accumulés")
        await ctx.send(f"🔨 {member.mention} a été banni (5 warns).")
        
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)  # en ms
    await ctx.send(f"Ping du bot: {latency}ms")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"Infos sur {member}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Pseudo", value=member.display_name, inline=False)
    embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="A rejoint le serveur le", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Rôles", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 Infos du serveur : {guild.name}", color=discord.Color.purple())
    embed.add_field(name="ID", value=guild.id, inline=False)
    embed.add_field(name="Membres", value=guild.member_count, inline=False)
    embed.add_field(name="Propriétaire", value=guild.owner, inline=False)
    embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Nombre de rôles", value=len(guild.roles), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def poll(ctx, *, question: str):
    embed = discord.Embed(title="📊 Sondage", description=question, color=discord.Color.gold())
    poll_message = await ctx.send(embed=embed)
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
    
# ------------------------- 
# Lancer le bot 
# ------------------------- 
if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)