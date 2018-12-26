'''
views.py dictates the api response given a request
'''

from django.http.response import HttpResponse, JsonResponse
import models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

dt_format = '%Y-%m-%dT%H:%M:%S.%fZ' # datetime string format given in the POS api

def parse_dt_string(dt_string):
    '''
    parse_dt_string() - returns a datetime object given a string that follows
    the format given by the universal variable, dt_format
    '''
    return datetime.strptime(dt_string, dt_format)

def get_time_ranges(start, end, time_interval):
    '''
    get_time_ranges() - returns a list of datetime objects containing the
    beginning and end of all time intervals that span start to end
    '''
    start = parse_dt_string(start)
    end = parse_dt_string(end)
    if time_interval == 'hour':
        time_delta = timedelta(hours=1)
    elif time_interval == 'day':
        time_delta = timedelta(days=1)
    elif time_interval == 'week':
        time_delta = timedelta(days=7)
    else:
        time_delta = relativedelta(months=+1)
    time_ranges = [start]
    while time_ranges[-1] < end:
        time_ranges.append(time_ranges[-1] + time_delta)
    if time_ranges[-1] < end:
        time_ranges.append(end)
    elif time_ranges[-1] > end:
        time_ranges[-1] = end

    return time_ranges

def calculate_hours_worked(clock_in, clock_out, start, end):
    '''
    calculate_hours_worked() - returns the number of hours worked that are
    applicable to a start and end datetime range across a shift that begins
    at clock_in and ends at clock_out
    '''
    time_a = max(clock_in, start)
    time_b = min(clock_out, end)
    seconds_worked = (time_b - time_a).total_seconds()
    hours_worked = seconds_worked/3600

    return hours_worked

def calculate_labor_cost(labor, time_frame):
    '''
    calculate_labor_cost() - returns the total cost of labor for all employees
    that worked during a given time frame
    '''
    labor['start'] = time_frame['start']
    labor['end'] = time_frame['end']

    zip_columns = zip(
        labor['clock_in'],
        labor['clock_out'],
        labor['start'],
        labor['end']
    )
    labor['hours_worked'] = [
        calculate_hours_worked(clock_in, clock_out, start, end)
        for clock_in, clock_out, start, end in zip_columns
    ]
    labor = labor[labor['hours_worked'] > 0]
    labor_cost = (labor['hours_worked']*labor['pay_rate']).sum()

    return labor_cost

def lcp_report(business_id, time_interval, start, end):
    '''
    lcp_report() - returns a dictionary containg the response for a
    Labor Cost Percentage (LCP) request
    '''

    # time_interval = 'hour'
    # business_id = 'f21c2579-b95e-4a5b-aead-a3cf9d60d43b'
    # start = '2018-07-15T15:00:00.000Z'
    # end = '2018-07-15T18:00:00.000Z'

    response = {
        'report': 'LCP',
        'timeInterval': time_interval
    }
    data = []

    checks = models.Checks[models.Checks['business_id'] == business_id].copy()
    ordered_items = models.OrderedItems[models.OrderedItems['business_id'] == business_id].copy()
    labor_entries = models.LaborEntries[models.LaborEntries['business_id'] == business_id].copy()

    time_ranges = get_time_ranges(start, end, time_interval)
    num_time_increments = len(time_ranges) - 1

    for n in xrange(num_time_increments):
        time_frame = {
            'start': time_ranges[n],
            'end': time_ranges[n+1]
        }

        timeFrame = {
            'start': time_frame['start'].strftime(dt_format),
            'end': time_frame['end'].strftime(dt_format)
        }

        data_n = {
            'timeFrame': timeFrame
        }

        dt_mask_a = checks['closed_at'] > time_frame['start']
        dt_mask_b = checks['closed_at'] <= time_frame['end']

        check_ids = list(checks[dt_mask_a & dt_mask_b]['id'].unique())

        if check_ids:
            check_mask = ordered_items['check_id'].isin(check_ids)
            void_mask = ordered_items['voided'] == False
            sales = float(ordered_items[check_mask & void_mask]['price'].sum())
            if sales == 0:
                data_n['value'] = 'Error: No sales made in this time inverval'
                data.append(data_n)
                continue

            labor = labor_entries.copy()
            labor_cost = calculate_labor_cost(labor, time_frame)

            data_n['value'] = round(labor_cost/sales, 2)
        else:
            data_n['value'] = 'Error: No sales made in this time inverval'

        data.append(data_n)

    response['data'] = data

    return response

