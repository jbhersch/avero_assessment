'''
write_flat_files.py - This script probes the POS API and writes all the data
from each end point to csv files that will be used in the Reporting API.  It is
not used at all by the Reporting API itself, but I decided to include it to
illustrate how the flat files were written.
'''

import os
import csv
import json
import requests

access_token = os.environ['AVERO_TOKEN']
base_url = 'https://secret-lake-26389.herokuapp.com'
uris = [
    'businesses',
    'menuItems',
    'checks',
    'orderedItems',
    'employees',
    'laborEntries'
]
headers = {'Authorization': access_token}
data_dirpath = 'reporting_api/reporting_api/data'

for uri in uris:
    print uri
    url = os.path.join(base_url, uri) # set end point url
    csv_path = os.path.join(data_dirpath, uri + '.csv') # path for end point

    # records will be extracte from each table in chunks of 500
    # which is the maximum quantity set on the limit parameter
    params = {'limit': '500'}
    response = requests.get(url, headers=headers, params=params).json()
    data = response['data'] # first set of up to 500 records
    num_records = response['count'] # total number of records at end point
    fieldnames = data[0].keys() # set column/field names

    # open csv file and write header
    csv_file = open(csv_path, 'w')
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    # write first chunk of records
    for item in data:
        csv_writer.writerow(item)

    # if there is more than one chunk, loop through remaining chunks
    num_chunks = num_records/500
    for n in xrange(num_chunks):
        params = {'limit': '500', 'offset': str((n+1)*500)}
        response = requests.get(url, headers=headers, params=params).json()
        data = response['data']
        for item in data:
            csv_writer.writerow(item)

    csv_file.close()
