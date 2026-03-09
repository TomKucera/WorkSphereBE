from playwright.sync_api import sync_playwright, Browser, Page


class PlaywrightSession:

    def __init__(self, headless: bool = True):
        self._headless = headless

        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    @property
    def page(self) -> Page:
        return self._page

    def start(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self._headless)
        self._page = self._browser.new_page()

    def stop(self):
        if self._browser:
            self._browser.close()

        if self._playwright:
            self._playwright.stop()
