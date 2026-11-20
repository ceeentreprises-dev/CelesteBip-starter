"""Régression clavier facultative de Carpe Rush (Playwright + Chromium).

Après un build : python tests/browser_game_keyboard.py
Version publiée : python tests/browser_game_keyboard.py --url https://…/carpe-rush/
Ce fichier n'est pas chargé par les tests unitaires de la bibliothèque standard.
"""
from contextlib import contextmanager
from functools import partial
import argparse
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading
from urllib.parse import urlsplit


@contextmanager
def game_url(public_url):
    if public_url:
        yield public_url
        return
    directory = Path(__file__).resolve().parents[1] / "dist"
    if not (directory / "carpe-rush/index.html").is_file():
        raise RuntimeError("Générez dist/ avec python CELESTBIP_MASTER.py build")

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(directory)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/carpe-rush/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def run(browser, url):
    result = {"url": url, "viewport": {"width": 390, "height": 844}, "main_sha256": [],
              "submenus": [], "controls": [], "javascript_errors": [], "failures": []}

    def require(condition, message):
        if not condition:
            result["failures"].append(message)

    def opened():
        context = browser.new_context(viewport=result["viewport"], locale="fr-CH")
        page = context.new_page()
        page.set_default_timeout(5000)
        page.on("pageerror", lambda error: result["javascript_errors"].append(str(error)))

        def response_received(response):
            if urlsplit(response.url).path.endswith("/js/main.js"):
                digest = hashlib.sha256(response.body()).hexdigest()
                if digest not in result["main_sha256"]:
                    result["main_sha256"].append(digest)

        page.on("response", response_received)
        response = page.goto(url, wait_until="networkidle", timeout=45000)
        require(response is not None and response.status == 200, "La page du jeu doit répondre HTTP 200")
        page.locator("#screen-menu").wait_for(state="visible")
        page.evaluate("""() => {
            window.__carpeKeyboardProbe = {updates: 0, game: null};
            const original = CR.Game.prototype.update;
            CR.Game.prototype.update = function (dt) {
                if (this.onEvent.name === 'onEvent') {
                    __carpeKeyboardProbe.updates++;
                    __carpeKeyboardProbe.game = this;
                }
                return original.call(this, dt);
            };
        }""")
        return context, page

    def snapshot(page):
        return page.evaluate("""() => ({
            screens: [...document.querySelectorAll('section.screen')]
                .filter(element => !element.classList.contains('hidden')).map(element => element.id),
            topbar: !document.getElementById('topbar').classList.contains('hidden'),
            updates: __carpeKeyboardProbe.updates,
            first: CR.Storage.data.achievements.first || null
        })""")

    def press_background(page, key):
        page.evaluate("document.activeElement.blur()")
        require(page.evaluate("document.activeElement.tagName") == "BODY", "Le raccourci doit cibler le fond")
        page.keyboard.press(key)
        page.wait_for_timeout(180)

    def end_game(page):
        # Fin de partie déterministe, sans attendre les collisions aléatoires.
        page.wait_for_function("__carpeKeyboardProbe.game !== null")
        page.evaluate("""() => {
            const game = __carpeKeyboardProbe.game;
            game.over = true; game.lives = 0; game.onEvent('over', {});
        }""")
        page.locator("#screen-over").wait_for(state="visible")

    # Chaque ouverture native au clavier vérifie aussi le garde des boutons.
    for source, button, screen in (("menu/shop", "btn-shop", "screen-shop"),
                                   ("menu/help", "btn-help", "screen-help"),
                                   ("menu/ach", "btn-ach", "screen-ach"),
                                   ("over/shop", "btn-over-shop", "screen-shop")):
        for key in ("Enter", "Space"):
            context, page = opened()
            try:
                if source.startswith("over/"):
                    page.locator("#btn-play").click()
                    end_game(page)
                initial = snapshot(page)
                page.locator("#" + button).focus()
                page.keyboard.press(key)
                page.locator("#" + screen).wait_for(state="visible")
                before = snapshot(page)
                require(before["updates"] == initial["updates"] and before["first"] == initial["first"],
                        f"{source} : {key} sur le bouton a lancé une partie")
                press_background(page, key)
                after = snapshot(page)
                preserved = (after["screens"] == [screen] and not after["topbar"]
                             and after["updates"] == before["updates"] and after["first"] == before["first"])
                require(preserved, f"{source} : {key} sur le fond a quitté la sous-vue ou lancé une partie")
                result["submenus"].append({"source": source, "key": key, "preserved": preserved,
                                           "before": before, "after": after})
            finally:
                context.close()

    for key in ("Enter", "Space"):
        context, page = opened()
        try:
            page.locator("#btn-mute").focus()
            page.keyboard.press(key)
            require(snapshot(page)["updates"] == 0 and snapshot(page)["first"] is None,
                    f"Son : {key} a lancé une partie")
            press_background(page, key)
            page.locator("#topbar").wait_for(state="visible")
            page.wait_for_function("__carpeKeyboardProbe.updates > 0")
            page.keyboard.press("p")
            page.locator("#screen-pause").wait_for(state="visible")
            page.keyboard.press("Escape")
            page.locator("#screen-pause").wait_for(state="hidden")
            end_game(page)
            previous = snapshot(page)["updates"]
            press_background(page, key)
            require(snapshot(page)["topbar"] and snapshot(page)["updates"] > previous,
                    f"Fin de partie : {key} sur le fond doit relancer")
            end_game(page)
            page.locator("#btn-again").focus()
            page.keyboard.press(key)
            page.locator("#topbar").wait_for(state="visible")
            page.locator("#btn-pause").click()
            page.locator("#btn-quit").click()
            page.locator("#btn-play").focus()
            page.keyboard.press(key)
            page.locator("#topbar").wait_for(state="visible")
            result["controls"].append({"key": key, "menu_start": True, "over_restart": True,
                                        "native_play_replay": True, "pause_resume": True})
        finally:
            context.close()
    require(len(result["main_sha256"]) == 1, "Le script du jeu doit être présent et rester identique pendant le test")
    require(not result["javascript_errors"], "Le navigateur a signalé des erreurs JavaScript")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="URL complète du dossier carpe-rush/ publié, sinon dist/ local")
    args = parser.parse_args()
    if args.url:
        parsed = urlsplit(args.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            parser.error("--url attend une URL HTTP(S) du jeu")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        parser.exit(2, "Test facultatif : Playwright et Chromium doivent être installés séparément.\n")
    with game_url(args.url) as url, sync_playwright() as playwright:
        browser_path = shutil.which("chromium") or shutil.which("chromium-browser")
        options = {"executable_path": browser_path} if browser_path else {}
        with playwright.chromium.launch(headless=True, args=["--no-sandbox"], **options) as browser:
            result = run(browser, url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
