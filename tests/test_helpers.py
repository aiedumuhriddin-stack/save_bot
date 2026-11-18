import unittest
from utils.helpers import (
    is_valid_url,
    is_youtube_url,
    is_instagram_url,
    clean_filename,
    extract_supported_url,
)


class URLValidationTests(unittest.TestCase):
    def test_youtube_hosts(self):
        self.assertTrue(is_youtube_url("https://youtu.be/abc123"))
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=abc123"))

    def test_instagram_hosts(self):
        self.assertTrue(is_instagram_url("https://www.instagram.com/reel/abc123/"))
        self.assertTrue(is_instagram_url("https://instagr.am/p/abc123/"))

    def test_rejects_lookalike_hosts(self):
        self.assertFalse(is_youtube_url("https://youtube.com.attacker.example/video"))
        self.assertFalse(is_instagram_url("https://instagram.com.attacker.example/p/1"))

    def test_valid_url_rejects_credentials_and_other_schemes(self):
        self.assertFalse(is_valid_url("javascript:alert(1)"))
        self.assertFalse(is_valid_url("https://user:pass@youtube.com/watch?v=1"))
        self.assertTrue(is_valid_url("https://youtube.com/watch?v=1"))

    def test_filename_is_safe(self):
        self.assertEqual(clean_filename("../hello?.mp4"), "_hello_.mp4")
        self.assertEqual(clean_filename("   "), "media")

    def test_extracts_supported_link_from_text(self):
        self.assertEqual(
            extract_supported_url("Mana video: https://youtu.be/abc123. Yuklab ol!"),
            "https://youtu.be/abc123",
        )
        self.assertEqual(
            extract_supported_url("https://www.instagram.com/reel/abc123/"),
            "https://www.instagram.com/reel/abc123/",
        )

    def test_extract_rejects_unsupported_and_lookalike_links(self):
        self.assertIsNone(extract_supported_url("https://example.com/video"))
        self.assertIsNone(extract_supported_url("https://youtube.com.attacker.example/video"))
        self.assertIsNone(extract_supported_url("odd text without a link"))


if __name__ == "__main__":
    unittest.main()
