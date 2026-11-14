import copy

import pytest

from solutions import (
    available, cook_book, manufacturers, mentors, models, person,
    repair_pc, shopping_list, unique_names,
)

# ---------- Задание 1: unique_names ----------

EXPECTED_NAMES = (
    'Адилет, Азамат, Александр, Алексей, Алена, Анатолий, Анна, Антон, Вадим, '
    'Валерий, Владимир, Денис, Дмитрий, Евгений, Елена, Иван, Илья, Кирилл, '
    'Константин, Максим, Михаил, Никита, Николай, Олег, Павел, Ринат, Роман, '
    'Сергей, Татьяна, Тимур, Филипп, Эдгар, Юрий'
)


@pytest.mark.parametrize('names, expected', [
    ([], ''),
    (['Иван Петров'], 'Иван'),
    (['Иван Петров', 'Иван Сидоров'], 'Иван'),                       # повторы убираются
    (['Олег Булыгин', 'Анна Юшина', 'Евгений Шек'], 'Анна, Евгений, Олег'),   # сортировка
    (['Алексей Степанов', 'Александр Иванов', 'Алена Батицкая'],
     'Александр, Алексей, Алена'),                                   # общий префикс «Але»
], ids=['empty', 'single', 'duplicates', 'sorting', 'common_prefix'])
def test_unique_names(names, expected):
    assert unique_names(names) == expected


def test_unique_names_full_list():
    result = unique_names(mentors)
    assert isinstance(result, str)
    assert result == EXPECTED_NAMES


# ---------- Задание 2: repair_pc ----------

@pytest.mark.parametrize('disks, in_stock, allowed, expected', [
    (['A Samsung', 'B WD', 'C Kingston'], [1, 1, 1], ['Samsung', 'WD'],
     (['A Samsung', 'B WD'], 2)),
    (['A Samsung', 'B WD'], [0, 0], ['Samsung', 'WD'], ([], 0)),      # ничего нет в наличии
    (['A Samsung', 'B WD'], [1, 0], ['Samsung', 'WD'], (['A Samsung'], 1)),   # часть в наличии
    (['A Kingston', 'B ADATA'], [1, 1], ['Samsung', 'WD'], ([], 0)),  # нет разрешённых
    (['A Samsung'], [1], [], ([], 0)),                                # пустой список производителей
    ([], [], ['Samsung'], ([], 0)),                                   # пустой магазин
], ids=['mixed', 'none_in_stock', 'partly_in_stock', 'no_allowed_brand',
        'no_manufacturers', 'empty_shop'])
def test_repair_pc(disks, in_stock, allowed, expected):
    assert repair_pc(disks, in_stock, allowed) == expected


def test_repair_pc_task_data():
    assert repair_pc(models, available, manufacturers) == (
        ['500 ГБ 2.5" SATA накопитель Samsung 870 EVO',
         '480 ГБ 2.5" SATA накопитель WD Green'],
        2,
    )


def test_repair_pc_overlapping_manufacturers():
    # диск подходит сразу под два названия из списка, но купить его можно только один раз
    disk = ['480 ГБ 2.5" SATA накопитель WD Green']
    assert repair_pc(disk, [1], ['WD', 'WD Green']) == (disk, 1)


# ---------- Задание 3: shopping_list ----------

SMALL_BOOK = [
    ['Чай', [['вода', 200, 'мл.']]],
    ['Салат', [['картофель', 100, 'гр.'], ['морковь', 50, 'гр.']]],
]


@pytest.mark.parametrize('book, persons, expected', [
    (SMALL_BOOK[:1], 1, ['Чай: вода 200 мл.']),        # один ингредиент: без запятой в конце
    (SMALL_BOOK[:1], 3, ['Чай: вода 600 мл.']),
    (SMALL_BOOK, 2, ['Чай: вода 400 мл.', 'Салат: картофель 200 гр., морковь 100 гр.']),
    (SMALL_BOOK, 0, ['Чай: вода 0 мл.', 'Салат: картофель 0 гр., морковь 0 гр.']),
    ([], 5, []),
], ids=['one_ingredient', 'three_persons', 'two_dishes', 'zero_persons', 'empty_book'])
def test_shopping_list(book, persons, expected):
    assert shopping_list(book, persons) == expected


def test_shopping_list_task_data():
    assert shopping_list(cook_book, person) == [
        'Салат: картофель 500 гр., морковь 250 гр., огурцы 250 гр., горошек 150 гр., майонез 350 мл.',
        'Пицца: сыр 250 гр., томаты 250 гр., тесто 500 гр., бекон 150 гр., колбаса 150 гр., грибы 100 гр.',
        'Фруктовый десерт: хурма 300 гр., киви 300 гр., творог 300 гр., сахар 50 гр., мед 250 мл.',
    ]


def test_shopping_list_does_not_change_cook_book():
    original = copy.deepcopy(cook_book)
    shopping_list(cook_book, person)
    assert cook_book == original
