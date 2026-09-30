import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import patch as recipe


class ToolchainTest(unittest.TestCase):
    def test_wrong_compile_or_runtime_zlib_stops_before_download(self):
        for field in ("ZLIB_VERSION", "ZLIB_RUNTIME_VERSION"):
            with (
                self.subTest(field=field),
                patch.object(recipe.zlib, field, "other"),
                patch.object(recipe, "get_bytes") as download,
            ):
                with self.assertRaisesRegex(SystemExit, "Expected zlib 1.3.2"):
                    recipe.main()
                download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
