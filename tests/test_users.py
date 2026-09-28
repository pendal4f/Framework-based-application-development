import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from users import add_interest, add_user, find_user, remove_interest


def test_add_user():
    users = {}
    user_id = add_user(users, "Иван Петров", ["Музыка"])
    assert user_id == 1
    assert users[1]["interests"] == {"Музыка"}


def test_find_user():
    users = {}
    add_user(users, "Иван Петров")
    assert find_user(users, "иван")


def test_add_interest_no_duplicates():
    users = {}
    add_user(users, "Иван Петров")
    add_interest(users, 1, "Музыка")
    add_interest(users, 1, "Музыка")
    assert users[1]["interests"] == {"Музыка"}


def test_remove_interest():
    users = {}
    add_user(users, "Иван Петров", ["Музыка", "Кино"])
    assert remove_interest(users, 1, "Кино")
    assert users[1]["interests"] == {"Музыка"}
    assert not remove_interest(users, 1, "Спорт")
