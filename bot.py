import time
import asyncio
from os import environ as evn
from database import Database
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid


app = Client(
    name='requestBot',
    bot_token=evn.get("BOT_TOKEN"),
    api_id=evn.get("API_ID"),
    api_hash=evn.get("API_HASH")
)
app.db = Database()


@app.on_chat_join_request(filters.group | filters.channel)
async def autoapprove(c, m):
    await c.db.add_user(m.from_user.id)
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
        button = [[
            InlineKeyboardButton('🌐 Support 🌐', url='https://t.me/mallu_hub_official')
            ],[
            InlineKeyboardButton('♥️ Update Channel ♥️', url='https://t.me/Mallu_Hub_TG')
        ]]
        markup = InlineKeyboardMarkup(button)
        caption = f'Hello {m.from_user.mention()}\nYou Request To Join {m.chat.title} Was Approved.'
        await c.send_photo(
            m.from_user.id, 
            photo='https://telegra.ph/file/f7738f04ea74e16c9db02.jpg', 
            caption=caption, 
            reply_markup=markup
        )
    except UserIsBlocked:
        print(f"{m.from_user.first_name} blocked the bot")
    except PeerIdInvalid:
        print(f"User {m.from_user.first_name} haven't started the bot yet")
    except Exception as e:
        print('Error:', e)


@app.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c, m):
    text = f'''Hello {m.from_user.mention()} 👋
I'm an auto approve Admin Join Requests Bot.
I can approve users in Groups/Channels.Add me to your chat and promote me to admin with add members permission.'''
    button = [[
            InlineKeyboardButton('💎JOIN GROUP✅️', url='https://t.me/mallu_hub_official')
            ],[
            InlineKeyboardButton('📣UPDATES🔔', url='https://t.me/Mallu_Hub_TG')
    ]]
    await m.reply_photo(
        photo='https://telegra.ph/file/f7738f04ea74e16c9db02.jpg', 
        caption=text,
        reply_markup=InlineKeyboardMarkup(button),
        quote=True
    )


AUTH_USER = [int(user) for user in evn.get('AUTH_USERS', 0).split(' ')]
@app.on_message(filters.command('broadcast') & filters.private & filters.incoming & filters.chat(AUTH_USER))
async def broadcast(c, m):
    if not m.reply_to_message:
        return await m.reply_text('Reply to a message that i need to broadast.', quote=True)

    msg = m.reply_to_message
    users = await c.db.get_all_users()

    start = time.time()
    last_edited = 0
    failed = 0
    success = 0
    total = await c.db.total_users_count()
    sts = await m.reply_text(f'Board Cast Started\n\nTotal no of users: {total}', quote=True)


    async def send_msg(c, user_id):
        try:
            return await msg.copy(user_id)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            return await send_msg(c, user_id)
        except InputUserDeactivated:
            await c.db.delete_user(user_id)
            print(f"{user_id} : deactivated")
        except UserIsBlocked:
            await c.db.delete_user(user_id)
            print(f"{user_id} : blocked the bot")
        except PeerIdInvalid:
            await c.db.delete_user(user_id)
            print(f"{user_id} : user id invalid")
        except Exception as e:
            print(f"{user_id} : {e}")

    async for user in users:
        user = await send_msg(c, user['id'])
        if user:
            success += 1
        else:
            failed += 1
        if last_edited - start == 5:
            try:
                await sts.edit(f'Total: {total}\nSuccess: {success}\nFailed: {failed}') 
                last_edited = time.time()
            except:
                pass
        await asyncio.sleep(0.5)

    await sts.edit(f'**BroadCast Completed:**\n\nTotal: {total}\nSuccess: {success}\nFailed: {failed}')

if __name__ == '__main__':
    app.run()
