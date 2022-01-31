from db.config import TOKEN
import discord
from discord.ext import commands
from discord.ui import Button, View
from discord.enums import ButtonStyle
# from discord_components import DiscordComponents, Button, ButtonStyle
import asyncio
import json
import random
import time
from datetime import datetime

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
client = commands.Bot(command_prefix='!', intents=intents)

with open(r'db\admin.json', 'r', encoding='utf-8') as base:
    ADMIN_DB = json.load(base)
with open(r'db\users.json', 'r', encoding='utf-8') as base:
    USERS = json.load(base)
embed_colors = [0xFF0000, 0xFF8000, 0xFFFF00, 0x00FF00,
                0x00FFFF, 0x0000FF, 0xFF00FF]  # F invisible
tdict = {}
texts_to_channels = {
    "932731504654712842": """**Привет :person_raising_hand:! Ты попал в канал поддержки Discord сервера midnight.**
**Опишите вашу проблему и мы постараемся вам помочь!**

*Напоминание: за неадекватное поведение или бессмысленное обращение ваш аккаунт может быть заблокирован*

 > :envelope:  - количество обращений за всё время: `{tickets_amount}`
 > :warning:  - не обработанных нашей поддержкой: `{tickets_unprocessed}`
 > :mag:  - на рассмотрении: `{tickets_in_process}`
 > :no_entry:  - закрытых: `{tickets_closed}`"""
}


# TODO LOGS!!!!!


def admin_db_renew(db_name):
    global ADMIN_DB
    with open(r'db\admin.json', 'w', encoding='utf-8') as base:
        base.write(json.dumps(db_name, ensure_ascii=False,
                   sort_keys=True, indent=2))
    with open(r'db\admin.json', 'r', encoding='utf-8') as base:
        ADMIN_DB = json.load(base)


def users_db_renew(db_name):
    global USERS
    with open(r'db\users.json', 'w', encoding='utf-8') as base:
        base.write(json.dumps(db_name, ensure_ascii=False,
                   sort_keys=True, indent=2))
    with open(r'db\users.json', 'r', encoding='utf-8') as base:
        USERS = json.load(base)


admin_db_renew(ADMIN_DB)


def timef(v_online):
    v_online_arr = []
    if v_online >= 86400:
        v_online_arr.append(f"{int(v_online / 86400)}д ")
        v_online -= 86400 * int(v_online / 86400)
    if 3600 <= v_online <= 86400:
        v_online_arr.append(f"{int(v_online / 3600)}ч ")
        v_online -= 3600 * int(v_online / 3600)
    if 60 <= v_online <= 3600:
        v_online_arr.append(f"{int(v_online / 60)}м ")
        v_online -= 60 * int(v_online / 60)
    if 0 <= v_online <= 59:
        v_online_arr.append(f"{str(v_online)}с")
    v_online = ""
    for i in v_online_arr:
        v_online += i + " "
    return v_online


@client.event
async def on_ready():
    # DiscordComponents(client)
    print("ready")


@client.command()
@commands.has_permissions()
async def ban(ctx, member: discord.Member, time=None, *, reason=None):
    print(member)
    print(time)
    print(reason)
    global ADMIN_DB
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

    def converttime(time):
        try:
            return int(time[:-1]) * time_convert[time[-1]]
        except:
            return time

    if member == ctx.message.author or member is None:
        await ctx.send("нельзя забанить себя, чел...")
        return
    if reason is None:
        reason = "пидорас"

    await member.ban(reason=reason)

    if member.id not in ADMIN_DB["bans"].keys():
        ADMIN_DB["bans"][member.id] = {
            str(member.id): {"moderator": "", "time_for": 0, "reason": ""}}
    ADMIN_DB["bans"][member.id]["moderator"] = ctx.message.author.name + \
        "#" + ctx.message.author.discriminator
    ADMIN_DB["bans"][member.id]["time_for"] = converttime(time)
    ADMIN_DB["bans"][member.id]["reason"] = reason
    embed = discord.Embed(title="Информация о блокировке", colour=0xff0000)
    embed.set_author(icon_url=ctx.guild.icon_url,
                     name=f"{ctx.guild.name} team")
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Заблокирован", value=member.mention, inline=False)
    embed.add_field(name="Заблокировал",
                    value=ctx.message.author.mention, inline=False)
    if time is not None or int(time) != 0:
        embed.add_field(name="Время", value=time, inline=False)
    embed.add_field(name="Причина", value=reason, inline=False)
    b = client.get_user(893937565609119774)
    embed.set_footer(icon_url=b.avatar_url,
                     text="Команда по безопастности Discrod Сервера.")
    await ctx.send(embed=embed)
    admin_db_renew(ADMIN_DB)
    if time:
        await asyncio.sleep(converttime(time))
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                del ADMIN_DB["bans"][str(member.id)]
                admin_db_renew(ADMIN_DB)
                return
            else:
                print("иди на хуй")

    if member is None:
        await ctx.send("u cant ban urself")
        return


