import logging


class Locators():
    def get_locator(page, name, format_text=""):
        logging.info(f"Identifying locator {name}")
        if page == "homepage":
            locators = {
                "close_popup_button": "//a[@class='fancybox-item fancybox-close' and @title='Close']",
                "reject_cookies_button": "//*[@id='onetrust-reject-all-handler']", ''
                "show_search_button": "//span[normalize-space()='Show Search']//preceding-sibling::*",
                "search_input": "//input[@class='SearchOverlay-search-input']",
                "search_submit_button": "//button[@class='SearchOverlay-search-submit']",
            }
        elif page == "search_results":
            locators = {
                "next_page_button": "//div[@class='Pagination-nextPage']/a",
                "news_group_divs": "div.SearchResultsModule-results > bsp-list-loadmore > div.PageList-items > div",
                "news_title_div": "div > div.PagePromo-content > bsp-custom-headline > div",
                "news_description_div": " div > div.PagePromo-content > div.PagePromo-description",
                "news_date_div": "div > div.PagePromo-content > div.PagePromo-byline > div",
                "news_picture_img": "div > div.PagePromo-media > a > picture > img",
                "close_banner_button": "//button[@class='Banner-close']",
                "expand_category_button": "//div[@class='SearchFilter-heading' and text()='Category']",
                "check_category_input": f"//span[normalize-space()='{format_text}']/preceding-sibling::input[@type='checkbox']",
                "sort_news_select": "//span[normalize-space()='Sort by']/following-sibling::select"
            }
        else:
            raise ValueError(f"The page {page} is not recognized")

        try:
            identified_locator = locators[name]
            return identified_locator
        except:
            raise ValueError(
                f"No locator was found with the name {name} in the page {page}")
