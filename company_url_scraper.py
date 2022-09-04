import scraping_helpers
import logging

def main():
    session = scraping_helpers.setup_session()
    complete_links = scraping_helpers.get_company_listings_complete_links(session)

    for link in complete_links:
        company_urls = scraping_helpers.get_company_urls(session, link)
        scraping_helpers.save_company_urls(company_urls)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s', 
        filename='company_url_scraper.log', 
        filemode='w')
    main()