from classes.apnews import APNews
import logging
from time import sleep
from datetime import datetime
import re
from datetime import timedelta
import pandas as pd
from classes.locators import Locators


class SearchResultsPage(APNews):
    def __init__(
        self,
        homepage_url: str = "https://apnews.com",
        browser_engine: str = "chromium"
    ):
        APNews.__init__(self, homepage_url, browser_engine)

    def apply_category_filter(page, category: str):
        logging.info(f"Applying category filter ({category})")
        try:
            page.click(
                Locators.get_locator("search_results", "expand_category_button"), timeout=60000)
        except:
            if page.is_visible(Locators.get_locator("search_results", "close_banner_button")):
                page.click(Locators.get_locator(
                    "search_results", "close_banner_button"))
                page.click(
                    Locators.get_locator("search_results", "expand_category_button"), timeout=10000
                )

        page.click(
            Locators.get_locator("search_results", "check_category_input", category), timeout=15000)
        sleep(5)

    def apply_sort_by(page, sort_by: str):
        logging.info(f"Applying sort ({sort_by})")
        page.select_option(
            selector=Locators.get_locator("search_results", "sort_news_select"), value=sort_by)
        sleep(5)

    def convert_to_datetime(date: str):
        logging.info(f"Converting string '{date}' to datetime")
        if re.match(r"^\w+ \d{1,2}$", date):  # Ex.: April 29
            return datetime.strptime(f"{date}, {datetime.today().year}", "%B %d, %Y")
        elif date == "Yesterday":
            return datetime.today() - timedelta(days=1)
        elif re.match(r"^\d{1,2} hours{0,1} ago$", date):
            return datetime.now() - timedelta(hours=int(date.split(" ")[0]))
        elif re.match(r"^\d{1,2} mins{0,1} ago$", date):
            return datetime.now() - timedelta(minutes=int(date.split(" ")[0]))
        elif re.match(r"^\w+ \d{1,2}, \d{4}$", date):
            return datetime.strptime(date, "%B %d, %Y")
        elif date == "Now":
            return datetime.now()
        else:
            raise ValueError("Date string inputed has an invalid format.")

    def contains_money(text: str):
        logging.info(f"Checking if string contains money substring")
        return re.match(text, r"(\$\d+(\.\d{1,2}){0,1})|(\$\d{1,3},(\d{3}(,|\.))+\d{1,2})|\d+ dollars|\d+ USD")

    def count_phrase_occurances(text: str, phrase: str):
        logging.info("Counting occurance of phrase in text")
        return text.lower().count(phrase.lower())

    def navigate_to_next_results_page(page):
        next_page_url = page.get_attribute(
            Locators.get_locator("search_results", "next_page_button"), "href")
        page.goto(next_page_url)
        sleep(4)

    def get_news_item_data(element, search_phrase) -> dict:
        try:
            title = element.query_selector(
                Locators.get_locator("search_results", "news_title_div")).inner_text()
            date = SearchResultsPage.convert_to_datetime(
                element.query_selector(Locators.get_locator("search_results", "news_date_div")).inner_text().strip())
        except:
            logging.err("Failed to get news title and/or date.")
            return {}

        try:
            description = element.query_selector(
                Locators.get_locator("search_results", "news_description_div")).inner_text()
        except:
            logging.warning("Failed to get news description.")
            description = None

        try:
            picture_filename = element.query_selector(
                Locators.get_locator("search_results", "news_picture_img")).get_attribute("srcset")
            picture_filename = picture_filename[picture_filename.rfind(
                r"%2F") + 3: -3]
        except:
            logging.warning("Failed to get news picture filename.")
            picture_filename = None

        contains_money = "True" if SearchResultsPage.contains_money(
            title) or SearchResultsPage.contains_money(description) else "False"

        search_phrases_count = SearchResultsPage.count_phrase_occurances(
            title, search_phrase) + SearchResultsPage.count_phrase_occurances(description, search_phrase)

        return {
            "Title": title,
            "Date": date,
            "Description": description,
            "Picture Filename": picture_filename,
            "Contains Money": contains_money,
            "Search Phrases Count": search_phrases_count
        }

    def get_search_results(page, min_date: datetime, search_phrase: str) -> pd.DataFrame:
        logging.info("Extracting news data to dataframe")

        pictures_path = "output/"
        date = datetime.now()

        df_news_data = pd.DataFrame(
            columns=[
                "Title",
                "Description",
                "Date",
                "Picture Filename",
                "Contains Money",
                "Search Phrases Count"
            ]
        )

        while date > min_date:
            news_elements = page.query_selector_all(
                Locators.get_locator("search_results", "news_group_divs")
            )
            for element in news_elements:
                news_item_data = SearchResultsPage.get_news_item_data(
                    element, search_phrase)

                if news_item_data.get("Date", None) is None or news_item_data["Date"] < min_date:
                    break
                else:
                    news_item_data["Date"] = datetime.strftime(
                        date, "%m/%d/%Y")

                if (news_item_data.get("Picture Filename", None) is not None):
                    element.query_selector(
                        Locators.get_locator("search_results", "news_picture_img")).screenshot(
                        path=pictures_path + news_item_data["Picture Filename"] + ".png", timeout=1000)

                df_news_data = pd.concat(
                    [df_news_data, pd.DataFrame([news_item_data])], ignore_index=True)
            else:
                SearchResultsPage.navigate_to_next_results_page()

            break

        return df_news_data
