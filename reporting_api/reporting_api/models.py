import os
from datetime import datetime
import pandas as pd

dt_format = '%Y-%m-%dT%H:%M:%S.%fZ'

def parse_dt_string(dt_string):
    return datetime.strptime(dt_string, dt_format)

Businesses = pd.read_csv('reporting_api/data/businesses.csv')
Checks = pd.read_csv('reporting_api/data/checks.csv')
Employees = pd.read_csv('reporting_api/data/employees.csv')
LaborEntries = pd.read_csv('reporting_api/data/laborEntries.csv')
MenuItems = pd.read_csv('reporting_api/data/menuItems.csv')
OrderedItems = pd.read_csv('reporting_api/data/orderedItems.csv')


# set list of all datetime fields across all tables
datetime_fields = ['updated_at', 'created_at', 'closed_at', 'clock_in', 'clock_out']
models = [Businesses, Checks, Employees, LaborEntries, MenuItems, OrderedItems]

# transform the data type of datetime fields to a python datetime object --
# convenience maneuver for filtering tables on dates in views
for model in models:
    for field in datetime_fields:
        if field in model.columns:
            model[field] = model[field].apply(parse_dt_string)
