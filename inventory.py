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
    """Small in-memory inventory service for local development and tests."""

    def __init__(self, initial_items: list[InventoryItem] | None = None) -> None:
        self._items = {item.sku: item for item in initial_items or []}
        self._movements: list[StockMovement] = []

    def add_item(self, item: InventoryItem) -> None:
        if item.sku in self._items:
            raise ValueError(f"SKU already exists: {item.sku}")
        if item.quantity < 0 or item.low_stock_threshold < 0:
            raise ValueError("Quantities and thresholds cannot be negative")
        self._items[item.sku] = item

    def get_item(self, sku: str) -> InventoryItem:
        try:
            return self._items[sku]
        except KeyError as exc:
            raise KeyError(f"Unknown SKU: {sku}") from exc

    def receive(self, sku: str, quantity: int, reason: str = "received", actor: str = "system") -> InventoryItem:
        return self._change(sku, quantity, reason, actor)

    def issue(self, sku: str, quantity: int, reason: str = "issued", actor: str = "system") -> InventoryItem:
        if quantity <= 0:
            raise ValueError("Issue quantity must be positive")
        item = self.get_item(sku)
        if item.quantity < quantity:
            raise ValueError(f"Insufficient stock for {sku}")
        return self._change(sku, -quantity, reason, actor)

    def adjust(self, sku: str, quantity: int, reason: str = "adjusted", actor: str = "system") -> InventoryItem:
        item = self.get_item(sku)
        delta = quantity - item.quantity
        return self._change(sku, delta, reason, actor)

    def low_stock_items(self) -> list[InventoryItem]:
        return [item for item in self._items.values() if item.quantity <= item.low_stock_threshold]

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
        self._movements.append(StockMovement(sku, delta, reason, actor))
        return item
