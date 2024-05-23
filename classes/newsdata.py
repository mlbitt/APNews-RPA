import pandas as pd
from datetime import datetime
import logging


class NewsData:
    def __init__(
        self,
        category: str,
        from_: str,
        sort_by: str,
        created: datetime,
        dataframe: pd.DataFrame
    ):
        self.category = category
        self.from_ = from_
        self.sort_by = sort_by
        self.created = created
        self.dataframe = dataframe

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
                    "The filepath provided is invalid. It must end with '.xlsx'.")

            try:
                self.dataframe.to_excel(
                    filepath,
                    index=False,
                    sheet_name=f"{self.category} - From {datetime.strftime(self.from_, '%m-%d-%Y')}")
            except Exception as err:
                raise ValueError(str(err))
        except ValueError as ve:
            logging.error(str(ve))