def fcp_report(business_id, time_interval, start, end):
    '''
    fcp_report() - returns a dictionary containg the response for a
    Food Cost Percentage (FCP) request
    '''
    response = {
        'report': 'FCP',
        'timeInterval': time_interval
    }
    data = []

    checks = models.Checks[models.Checks['business_id'] == business_id].copy()
    ordered_items = models.OrderedItems[models.OrderedItems['business_id'] == business_id].copy()

    time_ranges = get_time_ranges(start, end, time_interval)
    num_time_increments = len(time_ranges) - 1

    for n in xrange(num_time_increments):
        time_frame = {
            'start': time_ranges[n],
            'end': time_ranges[n+1]
        }

        data_n = {
            'start': time_frame['start'].strftime(dt_format),
            'end': time_frame['end'].strftime(dt_format)
        }

        dt_mask_a = checks['closed_at'] > time_frame['start']
        dt_mask_b = checks['closed_at'] <= time_frame['end']

        check_ids = list(checks[dt_mask_a & dt_mask_b]['id'].unique())

        if check_ids:
            check_mask = ordered_items['check_id'].isin(check_ids)
            void_mask = ordered_items['voided'] == False
            price = float(ordered_items[check_mask & void_mask]['price'].sum())
            if price == 0:
                data_n['value'] = 'Error: Total price is zero in this time inverval'
                data.append(data_n)
                continue

            cost = float(ordered_items[check_mask]['cost'].sum())

            data_n['value'] = round(100*cost/price, 2)
        else:
            data_n['value'] = 'Error: No sales made in this time inverval'

        data.append(data_n)

    response['data'] = data
    return response

def egs_report(business_id, time_interval, start, end):
    '''
    egs_report() - returns a dictionary containg the response for an
    Employee Gross Sales (EGS) request
    '''

    response = {
        'report': 'FCP',
        'timeInterval': time_interval
    }
    data = []

    checks = models.Checks[models.Checks['business_id'] == business_id].copy()
    ordered_items = models.OrderedItems[models.OrderedItems['business_id'] == business_id].copy()

    time_ranges = get_time_ranges(start, end, time_interval)
    num_time_increments = len(time_ranges) - 1

    for n in xrange(num_time_increments):
        time_frame = {
            'start': time_ranges[n],
            'end': time_ranges[n+1]
        }

        timeFrame = {
            'start': time_frame['start'].strftime(dt_format),
            'end': time_frame['end'].strftime(dt_format)
        }

        dt_mask_a = checks['closed_at'] > time_frame['start']
        dt_mask_b = checks['closed_at'] <= time_frame['end']

        df_checks = checks[dt_mask_a & dt_mask_b]
        df_join = pd.merge(
            df_checks,
            ordered_items,
            left_on='id',
            right_on='check_id',
            how='inner'
        )
        df_egs = df_join.groupby('name_x')[['price']].sum()

        num_employees = df_egs.shape[0]
        for m in xrange(num_employees):
            row = df_egs.iloc[m]
            data_m = {
                'timeFrame': timeFrame,
                'employee': row.name,
                'value': float(row['price'])
            }
            data.append(data_m)

    response['data'] = data
    return response

def reporting(request):
    if 'report' in request.GET:
        report = request.GET['report']
        report_types = ['lcp', 'fcp', 'egs']
        if report.lower() not in report_types:
            response = {'Error': '{} is an invalid report type'.format(report)}
            return JsonResponse(response)
        report = report.lower()
    else:
        response = {'Error': 'Report type not specified in request'}
        return JsonResponse(response)

    if 'business_id' in request.GET:
        business_id = request.GET['business_id']
    else:
        response = {'Error': 'Business ID not specified in request'}
        return JsonResponse(response)

    if 'timeInterval' in request.GET:
        time_interval = request.GET['timeInterval']
        time_intervals = ['hour', 'day', 'week', 'month']
        if time_interval.lower() not in time_interval:
            response = {'Error': '{} is an invalid time interval'.format(time_interval)}
            return JsonResponse(response)
        time_interval = time_interval.lower()
    else:
        response = {'Error': 'Time interval not specified in request'}
        return JsonResponse(response)

    if 'start' in request.GET:
        start = request.GET['start']
    else:
        response = {'Error': 'Start not specified in request'}
        return JsonResponse(response)

    if 'end' in request.GET:
        end = request.GET['end']
    else:
        response = {'Error': 'End not specified in request'}
        return JsonResponse(response)

    if report == 'lcp':
        response = lcp_report(business_id, time_interval, start, end)
    elif report == 'fcp':
        response = fcp_report(business_id, time_interval, start, end)
    elif report == 'egs':
        response = egs_report(business_id, time_interval, start, end)

    json_dumps_params = {'indent':4}
    return JsonResponse(response, json_dumps_params=json_dumps_params)

def welcome(request):
    s = 'Welcome.  Go to the /reporting end point to view the api.'
    return HttpResponse(s)