@client.command()
@commands.has_permissions()
async def unban(ctx, *, member):
    global ADMIN_DB
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            del ADMIN_DB["bans"][str(user.id)]
            embed = discord.Embed(
                title="Информация о разблокировке", colour=0x00ff00)
            embed.set_author(
                icon_url=ctx.guild.icon_url,
                name=f"{ctx.guild.name} team")
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Разблокирован", value=user, inline=False)
            embed.add_field(name="Разблокировал",
                            value=ctx.message.author.mention, inline=False)
            b = client.get_user(893937565609119774)
            embed.set_footer(icon_url=b.avatar_url,
                             text="Команда по безопастности Discrod Сервера.")
            await ctx.send(embed=embed)
            admin_db_renew(ADMIN_DB)
            return
        else:
            print("иди на хуй")

    if member == ctx.author:
        await ctx.send("нельзя разбанить себя, чел...")
        return


@client.command()
@commands.has_permissions()
async def warn(ctx, member: discord.Member, *, reason=None):
    global ADMIN_DB
    if str(member.id) not in ADMIN_DB["warns"].keys():
        ADMIN_DB["warns"][str(member.id)] = []
    if reason is None:
        reason = "пидорас"
    try:
        ADMIN_DB["warns"][str(member.id)].append({"moderator": ctx.message.author.id, "reason": reason,
                                                  "date": str(datetime.now().date().strftime("%d %b %Y"))})
        embed = discord.Embed(
            title="Информация предупреждении", colour=0xff0000)
        embed.set_author(
            icon_url=ctx.guild.icon_url,
            name=f"{ctx.guild.name} team")
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Предупреждение выдано",
                        value=member.mention, inline=False)
        embed.add_field(name="Предупреждение выдал",
                        value=ctx.message.author.mention, inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        b = client.get_user(893937565609119774)
        embed.set_footer(icon_url=b.avatar_url,
                         text="Команда по безопастности Discrod Сервера.")
        await ctx.send(embed=embed)
        admin_db_renew(ADMIN_DB)
    except Exception as e:
        print(f"ну хуй: {e}")


@client.command()
@commands.has_permissions()
async def unwarn(ctx, member: discord.Member):
    global ADMIN_DB
    if str(member.id) not in ADMIN_DB["warns"].keys():
        await ctx.send("братка, у него и так варнов нет")
    try:
        del ADMIN_DB["warns"][str(member.id)]
        embed = discord.Embed(
            title="Информация о снятии редупреждения", colour=0x00ff00)
        embed.set_author(
            icon_url=ctx.guild.icon_url,
            name=f"{ctx.guild.name} team")
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Предупреждения снято",
                        value=member.mention, inline=False)
        embed.add_field(name="Предупреждения снял",
                        value=ctx.message.author.mention, inline=False)
        b = client.get_user(893937565609119774)
        embed.set_footer(icon_url=b.avatar_url,
                         text="Команда по безопастности Discrod Сервера.")
        await ctx.send(embed=embed)
        admin_db_renew(ADMIN_DB)
    except Exception as e:
        print(f"ну хуй: {e}")


