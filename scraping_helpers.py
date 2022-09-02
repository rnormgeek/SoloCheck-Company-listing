from webbrowser import get
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import re

proxies = {
    'http': 'http://vfieczproxy.internal.vodafone.com:8080'
}


def setup_session(proxies):
    """
    Setup a requests session.
    """
    session = requests.Session()
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
    soup = BeautifulSoup(html_content, 'html.parser')
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
    links = [result['href'] for result in results.find_all('a')]
    # Format the links for proper use
    complete_links = [f'{root_url}{link}' for link in links]

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
    soup = BeautifulSoup(html_content, 'lxml')
    # Get the text from element id
    results = []
    for tag in soup.find_all('td'):
        for anchor in tag.find_all('a'):
            results.append(anchor['href'])
    # Format the links for proper use
    complete_links = [f'{root_url}{link}' for link in results]

    return complete_links

class Company:
    def __init__(self, url):
        self.url = url
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
        response = requests.get(self.url)
        html_content = response.content
        # Parse the html content
        soup = BeautifulSoup(html_content, 'html.parser')
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
        sentences = summary_text.split('.') # Split by sentence

        summary = {}
        # Check the third sentence for the number of companies the director has chaired
        director_companies = re.search(r'director of [0-9]+ other', sentences[2])
        if director_companies:
            summary['director_companies'] = re.search(r'[0-9]+', director_companies.group()).group() # Get the number of companies
        else:
            summary['director_companies'] = 0
        # Check the fourth sentence for the number of shareholders
        shareholders = re.search(r'[0-9]+ shareholder', sentences[3])
        if shareholders:
            summary['shareholders'] = re.search('[0-9]+', shareholders.group()).group() # Get the number of shareholders
        else:
            summary['shareholders'] = 0
        # Check if there is a fifth sentence, and if there is, get the number companies sharing the Eircode
        if len(sentences) >= 4:
            eircode = re.search(r'Eircode with at least [0-9]+ other', sentences[4])
            if eircode:
                summary['companies_sharing_eircode'] = re.search('[0-9]+', eircode.group()).group() # Get the number of companies sharing the Eircode
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
        logging.debug(f'Company vitals successfully extracted')
        return vitals

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
        df = pd.DataFrame([self.__dict__])
        df.to_csv(filename, mode='a', header=False, index=False)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s', 
        filename='scraping_helpers.log',
        filemode='a')

    session = setup_session(proxies)
    sample_company_url = 'https://www.solocheck.ie/Irish-Company/Saleslink-Solutions-International-Ireland-Limited-222937'
 
    test_company = Company(url=sample_company_url)
    print(test_company.show_vitals())
