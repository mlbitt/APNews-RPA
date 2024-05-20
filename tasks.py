
from robocorp.tasks import task
from robocorp import workitems
from classes.apnews import APNews
import logging
from datetime import date

logging.basicConfig(level=logging.INFO, filename=f"rpa_{date.today().strftime('%m-%d-%Y')}.log",
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt="%m/%d/%Y %H:%M:%S")


@task
def export_news():
    """
    Navigate through the APNews website and exports news according to filters provided in work-items.
    """
    logging.info("Starting program")

    param = workitems.inputs.current.payload

    news_website = APNews(homepage_url="https://apnews.com")

    news_data = news_website.get_news_data(
        search_phrase=param['search_phrase'], category=param['category'], n_months=param['n_months'], sort="Newest")

    news_data.export_to_excel(filepath="output/news_data.xlsx")

    #workitems.outputs.create(files=["news_data.xlsx"])

    logging.info("Program finished")


if __name__ == "__main__":
    export_news()