@client.command()
@commands.has_permissions()
async def cmute(ctx, member: discord.Member, time="", *, reason=None, ):
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    time_str = ""
    if "s" in time:
        time_str = str(time).replace("s", " сек.")
    if "m" in time:
        time_str = str(time).replace("m", " мин.")
    if "h" in time:
        time_str = str(time).replace("h", " час.")
    if "d" in time:
        time_str = str(time).replace("d", " дн.")
    if "w" in time:
        time_str = str(time).replace("w", " нед.")

    def converttime(time):
        try:
            time = str(time)
            return int(time[:-1]) * time_convert[time[-1]]
        except:
            return time

    if member.id == ctx.author.id:
        await ctx.send(f"{ctx.author.mention}, я, конечно, всё понимаю, но себя не замутишь")
        return
    role = ctx.guild.get_role(932347272849670265)
    if role:
        if str(member.id) not in ADMIN_DB["mutes"].keys():
            ADMIN_DB["mutes"][str(member.id)] = {"cmutes": [], "vmutes": []}
            admin_db_renew(ADMIN_DB)
        if role in ctx.guild.roles and time == 0:
            await member.add_roles(role)
            embed = discord.Embed(
                title="Информация о муте в чате", colour=0xff0000)
            embed.set_author(
                icon_url=ctx.guild.icon_url,
                name=f"{ctx.guild.name} team")
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Мут выдан",
                            value=member.mention, inline=False)
            embed.add_field(name="Мут выдал",
                            value=ctx.message.author.mention, inline=False)
            if reason:
                embed.add_field(name="Причина", value=reason, inline=False)
            b = client.get_user(893937565609119774)
            embed.set_footer(icon_url=b.avatar_url,
                             text="Команда по безопастности Discrod Сервера.")
            await ctx.send(embed=embed)
            ADMIN_DB["mutes"][str(member.id)]["cmutes"].append(
                {"date": str(datetime.now().date().strftime("%d %b %Y")), "reason": reason,
                 "moderator": ctx.message.author.id})
            admin_db_renew(ADMIN_DB)
            return
        if role in ctx.guild.roles:
            await member.add_roles(role)
            embed = discord.Embed(
                title="Информация о муте в чате", colour=0xff0000)
            embed.set_author(
                icon_url=ctx.guild.icon_url,
                name=f"{ctx.guild.name} team")
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Мут выдан",
                            value=member.mention, inline=False)
            embed.add_field(name="Мут выдал",
                            value=ctx.message.author.mention, inline=False)
            if time:
                embed.add_field(name="Время", value=time_str, inline=False)
            if reason:
                embed.add_field(name="Причина", value=reason, inline=False)
            b = client.get_user(893937565609119774)
            embed.set_footer(icon_url=b.avatar_url,
                             text="Команда по безопастности Discrod Сервера.")
            await ctx.send(embed=embed)
            ADMIN_DB["mutes"][str(member.id)]["cmutes"].append(
                {"date": str(datetime.now().date().strftime("%d %b %Y")), "reason": reason,
                 "moderator": ctx.message.author.id})
            admin_db_renew(ADMIN_DB)
            if time:
                await asyncio.sleep(converttime(time))
                await member.remove_roles(role)
        else:
            await ctx.send("чёт хуйня какая-то...")


@client.command()
@commands.has_permissions()
async def vmute(ctx, member: discord.Member, time="", *, reason=None, ):
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    time_str = ""
    if "s" in time:
        time_str = str(time).replace("s", " сек.")
    if "m" in time:
        time_str = str(time).replace("m", " мин.")
    if "h" in time:
        time_str = str(time).replace("h", " час.")
    if "d" in time:
        time_str = str(time).replace("d", " дн.")
    if "w" in time:
        time_str = str(time).replace("w", " нед.")

    def converttime(time):
        try:
            return int(time[:-1]) * time_convert[time[-1]]
        except:
            return time

    if member.id == ctx.author.id:
        await ctx.send(f"{ctx.author.mention}, я, конечно, всё понимаю, но себя не замутишь")
        return
    role = ctx.guild.get_role(932347333356695632)
    if role:
        if str(member.id) not in ADMIN_DB["mutes"].keys():
            ADMIN_DB["mutes"][str(member.id)] = {"cmutes": [], "vmutes": []}
            admin_db_renew(ADMIN_DB)
        if role in ctx.guild.roles and time == 0:
            await member.add_roles(role)
            embed = discord.Embed(
                title="Информация о голосовом муте", colour=0xff0000)
            embed.set_author(
                icon_url=ctx.guild.icon_url,
                name=f"{ctx.guild.name} team")
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Мут выдан",
                            value=member.mention, inline=False)
            embed.add_field(name="Мут выдал",
                            value=ctx.message.author.mention, inline=False)
            if reason:
                embed.add_field(name="Причина", value=reason, inline=False)
            b = client.get_user(893937565609119774)
            embed.set_footer(icon_url=b.avatar_url,
                             text="Команда по безопастности Discrod Сервера.")
            await ctx.send(embed=embed)
            ADMIN_DB["mutes"][str(member.id)]["vmutes"].append(
                {"date": str(datetime.now().date().strftime("%d %b %Y")), "reason": reason,
                 "moderator": ctx.message.author.id})
            admin_db_renew(ADMIN_DB)
            return
        if role in ctx.guild.roles:
            await member.add_roles(role)
            embed = discord.Embed(
                title="Информация о голосовом муте", colour=0xff0000)
            embed.set_author(
                icon_url=ctx.guild.icon_url,
                name=f"{ctx.guild.name} team")
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Мут выдан",
                            value=member.mention, inline=False)
            embed.add_field(name="Мут выдал",
                            value=ctx.message.author.mention, inline=False)
            if time:
                embed.add_field(name="Время", value=time_str, inline=False)
            if reason:
                embed.add_field(name="Причина", value=reason, inline=False)
            b = client.get_user(893937565609119774)
            embed.set_footer(icon_url=b.avatar_url,
                             text="Команда по безопастности Discrod Сервера.")
            await ctx.send(embed=embed)
            ADMIN_DB["mutes"][str(member.id)]["vmutes"].append(
                {"date": str(datetime.now().date().strftime("%d %b %Y")), "reason": reason,
                 "moderator": ctx.message.author.id})
            admin_db_renew(ADMIN_DB)
            if time:
                await asyncio.sleep(converttime(time))
                await member.remove_roles(role)
        else:
            await ctx.send("чёт хуйня какая-то...")


