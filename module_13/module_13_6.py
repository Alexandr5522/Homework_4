from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(keyboard=[[
    KeyboardButton(text="Информация"), KeyboardButton(text="Рассчитать")]],
    resize_keyboard=True, input_field_placeholder='Выберите кнопку')

ikb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')],
    [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')]])


class UserState(StatesGroup):
    # Эта группа(класс) будет использоваться в цепочке вызовов message_handler'ов
    age = State()  # возраст
    growth = State()  # рост
    weight = State()  # вес
    active = State()  # активность
    gender = State()  # пол


@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await message.answer('Привет! Я твой помощник.', reply_markup=kb)  # reply_markup добавляет кнопки после сообщения


@dp.message_handler(text=["Информация"])
async def inform(message):
    await message.answer(text='Рассчитываю суточную норму калорий.')


@dp.message_handler(text=["Рассчитать"])
async def main_menu(message):
    await message.answer(text='Выберите опцию:', reply_markup=ikb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(text='Формулы расчета Миффлина-Сан Жеора.\n\n'
                                   'Для мужчин:\n'
                                   'Калории = (10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5) * активность\n\n'
                                   'Для женщин:\n'
                                   'калории = (10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161) * активность')
    await call.answer()


@dp.callback_query_handler(text=['calories'])
async def set_age(call):  # функция
    await call.message.answer('Введите свой возраст.')  # отправляет ответ
    await call.answer()
    await UserState.age.set()  # ожидает ввода возраста в атрибут UserState.age при помощи метода set.


@dp.message_handler(state=UserState.age)  # реагирует на переданное состояние UserState.age
async def set_growth(message, state):  # ф-я обновляет данные в состоянии age на message.text (нап-е польз-м сообщение.)
    await state.update_data(first=message.text)  # обновляет с помощью метода update_data
    await message.answer('Введите свой рост в см.')  # отвечает в телеграмм-бот
    await UserState.growth.set()  # ожидает ввода роста в атрибут UserState.growth при помощи метода set


@dp.message_handler(state=UserState.growth)  # как в предыдущей функции
async def set_weight(message, state):
    await state.update_data(second=message.text)
    await message.answer('Введите свой вес в кг.')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_active(message, state):  # ф-я просит пол-ля выбрать коэффициент активности
    await state.update_data(third=message.text)
    await message.answer('Введите коэффициент активности:\n\n'
                         ' - Коэффициент 1.2 - сидячий образ жизни: офисная работа,'
                         ' минимальная физическая активность;\n\n'
                         ' - Коэффициент 1.375 - маленькая активность: легкая физическая нагрузка или занятия спортом '
                         '1-3 раза в неделю - ;\n\n'
                         ' - Коэффициент 1.55 - умеренная активность: занятия спортом 3-5 раз в неделю;\n\n'
                         ' - Коэффициент 1.725 - высокая активность: интенсивные занятия спортом 6-7 раз в неделю;\n\n'
                         ' - Коэффициент 1.9 экстремальная активность: ежедневные интенсивные тренировки или'
                         'физическая работа.')
    await UserState.active.set()


@dp.message_handler(state=UserState.active)
async def set_gender(message, state):  # ф-я просит пол-ля выбрать пол
    await state.update_data(fourth=message.text)
    await message.answer('Введите пол: мужской или женский')
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def send_calories(message, state):
    await state.update_data(fifth=message.text)
    data = await state.get_data()
    if int(data['fifth'] == 'мужской'):
        res = int((10 * int(data['third']) + 6.25 * int(data['second']) - 5 * int(data['first']) + 5)
                  * float(data['fourth']))
        await message.answer(f'Ваша норма калорий {res} ккал/сутки.\n\nБлагодарим за обращение!')
        await state.finish()
    if int(data['fifth'] == 'женский'):
        res = int((10 * int(data['third']) + 6.25 * int(data['second']) - 5 * int(data['first']) - 161)
                  * float(data['fourth']))
        await message.answer(f'Ваша норма калорий {res} ккал/сутки.\n\nБлагодарим за обращение!')
        await state.finish()
    # res = (10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161) * активность (для женщин)
    # res = (10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5) * активность (для мужчин)


@dp.message_handler()  # хендлер реагирует на любые сообщения
async def all_messages(message: types.Message):  # функция просит ввести конкретную команду
    await message.answer(text='Привет!', reply_markup=kb)  # повторно добавляет сообщения


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
