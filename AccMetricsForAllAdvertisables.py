# importing libraries
import requests
import csv

# set selected month to pull metrics by date
month = "10"

# set selected year to pull metrics by date
year = "2020"

# rollworks admin auth login credentials
auth = ('YOUR_ADMIN_EMAIL', 'YOUR_PASSWORD')

# graphql api endpoint
GRAPH_API_ENDPOINT = "https://app.adroll.com/reporting/api/v1/query"

# set request headers
req_headers = {"Content-Type": "application/json", "Accept": "application/json"}

# set request payload with query to get advertisables and campaigns
req_query_org = {"query": "{ advertisable { forUser {eid name campaigns {eid name abmType channel} }}}"}

# sending post request and saving response as response object
res_adv_obj = requests.post(GRAPH_API_ENDPOINT, json=req_query_org, auth=auth, headers=req_headers).json()

# parsing json
if 'data' in res_adv_obj:
    adv_list = res_adv_obj['data']['advertisable']['forUser']

    # create a CSV file for writing
    csv_file = open('RollWorksAccountMetrics_' + month + '_' + year + '.csv', 'w')
    csv_writer = csv.writer(csv_file)

    # create a header row in CSV
    header_row = ['advEID', 'advName', 'date', 'domain', 'cost', 'impressions', 'clicks',
                  'adjustedViewThroughs', 'adjustedClickThroughs', 'pageViews']
    csv_writer.writerow(header_row)

    # loop through each advertisable
    for adv in adv_list:
        adv_eid = adv['eid']
        print(adv_eid + " checking")
        adv_name = adv['name']
        adv_campaigns_str = ''

        # loop through each campaign to create its list
        for campaign in adv['campaigns']:
            if campaign['abmType'] == 'lead_locator' and campaign['channel'] == 'web':
                # append campaign eid to list of account targeting web campaigns
                if adv_campaigns_str != '':
                    adv_campaigns_str += ','
                adv_campaigns_str += '\"' + campaign['eid'] + '\"'

        if adv_campaigns_str != '':
            print(adv_eid + " running")

            # loop through each date
            for d in range(1, 31):
                # set date range
                if d < 10:
                    str_start = '0' + str(d)
                    if d != 9:
                        str_end = '0' + str(d + 1)
                    else:
                        str_end = str(d + 1)
                else:
                    str_start = str(d)
                    str_end = str(d + 1)
                date_string = 'start: "' + year + "-" + month + '-' + str_start + '", end: "' + year + '-' + month + '-' + str_end + '"'

                # query to get account metrics for adv campaigns list for each date in loop
                req_query_adv = {'query': '{accountMetrics {summary (' + date_string + ', advertisableEID: ' + adv_eid + ','
                                ' campaignEIDs:[' + adv_campaigns_str + ']) { domain cost impressions clicks '
                                'adjustedClickThroughs adjustedViewThroughs pageViews} } }'}

                # sending post request and saving response as response object
                res_acc_metrics = requests.post(GRAPH_API_ENDPOINT, json=req_query_adv, auth=auth, headers=req_headers)

                try:
                    res_acc_metrics_obj = res_acc_metrics.json()
                    # parsing json
                    if 'data' in res_acc_metrics_obj:
                        arr_account_metrics = res_acc_metrics_obj['data']['accountMetrics']['summary']
                        # create all records
                        if arr_account_metrics is not None:
                            for acc_metrics in arr_account_metrics:
                                if acc_metrics['cost'] != 0:
                                    record_row = [adv_eid, adv_name, year + '-' + month + '-' + str_start,
                                                  acc_metrics['domain'], round(acc_metrics['cost'], 2),
                                                  acc_metrics['impressions'], acc_metrics['clicks'],
                                                  acc_metrics['adjustedViewThroughs'], acc_metrics['adjustedClickThroughs'],
                                                  acc_metrics['pageViews']]
                                    csv_writer.writerow(record_row)
                except:
                    print(adv_eid + ": Response error in account metrics on" + date_string)
            print(adv_eid + " complete")
        else:
            print(adv_eid + ": No web Acc Targeting campaigns")
else:
    print("Response error in adv campaigns data")

# print complete
print("done")