@client.command()
@commands.has_permissions()
async def unmute(ctx, member: discord.Member):
    crole = discord.utils.get(ctx.guild.roles, name="cMuted")
    vrole = discord.utils.get(ctx.guild.roles, name="vMuted")
    embed = discord.Embed(title="Информация о снятии мута", colour=0x00ff00)
    embed.set_author(
        icon_url=ctx.guild.icon_url,
        name=f"{ctx.guild.name} team")
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Мут снят", value=member.mention, inline=False)
    embed.add_field(name="Мут снял",
                    value=ctx.message.author.mention, inline=False)
    b = client.get_user(893937565609119774)
    embed.set_footer(icon_url=b.avatar_url,
                     text="Команда по безопастности Discrod Сервера.")
    await ctx.send(embed=embed)
    await member.remove_roles(crole)
    await member.remove_roles(vrole)


@client.command(pass_context=True)
@commands.has_permissions()
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = "пидорас"
    embed = discord.Embed(title="Кик", colour=0xff0000)
    embed.set_author(
        icon_url=ctx.guild.icon_url,
        name=f"{ctx.guild.name} team")
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Кикнут", value=member.mention, inline=False)
    embed.add_field(
        name="Кикнул", value=ctx.message.author.mention, inline=False)
    embed.add_field(name="Причина", value=reason, inline=False)
    b = client.get_user(893937565609119774)
    embed.set_footer(icon_url=b.avatar_url,
                     text="Команда по безопастности Discrod Сервера.")
    await ctx.send(embed=embed)
    await member.kick(reason=reason)

    if member is None:
        await ctx.send("себя не кикнешь брат..")
        return


@client.command(aliases=['purge', 'delete'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=None):  # Set default value as None
    if amount is None:
        await ctx.channel.purge(limit=1000000)
    else:
        try:
            await ctx.channel.purge(limit=int(amount))
        except:  # Error handler
            await ctx.send('Нормальное число сообщений введи пжшка')
        else:
            await ctx.channel.purge(limit=amount)


@client.command()
@commands.has_permissions(administrator=True)
async def slowmode(ctx, seconds: int):
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Интервал сообщений {seconds} секунд!")
    except:
        await ctx.send("что-то явно не так.. может с цифрами пробоема..?")


# @client.command()
# @commands.has_permissions()
# async def help(ctx):
#     pass


@client.command()
@commands.has_permissions()
async def historyo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    mutes_amount = 0
    info = """"""
    warns_amount = 0
    # тип причина дата время

    if str(member.id) in ADMIN_DB["warns"].keys():
        c = 0
        for i in ADMIN_DB["warns"][str(member.id)]:
            info += f"""📛 | {ADMIN_DB["warns"][str(member.id)][c]["reason"]} | {ADMIN_DB["warns"][str(member.id)][c]["date"]} | {ctx.guild.get_member(int(ADMIN_DB["warns"][str(member.id)][c]["moderator"])).mention}
    """  # TODO moder id and mention
            warns_amount += 1
            c += 1

    if str(member.id) in ADMIN_DB["mutes"].keys():
        c = 0
        if len(ADMIN_DB["mutes"][str(member.id)]["cmutes"]):
            for i in ADMIN_DB["mutes"][str(member.id)]["cmutes"]:
                info += f"""💬 | {i["reason"]} | {i["date"]} | {ctx.guild.get_member(int(i["moderator"])).mention}
"""
                mutes_amount += 1
                c += 1
        if len(ADMIN_DB["mutes"][str(member.id)]["vmutes"]):
            for i in ADMIN_DB["mutes"][str(member.id)]["vmutes"]:
                info += f"""#{c + 1} 🔇 {i["date"]}
"""
                mutes_amount += 1
                c += 1
    embed = discord.Embed(title=f"История нарушений | {member}",
                          description=f"За всё время {mutes_amount} мутов {warns_amount} варнов", colour=0x2f3136)
    embed.set_thumbnail(url=member.avatar_url)
    if info:
        embed.add_field(name="Тип | Причина | Дата | Исполнитель",
                        value=info, inline=False)
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text="Запросил(а) " + ctx.author.name + "#" + ctx.author.discriminator)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions()
async def serverinfo(ctx):
    name = ctx.guild.name
    server_id = ctx.guild.id
    icon_url = ctx.guild.icon_url
    created_on = ctx.guild.created_at.date().strftime("%d %b %Y")
    owned_by = ctx.guild.owner
    members = str(len(ctx.guild.members))
    member_count = ctx.guild.member_count
    channels = len(ctx.guild.channels) - len(ctx.guild.categories)
    v_channels = len(ctx.guild.voice_channels)
    roles = str(len(ctx.guild.roles))
    embed = discord.Embed(colour=0x2f3136)
    embed.set_author(icon_url=icon_url, name=name)
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="ID сервера", value=server_id, inline=True)
    embed.add_field(name="Создан", value=created_on, inline=True)
    embed.add_field(name="Владелец", value=owned_by, inline=True)
    embed.add_field(name="Участники", value=member_count, inline=True)
    embed.add_field(name=f"Каналы {str(channels)}",
                    value=f"{str(channels - v_channels)} текстовые | {str(v_channels)} голосовые", inline=True)
    embed.add_field(name="Роли", value=roles, inline=False)
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text="Запросил(а) " + ctx.author.name + "#" + ctx.author.discriminator)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    mmb = member.name + "#" + member.discriminator
    avatar = member.avatar_url
    member_id = member.id
    joined_at = member.joined_at.date().strftime("%d %b %Y")
    created_at = member.created_at.date().strftime("%d %b %Y")
    status = member.status
    roles = member.roles[1::]
    roles_names = ""
    for i in roles:
        roles_names += i.name
    embed = discord.Embed(title="Информация о " + mmb, colour=0x2f3136)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name="Полное имя", value=mmb, inline=True)
    embed.add_field(name="ID пользователя", value=member_id, inline=True)
    embed.add_field(name="Статус", value=status, inline=False)
    embed.add_field(name="Присоединился к серверу",
                    value=joined_at, inline=True)
    embed.add_field(name="Аккаунт создан", value=created_at, inline=True)
    embed.add_field(name=f"Ролей ({len(roles)})",
                    value=roles_names, inline=True)
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text="Запросил(а) " + ctx.author.name + "#" + ctx.author.discriminator)
    await ctx.send(embed=embed)


