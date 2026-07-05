from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import config

router = Router()

class OrderState(StatesGroup):
    waiting_for_text = State()


def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="ℹ️ О нас", callback_data="about")
    builder.button(text="🛠️ Услуги и цены", callback_data="services")
    builder.button(text="🎁 Получить подарок", callback_data="gift")
    builder.button(text="✍️ Оставить заявку", callback_data="make_order")
    builder.adjust(2, 1, 1)
    return builder.as_markup()



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(config.TEXTS["start"], reply_markup=get_main_menu())


# Обработка нажатий на кнопки
@router.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    await callback.message.answer(config.TEXTS["about"], reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "services")
async def show_services(callback: CallbackQuery):
    await callback.message.answer(config.TEXTS["services"], reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "gift")
async def show_gift(callback: CallbackQuery):
    await callback.message.answer(config.TEXTS["lead_magnet"], reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()

# Начало процесса сбора заявки
@router.callback_query(F.data == "make_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(config.TEXTS["order_start"])
    await state.set_state(OrderState.waiting_for_text)
    await callback.answer()




@router.message(OrderState.waiting_for_text)
async def process_order(message: Message, state: FSMContext):
    user = message.from_user


    admin_text = (
        f"🚨 <b>Новая заявка в боте!</b>\n\n"
        f"👤 <b>Отправитель:</b> {user.full_name} (@{user.username if user.username else 'нет_юзернейма'})\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
        f"📋 <b>Текст задачи:</b>\n{message.text}"
    )

    try:
        await message.bot.send_message(chat_id=config.ADMIN_ID, text=admin_text, parse_mode="HTML")

        await message.answer("✅ Ваша заявка успешно отправлена! Менеджер напишет вам.", reply_markup=get_main_menu())
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")
        await message.answer("⚠️ Произошла ошибка при отправке заявки. Проверьте ADMIN_ID в конфиге.",
                             reply_markup=get_main_menu())

    await state.clear()

@router.message()
async def handle_unknown_messages(message: Message):
    await message.answer(
        "🤖 Я вас не совсем понял. Пожалуйста, используйте кнопки меню для навигации 👇",
        reply_markup=get_main_menu()
    )
