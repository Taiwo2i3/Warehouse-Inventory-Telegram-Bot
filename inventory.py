from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InventoryItem:
    sku: str
    name: str
    quantity: int = 0
    low_stock_threshold: int = 5


@dataclass(frozen=True)
class StockMovement:
    sku: str
    delta: int
    reason: str
    actor: str = "system"


class Inventory:
    """In-memory inventory service. Data resets when the process restarts."""

    def __init__(self, initial_items: list[InventoryItem] | None = None) -> None:
        self._items: dict[str, InventoryItem] = {}
        self._movements: list[StockMovement] = []
        for item in initial_items or []:
            self.add_item(item)

    def add_item(self, item: InventoryItem) -> None:
        sku = item.sku.strip().upper()
        if not sku:
            raise ValueError("SKU cannot be empty")
        if not item.name.strip():
            raise ValueError("Item name cannot be empty")
        if sku in self._items:
            raise ValueError(f"SKU already exists: {sku}")
        if item.quantity < 0 or item.low_stock_threshold < 0:
            raise ValueError("Quantities and thresholds cannot be negative")
        item.sku = sku
        self._items[sku] = item

    def all_items(self) -> list[InventoryItem]:
        return sorted(self._items.values(), key=lambda item: item.sku)

    def get_item(self, sku: str) -> InventoryItem:
        key = sku.strip().upper()
        try:
            return self._items[key]
        except KeyError as exc:
            raise KeyError(f"Unknown SKU: {key}") from exc

    def receive(self, sku: str, quantity: int, reason: str = "received", actor: str = "system") -> InventoryItem:
        if quantity <= 0:
            raise ValueError("Receive quantity must be positive")
        return self._change(sku, quantity, reason, actor)

    def issue(self, sku: str, quantity: int, reason: str = "issued", actor: str = "system") -> InventoryItem:
        if quantity <= 0:
            raise ValueError("Issue quantity must be positive")
        item = self.get_item(sku)
        if item.quantity < quantity:
            raise ValueError(f"Insufficient stock for {item.sku}")
        return self._change(sku, -quantity, reason, actor)

    def adjust(self, sku: str, quantity: int, reason: str = "adjusted", actor: str = "system") -> InventoryItem:
        if quantity < 0:
            raise ValueError("Adjusted quantity cannot be negative")
        item = self.get_item(sku)
        delta = quantity - item.quantity
        if delta == 0:
            return item
        return self._change(sku, delta, reason, actor)

    def low_stock_items(self) -> list[InventoryItem]:
        return [item for item in self.all_items() if item.quantity <= item.low_stock_threshold]

    def movement_history(self) -> list[StockMovement]:
        return list(self._movements)

    def _change(self, sku: str, delta: int, reason: str, actor: str) -> InventoryItem:
        if delta == 0:
            raise ValueError("Stock change must not be zero")
        item = self.get_item(sku)
        new_quantity = item.quantity + delta
        if new_quantity < 0:
            raise ValueError("Stock cannot become negative")
        item.quantity = new_quantity
        self._movements.append(StockMovement(item.sku, delta, reason.strip() or "unspecified", actor))
        return item
