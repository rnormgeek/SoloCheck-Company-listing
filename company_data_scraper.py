import scraping_helpers as sh
from csv import reader
import logging

def main():
    session = sh.setup_session()
    with open('data/company_urls.csv', 'r') as f:
        for company_url in reader(f):
            logging.info(f'Fetching data for {company_url[0]}')
            company = sh.Company(url=company_url[0], session=session)
            logging.info(f'Successfully fetched {company.company_name}. Writing data to csv...')
            company.write_to_csv('data/company_data.csv')


if __name__ == "__main__":
    logging.basicConfig(
        filename='company_data_scraper.log',
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w')

    main() #TODO: add a try/except block to catch errors, log them and continue with the next company url