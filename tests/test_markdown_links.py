"""Liens Markdown : liste blanche et échappement, sans dépendance externe."""
from html import escape
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import CELESTBIP_MASTER as cb


class MarkdownLinkTests(unittest.TestCase):
    def render(self, markdown):
        return cb.md_to_html("# Titre\n2026-11-17 · Résumé\n" + markdown)[2]

    def test_allowed_external_urls(self):
        urls = [
            cb.GUMROAD_PREFIX + "lkeew",
            cb.STRIPE_PREFIX + "abc",
            cb.PAYPAL_PREFIX + "ABC",
            cb.SPONSORS_URL,
            "https://github.com/ceeentreprises-dev/CelesteBip-starter/issues/new?template=partenariat.md&title=Projet",
            cb.SITE_URL + "partenaires.html#collaborer",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertIn(f'<a href="{escape(url, quote=True)}">Lien</a>', self.render(f"[Lien]({url})"))

    def test_relative_paths_fragments_and_queries(self):
        urls = ["partenaires.html", "./a-propos.html", "../guide.pdf", "/CelesteBip-starter/",
                "#collaborer", "?recherche=IA&lang=fr", "guide.pdf?version=2#page-1",
                "documents/guide%20pratique.pdf"]
        for url in urls:
            with self.subTest(url=url):
                self.assertIn(f'<a href="{escape(url, quote=True)}">Lire</a>', self.render(f"[Lire]({url})"))

    def test_forbidden_urls_remain_escaped_markdown(self):
        urls = [
            "https://evil.example/pay", "javascript:alert", "JaVaScRiPt:alert",
            "data:text/html,<svg>", "//evil.example/x", "///evil.example/x",
            "\\evil.example", "/\\evil.example", "http://buy.stripe.com/abc",
            'partenaires.html"onclick="alert', "guide.pdf'onclick='alert",
            " guide.pdf", "guide .pdf", "guide\t.pdf", "guide\x00.pdf",
        ]
        for url in urls:
            with self.subTest(url=repr(url)):
                markdown = f"[Lien]({url})"
                html = self.render(markdown)
                self.assertNotIn("<a ", html)
                self.assertEqual(html, "<p>" + escape(markdown) + "</p>")

    def test_control_characters_are_refused_even_when_markdown_lines_split(self):
        for control in ("\n", "\r", "\x85", "\x1f", "\x7f"):
            url = "guide" + control + ".pdf"
            with self.subTest(control=repr(control)):
                self.assertFalse(cb.markdown_link_allowed(url))
                self.assertNotIn("<a ", self.render(f"[Lien]({url})"))

    def test_domain_path_and_authority_spoofing_is_refused(self):
        urls = [
            "https://buy.stripe.com.evil.example/abc", "https://buy.stripe.com@evil.example/abc",
            "https://buy.stripe.com:8443/abc", "https://github.com/ceeentreprises-dev-evil/repo",
            "https://github.com/sponsors/ceeentreprises-dev-evil",
            "https://ceeentreprises-dev.github.io/CelesteBip-starter-evil/page",
            "https://www.paypal.com/ncp/payment-evil/ABC",
            "https://laracail.gumroad.com/l/../other",
            "https://laracail.gumroad.com/l/%2e%2e/other",
            "https://laracail.gumroad.com/l/..%2fother",
            cb.SITE_URL + "../other-project/page",
            "https://[invalid/",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(cb.markdown_link_allowed(url))
                self.assertNotIn("<a ", self.render(f"[Lien]({url})"))

    def test_text_href_and_surrounding_html_are_escaped_once(self):
        html = self.render('<script> [<b>& "Lire"](?q=un&lang=fr) après &')
        self.assertEqual(html, '<p>&lt;script&gt; <a href="?q=un&amp;lang=fr">&lt;b&gt;&amp; &quot;Lire&quot;</a> après &amp;</p>')
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>", html)

    def test_links_work_in_paragraphs_lists_and_headings(self):
        body = self.render("## [Titre](#titre)\n- [Liste](partenaires.html)\nTexte [un](#un) et [deux](#deux).")
        self.assertIn('<h2><a href="#titre">Titre</a></h2>', body)
        self.assertIn('<ul>\n<li><a href="partenaires.html">Liste</a></li>\n</ul>', body)
        self.assertIn('<p>Texte <a href="#un">un</a> et <a href="#deux">deux</a>.</p>', body)


if __name__ == "__main__":
    unittest.main()
