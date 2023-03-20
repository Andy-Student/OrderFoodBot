from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext 
from keyboards.simple_row import make_row_keyboard

router = Router()



## Обработка шага 1

# Рассмотрим описание шагов для «заказа» еды. Создадим файл , где опишем
# списки блюд и их размеров (в реальной жизни эта информация может динамически
# подгружаться из какой-либо БД)

# Эти значения далее будут подставляться в итоговый текст, отсюда 
# такая на первый взгляд странная форма прилагательных
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]

#Для хранения состояний необходимо создать класс, наследующийся
# от класса , внутри него нужно создать переменные, присвоив им 
# экземпляры класса
class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()

#Напишем обработчик первого шага, реагирующий на команду /food

@router.message(Command(commands=["food"]))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(OrderFood.choosing_food_name)

"""Чтобы работать с механизмом FSM, в хэндлер необходимо прокинуть 
аргумент с именем , который будет иметь тип.
А в последней строке мы явно говорим боту встать в состояние из группы
await.state FSMContext choosing_food_name OrderFood"""

# Далее напишем хэндлер, который ловит один из вариантов блюд из нашего списка:
@router.message(
    OrderFood.choosing_food_name, 
    F.text.in_(available_food_names)
)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)

"""
Напишем дополнительный хэндлер, у которого будет фильтр только на 
состояние , а фильтра на текст не будет. Если расположить его под 
функцией , то получится «реагируй в состоянии choosing_food_name, 
на все тексты, кроме тех, что ловит предыдущий хэндлер» (иными словами,
«лови все неправильные варианты»).OrderFood.choosing_food_namefood_chosen()
"""
@router.message(OrderFood.choosing_food_name)
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(available_food_names)
    )

## Обработка шага 2

# Второй и последний этап — обработать ввод размера порции юзером.
# Аналогично предыдущему этапу сделаем два хэндлера (на верный и 
# неверный ответы), но в первом из них добавим выбор сводной информации о заказе:

@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
             f"Попробуйте теперь заказать напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого размера порции.\n\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )



