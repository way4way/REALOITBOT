from utils.other import b_msg
from data.sqlite import Database
from data.config import password
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


db = Database()


async def main_start_msg(user_id):
    user_info = await db.get_user(user_id=user_id)
    if user_info[2] == 0:
        msg = f'ℹ️ Для доступа к боту, введите пароль:'
        status = user_info[2]
    elif user_info[2] == 1:
        msg = (f'ℹ️ Заполните анкету для доступа к боту\n\n'
               f'✏️ Введите адрес:')
        status = user_info[2]
    else:
        msg = f'ℹ️ Выберите направление:'
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton('ОИТ'))
        kb.insert(KeyboardButton('АХЧ'))
        kb.insert(KeyboardButton('Водители'))
        status = kb
    return b_msg(msg), status


async def check_password_msg(user_id, writen_password):
    if writen_password == password:
        await db.update_user(user_id, is_user=1)
        msg = (f'ℹ️ Заполните анкету для доступа к боту\n\n'
               f'✏️ Введите адрес:')
        return b_msg(msg), True
    else:
        msg = f'❌ Введен неверный пароль, повторите ввод:'
        return b_msg(msg), False


class QueMsg:
    address_text = b_msg(f'✏️ Введите ваш адрес:')
    phone_number_text = b_msg(f'✏️ Введите ваш номер телефона:')
    pc_ip_text = b_msg(f'✏️ Введите айпи компьютера:')

    @staticmethod
    async def check_writen_info(address, phone, pc_ip):
        msg = (f'ℹ️ Проверьте введенную вами информацию\n\n'
               f'Адрес: <code>{address}</code>\n'
               f'Номер Телефона: <code>{phone}</code>\n'
               f'Айпи Компьютера: <code>{pc_ip}</code>\n\n'
               f'"✅" - Подтвердить данные | "❌" - Заполнить анкету заново')
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('✅', callback_data='1'))
        kb.insert(InlineKeyboardButton('❌', callback_data='2'))
        return b_msg(msg), kb

    @staticmethod
    async def commit_info(user_id, address, phone, pc_id):
        await db.update_user(user_id, address=address, phone=phone, pc_ip=pc_id, is_user=2)
        msg = (f'✅ Ваши данные сохранены\n\n'
               f'Адрес: <code>{address}</code>\n'
               f'Номер Телефона: <code>{phone}</code>\n'
               f'Айпи Компьютера: <code>{pc_id}</code>')
        return b_msg(msg)


class QueState(StatesGroup):
    address = State()
    phone = State()
    pc_ip = State()
    confirm = State()


