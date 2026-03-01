from playwright.sync_api import sync_playwright


class WebUserSimulator:
    def __init__(self, base_url: str, headless: bool = False):
        self.base_url = base_url
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    # --- lifecycle ---------------------------------------------------------

    def start(self):
        """Start browser and open a new page."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()

    def stop(self):
        """Close browser and cleanup."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    # --- user actions -------------------------------------------------------

    def open_home(self):
        """Navigate to base URL."""
        self.page.goto(self.base_url)

    def click_text(self, text: str):
        """Click element containing visible text."""
        self.page.click(f"text={text}")

    def fill_input(self, selector: str, value: str):
        """Fill input field."""
        self.page.fill(selector, value)

    def press_key(self, selector: str, key: str):
        """Press keyboard key inside element."""
        self.page.press(selector, key)

    def wait(self, milliseconds: int = 2000):
        """Simple wait helper."""
        self.page.wait_for_timeout(milliseconds)

    def screenshot(self, path: str = "screenshot.png"):
        """Save page screenshot."""
        self.page.screenshot(path=path)


if __name__ == "__main__":
    user = WebUserSimulator("https://example.com", headless=False)

    user.start()
    user.open_home()
    user.click_text("More information")
    user.wait(1000)
    user.screenshot("result.png")
    user.stop()


# https://www.startupjobs.cz/nabidka/37030/hr-it-recruiter
# https://www.startupjobs.cz/nabidka/24456/account-manazer-v-online-marketingu-pro-ehub-cz