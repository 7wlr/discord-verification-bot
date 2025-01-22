import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import asyncio
import json
import os

BOT_TOKEN = "put your bot token here lol"  # replace with your own bot token aswell put every intent ;)
STAFF_ROLE_ID = 1234567890  # replace with your server's staff id 
ALLOWED_USER_ID = 1234567890  # replace with your own user id
DATA_FILE = "bot_data.json"

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

verification_channel_id = None
user_verification_channels = {}
verification_message_id = None

def load_data():
    global verification_channel_id, user_verification_channels, verification_message_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                verification_channel_id = data.get("verification_channel_id")
                user_verification_channels = data.get("user_verification_channels", {})
                verification_message_id = data.get("verification_message_id")
            except json.JSONDecodeError:
                print("Error decoding bot data file.")


def save_data():
    data = {
        "verification_channel_id": verification_channel_id,
        "user_verification_channels": user_verification_channels,
        "verification_message_id": verification_message_id,
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    load_data()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    
    if verification_channel_id and verification_message_id:
         channel = bot.get_channel(verification_channel_id)
         if channel:
            try:
                verify_button = VerifyButton()
                view = View()
                view.add_item(verify_button)
                message = await channel.fetch_message(verification_message_id)
                await message.edit(view=view)
            except discord.errors.NotFound:
               print("Could not find the verification message with the saved id, ignoring")


@bot.tree.command(name="setchannel", description="Sets the channel where the verification message will be sent")
@app_commands.describe(channel_id="The ID of the channel to set")
async def set_channel(interaction: discord.Interaction, channel_id: str):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return
    global verification_channel_id
    try:
        verification_channel_id = int(channel_id)
        save_data()
        await interaction.response.send_message(
            f"Verification channel set to <#{verification_channel_id}>.", ephemeral=True
        )
    except ValueError:
        await interaction.response.send_message(
            "Invalid channel ID. Please provide a number.", ephemeral=True
        )
    except discord.errors.NotFound:
        await interaction.response.send_message(
            "Invalid channel ID. The channel provided is not a channel in this server.",
            ephemeral=True,
        )


class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="Verify", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if user.id in user_verification_channels:
            existing_channel_id = user_verification_channels[user.id]
            existing_channel = bot.get_channel(existing_channel_id)
            if existing_channel:
                await interaction.response.send_message(
                    f"You already have a pending verification channel: {existing_channel.mention}. Please use that channel.",
                    ephemeral=True,
                )
            else:
                del user_verification_channels[user.id]
                await self.create_verification_channel(interaction)
            return

        await self.create_verification_channel(interaction)

    async def create_verification_channel(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        try:
            channel = await guild.create_text_channel(f"✅-verification-{user.name}")
            
            await channel.set_permissions(user, read_messages=True, send_messages=True)
            staff_role = discord.utils.get(guild.roles, id=STAFF_ROLE_ID)
            if staff_role:
                await channel.set_permissions(staff_role, read_messages=True, send_messages=True)
            await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
            await channel.set_permissions(interaction.guild.me, read_messages=True, send_messages=True)
            allowed_user = bot.get_user(ALLOWED_USER_ID)
            if allowed_user:
                 await channel.set_permissions(allowed_user, read_messages=True, send_messages=True)
            
            user_verification_channels[user.id] = channel.id
            save_data()
            await interaction.response.send_message(
                f"Created a verification channel: {channel.mention}", ephemeral=True
            )
            await channel.send(
                f"{user.mention}, please send a message here to start your verification. || <@&{STAFF_ROLE_ID}> ||"
            )

        except discord.errors.Forbidden:
            await interaction.response.send_message(
                "I do not have the necessary permissions to create a channel or modify its permissions.",
                ephemeral=True,
            )
        except discord.errors.HTTPException:
            await interaction.response.send_message(
                "Error creating the verification channel", ephemeral=True
            )


@bot.tree.command(
    name="sendverification", description="Sends the verification message with the button."
)
async def send_verification(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    global verification_channel_id, verification_message_id
    if verification_channel_id is None:
        await interaction.response.send_message(
            "Please set a verification channel first using /setchannel.", ephemeral=True
        )
        return

    verify_button = VerifyButton()
    view = View()
    view.add_item(verify_button)
    try:
        channel = bot.get_channel(verification_channel_id)
        if channel:
            if verification_message_id:
                try:
                    old_message = await channel.fetch_message(verification_message_id)
                    await old_message.delete()  
                except discord.errors.NotFound:
                    pass  
            message = await channel.send("Please press the button below to verify!", view=view)
            verification_message_id = message.id
            save_data()
            await interaction.response.send_message(
                f"Sent verification message to <#{verification_channel_id}>!",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"The channel <#{verification_channel_id}> is invalid.", ephemeral=True
            )
    except discord.errors.NotFound:
        await interaction.response.send_message(
            f"The channel <#{verification_channel_id}> is invalid.", ephemeral=True
        )


@bot.tree.command(name="verify", description="Verifies a user and gives them the role.")
@app_commands.describe(user="The user to verify")
async def verify(interaction: discord.Interaction, user: discord.Member):
    staff_role = discord.utils.get(interaction.guild.roles, id=STAFF_ROLE_ID)
    if staff_role not in interaction.user.roles:
        await interaction.response.send_message(
            "You are not allowed to use this command.", ephemeral=True
        )
        return

    try:
        if user.id in user_verification_channels:
            channel_id = user_verification_channels[user.id]
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.delete()
            del user_verification_channels[user.id]
            save_data()

    except discord.errors.NotFound:
        await interaction.response.send_message(
            "Could not find the verification channel associated with the user.",
            ephemeral=True,
        )

    try:
        role = discord.utils.get(
            interaction.guild.roles, name="Verified")
        await user.add_roles(role)
        await interaction.response.send_message(f"Verified {user.mention}!", ephemeral=True)
    except discord.errors.Forbidden:
        await interaction.response.send_message(
            "I do not have permission to assign roles.", ephemeral=True
        )
    except discord.errors.HTTPException:
        await interaction.response.send_message("Error assigning role to user.", ephemeral=True)


bot.run(BOT_TOKEN)