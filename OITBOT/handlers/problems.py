from loader import dp, bot
from utils.other import IsUser, cancel_kb
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType
from design.problems_msg import (write_oit_problem_text, write_ahc_problem_text, write_driver_order_text,
                                 check_problem_msg, send_problem_msg, edit_description_msg, new_status_msg)


@dp.message_handler(IsUser(), text='ОИТ', state="*")
async def oit_handler(message: Message, state: FSMContext):
    await state.finish()
    await message.delete()
    del_msg = await message.answer(write_oit_problem_text, reply_markup=cancel_kb)
    await state.update_data(way=message.text, del_msg=del_msg.message_id)
    await state.set_state('write_problem_desc')


@dp.message_handler(IsUser(), text='АХЧ', state="*")
async def ahc_handler(message: Message, state: FSMContext):
    await state.finish()
    await message.delete()
    del_msg = await message.answer(write_ahc_problem_text, reply_markup=cancel_kb)
    await state.update_data(way=message.text, del_msg=del_msg.message_id)
    await state.set_state('write_problem_desc')


@dp.message_handler(IsUser(), text='Водители', state="*")
async def ahc_handler(message: Message, state: FSMContext):
    await state.finish()
    await message.delete()
    del_msg = await message.answer(write_driver_order_text, reply_markup=cancel_kb)
    await state.update_data(way=message.text, del_msg=del_msg.message_id)
    await state.set_state('write_problem_desc')


@dp.message_handler(IsUser(), state='write_problem_desc')
async def write_problem_desc_handler(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    way = data['way']
    text = message.text
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['del_msg'])
    msg, kb = await check_problem_msg(way, text)
    await message.answer(msg, reply_markup=kb)
    await state.update_data(text=text)
    await state.set_state('confirm_send_req')


@dp.callback_query_handler(IsUser(), state='confirm_send_req')
async def confirm_send_req_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    way = data['way']
    text = data['text']
    user_id = call.from_user.id
    msg = await send_problem_msg(way, text, user_id)
    text = call.message.html_text.replace("заказ", "").replace("проблему", "")
    text = text.replace('"✅" - Отправить  в обработку | "❌" - Отменить отправку', "")
    text = f'{text}{msg}'
    await call.message.edit_text(text)


@dp.callback_query_handler(IsUser(), text_startswith='app:', state="*")
async def in_process_handler(call: CallbackQuery, state: FSMContext):
    new_status = call.data.split(":")[1]
    msg, kb = await new_status_msg(call.message.html_text, new_status, call.data.split(":")[2], call.data.split(":")[3])
    await call.message.edit_text(msg, reply_markup=kb)
    if new_status == '2':
        await call.message.unpin()


@dp.message_handler(IsUser(), state="*")
async def reply_handler(message: Message, state: FSMContext):
    is_reply = message.reply_to_message
    if is_reply:
        message_id = is_reply.message_id
        text = message.text
        msg = await edit_description_msg(is_reply.html_text, text)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text=msg,
                                    reply_markup=is_reply.reply_markup)
