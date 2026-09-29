from __future__ import annotations


class User:
    """User of the place recommendation service."""

    def __init__(self, user_id: int, name: str, interests: list[str] | None = None) -> None:
        self.id = user_id
        self.name = name
        self.interests = set(interests or [])

    @classmethod
    def from_data(cls, data: dict) -> "User":
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            interests=list(data.get("interests", [])),
        )

    def add_interest(self, interest: str) -> None:
        self.interests.add(interest)

    def remove_interest(self, interest: str) -> bool:
        if interest in self.interests:
            self.interests.remove(interest)
            return True
        return False

    def has_interest(self, category_name: str) -> bool:
        return category_name in self.interests

    def to_data(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "interests": sorted(self.interests),
        }

    def __str__(self) -> str:
        interests = ", ".join(sorted(self.interests)) or "нет интересов"
        return f"{self.id}. {self.name} - интересы: {interests}"
