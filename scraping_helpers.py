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
        self.name = self.get_name()
        self.address = self.get_address()
        self.phone = self.get_phone()
        self.email = self.get_email()
        self.website = self.get_website()
        self.description = self.get_description()
        self.sector = self.get_sector()
        self.employees = self.get_employees()
        self.founded = self.get_founded()
        self.revenue = self.get_revenue()
        self.employees = self.get_employees()
        self.industry = self.get_industry()
        self.tags = self.get_tags()
        self.keywords = self.get_keywords()

    def get_name(self):
        """
        Get the company name from the company url.
        """
        # Get the html content from the url
        response = requests.get(self.url)
        html_content = response.content
        # Parse the html content
        soup = BeautifulSoup(html_content, 'lxml')
        # Get the text from element tag name
        tag = soup.find('header')
        name = tag.find('h1').text
        return name.text

    def get_address(self):
        """
        Get the company address from the company url.
        """
        # Get the html content from the url
        response = requests.get(self.url)
        html_content = response.content
        # Parse the html content
        soup = BeautifulSoup(html_content, 'lxml')
        # Get the text from element tag name
        tag = soup.find('div', {'class': 'address'})
        address = tag.text
        return address.text


if __name__ == "__main__":
    session = setup_session(proxies)
    logging.basicConfig()
    print(get_company_listings_complete_links(session))
    print(get_company_urls(session, "https://www.solocheck.ie/IrishCompanyInfo?i=00"))
    sample_company_url = 'https://www.solocheck.ie/Irish-Company/007-Iventure-Innovations-Limited-551996'
 