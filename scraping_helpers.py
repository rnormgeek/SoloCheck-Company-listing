from urllib import request
from webbrowser import get
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

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

    def _get_company_report(self):
        """
        Get the company report
        """
        # Get the html from the url
        response = requests.get(self.url)
        html_content = response.content
        # Parse the html content
        soup = BeautifulSoup(html_content, 'html.parser')
        # Get the content from the tag
        tag = soup.find('div', id='report-1')
        return tag

    def _get_vitals_from_report(self):
        """
        Using the company report, extract all the vital info of the company
        """
        vitals = {}
        for ul in self._get_company_report().find_all('ul'):
            for li in ul.find_all('li'):
                for span in li.find_all('span'):
                    if span.has_attr('class'):
                        if span['class'] == ['title']:
                            key = span.text.replace(':', '').lower()
                        if span['class'] == ['desc']:
                            value = span.text
                        try:
                            vitals[key] = value
                        except UnboundLocalError:
                            pass
        return vitals

    def set_company_attributes(self):
        vitals = self._get_vitals_from_report()
        self.name = vitals['company name']
        self.age = vitals['time in business']
        self.company_number = vitals['company number']
        self.size = vitals['size']
        self.current_status = vitals['current status']
        self.activity = vitals['principal activity']
        self.trading_name = vitals['may trade as']
        self.address = self._format_address(vitals['registered address'])

    def show(self, attr):
        print(f'{attr}: {self.__getattribute__(attr)}')

    def show_vitals(self):
        for v in ['name', 'age', 'company_number', 'size', 'current_status', 'activity', 'trading_name', 'address']:
            self.show(v)

if __name__ == "__main__":
    session = setup_session(proxies)
    # print(get_company_listings_complete_links(session))
    # print(get_company_urls(session, "https://www.solocheck.ie/IrishCompanyInfo?i=00"))
    sample_company_url = 'https://www.solocheck.ie/Irish-Company/N-Oconnor-Construction-Limited-635031'
 
    test_company = Company(url=sample_company_url)
    test_company.show_vitals()