@client.command()
async def test(ctx):
    embed = discord.Embed(title="Управление приватной комнатой", description="""Жми следующие кнопки, чтобы настроить свою комнату \n Использовать их можно только, когда у тебя есть приватный канал! \n
    > 📝 — `изменить название комнаты` \n
    > 👥 — `установить лимит пользователей` \n
    > 🔒 — `закрыть комнату для всех` \n
    > 🔓 — `открыть комнату для всех` \n
    > ❎ — `забрать доступ к комнате у пользователя` \n
    > ✅ — `выдать доступ к комнате пользователю` \n
    > 👋 — `выгнать пользователя из комнаты` \n
    > 🔇 — `забрать у пользователя право говорить` \n
    > 🔊 — `выдать пользователю право говорить` \n
    > 👑 — `передать пользователю права на комнату`""")
    view = View()

    # Define the check function within your code

    # This checks if the author of the message is the author of the ❌ reaction
    # AND checks if the message author is a bot or not

    async def button_callback(interaction):
        def check(msg):
            return msg.author == interaction.user and not msg.author.bot
        if interaction.data["custom_id"] == "name":
            await ctx.send("Чтобы установить новое название комнаты, введите его ниже")
            message = await client.wait_for("message", check=check, timeout=15)
            channel = ctx.message.author.voice.channel
            await channel.edit(name=message.content)

        elif interaction.data["custom_id"] == "limit":
            await ctx.send("Чтобы установить новый лимит пользователей, введите его ниже")
            message = await client.wait_for("message", check=check, timeout=15)
            channel = ctx.message.author.voice.channel
            await channel.edit(user_limit=int(message.content))

        elif interaction.data["custom_id"] == "lock":
            channel = ctx.message.author.voice.channel
            await channel.set_permissions(connect=False)
            await ctx.send("Комната закрыта")

        elif interaction.data["custom_id"] == "unlock":
            channel = ctx.message.author.voice.channel
            await channel.set_permissions(connect=True)
            await ctx.send("Комната открыта")

        elif interaction.data["custom_id"] == "no_access":
            await ctx.send("Укажите пользователя, у которого вы хотите забрать доступ")
            message = await client.wait_for("message", check=check, timeout=20)
            overwrites = {message.guild.get_member(
                message.mentions[0]): discord.PermissionOverwrite(connect=False)}  # TODO по упоминанию
            channel = ctx.message.author.voice.channel
            await channel.edit(overwrites=overwrites)

        elif interaction.data["custom_id"] == "access":
            await ctx.send("Укажите пользователя, которому вы хотите предоставить доступ")
            message = await client.wait_for("message", check=check, timeout=20)
            overwrites = {message.guild.get_member(
                message.mentions[0]): discord.PermissionOverwrite(connect=True)}
            channel = ctx.message.author.voice.channel
            await channel.edit(overwrites=overwrites)

        elif interaction.data["custom_id"] == "kick":
            await ctx.send("Укажите пользователя, которого вы хотите кикнуть")
            message = await client.wait_for("message", check=check, timeout=20)
            await message.mentions[0].move_to(None)
            # channel = ctx.message.author.voice.channel
            # await channel.edit(name=message.content)

        elif interaction.data["custom_id"] == "mute":
            await ctx.send("Укажите пользователя, у которого вы хотите забрать право говорить")
            message = await client.wait_for("message", check=check, timeout=20)
            overwrites = {message.guild.get_member(
                message.mentions[0]): discord.PermissionOverwrite(speak=False)}
            channel = ctx.message.author.voice.channel
            await channel.edit(overwrites=overwrites)

        elif interaction.data["custom_id"] == "unmute":
            await ctx.send("Укажите пользователя, которому вы хотите выдать право говорить")
            message = await client.wait_for("message", check=check, timeout=20)
            overwrites = {message.guild.get_member(
                message.mentions[0]): discord.PermissionOverwrite(speak=True)}
            channel = ctx.message.author.voice.channel
            await channel.edit(overwrites=overwrites)

        elif interaction.data["custom_id"] == "give_rights":
            await ctx.send("Укажите пользователя, которому вы хотите передать комнату")
            message = await client.wait_for("message", check=check, timeout=20)
            overwrites = {message.guild.get_member(
                message.mentions[0]): discord.PermissionOverwrite(speak=False)}
            channel = ctx.message.author.voice.channel
            await channel.edit(overwrites=overwrites)
            # в базе айди комнаты айди человека при передачи прав айди человека переписывается (доделать удаление при выходе) переделать ф-ю check()

    callback = button_callback
    buttons = [
        Button(emoji="📝", style=ButtonStyle.primary, custom_id="name", row=1),
        Button(emoji="👥", style=ButtonStyle.primary, custom_id="limit", row=1),
        Button(emoji="🔒", style=ButtonStyle.primary, custom_id="lock", row=1),
        Button(emoji="🔓", style=ButtonStyle.primary,
               custom_id="unlock", row=1),
        Button(emoji="❎", style=ButtonStyle.primary,
               custom_id="no_access", row=1),
        Button(emoji="✅", style=ButtonStyle.primary,
               custom_id="access", row=2),
        Button(emoji="👋", style=ButtonStyle.primary, custom_id="kick", row=2),
        Button(emoji="🔇", style=ButtonStyle.primary, custom_id="mute", row=2),
        Button(emoji="🔊", style=ButtonStyle.primary,
               custom_id="unmute", row=2),
        Button(emoji="👑", style=ButtonStyle.primary,
               custom_id="give_rights", row=2),
    ]
    for i in buttons:
        i.callback = callback
        view.add_item(i)
    await ctx.send(embed=embed, view=view)


