import unittest

from inventory import Inventory, InventoryItem


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = Inventory([
            InventoryItem("SKU-1", "Sample item", quantity=10, low_stock_threshold=3)
        ])

    def test_receive_increases_stock_and_records_movement(self) -> None:
        item = self.inventory.receive("SKU-1", 5, actor="tester")
        self.assertEqual(item.quantity, 15)
        self.assertEqual(len(self.inventory.movement_history()), 1)

    def test_issue_decreases_stock(self) -> None:
        item = self.inventory.issue("SKU-1", 4)
        self.assertEqual(item.quantity, 6)

    def test_issue_rejects_insufficient_stock(self) -> None:
        with self.assertRaises(ValueError):
            self.inventory.issue("SKU-1", 11)

    def test_unknown_sku_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.inventory.get_item("MISSING")

    def test_low_stock_filter(self) -> None:
        self.inventory.issue("SKU-1", 7)
        self.assertEqual([item.sku for item in self.inventory.low_stock_items()], ["SKU-1"])

    def test_duplicate_sku_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.inventory.add_item(InventoryItem("SKU-1", "Duplicate"))

    def test_negative_receive_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.inventory.receive("SKU-1", -2)


if __name__ == "__main__":
    unittest.main()
