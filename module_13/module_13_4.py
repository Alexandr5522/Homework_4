from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup


api = ""
bot = Bot(token= api)
dp = Dispatcher(bot, storage= MemoryStorage())

class UserState(StatesGroup):
    # Эта группа(класс) будет использоваться в цепочке вызовов message_handler'ов
    age = State() # возраст
    growth = State() # рост
    weight = State() # вес
    active = State() # активность

@dp.message_handler(text=['Калории']) # хендлер реагирует на сообщение start
async def set_age(message): # функция
    await message.answer('Введите свой возраст.') # отправляет ответ
    await UserState.age.set() # ожидает ввода возраста в атрибут UserState.age при помощи метода set.

@dp.message_handler(state=UserState.age) # реагирует на переданное состояние UserState.age
async def set_growth(message, state): # ф-я обновляет данные в состоянии age на message.text (нап-е польз-м сообщение.)
    await state.update_data(first=message.text) # обновляет с помощью метода update_data
    await message.answer('Введите свой рост в см.') # отвечает в телеграмм-бот
    await UserState.growth.set() # ожидает ввода роста в атрибут UserState.growth при помощи метода set

@dp.message_handler(state=UserState.growth) # как в предыдущей функции
async def set_weight(message, state):
    await state.update_data(second=message.text)
    await message.answer('Введите свой вес в кг.')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def set_active(message, state): # ф-я просит пол-ля выбрать коэффициент активности
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
async def send_calories(message, state):
    await state.update_data(fourth=message.text)
    data = await state.get_data()
    res = (10 * int(data['third']) + 6.25 * int(data['second']) - 5 * int(data['first']) + 5) * float(data['fourth'])
    await message.answer(f'Ваша норма калорий {res} ккал/сутки.\n\nБлагодарим за обращение!')
    await state.finish()
    # res = (10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5) * активность

@dp.message_handler() # хендлер реагирует на любые сообщения
async def all_messages(message): # функция просит ввести конкретную команду
    await message.answer('Здравствуйте!\n'
                         'Желаете рассчитать суточную норму калорий?\n'
                         'Введите, пожалуйста, Калории.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)