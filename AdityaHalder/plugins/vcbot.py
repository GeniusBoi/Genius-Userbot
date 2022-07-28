import re
import asyncio
from AdityaHalder.modules.cache.admins import admins
from AdityaHalder.modules.helpers.filters import other_filters
from AdityaHalder.utilities.utils import bash, skip_current_song, skip_item
from AdityaHalder.modules.helpers.command import commandpro as command
from AdityaHalder.modules.clientbot.queues import QUEUE, add_to_queue, clear_queue
from AdityaHalder.modules.clientbot import client as app, pytgcalls as aditya
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from youtubesearchpython import VideosSearch
from AdityaHalder.utilities.misc import SUDOERS


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        return [songname, url]
    except Exception as e:
        print(e)
        return 0

async def ytdl(link: str):
    stdout, stderr = await bash(
        f'yt-dlp -g -f "best[height<=?720][width<=?1280]" {link}'
    )
    if stdout:
        return 1, stdout
    return 0, stderr


async def ytdl_(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command([".ply", "ply"]) & SUDOERS)
async def play(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    user_id = m.from_user.id
    if replied:
        if replied.audio or replied.voice:
            suhu = await replied.reply("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
            dl = await replied.download()
            link = replied.link
            
            try:
                if replied.audio:
                    songname = replied.audio.title[:70]
                    songname = replied.audio.file_name[:70]
                elif replied.voice:
                    songname = "Voice Note"
            except BaseException:
                songname = "Audio"
            
            if chat_id in QUEUE:
                title = songname
                userid = m.from_user.id
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await suhu.delete()
                await m.reply_text(f"**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞 \n🔊 𝐐𝐮𝐞𝐮𝐞𝐝 💞 𝐀𝐭 » #{pos} 🌷 ...**",
                )
            else:
                try:
                    title = songname
                    userid = m.from_user.id
                    await suhu.edit("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
                    await aditya.join_group_call(
                        chat_id,
                        AudioPiped(
                            dl,
                            HighQualityAudio(),
                        ),
                        stream_type=StreamType().local_stream,
                    )
                    add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                    await suhu.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_text("**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞\n🔊 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 😍 𝐎𝐏 🥀 ...**",
                    )
                except Exception as e:
                    await suhu.delete()
                    await m.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫:\n\n» {e}")
        else:
            if len(m.command) < 2:
                await m.reply(
                    "**🤖 𝐆𝐢𝐯𝐞 🙃 𝐒𝐨𝐦𝐞 💿 𝐐𝐮𝐞𝐫𝐲 😍\n💞 𝐓𝐨 🔊 𝐏𝐥𝐚𝐲 🥀 𝐒𝐨𝐧𝐠 🌷...**"
                )
            else:
                suhu = await c.send_message(chat_id, "**🔎 𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 ...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("**🚫 𝐒𝐨𝐧𝐠 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝❗...**")
                else:
                    songname = search[0]
                    title = search[0]
                    url = search[1]
                    userid = m.from_user.id
                    coders, ytlink = await ytdl(url)
                    if coders == 0:
                        await suhu.edit(f"**❌ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐈𝐬𝐬𝐮𝐞𝐬 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝\n\n» `{ytlink}`**")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Audio", 0
                            )
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_text(f"**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞 \n🔊 𝐐𝐮𝐞𝐮𝐞𝐝 💞 𝐀𝐭 » #{pos} 🌷 ...**",
                            )
                        else:
                            try:
                                await suhu.edit("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
                                await aditya.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                await suhu.delete()
                                requester = (
                                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                )
                                await m.reply_text("**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞\n🔊 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 😍 𝐎𝐏 🥀 ...**",
                                )
                            except Exception as ep:
                                await suhu.delete()
                                await m.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "**🤖 𝐆𝐢𝐯𝐞 🙃 𝐒𝐨𝐦𝐞 💿 𝐐𝐮𝐞𝐫𝐲 😍\n💞 𝐓𝐨 🔊 𝐏𝐥𝐚𝐲 🥀 𝐒𝐨𝐧𝐠 🌷...**"
            )
        else:
            suhu = await c.send_message(chat_id, "**🔎 𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 ...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("**🚫 𝐒𝐨𝐧𝐠 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝❗...**")
            else:
                songname = search[0]
                title = search[0]
                url = search[1]
                userid = m.from_user.id
                coders, ytlink = await ytdl(url)
                if coders == 0:
                    await suhu.edit(f"**❌ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐈𝐬𝐬𝐮𝐞𝐬 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝\n\n» `{ytlink}`**")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await suhu.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        await m.reply_text(f"**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞 \n🔊 𝐐𝐮𝐞𝐮𝐞𝐝 💞 𝐀𝐭 » #{pos} 🌷 ...**",
                        )
                    else:
                        try:
                            await suhu.edit("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
                            await aditya.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_text("**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞\n🔊 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 😍 𝐎𝐏 🥀 ...**",
                            )
                        except Exception as ep:
                            await suhu.delete()
                            await m.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫: `{ep}`")


@Client.on_message(command([".vply", "vply"]) & SUDOERS)
async def vplay(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    user_id = m.from_user.id
    if replied:
        if replied.video or replied.document:
            loser = await replied.reply("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await loser.edit(
                        "» __𝐎𝐧𝐥𝐲 720, 480, 360 𝐀𝐥𝐥𝐨𝐰𝐞𝐝__ \n💡 **𝐍𝐨𝐰 𝐒𝐭𝐫𝐞𝐚𝐦𝐢𝐧𝐠 𝐕𝐢𝐝𝐞𝐨 𝐈𝐧 720𝐏**"
                    )
            try:
                if replied.video:
                    songname = replied.video.file_name[:70]
                    duration = replied.video.duration
                elif replied.document:
                    songname = replied.document.file_name[:70]
                    duration = replied.document.duration
            except BaseException:
                songname = "Video"

            if chat_id in QUEUE:
                title = songname
                userid = m.from_user.id
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_text(f"**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞 \n🔊 𝐐𝐮𝐞𝐮𝐞𝐝 💞 𝐀𝐭 » #{pos} 🌷 ...**",
                )
            else:
                title = songname
                userid = m.from_user.id
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                await loser.edit("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
                await aditya.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        dl,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_text("**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞\n🔊 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 😍 𝐎𝐏 🥀 ...**",
                )
        else:
            if len(m.command) < 2:
                await m.reply(
                    "**🤖 𝐆𝐢𝐯𝐞 🙃 𝐒𝐨𝐦𝐞 💿 𝐐𝐮𝐞𝐫𝐲 😍\n💞 𝐓𝐨 🔊 𝐏𝐥𝐚𝐲 🥀 𝐒𝐨𝐧𝐠 🌷...**"
                )
            else:
                loser = await c.send_message(chat_id, "**🔎 𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 ...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                Q = 720
                amaze = HighQualityVideo()
                if search == 0:
                    await loser.edit("**🚫 𝐒𝐨𝐧𝐠 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝❗...**")
                else:
                    songname = search[0]
                    title = search[0]
                    url = search[1]
                    userid = m.from_user.id
                    coders, ytlink = await ytdl_(url)
                    if coders == 0:
                        await loser.edit(f"**❌ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐈𝐬𝐬𝐮𝐞𝐬 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝\n\n» `{ytlink}`**")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Video", Q
                            )
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_text(f"**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞 \n🔊 𝐐𝐮𝐞𝐮𝐞𝐝 💞 𝐀𝐭 » #{pos} 🌷 ...**",
                            )
                        else:
                            try:
                                await loser.edit("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
                                await aditya.join_group_call(
                                    chat_id,
                                    AudioVideoPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                        amaze,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                                await loser.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_text("**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞\n🔊 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 😍 𝐎𝐏 🥀 ...**",
                                )
                            except Exception as ep:
                                await loser.delete()
                                await m.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "**🤖 𝐆𝐢𝐯𝐞 🙃 𝐒𝐨𝐦𝐞 💿 𝐐𝐮𝐞𝐫𝐲 😍\n💞 𝐓𝐨 🔊 𝐏𝐥𝐚𝐲 🥀 𝐒𝐨𝐧𝐠 🌷...**"
            )
        else:
            loser = await c.send_message(chat_id, "**🔎 𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 ...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            amaze = HighQualityVideo()
            if search == 0:
                await loser.edit("**🚫 𝐒𝐨𝐧𝐠 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝❗...**")
            else:
                songname = search[0]
                title = search[0]
                url = search[1]
                userid = m.from_user.id
                coders, ytlink = await ytdl_(url)
                if coders == 0:
                    await loser.edit(f"**❌ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐈𝐬𝐬𝐮𝐞𝐬 𝐃𝐞𝐭𝐞𝐜𝐭𝐞𝐝\n\n» `{ytlink}`**")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await loser.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_text(f"**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞 \n🔊 𝐐𝐮𝐞𝐮𝐞𝐝 💞 𝐀𝐭 » #{pos} 🌷 ...**",
                        )
                    else:
                        try:
                            await loser.edit("**🔄 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 ...**")
                            await aditya.join_group_call(
                                chat_id,
                                AudioVideoPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                    amaze,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_text("**💥 ❰𝐀𝐝𝐢𝐭𝐲𝐚✘𝐏𝐥𝐚𝐲𝐞𝐫❱ 💿 𝐍𝐨𝐰 💞\n🔊 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 😍 𝐎𝐏 🥀 ...**",
                            )
                        except Exception as ep:
                            await loser.delete()
                            await m.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫: `{ep}`")


@Client.on_message(command([".pse", "pse"]) & SUDOERS)
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await aditya.pause_stream(chat_id)
            await m.reply(
                f"**▶️ 𝐏𝐚𝐮𝐬𝐞𝐝 🌷 ...**"
            )
        except Exception as e:
            await m.reply(f"🚫 **𝐄𝐫𝐫𝐨𝐫:**\n\n`{e}`")
    else:
        await m.reply("**❌ 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐏𝐥𝐚𝐲𝐢𝐧𝐠❗...**")


@Client.on_message(command(["r", "rsm"]) & SUDOERS)
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await aditya.resume_stream(chat_id)
            await m.reply(
                f"**⏸ 𝐑𝐞𝐬𝐮𝐦𝐞𝐝 🌷 ...**"
            )
        except Exception as e:
            await m.reply(f"🚫 **𝐄𝐫𝐫𝐨𝐫:**\n\n`{e}`")
    else:
        await m.reply("**❌ 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐏𝐥𝐚𝐲𝐢𝐧𝐠❗...**")
        
        
@Client.on_message(command([".skp", "skp"]) & SUDOERS)
async def skip(c: Client, m: Message):
    await m.delete()
    user_id = m.from_user.id
    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("**❌ 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐏𝐥𝐚𝐲𝐢𝐧𝐠❗...**")
        elif op == 1:
            await m.reply("**🥀 𝐄𝐦𝐩𝐭𝐲 𝐐𝐮𝐞𝐮𝐞, 𝐋𝐞𝐚𝐯𝐢𝐧𝐠\n𝐅𝐫𝐨𝐦 𝐕𝐂 ✨...**")
        elif op == 2:
            await m.reply("**🥀 𝐂𝐥𝐞𝐚𝐫𝐢𝐧𝐠 𝐐𝐮𝐞𝐮𝐞, 𝐋𝐞𝐚𝐯𝐢𝐧𝐠\n𝐅𝐫𝐨𝐦 𝐕𝐂 ✨...**")
        else:
            await m.reply("**🥀 𝐒𝐤𝐢𝐩𝐩𝐞𝐝 💞 ...**",
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "🗑 **𝐈 𝐚𝐦 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐒𝐨𝐧𝐠 𝐅𝐫𝐨𝐦 𝐐𝐮𝐞𝐮𝐞:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(command([".end", "end", "x", ".stp", "stp"]) & SUDOERS)
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await aditya.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("**❌ 𝐒𝐭𝐨𝐩𝐩𝐞𝐝 ✨ ...**")
        except Exception as e:
            await m.reply(f"🚫 **𝐄𝐫𝐫𝐨𝐫:**\n\n`{e}`")
    else:
        await m.reply("**❌ 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐏𝐥𝐚𝐲𝐢𝐧𝐠❗...**")




__MODULE__ = "Vᴄ Bᴏᴛ"
__HELP__ = f"""
**Yᴏᴜ Cᴀɴ Pʟᴀʏ Mᴜsɪᴄ Oɴ VC**

`.ply` - Pʟᴀʏ Mᴜsɪᴄ Oɴ Vᴄ
`.pse` - Pᴀᴜsᴇ Yᴏᴜʀ Mᴜsɪᴄ
`.rsm` - Rᴇsᴜᴍᴇ Yᴏᴜʀ Mᴜsɪᴄ
`.skp` - Sᴋɪᴘ Tᴏ Tʜᴇ Nᴇxᴛ Sᴏɴɢ
`.stp` - Sᴛᴏᴘ Pʟᴀʏɪɴɢ Aɴᴅ Lᴇᴀᴠᴇ
`.sng` - Dᴏᴡɴʟᴏᴀᴅ Sᴏɴɢ Yᴏᴜ Wᴀɴᴛ
`.rld` - Rᴇʟᴏᴀᴅ Yᴏᴜʀ VC Cʟɪᴇɴᴛ

(__.sng Cᴏᴍᴍᴀɴᴅ Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ Aᴛ Tʜɪs Mᴏᴍᴇɴᴛ ...__) 
"""
