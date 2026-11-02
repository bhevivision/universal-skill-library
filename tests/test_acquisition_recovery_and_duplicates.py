import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.acquire_material import (
    DuplicateMaterialError,
    acquire_material,
    recover_interrupted_acquisitions,
)
from test_validate_library import make_repo


class AcquisitionRecoveryAndDuplicateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "library"
        self.root.mkdir()
        make_repo(self.root)
        self.incoming = Path(self.temp.name) / "incoming"
        self.incoming.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def catalog(self):
        return json.loads((self.root / "catalog/materials.json").read_text(encoding="utf-8"))

    def write_stale_lock(self):
        lock = self.root / ".materials-acquisition.lock"
        process = subprocess.Popen([sys.executable, "-c", "pass"])
        process.wait()
        lock.write_text(json.dumps({
            "pid": process.pid,
            "hostname": socket.gethostname(),
            "created_at": "2020-01-01T00:00:00Z"
        }), encoding="utf-8")
        return lock

    def test_rejects_intake_directory_symlink(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        import shutil
        shutil.rmtree(self.root / "intake")
        try:
            (self.root / "intake").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Il sistema operativo non consente la creazione di collegamenti simbolici.")
        source = self.incoming / "outside.txt"
        source.write_text("contenuto", encoding="utf-8")
        with self.assertRaises(ValueError):
            acquire_material(self.root, source, "acq.outside")
        self.assertEqual(list(outside.iterdir()), [])

    def test_rejects_identical_file_content_under_a_different_identifier(self):
        first = self.incoming / "first.txt"
        second = self.incoming / "renamed-copy.txt"
        first.write_bytes(b"same bytes")
        second.write_bytes(b"same bytes")
        acquire_material(self.root, first, "acq.first")

        with self.assertRaises(DuplicateMaterialError) as caught:
            acquire_material(self.root, second, "acq.second")

        self.assertIn("acq.first", caught.exception.existing_ids)
        self.assertEqual(len(self.catalog()["materials"]), 1)
        self.assertFalse((self.root / "intake/acq-second").exists())

    def test_rejects_identical_directory_content_under_a_different_identifier(self):
        first = self.incoming / "folder-one"
        second = self.incoming / "folder-two"
        (first / "empty").mkdir(parents=True)
        (second / "empty").mkdir(parents=True)
        (first / "guide.txt").write_text("identico", encoding="utf-8")
        (second / "guide.txt").write_text("identico", encoding="utf-8")
        acquire_material(self.root, first, "acq.folder-one", kind="package")

        with self.assertRaises(DuplicateMaterialError):
            acquire_material(self.root, second, "acq.folder-two", kind="package")

        self.assertEqual(len(self.catalog()["materials"]), 1)

    def test_recovery_finishes_catalog_registration_after_publish_crash(self):
        source = self.incoming / "recovered.txt"
        source.write_bytes(b"recover me")
        record = acquire_material(self.root, source, "acq.seed")
        catalog = self.catalog()
        catalog["materials"].clear()
        (self.root / "catalog/materials.json").write_text(json.dumps(catalog), encoding="utf-8")
        destination = self.root / "intake/acq-recovered"
        destination.mkdir(parents=True)
        (destination / "source").mkdir()
        (destination / "source/recovered.txt").write_bytes(b"recover me")
        record["id"] = "acq.recovered"
        record["acquisition"]["original"]["path"] = "intake/acq-recovered/source/recovered.txt"
        transactions = self.root / "intake/.transactions"
        transactions.mkdir(parents=True)
        (transactions / "acq-recovered.json").write_text(json.dumps({
            "version": 1,
            "id": "acq.recovered",
            "stage": None,
            "destination": "acq-recovered",
            "record": record
        }), encoding="utf-8")
        self.write_stale_lock()

        recovered = recover_interrupted_acquisitions(self.root)

        self.assertEqual(recovered["completed"], ["acq.recovered"])
        self.assertEqual([item["id"] for item in self.catalog()["materials"]], ["acq.recovered"])
        self.assertFalse((transactions / "acq-recovered.json").exists())
        self.assertFalse((self.root / ".materials-acquisition.lock").exists())

    def test_recovery_discards_unpublished_staging_directory(self):
        staging = self.root / "intake/.staging-acq-abandoned-random"
        staging.mkdir(parents=True)
        (staging / "partial.bin").write_bytes(b"partial")
        self.write_stale_lock()

        recovered = recover_interrupted_acquisitions(self.root)

        self.assertEqual(recovered["discarded_staging"], [staging.name])
        self.assertFalse(staging.exists())
        self.assertEqual(self.catalog()["materials"], [])

    def test_recovery_refuses_lock_owned_by_a_live_process(self):
        lock = self.root / ".materials-acquisition.lock"
        lock.write_text(json.dumps({
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "created_at": "2020-01-01T00:00:00Z"
        }), encoding="utf-8")

        with self.assertRaises(RuntimeError):
            recover_interrupted_acquisitions(self.root)

        self.assertTrue(lock.exists())


if __name__ == "__main__":
    unittest.main()
