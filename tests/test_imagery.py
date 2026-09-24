import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_esri_mosaic import fetch_tile
from refresh_imagery import specs, refresh


def jpeg(size=(256, 256)):
    data = io.BytesIO()
    Image.new("RGB", size, "#449977").save(data, "JPEG")
    return data.getvalue()


class ImageryTests(unittest.TestCase):
    def test_cached_tile_is_decoded_and_validated(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "tile.jpg"
            dest.write_bytes(jpeg())
            with patch("fetch_esri_mosaic.urllib.request.urlopen") as network:
                self.assertEqual(fetch_tile(1, 1, 1, dest).size, (256, 256))
                network.assert_not_called()

    def test_corrupt_cache_is_replaced_only_with_valid_image(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "tile.jpg"
            dest.write_bytes(b"bad cache" * 200)
            with patch("fetch_esri_mosaic.urllib.request.urlopen", return_value=io.BytesIO(jpeg())):
                self.assertEqual(fetch_tile(1, 1, 1, dest).size, (256, 256))
            with Image.open(dest) as image:
                self.assertEqual(image.size, (256, 256))

    def test_wrong_size_or_non_image_response_is_not_cached(self):
        for response in (jpeg((512, 512)), b"server error"):
            with self.subTest(response_size=len(response)), tempfile.TemporaryDirectory() as temp:
                dest = Path(temp) / "tile.jpg"
                with patch("fetch_esri_mosaic.urllib.request.urlopen", return_value=io.BytesIO(response)), patch("fetch_esri_mosaic.time.sleep"):
                    with self.assertRaises(RuntimeError):
                        fetch_tile(1, 1, 1, dest, retries=1)
                self.assertFalse(dest.exists())

    def test_failed_download_does_not_replace_published_images(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plate = root / "docs/plates/city/plate.jpg"
            plate.parent.mkdir(parents=True)
            plate.write_bytes(b"previous published plate")
            manifest = root / "docs/imagery.json"
            manifest.write_text("previous manifest")
            mosaics = {"city/raw.jpg": dict(lat=0, lon=0, z=1, half=0)}
            plates = [dict(src="city/raw.jpg", dest="city/plate.jpg")]
            with patch("refresh_imagery.ROOT", root), patch("refresh_imagery.specs", return_value=(mosaics, plates)), patch("refresh_imagery.fetch_tile", side_effect=RuntimeError("network failed")):
                with self.assertRaisesRegex(RuntimeError, "network failed"):
                    refresh(workers=1)
            self.assertEqual(plate.read_bytes(), b"previous published plate")
            self.assertEqual(manifest.read_text(), "previous manifest")

    def test_every_plate_has_reproducible_coordinates_and_all_cities_covered(self):
        mosaics, plates = specs()
        self.assertEqual(len({p["dest"].split("/")[0] for p in plates}), 11)
        self.assertEqual(len({p["dest"] for p in plates}), len(plates))
        for plate in plates:
            self.assertIn(plate["src"], mosaics)
            self.assertTrue(0 < mosaics[plate["src"]]["z"] <= 18)
            self.assertTrue(mosaics[plate["src"]]["half"] > 0)


if __name__ == "__main__":
    unittest.main()
