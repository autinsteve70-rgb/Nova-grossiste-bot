import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 10000))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CATEGORIE_COMMANDES = "📦 Commande"


# =========================
# SERVEUR POUR RAILWAY
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Nova Grossiste Bot OK")

    def log_message(self, format, *args):
        pass


def start_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()


# =========================
# BOUTONS COMMANDES
# =========================

class CommandeButtons(discord.ui.View):

    def __init__(self, membre_id):
        super().__init__(timeout=None)
        self.membre_id = membre_id

    async def interaction_check(self, interaction):
        # Seuls les membres pouvant gérer les salons peuvent utiliser les boutons
        if interaction.user.guild_permissions.manage_channels:
            return True

        await interaction.response.send_message(
            "❌ Tu n'as pas la permission de gérer cette commande.",
            ephemeral=True
        )
        return False

    @discord.ui.button(
        label="Accepter",
        style=discord.ButtonStyle.success,
        emoji="🟢"
    )
    async def accepter(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        membre = interaction.guild.get_member(self.membre_id)

        if membre:
            try:
                await membre.send(
                    "📦 **NOVA GROSSISTE**\n\n"
                    "✅ **Votre commande a été acceptée !**\n\n"
                    "Nous allons préparer votre commande."
                )
            except discord.Forbidden:
                pass

        await interaction.response.send_message(
            "🟢 **Commande acceptée.** Le client a été informé par DM."
        )

        button.disabled = True

        for item in self.children:
            item.disabled = True

        await interaction.message.edit(view=self)

    @discord.ui.button(
        label="Refuser",
        style=discord.ButtonStyle.danger,
        emoji="🔴"
    )
    async def refuser(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        membre = interaction.guild.get_member(self.membre_id)

        if membre:
            try:
                await membre.send(
                    "📦 **NOVA GROSSISTE**\n\n"
                    "❌ **Votre commande a été refusée.**\n\n"
                    "Pour plus d'informations, veuillez contacter le grossiste."
                )
            except discord.Forbidden:
                pass

        await interaction.response.send_message(
            "🔴 **Commande refusée.** Le client a été informé par DM."
        )

        for item in self.children:
            item.disabled = True

        await interaction.message.edit(view=self)


# =========================
# BOT
# =========================

@bot.event
async def on_ready():
    print(f"Bot connecté : {bot.user}")


@bot.command()
async def commande(ctx, membre: discord.Member, numero: str, *, details: str):

    categorie = discord.utils.get(
        ctx.guild.categories,
        name=CATEGORIE_COMMANDES
    )

    if not categorie:
        await ctx.send(
            "❌ La catégorie **📦 Commande** est introuvable."
        )
        return

    nom_client = membre.display_name.lower().replace(" ", "-")

    salon = await ctx.guild.create_text_channel(
        f"commande-{numero}-{nom_client}",
        category=categorie
    )

    message = (
        f"📦 **NOUVELLE COMMANDE #{numero}**\n\n"
        f"👤 **Client :** {membre.mention}\n\n"
        f"📋 **Commande :**\n{details}\n\n"
        "⏳ **Statut :** Nouvelle commande"
    )

    view = CommandeButtons(membre.id)

    await salon.send(
        message,
        view=view
    )

    await ctx.send(
        f"✅ Commande **#{numero}** créée dans {salon.mention}."
    )


# =========================
# DM LIBRE
# =========================

@bot.command()
async def dm(ctx, membre: discord.Member, *, message: str):

    try:
        await membre.send(
            f"📦 **NOVA GROSSISTE**\n\n{message}"
        )

        await ctx.send(
            f"✅ Message envoyé en DM à {membre.mention}."
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Impossible d'envoyer un DM à ce membre."
        )


# =========================
# LANCEMENT
# =========================

threading.Thread(
    target=start_web_server,
    daemon=True
).start()

bot.run(TOKEN)
