import scraping_helpers as sh
import logging

def main():
    session = sh.setup_session()
    complete_links = sh.get_company_listings_complete_links(session)

    for link in complete_links:
        company_urls = sh.get_company_urls(session, link)
        sh.save_company_urls(company_urls, 'data/company_urls.csv')

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s', 
        filename='company_url_scraper.log', 
        filemode='w')
    main()