from loader import dp, bot
from utils.other import IsUser
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType
from design.main_start_msg import main_start_msg, QueMsg, QueState, check_password_msg


@dp.message_handler(IsUser(), commands=['start'], state="*")
async def start_handler(message: Message, state: FSMContext):
    await state.finish()
    msg, status = await main_start_msg(message.from_user.id)
    if status == 0:
        await message.answer(msg)
        await state.set_state('write_password')
    elif status == 1:
        await message.answer(msg)
        await QueState.address.set()
    else:
        await message.answer(msg, reply_markup=status)


@dp.message_handler(IsUser(), state='write_password')
async def check_password_handler(message: Message, state: FSMContext):
    msg, status = await check_password_msg(message.from_user.id, message.text)
    await message.answer(msg)
    if status:
        await QueState.address.set()
    else:
        await state.set_state('write_password')


@dp.message_handler(IsUser(), state=QueState.address)
async def write_address_handler(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer(QueMsg.phone_number_text)
    await QueState.phone.set()


@dp.message_handler(IsUser(), state=QueState.phone)
async def write_phone_handler(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(QueMsg.pc_ip_text)
    await QueState.pc_ip.set()


@dp.message_handler(IsUser(), state=QueState.pc_ip)
async def write_pc_ip_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(pc_ip=message.text)
    phone = data['phone']
    address = data['address']
    msg, kb = await QueMsg.check_writen_info(address, phone, message.text)
    await message.answer(msg, reply_markup=kb)
    await QueState.confirm.set()


@dp.callback_query_handler(IsUser(), state=QueState.confirm)
async def confirm_que_handler(call: CallbackQuery, state: FSMContext):
    answer = call.data
    if answer == '1':
        data = await state.get_data()
        phone = data['phone']
        address = data['address']
        pc_id = data['pc_ip']
        msg = await QueMsg.commit_info(call.from_user.id, address, phone, pc_id)
        await call.message.edit_text(msg)
        msg, kb = await main_start_msg(call.from_user.id)
        await call.message.answer(msg, reply_markup=kb)
        await state.finish()

    else:
        await state.finish()
        await call.message.edit_text(text=call.message.html_text.replace('"✅" - Подтвердить данные | "❌" - Заполнить анкету заново', ""))
        await call.message.answer(QueMsg.address_text)
        await QueState.address.set()


@dp.callback_query_handler(IsUser(), text='hide', state="*")
async def cancel_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()


