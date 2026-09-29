from __future__ import annotations


class Category:
    """Category that describes a user's interest and a place direction."""

    def __init__(self, category_id: int, name: str, description: str = "") -> None:
        self.id = category_id
        self.name = name
        self.description = description

    @classmethod
    def from_data(cls, data: dict) -> "Category":
        return cls(
            category_id=int(data["id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
        )

    def matches(self, query: str) -> bool:
        return self.name.lower() == query.lower()

    def to_data(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def __str__(self) -> str:
        return f"{self.id}. {self.name} - {self.description}"
