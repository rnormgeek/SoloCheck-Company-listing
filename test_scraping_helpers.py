from unittest.mock import MagicMock
import pytest
from scraping_helpers import Company
from bs4 import BeautifulSoup

@pytest.fixture
def soup():
    with open('sample_soup.html') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    return soup


def test_get_vitals_from_report(soup):
    company = Company('https://www.solocheck.ie/Irish-Company/Saleslink-Solutions-International-Ireland-Limited-222937')
    vitals = company._get_vitals_from_report(soup)
    assert vitals == {
        'company_name': 'Saleslink Solutions International Ireland Limited',
        'company_number': '222937',
        'current_status': 'NORMAL',
        'largest_company_shareholder': ['Ilogistix', 'Saleslink', 'Moduslink', 'Saleslink Solutions', 'Saleslink Solutions International Ireland'],
        'may_trade_as': ['Ilogistix', 'Saleslink', 'Moduslink', 'Saleslink Solutions', 'Saleslink Solutions International Ireland'],
        'principal_activity': '[30.02] Manufacture of Computers and Other Information Processing Equipment',
        'registered_address': '10 Earlsfort Terrace,Dublin 2,Dublin',
        'size': 'Micro Company',
        'time_in_business': '27 Years'
    }

def test_get_company_summary(soup):
    company = Company('https://www.solocheck.ie/Irish-Company/Saleslink-Solutions-International-Ireland-Limited-222937')
    summary = company._get_company_summary(soup)
    assert summary == {
        'companies_sharing_eircode': 0,
        'director_companies': 6,
        'shareholders': 2
    }