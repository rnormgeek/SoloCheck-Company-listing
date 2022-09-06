import scraping_helpers as sh
from csv import reader
import logging
import multiprocessing
from joblib import Parallel, delayed
import pandas as pd
from tqdm import tqdm

num_cores = multiprocessing.cpu_count()

def main():
    session = sh.setup_session()
    with open('data/company_urls.csv', 'r') as f:
        for company_url in reader(f):
            logging.info(f'Fetching data for {company_url[0]}')
            company = sh.Company(url=company_url[0], session=session)
            logging.info(f'Successfully fetched {company.company_name}. Writing data to csv...')
            company.write_to_csv('data/company_data.csv')

def main_process(company_url, session):
    logging.info(f'Fetching data for {company_url}')
    try:
        company = sh.Company(url=company_url, session=session)
        logging.info(f'Successfully fetched {company.company_name}. Writing data to csv...')
        company.write_to_csv('data/company_data.csv')
    except Exception as e:
        logging.error(f'Error fetching data for {company_url}: {e}')
        pass

if __name__ == "__main__":
    logging.basicConfig(
        filename='company_data_scraper.log',
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w')

    # main()

    # Parallel version:
    session = sh.setup_session()
    company_urls = pd.read_csv('data/company_urls.csv', header=None, names=['url'])['url'].tolist()
    Parallel(n_jobs=num_cores)(delayed(main_process)(company_url, session) for company_url in tqdm(company_urls))