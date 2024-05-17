from robocorp import browser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from time import sleep
import pandas as pd
import re
import os
import logging


class APNews:
    """
    A class to navigate the AP News website and scrape news data.
    Args:
        homepage_url:
            The url of the home page of the AP News website.
            default: "https://apnews.com"
    """

    def __init__(
        self,
        homepage_url: str = "https://apnews.com",
    ):
        logging.info("Starting browser")
        browser.configure(
            browser_engine="chromium",
            screenshot="only-on-failure",
            headless=False,
        )
        logging.info(f"Creating browser page")
        self.page = browser.page()
        self.homepage_url = homepage_url

    def get_news_data(
        self,
        search_phrase: str,
        n_months: int = 1,
        category: str = "",
        sort: str = "Newest",
    ):
        """
        Navigate throug the AP News website searching for a phrase, filtering the results and extracting data.
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

                sort:
                Sort option of the filtered news.
                default: "Newest"
                choices: ("Newest", "Oldest", "Relevance")

        Returns:
            APNews.NewsData:
            NewsData object containig the data extracted, filter e sorting applied and min date.
        """
        try:
            logging.info("Formating and validating arguments")
            category = category.capitalize()
            self.assert_category_is_valid(category)
            sort = sort.capitalize()
            self.assert_sort_is_valid(sort)
            try:
                assert n_months >= 0
            except:
                logging.error(
                    "The number of months for which news will be searched must be greater or equal to 0 (zero)"
                )
                raise ValueError(
                    "The number of months for which news will be searched must be greater or equal to 0 (zero)"
                )

            min_date = self.get_min_date(n_months)

            self.search_for_phrase(search_phrase)

            if category != "":
                self.apply_category_filter(category)

            self.apply_sorting(sort)

            df_news_data = self.extract_news_data_to_dataframe(
                min_date, search_phrase)

            logging.info("Returning dataframe with extracted news data")
            return self.NewsData(
                df_news_data, category, min_date, sort, created=datetime.now()
            )
        except Exception as err:
            logging.error(str(err))
            raise err

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
                f"'Category' parameter is invalid. You must choose one of the following values: {allowed_values}."
            )
        return True

    def assert_sort_is_valid(self, sort: str):
        allowed_values = ("Newest", "Oldest", "Relevance")
        if sort not in allowed_values:
            raise ValueError(
                f"'Sort' parameter is invalid. You must choose one of the following values: {allowed_values}."
            )
        return True

    def get_min_date(self, n_months: int):
        logging.info(f"Getting min date from n_month = {n_months}")
        first_day_of_current_month = datetime(
            year=datetime.today().year, month=datetime.today().month, day=1
        )
        months_to_subtract = relativedelta(
            months=n_months - 1 if n_months >= 2 else 0)
        return first_day_of_current_month - months_to_subtract

    def search_for_phrase(self, phrase: str):
        element_selectors = {
            "close_popup_button": "//a[@class='fancybox-item fancybox-close' and @title='Close']",
            "reject_cookies_button": "//*[@id='onetrust-reject-all-handler']",''
            "show_search_button": "//span[normalize-space()='Show Search']//preceding-sibling::*",
            "search_input": "//input[@class='SearchOverlay-search-input']",
            "search_submit_button": "//button[@class='SearchOverlay-search-submit']",
        }

        logging.info(f"Navigating to '{self.homepage_url}'")
        self.page.goto(self.homepage_url,
                       wait_until="domcontentloaded", timeout=120000)
        logging.info("Typing search phrase in search bar")

        
        self.page.click(
            element_selectors["reject_cookies_button"], timeout=120000)
        
        
        if self.page.is_visible(element_selectors["close_popup_button"]):
            self.page.click(
                element_selectors["close_popup_button"], force=True)
            sleep(5)    
        
        self.page.click(
            element_selectors["show_search_button"], timeout=60000)
        self.page.fill(
            element_selectors["search_input"], phrase, timeout=10000)
        self.page.click(
            element_selectors["search_submit_button"], timeout=10000)
        
        
    def apply_category_filter(self, category: str):
        logging.info(f"Applying category filter ({category})")
        element_selectors = {
            "close_banner_button": "//button[@class='Banner-close']",
            "expand_category_button": "//div[@class='SearchFilter-heading' and text()='Category']",
            "check_category_input": f"//span[normalize-space()='{category}']/preceding-sibling::input[@type='checkbox']",
        }
        try:
            self.page.click(
                element_selectors["expand_category_button"], timeout=60000)
        except:
            if self.page.is_visible(element_selectors["close_banner_button"]):
                self.page.click(element_selectors["close_banner_button"])
                self.page.click(
                    element_selectors["expand_category_button"], timeout=10000
                )

        self.page.click(
            element_selectors["check_category_input"], timeout=15000)
        sleep(5)

    def apply_sorting(self, sort: str):
        logging.info(f"Applying sort ({sort})")
        element_selectors = {
            "sort_news_select": "//span[normalize-space()='Sort by']/following-sibling::select"
        }

        self.page.select_option(
            selector=element_selectors["sort_news_select"], value=sort
        )
        sleep(5)

    def extract_news_data_to_dataframe(self, min_date: datetime, search_phrase: str):
        element_selectors = {
            "news_group_divs": "div.SearchResultsModule-results > bsp-list-loadmore > div.PageList-items > div",
            "news_title_div": "div > div.PagePromo-content > bsp-custom-headline > div",
            "news_description_div": " div > div.PagePromo-content > div.PagePromo-description",
            "news_date_div": "div > div.PagePromo-content > div.PagePromo-byline > div",
            "news_picture_img": "div > div.PagePromo-media > a > picture > img"
        }
        logging.info("Extracting news data to dataframe")

        df_news_data = pd.DataFrame(
            columns=[
                "Title",
                "Description",
                "Date",
                "Picture Filename",
                "Contains Money",
            ]
        )
        pictures_path = "output/"
        date = datetime.now()

        while date > min_date:
            news_elements = self.page.query_selector_all(
                element_selectors["news_group_divs"]
            )
            for item in news_elements:
                try:
                    date = self.convert_to_datetime(
                        item.query_selector(
                            element_selectors["news_date_div"]).inner_text().strip()
                    )
                    if date < min_date:
                        break
                except:
                    logging.warning("Failed to get news date.")
                    break

                try:
                    description = item.query_selector(
                        element_selectors["news_description_div"]).inner_text()
                except:
                    logging.warning("Failed to get news description.")
                    description = None

                try:
                    picture_element = item.query_selector(
                        element_selectors["news_picture_img"])
                    picture_filename = self.get_picture_filename(
                        picture_element)

                    picture_element.screenshot(
                        path=pictures_path + picture_filename, timeout=1000)
                except:
                    logging.warning("Failed to get news picture.")
                    picture_filename = None

                title = item.query_selector(
                    element_selectors["news_title_div"]).inner_text()

                df_news_data = pd.concat(
                    [
                        df_news_data,
                        pd.DataFrame(
                            [
                                {
                                    "Title": title,
                                    "Description": description,
                                    "Date": datetime.strftime(date, "%m/%d/%Y"),
                                    "Picture Filename": picture_filename,
                                    "Contains Money": (
                                        "True"
                                        if self.contains_money(title)
                                        or self.contains_money(description)
                                        else "False"
                                    ),
                                    "Search Phrases Count": self.count_phrase_occurances(
                                        title, search_phrase
                                    )
                                    + self.count_phrase_occurances(
                                        description, search_phrase
                                    ),
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )
            else:
                try:
                    self.navigate_to_next_newspage()
                    continue
                except:
                    break
            break

        return df_news_data

    def convert_to_datetime(self, date: str):
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

    def contains_money(self, text: str):
        logging.info(f"Checking if string contains money substring")
        return re.match(
            text,
            r"(\$\d+(\.\d{1,2}){0,1})|(\$\d{1,3},(\d{3}(,|\.))+\d{1,2})|\d+ dollars|\d+ USD",
        )

    def get_picture_filename(self, picture_element):
        logging.info("Trying to get picture filename")
        scrset_attribute = picture_element.get_attribute("srcset")
        filename = scrset_attribute[scrset_attribute.rfind(r"%2F") + 3: -3].split(
            ".jpg"
        )[0]
        fileformat = ".png"
        return filename + fileformat

    def count_phrase_occurances(self, text: str, phrase: str):
        logging.info("Counting occurance of phrase in text")
        return text.lower().count(phrase.lower())

    def navigate_to_next_newspage(self):
        element_selectors = {
            "next_page_button": "//div[@class='Pagination-nextPage']/a",
        }
        next_page_url = self.page.get_attribute(
            element_selectors["next_page_button"], "href")
        self.page.goto(next_page_url)
        sleep(4)

    class NewsData:
        def __init__(
            self,
            dataframe: pd.DataFrame,
            category: str,
            from_: str,
            sort: str,
            created: datetime,
        ):
            self.dataframe = dataframe
            self.category = category
            self.from_ = from_
            self.sort = sort
            self.created = created

        def export_to_excel(self, filepath: str):
            """
            Exports dataframe containing news data to an excel file.
                Parameters:
                        filepath (str): Parent folder path, name of the file and suffix '.xlsx' concatenated into one string.
                                        Example: "./myfile.xlsx" ; "C:/myuser/Documents/apnews/data.xlsx"
                Returns:
                        None
            """
            try:
                logging.info("Exporting dataframe to excel")
                try:
                    logging.info("Validating filepath")
                    assert filepath.endswith(".xlsx")
                except:
                    raise ValueError(
                        "The filepath provided is invalid. It must end with '.xlsx'."
                    )

                try:
                    self.dataframe.to_excel(
                        filepath,
                        index=False,
                        sheet_name=f"{self.category} - From {datetime.strftime(self.from_, '%m-%d-%Y')}",
                    )
                except Exception as err:
                    raise ValueError(str(err))
            except ValueError as ve:
                logging.error(str(ve))
