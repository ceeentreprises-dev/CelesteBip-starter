"""Tests unitaires de CelestBIP Starter (bibliothèque standard uniquement).

Lancer : python -m unittest discover -s tests -v
"""
import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import CELESTBIP_MASTER as cb  # noqa: E402


class IbanTests(unittest.TestCase):
    def test_valid_example(self):
        self.assertTrue(cb.valid_swiss_iban("CH93 0076 2011 6238 5295 7"))

    def test_wrong_checksum(self):
        self.assertFalse(cb.valid_swiss_iban("CH94 0076 2011 6238 5295 7"))

    def test_wrong_country_or_length(self):
        self.assertFalse(cb.valid_swiss_iban("FR7630006000011234567890189"))
        self.assertFalse(cb.valid_swiss_iban("CH93"))


class MarkdownTests(unittest.TestCase):
    def test_md_to_html_escapes_and_lists(self):
        title, meta, body = cb.md_to_html("# T <x>\n2026 · r\n## S\n- a\n- b\ntexte <b>")
        self.assertEqual(title, "T <x>")
        self.assertIn("<h2>S</h2>", body)
        self.assertIn("<ul>\n<li>a</li>\n<li>b</li>\n</ul>", body)
        self.assertIn("&lt;b&gt;", body)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._old = (cb.DIST, cb.RELEASE, cb.CONFIG_FILE)
        cb.DIST, cb.RELEASE, cb.CONFIG_FILE = tmp / "dist", tmp / "release", tmp / "support-approved.json"

    def tearDown(self):
        cb.DIST, cb.RELEASE, cb.CONFIG_FILE = self._old
        self._tmp.cleanup()

    def test_build_passes_checks(self):
        cb.build()
        self.assertEqual(cb.checks(), [])

    def test_only_stripe_links_become_buttons(self):
        html = cb.offers_html([("A", "1 CHF", "d", "https://buy.stripe.com/abc"),
                               ("B", "2 CHF", "d", "https://evil.example/pay"),
                               ("C", "3 CHF", "d", ""),
                               ("D", "4 CHF", "d", "https://www.paypal.com/ncp/payment/PLB-X")])
        self.assertIn('href="https://www.paypal.com/ncp/payment/PLB-X"', html)
        self.assertIn('href="https://buy.stripe.com/abc"', html)
        self.assertNotIn("evil.example", html)
        self.assertEqual(html.count("bientôt disponible"), 2)

    def test_pme_workshop_is_displayed_without_payment_link(self):
        offer = next(item for item in cb.OFFERS if item[0].startswith("Atelier PME"))
        self.assertEqual(offer[0], "Atelier PME sur site (3 h, jusqu'à 12 personnes)")
        self.assertEqual(offer[1], "900 CHF")
        self.assertEqual(offer[3], "")
        card = cb.offers_html([offer])
        self.assertIn("900 CHF", card)
        self.assertIn("bientôt disponible", card)
        self.assertNotIn("href=", card)

    def test_partners_page_is_generated_linked_and_in_sitemap(self):
        cb.build()
        page = (cb.DIST / "partenaires.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Partenaires</h1>", page)
        self.assertIn("aucun partenaire signé", page)
        self.assertIn('href="partenaires.html"', (cb.DIST / "index.html").read_text())
        self.assertIn(cb.SITE_URL + "partenaires.html", (cb.DIST / "sitemap.xml").read_text())

    def test_checks_refuse_a_similar_unapproved_github_owner(self):
        cb.build()
        index = cb.DIST / "index.html"
        index.write_text(index.read_text().replace(cb.CONTACT_URL,
                         "https://github.com/ceeentreprises-dev-evil/repo"), encoding="utf-8")
        self.assertIn("external_links_allowed_only", cb.checks())

    def test_privacy_article_is_listed_and_generated(self):
        source = cb.ARTICLES / "07-donnees-personnelles.md"
        words = " ".join(source.read_text().splitlines()[2:]).split()
        self.assertGreaterEqual(len(words), 300)
        self.assertLessEqual(len(words), 500)
        cb.build()
        path = "article-07-donnees-personnelles.html"
        self.assertIn(f'href="{path}"', (cb.DIST / "index.html").read_text())
        self.assertIn("<h1>IA et données personnelles au quotidien</h1>",
                      (cb.DIST / path).read_text(encoding="utf-8"))

    def test_skip_link_stays_in_each_page_with_a_keyboard_target(self):
        class Elements(HTMLParser):
            def __init__(self):
                super().__init__()
                self.elements = []
            def handle_starttag(self, tag, attrs):
                self.elements.append((tag, dict(attrs)))
        cb.build()
        for path in cb.DIST.glob("*.html"):
            with self.subTest(page=path.name):
                parser = Elements()
                parser.feed(path.read_text(encoding="utf-8"))
                skip = next(a for tag, a in parser.elements if tag == "a" and a.get("class") == "skip")
                target = next(a for tag, a in parser.elements if tag == "main" and a.get("id") == skip["href"].lstrip("#"))
                self.assertEqual(skip["href"], "#contenu")
                self.assertEqual(target["tabindex"], "-1")
                if path.name != "index.html":
                    self.assertTrue(any(a.get("href") == "index.html#projet" for tag, a in parser.elements if tag == "a"))

    def test_checks_detect_a_skip_link_that_leaves_the_page(self):
        cb.build()
        article = cb.DIST / "article-07-donnees-personnelles.html"
        article.write_text(article.read_text().replace('href="#contenu"', 'href="index.html#contenu"'), encoding="utf-8")
        self.assertIn("local_skip_links", cb.checks())

    def test_support_needs_three_approvals(self):
        cb.CONFIG_FILE.write_text(json.dumps({
            "iban": "CH93 0076 2011 6238 5295 7", "beneficiary": "Test",
            "bank_owner_confirmed": True, "legal_checks_confirmed": True,
            "explicit_publish_approval": False}), encoding="utf-8")
        self.assertIsNone(cb.load_approved_support())

    def test_invalid_iban_is_rejected(self):
        cb.CONFIG_FILE.write_text(json.dumps({
            "iban": "CH00 0000 0000 0000 0000 0", "beneficiary": "Test",
            "bank_owner_confirmed": True, "legal_checks_confirmed": True,
            "explicit_publish_approval": True}), encoding="utf-8")
        with self.assertRaises(ValueError):
            cb.load_approved_support()

    def test_package_creates_archive(self):
        path = cb.package()
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
