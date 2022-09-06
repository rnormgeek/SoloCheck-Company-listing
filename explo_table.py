import pandas as pd

df = pd.read_csv('data/company_data.csv', 
    names=['url', 'company_name', 'time_in_business',
 'company_number', 'size', 'current_status', 
 'website', 'phone', 'principal_activity',
  'may_trade_as', 'largest_company_shareholder',
   'registered_address', 'director_companies',
    'shareholders', 'companies_sharing_eircode'],
    on_bad_lines='warn',
    encoding='ISO-8859-1')

print(df.shape)