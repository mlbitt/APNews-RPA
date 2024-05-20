# Challenge: Getting News from Websites

This project presents a solution to the PixelDu Challenge 3.0 (RPA). It takes three parameters: `search_phrase`, `category`, and `n_months`. The program navigates to the APNews website, searches for the provided phrase, filters by category, orders the results by the newest news first, and retrieves the date from each news article displayed until it finds a date preceding $n_months-1 months ago.

## Running

### Robocorp Cloud

If you have access, you can visit [this link](https://cloud.robocorp.com/maguilarzm9ck/maguilar/), select the process, input the parameters, and run the program online.

### Local

For local execution, it's necessary to input the parameters in the file `devdata/work-items-in/parameters`.

## Results

Upon running the bot, images of the news and a .XLSX file containing data for each news article will be available in the `output/` folder.

## Dependencies

- Robocorp Extension