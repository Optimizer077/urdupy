"""Dependency metadata contracts without importing optional frameworks."""

from pathlib import Path
import tomllib
import unittest


class PackagingMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    def test_core_keeps_its_existing_identity_and_no_runtime_dependencies(self):
        self.assertEqual(self.project["name"], "urdupy-design-lab")
        self.assertEqual(self.project["dependencies"], [])
        self.assertEqual(self.project["scripts"]["urdupy"], "urdupy.cli:main")

    def test_science_profile_uses_one_opencv_provider_and_is_included_in_ai(self):
        extras = self.project["optional-dependencies"]
        self.assertEqual(set(extras), {"science", "ai"})
        self.assertTrue(set(extras["science"]).issubset(extras["ai"]))
        for requirements in extras.values():
            opencv = [r for r in requirements if r.startswith("opencv-")]
            self.assertEqual(opencv, ["opencv-python-headless==5.0.0.93"])

    def test_ai_profile_covers_training_plotting_and_nlp_without_device_urls(self):
        requirements = self.project["optional-dependencies"]["ai"]
        expected = {"numpy", "Pillow", "opencv-python-headless", "torch", "torchvision",
                    "transformers", "matplotlib", "arabic-reshaper", "python-bidi"}
        self.assertEqual({r.split("==")[0] for r in requirements}, expected)
        self.assertEqual(len(requirements), len(expected))
        for requirement in requirements:
            self.assertIn("==", requirement)
            self.assertNotIn("+", requirement, "CPU/CUDA build suffix belongs to user's selected wheel")
            self.assertNotIn("http", requirement)
            self.assertNotIn(";", requirement, "Do not silently skip requested dependencies by interpreter")


if __name__ == "__main__":
    unittest.main()
