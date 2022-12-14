from webbrowser import get
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime
import re

proxies = {
    'http': 'http://vfieczproxy.internal.vodafone.com:8080'
}


def setup_session(proxies=None):
    """
    Setup a requests session.
    """
    session = requests.Session()
    if proxies is not None:
        session.proxies = proxies
    return session


def get_tag_from_url_and_id(session, url, id):
    """
    Given an url and a html element id, returns the corresponding element as a bs4 tag.
    """
    # Get the html content from the url
    response = session.get(url)
    html_content = response.content
    # Parse the html content
    soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
    # Get the text from element id
    results = soup.find(id=id)
    return results

# Get company listings complete links
def get_company_listings_complete_links(session):
    """
    This function returns all company listings available
    """
    root_url = 'https://www.solocheck.ie'
    url = "https://www.solocheck.ie/IrishCompanyInfo"
    id = "level-links"
    # Get the links
    results = get_tag_from_url_and_id(session, url, id)
    higher_links = [result['href'] for result in results.find_all('a')]
    # Second iteration to get the links for the next page
    lower_links = []
    for link in higher_links:
        # Get the links
        results = get_tag_from_url_and_id(session, root_url+link, id)
        [lower_links.append(result['href']) for result in results.find_all('a') if result['href'] not in higher_links]
    
    # Get the complete links
    complete_links = [f'{root_url}{link}' for link in lower_links]
    return complete_links

def get_company_urls(session, url):
    """
    Get the company urls from the solocheck website.
    """
    root_url = "https://www.solocheck.ie"
    # Get the html content from the url
    response = session.get(url)
    html_content = response.content
    # Parse the html content
    soup = BeautifulSoup(html_content, 'lxml', from_encoding='utf-8')
    # Get the text from element id
    results = []
    for tag in soup.find_all('td'):
        for anchor in tag.find_all('a'):
            results.append(anchor['href'])
    # Format the links for proper use
    complete_links = [f'{root_url}{link}' for link in results]
    logging.info(f'Found {len(complete_links)} urls')
    return complete_links

def save_company_urls(company_urls, csv_path):
    """
    Write the company urls to a csv file.
    """
    # Write the company urls to a csv file
    pd.DataFrame(company_urls).to_csv(csv_path, index=False, header=False, mode='a')
    logging.info(f'Wrote {len(company_urls)} urls to {csv_path}')

class Company:
    def __init__(self, url, session=None):
        self.url = url
        self.session = session
        self.set_company_attributes()

    def _format_address(self, unformated_address):
        """
        Format the company address
        """
        address_elements = unformated_address.split(",")
        formated_address = " ".join(address_elements)
        return formated_address
    
    def _get_element_from_soup(self, soup, id):
        """
        Get the element from the soup
        """
        element = soup.find(id=id)
        logging.debug(f'{id} found')
        return element
    
    def _get_soup(self):
        if self.session is None:
            response = requests.get(self.url)
        else:
            response = self.session.get(self.url)
        html_content = response.content
        # Parse the html content
        soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
        logging.debug(f'Parsing complete.')
        return soup

    def _get_company_summary(self, soup):
        """
        Get the company summary from the soup and parse it to a dictinary
        """
        # Get the content from the tag
        tag = soup.find('div', id='report-6')
        logging.debug(f'report-6 found')
        summary_text = tag.find('p').text

        summary = {}
        # Check the third sentence for the number of companies the director has chaired
        director_companies = re.search(r'director of [0-9]+ other', summary_text)
        if director_companies:
            summary['director_companies'] = int(re.search(r'[0-9]+', director_companies.group()).group()) # Get the number of companies
        else:
            summary['director_companies'] = 0
        # Check the fourth sentence for the number of shareholders
        shareholders = re.search(r'[0-9]+ shareholder', summary_text)
        if shareholders:
            summary['shareholders'] = int(re.search('[0-9]+', shareholders.group()).group()) # Get the number of shareholders
        else:
            summary['shareholders'] = 0
        # Check if there is a fifth sentence, and if there is, get the number companies sharing the Eircode
        eircode = re.search(r'Eircode with at least [0-9]+ other', summary_text)
        if eircode:
            summary['companies_sharing_eircode'] = int(re.search('[0-9]+', eircode.group()).group()) # Get the number of companies sharing the Eircode
        else:
            summary['companies_sharing_eircode'] = 0
        return summary

    def _get_vitals_from_report(self, soup):
        """
        Using the company report, extract all the vital info of the company
        """
        vitals = {}
        company_report = self._get_element_from_soup(soup, 'report-1')
        for ul in company_report.find_all('ul'):
            for li in ul.find_all('li'):
                for span in li.find_all('span'):
                    if span.has_attr('class'):
                        if span['class'] == ['title']:
                            key = span.text.replace(':', '').lower().replace(' ', '_')
                        if span['class'] == ['desc']:
                            hidden = span.find_all('li')
                            if len(hidden) > 0:
                                value = [h.text for h in hidden if re.search(r'\. \. \.', h.text) is None]
                            else:
                                value = span.text
                        try:
                            vitals[key] = value
                        except UnboundLocalError:
                            pass

        vitals_list = ['company_name', 'time_in_business', 'company_number', 'size',
            'current_status', 'website', 'phone', 'principal_activity', 'may_trade_as', 
            'largest_company_shareholder', 'registered_address']
        # Formatting the vitals so missing keys are not a problem
        for k in vitals_list:
            if k not in vitals:
                vitals[k] = ''

        # Keeping the vitals that are required
        vitals_updated = {k:v for k,v in vitals.items() if k in vitals_list}

        logging.debug(f'Company vitals successfully extracted')
        return vitals_updated

    def set_company_attributes(self):
        """
        Set the company attributes after fetching the data from the company url
        """
        soup = self._get_soup()
        self.__dict__.update(self._get_vitals_from_report(soup=soup)) # adding the vitals to the company attributes
        self.__dict__.update(self._get_company_summary(soup=soup)) # adding the summary to the company attributes

    def show(self, attr):
        print(f'{attr}: {self.__getattribute__(attr)}')

    def show_vitals(self):
        for v in ['company_name', 'time_in_business', 'company_number', 'size', 'current_status', 'principal_activity', 'may_trade_as', 'registered_address', 'largest_company_shareholder']:
            try:
                self.show(v)
            except AttributeError:
                pass

    def write_to_csv(self, filename):
        del self.__dict__['session']
        df = pd.DataFrame([self.__dict__])
        df['date_added_to_database'] = datetime.now().strftime('%Y-%m-%d')
        # Making sure the columns are in the right order
        df.reindex(columns=['url', 'company_name', 
            'time_in_business', 'company_number', 'size', 
            'current_status', 'website', 'phone', 'principal_activity', 'may_trade_as', 
            'largest_company_shareholder', 'registered_address', 
            'director_companies', 'shareholders', 'companies_sharing_eircode', 
            'date_added_to_database']).to_csv(filename, mode='a', header=False, index=False)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s', 
        filename='scraping_helpers.log',
        filemode='w')

    session = setup_session(proxies)

    test_company1 = Company(url='https://www.solocheck.ie/Irish-Company/Aughey-Holdings-Limited-300765')
    test_company2 = Company(url='https://www.solocheck.ie/Irish-Company/Abbey-Healthcare-Unlimited-Company-267243')

    print(test_company1.__dict__)
    print(test_company2.__dict__)

    """ To test the listings
    listings = get_company_listings_complete_links(session)
    logging.debug(f'Listings found: {listings}')

    for listing in listings[:1]:
        logging.debug(f'For listing {listing}: {get_company_urls(session, listing)}')
    """