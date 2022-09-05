# SoloCheck Scraping Project


### Technical documentation

This project is a simple web scraper that scrapes the SoloCheck website for the company listings and store it in a CSV file.

### Company class

The Company class is the main object of the project, it has two params:
- the company url, which links directly to the Solocheck intro page of the company
- (optional) the session to use to make the requests for data. If this is not available, it will use requests.get default behaviour to make a request instead.

Once an instance of the Company class is created, it will be automatically populated by the information available on the website, such as company name and tenure, industry, number of related companies, etc...
- The method .write_to_csv(*filepath*) writes the company information within a CSV file to store the information. It does not overwrite the file but append instead, adding the company.

### company_url_scraper.py

This script calls the functions and runs in order to extract from the Solocheck website all the links to the companies on the website. This list is then written inside a CSV file.

### company_data_scraper.py

This script uses the Company class and helper functions to scrape the data on the Solocheck website and stores it to a CSV. It takes approx 4 hours to complete a single sweep of the whole database (273K companies as of 05/09/2022). To do that it needs to be able to run on 8 parallel processes.