from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_function import *


api = '7037708319:AAFaxoOelXsZx_U5h7XzSwJJpa78tgNpilE'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

menu = ReplyKeyboardMarkup(keyboard=
    [[KeyboardButton(text='Записаться онлацй'),KeyboardButton(text="Информация"),
      KeyboardButton(text="Купить"), KeyboardButton(text="Регистрация")]
],
    resize_keyboard=True)

inline_choice = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
                 InlineKeyboardButton('Формула расчета', callback_data='formulas')]])

inline_products = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('Produkt1', callback_data='product_buying'),
                InlineKeyboardButton('Produkt2', callback_data='product_buying'),
                InlineKeyboardButton('Produkt3', callback_data='product_buying'),
                InlineKeyboardButton('Produkt4', callback_data='product_buying')
                ]
        ]
)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State('1000')


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    for index, product in enumerate(get_all_products()):
        await message.answer(f'Название: Product{product[1]} | Описание: {product[2]} | Цена: {product[3]}')
        print(f'Название: Product{product[1]} | Описание: {product[2]} | Цена: {product[3]}')
        with open(f'files/{index+1}.jpg', 'rb') as photo:
            await message.answer_photo(photo)
            print('Изображение отправлено')
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_products)
    print("Выберите продукт для покупки:")


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    print(f'Товар куплен:')

@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите ваше имя:')
    print('Введите ваше имя:')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите ваш email:')
        print('Введите ваш email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Имя занято. Введите другое имя:')
        print('Имя занято. Введите другое имя:')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите ваш возраст:')
    print('Введите ваш возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    if 120 >= int(message.text) >= 0:
        await state.update_data(age=message.text)
        data = await state.get_data()
        add_user(data['username'], data['email'], data['age'])
        await message.answer('Регистрация прошла успешно!')
        print('Регистрация прошла успешно!')
    else:
        await message.answer('Введите корректный возраст!')
        print('Введите корректный возраст!')
        await RegistrationState.age.set()
        await state.finish()

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите интересующий вас пункт', reply_markup=inline_choice)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула расчета: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст в годах:')
    print('Введите свой возраст в годах:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост в см:')
    print('Введите свой рост в см:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес в кг:')
    print('Введите свой вес в кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age'])
    await message.answer(calories)
    await state.finish()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=menu)

@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)