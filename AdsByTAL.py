# importing libraries
import requests
import csv
import datetime
import json

# rollworks admin auth login credentials ---REPLACE WITH YOURS-----
auth = ('YOUR_ADMIN_EMAIL', 'YOUR_ADMIN_PASSWORD')

# graphql api endpoint
GRAPH_API_ENDPOINT = "https://app.adroll.com/reporting/api/v1/query"

# set request headers
req_headers = {"Content-Type": "application/json", "Accept": "application/json"}

# set request payload with query to get advertisable active adgroups, ads and included audiences
req_query = {"query": "{advertisable { forUser { eid name "
                      "adgroups { eid isActive actualStatusString "
                      "ads(isActive: true) { eid name type adFormatName actualStatusString src destinationURL} "
                      "audiences { type inclusion segmentEID } } } } }"}
try:
    # sending post request and saving response as response object
    res_adv_obj = requests.post(GRAPH_API_ENDPOINT, json=req_query, auth=auth, headers=req_headers).json()

    # parsing json
    if 'data' in res_adv_obj:
        adv_list = res_adv_obj['data']['advertisable']['forUser']

        # create a CSV file for writing with current date time appended to file name
        ct = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        csv_file = open('Test_Audiences_' + ct + '.csv', 'w')
        csv_writer = csv.writer(csv_file)

        # create a header row in CSV
        header_row = ['advEID', 'adgroupEID', 'adgroup_status', 'segment_EIDs', 'TAL_EIDs', 'ads']
        csv_writer.writerow(header_row)

        # loop through each advertisable that auth user has access to
        for adv in adv_list:
            adv_eid = adv['eid']

            # audience api base endpoint
            AUDIENCE_API_ENDPOINT = "https://app.adroll.com/audience/v1/segments"

            # get components of composite seg (if any) in adv
            res_composite_seg_obj = requests.get(AUDIENCE_API_ENDPOINT+'?advertiser_id='+adv_eid+'&type=composite&omit_fields=attributes',
                                                 auth=auth, headers=req_headers).json()
            # create a dictionary to map composite seg id with list of its component seg ids
            dict_adv_composite_seg = {}
            if 'segments' in res_composite_seg_obj:
                for segment in res_composite_seg_obj['segments']:
                    if segment['is_active']:
                        # add composite seg id mapped to its list of components seg ids
                        dict_adv_composite_seg[segment['segment_id']] = segment['components']

            # get user attribute seg in adv
            res_user_attr_seg_obj = requests.get(AUDIENCE_API_ENDPOINT+'?advertiser_id='+adv_eid+'&type=user_attributes&omit_fields=attributes',
                                                 auth=auth, headers=req_headers).json()
            # create a dictionary to map user attribute seg id with its TAL id
            dict_adv_user_attr_seg = {}
            if 'segments' in res_user_attr_seg_obj:
                for segment in res_user_attr_seg_obj['segments']:
                    if segment['is_active']:
                        # add user attribute seg id mapped to its TAL id
                        dict_adv_user_attr_seg[segment['segment_id']] = segment['tal_eid']

            # list of adgroup eids to avoid checking them again in the loop if they are reused in other campaigns
            adgroups_checked = []

            # loop through each adgroup
            if adv['adgroups']:
                for adgroup in adv['adgroups']:
                    # check if adgroup is active and not already checked
                    if adgroup['isActive'] and adgroup['eid'] not in adgroups_checked:
                        adgroup_eid = adgroup['eid']
                        adgroups_checked.append(adgroup_eid)
                        # actual status of campaign where adgroup is present
                        adgroup_status = adgroup['actualStatusString']
                        # get list of ads
                        ads_list = []
                        if adgroup['ads']:
                            ads_list = json.dumps(adgroup['ads'])
                            # loop through each segment in adgroup
                            if adgroup['audiences']:
                                audience_eids_list = []
                                tal_eids_list = []
                                for audience in adgroup['audiences']:
                                    # check if positively targeted (included) and attribute or composite segment
                                    if audience['inclusion'] and audience['type'] in ('user_attributes', 'composite'):
                                        if audience['type'] == 'composite':
                                            if audience['segmentEID'] in dict_adv_composite_seg:
                                                for component_eid in dict_adv_composite_seg[audience['segmentEID']]:
                                                    audience_eids_list.append(component_eid)
                                                    if component_eid in dict_adv_user_attr_seg:
                                                        tal_eids_list.append(dict_adv_user_attr_seg[component_eid])
                                        else:
                                            # attribute segment
                                            audience_eids_list.append(audience['segmentEID'])
                                            if audience['segmentEID'] in dict_adv_user_attr_seg:
                                                tal_eids_list.append(dict_adv_user_attr_seg[audience['segmentEID']])
                                #write data in CSV row
                                record_row = [adv_eid, adgroup_eid, adgroup_status, json.dumps(audience_eids_list),
                                              json.dumps(tal_eids_list), ads_list]
                                csv_writer.writerow(record_row)
        # print complete
        print("Done")
    else:
        print("No adgroups data")
except:
    print("Script Error")