# @client.event
# async def on_button_click(interaction):
#     print(1)
#     print(interaction)


@client.command()
@commands.has_permissions()
async def userbyid(ctx, user_id):
    try:
        member = client.get_user(int(user_id))
        await ctx.send(member.mention)
    except:
        await ctx.send("какая-то ошиб0чка..")


@client.command()
@commands.has_permissions()
async def toponline(ctx):
    global USERS
    top = []
    id_s = {}
    for i in USERS:
        top.append(USERS[i])
        id_s[str(USERS[i])] = i
    top.sort(reverse=True)
    text = """"""
    c = 1

    for i in top:
        if c <= 10:
            text += f"""#{c} {ctx.guild.get_member(int(id_s[str(i)])).mention} {timef(i)}
"""
            c += 1
    embed = discord.Embed(title=f"Топ-10 олосового онлайна",
                          colour=random.choice(embed_colors))
    embed.add_field(name="----------------", value=f"{text}")
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text="Запросил(а) " + ctx.author.name + "#" + ctx.author.discriminator)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions()
async def vonline(ctx, member: discord.Member = None):
    global USERS
    # TODO онлвйн за месяц
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"Голосовой онлайн | {member.name + '#' + member.discriminator}",
                          colour=random.choice(embed_colors))
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="----------------",
                    value=f"{timef(USERS[str(member.id)])}")
    embed.set_footer(icon_url=ctx.author.avatar_url,
                     text="Запросил(а) " + ctx.author.name + "#" + ctx.author.discriminator)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions()
