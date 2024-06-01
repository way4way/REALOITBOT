import random

from loader import bot
from utils.other import b_msg
from data.sqlite import Database
from data.config import ahc_chat_id, oit_chat_id, drivers_chat_id
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

db = Database()


write_oit_problem_text = b_msg(f'ℹ️ Выбрано направление: <code>ОИТ</code>\n\n'
                               f'✏️ Опишите вашу проблему:')
write_ahc_problem_text = b_msg(f'ℹ️ Выбрано направление: <code>АХЧ</code>\n\n'
                               f'✏️ Опишите вашу проблему:')
write_driver_order_text = b_msg(f'ℹ️ Выбрано направление: <code>Водитель</code>\n\n'
                                f'✏️ Введите место и время для заказа автомобиля:')


async def check_problem_msg(way, text):
    msg = f'Выбрано направление: <code>{way}</code>\n\n'
    if way == 'Водители':
        msg += f'Заказ:'
    else:
        msg += f'Проблема:'
    msg += f' <code>{text}</code>\n\n"✅" - Отправить {"заказ" if way == "Водители" else "проблему"} в обработку | "❌" - Отменить отправку'
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('✅', callback_data='1'))
    kb.insert(InlineKeyboardButton('❌', callback_data='hide'))
    return b_msg(msg), kb


async def send_problem_msg(way, text, user_id):
    user_info = await db.get_user(user_id=user_id)
    username = user_info[1]
    address = user_info[3]
    phone = user_info[4]
    pc_ip = user_info[5]
    msg = '🔔 Заказ' if way == 'Водители' else '🔔 Проблема'
    msg += f'\n\n<code>{text}</code>\n\n'
    if way == 'ОИТ' or way == 'АХЧ':
        msg += f'@{username} | <code>{address}</code> | <code>{phone}</code> | <code>{pc_ip}</code>'
    elif way == 'Водители':
        msg += f'@{username} | {phone}'
    msg += f'\n\nСтатус: <code>⏳ В ожидании</code>'
    app_id = random.randint(10000000, 99999999)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('♻️ В работе', callback_data=f'app:1:{user_id}:{app_id}'))
    kb.insert(InlineKeyboardButton('✅ Готово', callback_data=f'app:2:{user_id}:{app_id}'))
    if way == 'ОИТ':
        chat_id = oit_chat_id
    elif way == 'АХЧ':
        chat_id = ahc_chat_id
    else:
        chat_id = drivers_chat_id
    send_msg = await bot.send_message(chat_id=chat_id, text=b_msg(msg), reply_markup=kb)
    await send_msg.pin(disable_notification=True)
    msg = f'✅ Ваша заявка #{app_id} отправлена, ожидайте обратной связи'
    return b_msg(msg)


async def new_status_msg(message_text, new_status, user_id, app_id):
    kb = InlineKeyboardMarkup()
    if new_status == '1':
        msg = message_text.replace("⏳ В ожидании", "♻️ В работе")
        kb.add(InlineKeyboardButton('✅ Готово', callback_data=f'app:2:{user_id}:{app_id}'))
    else:
        msg = message_text.replace("♻️ В работе", "✅ Готово").replace("⏳ В ожидании", "✅ Готово")
    try:
        await bot.send_message(chat_id=user_id, text=b_msg(f'🔔 Статус заявки #{app_id}: {"♻️ В работе" if new_status == "1" else "✅ Готово"}'))
    except Exception as ex:
        print(ex)
    return msg, kb


async def edit_description_msg(message_text, desc_text):
    if 'Примечание:' not in message_text:
        msg = (f'{message_text}\n\n'
               f'<b>Примечание: <code>{desc_text}</code></b>')
    else:
        text = message_text.split("\n\n<b>Примечание:")
        msg = (f'{text[0]}\n\n'
               f'<b>Примечание: <code>{desc_text}</code></b>')
    return msg

