from robocorp import browser
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
from classes.newsdata import NewsData


class APNews:
    """
    A class to navigate the AP News website and scrape news data.
    Args:
        homepage_url:
            The url of the home page of the AP News website.
            default: "https://apnews.com"
        browser_engine: 
            The engine which will be used to start a browser service
            choices: ["chromium", "chrome", "chrome-beta", "msedge",
                 "msedge-beta", "msedge-dev", "firefox", "webkit"]
    """

    def __init__(self, homepage_url: str = "https://apnews.com", browser_engine: str = "chromium"):
        logging.info("Starting browser")
        self.page = self.start_browser(browser_engine)
        self.page.goto(homepage_url,
                       wait_until="domcontentloaded", timeout=120000)

    def start_browser(self, browser_engine):
        try:
            logging.info(f"Creating browser page")
            browser.configure(browser_engine=browser_engine,
                              screenshot="only-on-failure", headless=False)
            page = browser.page()
            return page
        except Exception as err:
            logging.error("Could not configure and start browser")
            raise ValueError(err)

    def get_news_data(
        self,
        search_phrase: str,
        n_months: int = 1,
        category: str = "",
        sort_by: str = "Newest",
    ) -> NewsData:
        """
        Navigate through the AP News website searching for a phrase, filtering the results and extracting data.
        Args:
                search_phrase:
                The text that will be searched in the AP News website.

                n_months:
                Number of months for which needed to receive news.
                default: 1
                example:
                    0|1: Only current month;
                    2: current and previous month;
                    3: current and 2 previous months

                category:
                Category of the news to be filtered.
                default: ""
                choices: ["Photo Galleries", "Sections", "Stories" "Subsections", "Videos", ""]

                sort_by:
                sort_by option of the filtered news.
                default: "Newest"
                choices: ("Newest", "Oldest", "Relevance")

        Returns:
            APNews.NewsData:
            NewsData object containig the data extracted, filter e sort_by applied and min date.
        """
        try:
            logging.info("Importing APNews child methods")
            from classes.homepage import Homepage
            from classes.searchresultspage import SearchResultsPage

            logging.info("Formating and validating arguments")
            category = category.capitalize()
            sort_by = sort_by.capitalize()

            self.assert_category_is_valid(category)
            self.assert_sort_by_is_valid(sort_by)
            self.assert_n_months_is_valid(n_months)

            min_date = self.get_min_date(n_months)

            Homepage.search_for_phrase(self.page, search_phrase)

            if category != "":
                SearchResultsPage.apply_category_filter(self.page, category)

            SearchResultsPage.apply_sort_by(self.page, sort_by)

            df_news_data = SearchResultsPage.get_search_results(
                self.page, min_date, search_phrase)

            news_data = NewsData(category=category,
                                 from_=min_date,
                                 sort_by=sort_by,
                                 dataframe=df_news_data,
                                 created=datetime.now())

            logging.info("News data successfully obtained")
            return news_data
        except Exception as err:
            logging.error(str(err))
            raise err

    def assert_n_months_is_valid(self, n_months: int):
        try:
            assert n_months >= 0
        except:
            logging.error(
                "The number of months for which news will be searched must be greater or equal to 0 (zero)")
            raise ValueError(
                "The number of months for which news will be searched must be greater or equal to 0 (zero)")

    def assert_category_is_valid(self, category: str):
        allowed_values = (
            "Photo Galleries",
            "Sections",
            "Stories",
            "Subsections",
            "Videos",
            "",
        )

        if category not in allowed_values:
            raise ValueError(
                f"'Category' parameter is invalid. You must choose one of the following values: {allowed_values}.")

        return True

    def assert_sort_by_is_valid(self, sort_by: str):
        allowed_values = ("Newest", "Oldest", "Relevance")

        if sort_by not in allowed_values:
            raise ValueError(
                f"'sort_by' parameter is invalid. You must choose one of the following values: {allowed_values}."
            )

        return True

    def get_min_date(self, n_months: int):
        logging.info(f"Getting min date from n_month = {n_months}")

        first_day_of_current_month = datetime(
            year=datetime.today().year, month=datetime.today().month, day=1)
        months_to_subtract = relativedelta(
            months=n_months - 1 if n_months >= 2 else 0)

        return first_day_of_current_month - months_to_subtract
