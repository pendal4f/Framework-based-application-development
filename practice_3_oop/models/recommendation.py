from __future__ import annotations

from .place import Place
from .user import User


class Recommendation:
    """Recommendation that links a user with a suitable place."""

    def __init__(
        self,
        recommendation_id: int,
        user: User,
        place: Place,
        is_cancelled: bool = False,
    ) -> None:
        self.id = recommendation_id
        self.user = user
        self.place = place
        self.is_cancelled = is_cancelled

    @property
    def status(self) -> str:
        return "отменена" if self.is_cancelled else "активна"

    def cancel(self) -> None:
        self.is_cancelled = True

    def to_data(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user.id,
            "place_id": self.place.id,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        return (
            f"{self.id}. {self.user.name} -> {self.place.name}, "
            f"статус: {self.status}"
        )
