"""Tests unitaires de CelestBIP Starter (bibliothèque standard uniquement).

Lancer : python -m unittest discover -s tests -v
"""
import json
import hashlib
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

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
        self._old = (cb.DIST, cb.RELEASE, cb.CONFIG_FILE, cb.GAME)
        cb.DIST, cb.RELEASE, cb.CONFIG_FILE = tmp / "dist", tmp / "release", tmp / "support-approved.json"

    def tearDown(self):
        cb.DIST, cb.RELEASE, cb.CONFIG_FILE, cb.GAME = self._old
        self._tmp.cleanup()

    def test_build_passes_checks(self):
        cb.build()
        self.assertEqual(cb.checks(), [])

    def test_return_page_does_not_claim_that_a_visit_proves_payment(self):
        cb.build()
        page = (cb.DIST / "merci.html").read_text(encoding="utf-8")
        self.assertIn("elle ne vérifie pas qu'un paiement a été reçu", page)
        self.assertIn("Gumroad", page)
        self.assertNotIn("Votre paiement est confirmé", page)
        self.assertNotIn('content="Paiement reçu.', page)

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

    def test_game_runtime_matches_reviewed_sources_and_mit_licence(self):
        summary = cb.build()
        for name in cb.GAME_FILES:
            with self.subTest(file=name):
                source = (cb.GAME / name).read_bytes()
                exported = (cb.DIST / "carpe-rush" / name).read_bytes()
                self.assertEqual(exported, source)
                self.assertEqual(summary["files"]["carpe-rush/" + name],
                                 hashlib.sha256(source).hexdigest())
        licence = (cb.DIST / "carpe-rush/LICENSE").read_text()
        self.assertIn("MIT License", licence)
        self.assertIn("Copyright (c) 2026 ceeentreprises-dev", licence)
        self.assertEqual(licence, (cb.ROOT / "LICENSE").read_text())

    def test_game_is_linked_and_in_sitemap(self):
        summary = cb.build()
        self.assertIn('href="carpe-rush/"', (cb.DIST / "index.html").read_text())
        self.assertIn(cb.SITE_URL + "carpe-rush/", (cb.DIST / "sitemap.xml").read_text())
        self.assertEqual(summary["pages_web"], len(list(cb.DIST.glob("*.html"))) + 1)

    def test_game_export_and_zip_exclude_unlisted_and_stale_files(self):
        original = cb.GAME
        cb.GAME = Path(self._tmp.name) / "reviewed-game"
        for name in cb.GAME_FILES:
            target = cb.GAME / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((original / name).read_bytes())
        for name in ("README.md", ".env", "tools/balance.js", "assets/capture.png"):
            target = cb.GAME / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Not part of the public runtime")
        cb.build()
        (cb.DIST / "carpe-rush/stale-private.txt").write_text("Must not survive a rebuild")
        archive = cb.package()
        with ZipFile(archive) as zipped:
            names = zipped.namelist()
            self.assertTrue(all(not name.endswith("/") for name in names))
            exported = {name for name in names if name.startswith("carpe-rush/")}
            self.assertEqual(exported, set(cb.PUBLIC_GAME_FILES))
            for name in cb.GAME_FILES:
                self.assertEqual(zipped.read("carpe-rush/" + name), (original / name).read_bytes())
        self.assertFalse((cb.DIST / "carpe-rush/stale-private.txt").exists())

    def test_game_export_rejects_a_symlink_outside_reviewed_folder(self):
        original = cb.GAME
        cb.GAME = Path(self._tmp.name) / "reviewed-game"
        for name in cb.GAME_FILES:
            target = cb.GAME / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((original / name).read_bytes())
        script = cb.GAME / "js/main.js"
        script.unlink()
        script.symlink_to(cb.ROOT / "CELESTBIP_MASTER.py")
        with self.assertRaisesRegex(ValueError, "Fichier du jeu"):
            cb.build()

    def test_checks_detect_an_incomplete_or_unlisted_game_export(self):
        cb.build()
        (cb.DIST / "carpe-rush/js/audio.js").unlink()
        (cb.DIST / "carpe-rush/private.txt").write_text("Unexpected file")
        self.assertIn("game_runtime_exported", cb.checks())
        self.assertIn("game_export_allowlist", cb.checks())

    def test_game_export_rejects_redirected_source_and_destination_folders(self):
        original = cb.GAME
        linked_source = Path(self._tmp.name) / "linked-game"
        linked_source.symlink_to(original, target_is_directory=True)
        cb.GAME = linked_source
        with self.assertRaisesRegex(ValueError, "dossier du jeu"):
            cb.build()
        cb.GAME = original
        cb.build()
        target = cb.DIST / "carpe-rush"
        shutil.rmtree(target)
        outside = Path(self._tmp.name) / "outside"
        outside.mkdir()
        marker = outside / "private.txt"
        marker.write_text("Must not be modified")
        target.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "destination du jeu"):
            cb.build()
        self.assertTrue(target.is_symlink())
        self.assertEqual(marker.read_text(), "Must not be modified")
        self.assertEqual(list(outside.iterdir()), [marker])


if __name__ == "__main__":
    unittest.main()
