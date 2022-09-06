import pandas as pd

df = pd.read_csv('data/company_data.csv', 
    names=['url', 'company_name', 
            'time_in_business', 'company_number', 'size', 
            'current_status', 'website', 'phone', 'principal_activity', 'may_trade_as', 
            'largest_company_shareholder', 'registered_address', 
            'director_companies', 'shareholders', 'companies_sharing_eircode', 
            'date_added_to_database'],
    encoding='ISO-8859-1')

print(df.shape)

print(df.info())

print(df['current_status'].value_counts())

print(df['may_trade_as'].head())
