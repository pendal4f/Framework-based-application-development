import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from categories import add_category, find_category_by_name, get_category


def test_add_category():
    categories = {}
    category_id = add_category(categories, "Музыка", "Музыкальные места")
    assert category_id == 1
    assert categories[1]["name"] == "Музыка"


def test_find_category_by_name():
    categories = {}
    add_category(categories, "Музыка")
    assert find_category_by_name(categories, "музыка")["id"] == 1
    assert find_category_by_name(categories, "Кино") is None


def test_get_category_raises_for_unknown_id():
    try:
        get_category({}, 1)
    except KeyError as error:
        assert "Категория" in str(error)
    else:
        assert False