async def ava(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed = discord.Embed(title="Аватарка " + member.name +
                          "#" + member.discriminator, colour=0x2f3136)
    embed.set_image(url=member.avatar.url)
    embed.set_footer(icon_url=ctx.author.avatar.url,
                     text="Запросил(а) " + ctx.author.name + "#" + ctx.author.discriminator)
    await ctx.send(embed=embed)


# @client.command()
# @commands.has_permissions()
# async def balance(ctx):
#     pass
#
# @client.command()
# @commands.has_permissions()
# async def rank(ctx):
#     pass


@client.event
async def on_message(message):
    await client.process_commands(message)
    global ADMIN_DB
    if message.channel.id == 932731504654712842:
        overwrites = {
            message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.guild.get_member(message.author.id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            message.guild.get_role(934554685803728957): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            message.guild.get_role(934554703201714226): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            message.guild.get_role(934554707429589123): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        category = message.guild.get_channel(934557584688578580)
        channel = await message.guild.create_text_channel(f"ticket-{str(ADMIN_DB['tickets']['tickets_amount'] + 1)}", category=category, overwrites=overwrites)
        ADMIN_DB["tickets"]["tickets_amount"] += 1
        ADMIN_DB["tickets"]["tickets_unprocessed"] += 1
        admin_db_renew(ADMIN_DB)
        await channel.send(f"{message.author.mention}: {message.content}")
        await message.delete()
        tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
        tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
        tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
        tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
        channel_appealed = message.guild.get_channel(932731504654712842)
        msg = discord.utils.get(await channel_appealed.history(limit=1).flatten())
        # await msg.edit(content=texts_to_channels[str(channel_appealed.id)].format(tickets_amount=tickets_amount, tickets_unprocessed=tickets_unprocessed, tickets_in_process=tickets_in_process, tickets_closed=tickets_closed))

        embed = discord.Embed(colour=0x2f3136)
        tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
        tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
        tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
        tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
        embed.description = texts_to_channels[str(932731504654712842)].format(tickets_amount=tickets_amount,
                                                                              tickets_unprocessed=tickets_unprocessed,
                                                                              tickets_in_process=tickets_in_process,
                                                                              tickets_closed=tickets_closed)
        embed.set_image(
            url="https://i.pinimg.com/originals/27/71/dc/2771dc4257d8d2f61a9857356910f2fd.gif")
        await msg.edit(embed=embed)

    if not message.content.startswith("!") and message.author.id != 893937565609119774:
        if message.channel.id == 934227090990047323:
            embed = discord.Embed(colour=0x2f3136)
            if message.content and message.attachments:
                embed = discord.Embed(description=f"""Отправил {message.author.mention}
`{message.content}`""", colour=0x2f3136)
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            elif message.content and not message.attachments:
                content = message.content
                await message.channel.send(content)
            elif message.attachments and not message.content:
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(content=f"Отправил {message.author.mention}", embed=embed)
            await message.delete()

        if message.channel.id == 934227145264345088:
            embed = discord.Embed(colour=0x2f3136)
            if message.content and message.attachments:
                embed = discord.Embed(
                    description=f"`{message.content}`", colour=0x2f3136)
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            elif message.content and not message.attachments:
                content = message.content
                await message.channel.send(content)
            elif message.attachments and not message.content:
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            await message.delete()

        if message.channel.id == 934552482867183626:
            embed = discord.Embed(colour=0x2f3136)
            if message.content and message.attachments:
                embed = discord.Embed(
                    description=f"`{message.content}`", colour=0x2f3136)
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            elif message.content and not message.attachments:
                content = message.content
                await message.channel.send(content)
            elif message.attachments and not message.content:
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            await message.delete()

        if message.channel.id == 934867751141535774:
            embed = discord.Embed(colour=0x2f3136)
            if message.content and message.attachments:
                embed = discord.Embed(
                    description=f"`{message.content}`", colour=0x2f3136)
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            elif message.content:
                content = message.content
                await message.channel.send(content)
            elif message.attachments:
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            await message.delete()

        if message.channel.id == 934224717513097246:
            embed = discord.Embed(colour=0x2f3136)
            if message.content and message.attachments:
                embed = discord.Embed(
                    description=f"`{message.content}`", colour=0x2f3136)
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            elif message.content and not message.attachments:
                content = message.content
                await message.channel.send(content)
            elif message.attachments and not message.content:
                attachment = message.attachments[0].url
                embed.set_image(url=attachment)
                await message.channel.send(embed=embed)
            await message.delete()


@client.command()
async def startticket(ctx):
    global ADMIN_DB
    ADMIN_DB["tickets"]["tickets_in_process"] += 1
    ADMIN_DB["tickets"]["tickets_unprocessed"] -= 1
    admin_db_renew(ADMIN_DB)
    await ctx.channel.purge(limit=1)
    await ctx.send("[!] Начата работа по обращению")
    tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
    tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
    tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
    tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
    channel_appealed = ctx.guild.get_channel(932731504654712842)
    msg = discord.utils.get(await channel_appealed.history(limit=1).flatten())

    embed = discord.Embed(colour=0x2f3136)
    tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
    tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
    tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
    tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
    embed.description = texts_to_channels[str(932731504654712842)].format(tickets_amount=tickets_amount,
                                                                          tickets_unprocessed=tickets_unprocessed,
                                                                          tickets_in_process=tickets_in_process,
                                                                          tickets_closed=tickets_closed)
    embed.set_image(
        url="https://i.pinimg.com/originals/27/71/dc/2771dc4257d8d2f61a9857356910f2fd.gif")
    await msg.edit(embed=embed)


@client.command()
async def closeticket(ctx):
    global ADMIN_DB
    ADMIN_DB["tickets"]["tickets_closed"] += 1
    ADMIN_DB["tickets"]["tickets_in_process"] -= 1
    admin_db_renew(ADMIN_DB)
    await ctx.channel.purge(limit=1)
    await ctx.send("[!] Работа по обращению завершена")

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.get_role(934554685803728957): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        ctx.guild.get_role(934554703201714226): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        ctx.guild.get_role(934554707429589123): discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    await ctx.channel.edit(category=ctx.guild.get_channel(934557633770324008), overwrites=overwrites)
    tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
    tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
    tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
    tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
    channel_appealed = ctx.guild.get_channel(932731504654712842)
    msg = discord.utils.get(await channel_appealed.history(limit=1).flatten())

    embed = discord.Embed(colour=0x2f3136)
    tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
    tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
    tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
    tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
    embed.description = texts_to_channels[str(932731504654712842)].format(tickets_amount=tickets_amount,
                                                                          tickets_unprocessed=tickets_unprocessed,
                                                                          tickets_in_process=tickets_in_process,
                                                                          tickets_closed=tickets_closed)
    embed.set_image(
        url="https://i.pinimg.com/originals/27/71/dc/2771dc4257d8d2f61a9857356910f2fd.gif")
    await msg.edit(embed=embed)

    await asyncio.sleep(259200)
    # await asyncio.sleep(5)
    await ctx.channel.delete()


@client.command()
async def send_to(ctx):
    global ADMIN_DB
    tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
    tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
    tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
    tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
    channel_appealed = ctx.guild.get_channel(932731504654712842)
    msg = discord.utils.get(await channel_appealed.history(limit=1).flatten())
    await msg.edit(content=texts_to_channels[str(channel_appealed.id)].format(tickets_amount=tickets_amount,
                                                                              tickets_unprocessed=tickets_unprocessed,
                                                                              tickets_in_process=tickets_in_process,
                                                                              tickets_closed=tickets_closed))


@client.command()
async def img(ctx):
    embed = discord.Embed(colour=0x2f3136)
    global ADMIN_DB
    tickets_amount = ADMIN_DB["tickets"]["tickets_amount"]
    tickets_unprocessed = ADMIN_DB["tickets"]["tickets_unprocessed"]
    tickets_in_process = ADMIN_DB["tickets"]["tickets_in_process"]
    tickets_closed = ADMIN_DB["tickets"]["tickets_closed"]
    embed.description = texts_to_channels[str(932731504654712842)].format(tickets_amount=tickets_amount,
                                                                          tickets_unprocessed=tickets_unprocessed,
                                                                          tickets_in_process=tickets_in_process,
                                                                          tickets_closed=tickets_closed)
    embed.set_image(
        url="https://i.pinimg.com/originals/27/71/dc/2771dc4257d8d2f61a9857356910f2fd.gif")
    await ctx.send(embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
    global tdict
    author = str(member.id)
    if before.channel is None and after.channel is not None:
        t1 = time.time()
        tdict[author] = t1
        if author not in USERS:
            USERS[author] = 0
            users_db_renew(USERS)
    elif before.channel is not None and after.channel is None and author in tdict:
        t2 = time.time()
        USERS[author] += int(t2 - tdict[author])
        users_db_renew(USERS)
    if before.channel is None and after.channel.id == 934908092947243008:
        cat = client.get_channel(after.channel.category_id)
        private_channel = await member.guild.create_voice_channel(name=f"├∘⊰•{member.name}•", category=cat)
        await member.move_to(private_channel)
    elif after.channel is None and before.channel.id:
        await before.channel.delete()


client.run(TOKEN)  # TODO ЛОГИ
