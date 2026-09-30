from __future__ import annotations

from .category import Category


class Place:
    """Place that can be recommended to users."""

    def __init__(
        self,
        place_id: int,
        name: str,
        category: Category,
        address: str,
        rating: int,
        is_available: bool = True,
    ) -> None:
        if not self.is_valid_rating(rating):
            raise ValueError("Рейтинг места должен быть от 0 до 10")
        self.id = place_id
        self.name = name
        self.category = category
        self.address = address
        self.rating = rating
        self.is_available = is_available

    @staticmethod
    def is_valid_rating(rating: int) -> bool:
        return 0 <= rating <= 10

    def matches_category(self, category: Category) -> bool:
        return self.category.id == category.id

    def is_suitable_for_interest(self, interest: str, min_rating: int) -> bool:
        return (
            self.category.name == interest
            and self.rating >= min_rating
            and self.is_available
        )

    def to_data(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category.id,
            "address": self.address,
            "rating": self.rating,
            "is_available": self.is_available,
        }

    def __str__(self) -> str:
        status = "доступно" if self.is_available else "недоступно"
        return (
            f"{self.id}. {self.name} ({self.category.name}) - "
            f"{self.address}, рейтинг {self.rating}, {status}"
        )
