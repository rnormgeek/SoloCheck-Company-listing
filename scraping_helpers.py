from webbrowser import get
import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests_html import HTMLSession


def get_tag_from_url_and_id(url, id):
    """
    Given an url and a html element id, returns the corresponding element as a bs4 tag.
    """
    # Get the html content from the url
    response = requests.get(url)
    html_content = response.content
    # Parse the html content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Get the text from element id
    results = soup.find(id=id)

    return results


def find_html_tag_from_url(session, url, tag):
    """
    find the html element from the url using requests_html
    """
    r = session.get(url)
    r.html.render()
    result = r.html.find(tag)

    return result


url = "https://www.solocheck.ie/IrishCompanyInfo"
root_url = "https://www.solocheck.ie"
id = "level-links"

# Get the links
results = get_tag_from_url_and_id(url, id)
links = [result['href'] for result in results.find_all('a')]
# Format the links for proper use
complete_links = [f'{root_url}{link}' for link in links]

print(complete_links)


def get_company_urls(url):
    """
    Get the company urls from the solocheck website.
    """
    root_url = "https://www.solocheck.ie"
    # Get the html content from the url
    response = requests.get(url)
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


print(get_company_urls("https://www.solocheck.ie/IrishCompanyInfo?i=00"))
