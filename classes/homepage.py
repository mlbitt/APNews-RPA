from classes.apnews import APNews
import logging
from time import sleep
from classes.locators import Locators


class Homepage(APNews):
    def __init__(
        self,
        homepage_url: str = "https://apnews.com",
        browser_engine: str = "chromium"
    ) -> None:
        APNews.__init__(self, homepage_url, browser_engine)

    def search_for_phrase(page, phrase: str) -> None:

        logging.info("Typing search phrase in search bar")

        try:
            page.click(
                Locators.get_locator("homepage", "reject_cookies_button"),
                timeout=120000,
            )
        except:
            pass

        if page.is_visible(Locators.get_locator("homepage", "close_popup_button")):
            page.click(
                Locators.get_locator("homepage", "close_popup_button"), force=True
            )
            sleep(5)
        
        page.click(
            Locators.get_locator("homepage", "show_search_button"), timeout=60000
        )
        page.fill(
            Locators.get_locator("homepage", "search_input"), phrase, timeout=10000
        )
        page.click(
            Locators.get_locator("homepage", "search_submit_button"), timeout=10000
        )
