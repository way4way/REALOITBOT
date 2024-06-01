from aiogram.dispatcher.filters import BoundFilter
from data.sqlite import Database
from loader import bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


db = Database()


class IsUser(BoundFilter):
    async def check(self, message: Message):
        user_id = message.from_user.id
        user_info = await db.get_user(user_id=user_id)
        if not user_info:
            await db.add_user(user_id, message.from_user.username)
            return True
        if user_info[2] != 3:
            if message.from_user.username != user_info[1]:
                await db.update_user(user_id, username=message.from_user.username)
            return True
        else:
            msg = f'<b>❌ Доступ к боту заблокирован</b>'
            await bot.send_message(chat_id=user_id, text=msg)
            return False


cancel_kb = InlineKeyboardMarkup()
cancel_kb.add(InlineKeyboardButton('❌ Отменить', callback_data='hide'))


def b_msg(text):
    return f'<b>{text}</b>'
