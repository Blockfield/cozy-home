import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import patch as recipe


class ModelPatchTests(unittest.TestCase):
    def fixture(self, root, *, omit=None, texture_drift=False):
        entries = {
            "fabric.mod.json": b'{"id":"fixture"}',
            "assets/cozyhome/textures/unrelated.png": b"untouched",
        }
        for entry, old, _ in recipe.JARS[0]["replace"]:
            if entry != omit:
                entries[entry] = json.dumps(
                    {
                        "parent": "fixture",
                        "textures": {
                            "water": "cozyhome:block/new" if texture_drift else old
                        },
                        "ambientocclusion": False,
                    }
                ).encode()
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            for name, payload in entries.items():
                archive.writestr(zipfile.ZipInfo(name, (2020, 2, 3, 4, 5, 6)), payload)
        spec = {**recipe.JARS[0], "sha512": hashlib.sha512(data.getvalue()).hexdigest()}
        local = root / "files/mods" / spec["upstream_name"]
        local.parent.mkdir(parents=True)
        local.write_bytes(data.getvalue())
        return spec, entries

    def build(self, root, spec):
        with (
            patch.object(recipe, "ROOT", root),
            patch.object(recipe, "JARS", [spec]),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            recipe.main()
        return root / spec["out"]

    def test_all_water_textures_are_repaired_without_changing_other_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec, original = self.fixture(root)
            output = self.build(root, spec)
            first = output.read_bytes()
            self.build(root, spec)
            self.assertEqual(first, output.read_bytes())
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(set(original), set(archive.namelist()))
                for entry, _, new in spec["replace"]:
                    result = json.loads(archive.read(entry))
                    expected = json.loads(original[entry])
                    expected["textures"]["water"] = new
                    self.assertEqual(expected, result)
                    self.assertEqual(
                        (2020, 2, 3, 4, 5, 6), archive.getinfo(entry).date_time
                    )
                self.assertEqual(
                    original["assets/cozyhome/textures/unrelated.png"],
                    archive.read("assets/cozyhome/textures/unrelated.png"),
                )

    def test_missing_model_or_changed_texture_fails_closed(self):
        for variation in (
            {"omit": recipe.JARS[0]["replace"][0][0]},
            {"texture_drift": True},
        ):
            with (
                self.subTest(variation=variation),
                tempfile.TemporaryDirectory() as temporary,
            ):
                root = Path(temporary)
                spec, _ = self.fixture(root, **variation)
                with self.assertRaises(SystemExit):
                    self.build(root, spec)

    def test_wrong_checksum_preserves_candidate_and_does_not_fetch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec, _ = self.fixture(root)
            output = root / spec["out"]
            output.write_bytes(b"reviewed candidate")
            spec["sha512"] = "0" * 128
            with (
                patch.object(recipe, "get_bytes") as fetch,
                self.assertRaisesRegex(SystemExit, "sha512"),
            ):
                self.build(root, spec)
            fetch.assert_not_called()
            self.assertEqual(b"reviewed candidate", output.read_bytes())


if __name__ == "__main__":
    unittest.main()
