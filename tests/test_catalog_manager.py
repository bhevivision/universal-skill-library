import json
import tempfile
import unittest
from pathlib import Path
from shutil import copytree

from scripts.catalog_manager import CatalogError, get_entry, list_entries, put_entry, remove_entry, search_entries


class CatalogManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1] / "schemas"
        copytree(source, self.root / "schemas")
        (self.root / "catalog").mkdir()
        for name, collection in (
            ("skills", "skills"), ("capabilities", "capabilities"),
            ("implementations", "implementations"), ("materials", "materials")
        ):
            (self.root / "catalog" / f"{name}.json").write_text(
                json.dumps({"catalog_version": "1.0", collection: []}), encoding="utf-8"
            )

    def tearDown(self):
        self.temp.cleanup()

    def capability(self, entry_id="cap.read"):
        return {
            "id": entry_id,
            "name": "Lettura documenti",
            "description": "Legge documenti testuali.",
            "category": "documenti",
            "expected_result": "Contenuto estratto.",
            "verification_criteria": ["Il testo è recuperabile."],
            "status": "draft"
        }

    def test_add_list_show_and_search(self):
        put_entry(self.root, "capabilities", self.capability())
        self.assertEqual(list_entries(self.root, "capabilities")[0]["id"], "cap.read")
        self.assertEqual(get_entry(self.root, "capabilities", "cap.read")["name"], "Lettura documenti")
        self.assertEqual(len(search_entries(self.root, "capabilities", "documenti")), 1)

    def test_duplicate_add_is_rejected(self):
        put_entry(self.root, "capabilities", self.capability())
        with self.assertRaises(CatalogError):
            put_entry(self.root, "capabilities", self.capability())

    def test_update_replaces_existing_entry(self):
        put_entry(self.root, "capabilities", self.capability())
        updated = self.capability()
        updated["name"] = "Lettura e analisi documenti"
        put_entry(self.root, "capabilities", updated, replace=True)
        self.assertEqual(get_entry(self.root, "capabilities", "cap.read")["name"],
                         "Lettura e analisi documenti")

    def test_remove_deletes_entry(self):
        put_entry(self.root, "capabilities", self.capability())
        remove_entry(self.root, "capabilities", "cap.read")
        self.assertEqual(list_entries(self.root, "capabilities"), [])

    def test_invalid_entry_is_not_written(self):
        with self.assertRaises(CatalogError):
            put_entry(self.root, "capabilities", {"id": "bad"})
        self.assertEqual(list_entries(self.root, "capabilities"), [])


if __name__ == "__main__":
    unittest.main()
