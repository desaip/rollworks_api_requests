# importing libraries
import requests 
import json
import csv
  
# set selected advertisable EID 
advertisableEID = "XYZEID"

# set selected start date
start_date = "2020-07-01"

# set selected end date
end_date = "2020-07-30"

# adroll login credentials
adroll_auth = ('email', 'password')

# create a CSV file for writing
csv_file = open('CampaignAccountMetrics_'+start_date+'_'+end_date+'.csv', 'w')
csvwriter = csv.writer(csv_file)

# create a header row
header_row = ['campaignEID','campaignName','domain','cost','impressions','clicks','adjustedViewThroughs','adjustedClickThroughs']
csvwriter.writerow(header_row)

# adroll graphql api endpoint  
GRAPH_API_ENDPOINT = "https://app.adroll.com/reporting/api/v1/query"

# set request headers
req_headers = {
	"Content-Type": "application/json", "Accept": "application/json"
}

# query to get campaigns
adv_data = {
		        'query': '{ advertisable { byEID(advertisable: "'+ advertisableEID +'") { campaigns { eid name abmType} }}}'	
		    }

# sending post request and saving response as response object 
adv_r = requests.post(GRAPH_API_ENDPOINT, json=adv_data, auth=adroll_auth, headers=req_headers) 

# extracting response json  
adv_response_obj = adv_r.json() 

#parsing json
campaign_list = adv_response_obj['data']['advertisable']['byEID']['campaigns']

#loop through each campaign
for campaign in campaign_list:
	campaign_name = campaign['name']
	campaignEID = campaign['eid']
	campaign_abm_type = campaign['abmType']

	if (campaign_abm_type == 'lead_locator'):
		date_string = 'start: "'+start_date+'", end: "'+end_date+'"'
		# query for graphQL 
		data = {
			        'query': '{accountMetrics {summary ('+ date_string +', advertisableEID: '+ advertisableEID +', campaignEIDs:["'+ campaignEID +'"]) { domain cost impressions clicks adjustedViewThroughs adjustedClickThroughs} } }'    
			   }
		# sending post request and saving response as response object 
		r = requests.post(GRAPH_API_ENDPOINT, json=data, auth=adroll_auth, headers=req_headers) 
		# extracting response json  
		try:
			response_obj = r.json()
			#parsing json
			if 'data' in response_obj:
				arr_account_metrics = response_obj['data']['accountMetrics']['summary']
				# create all records
				if arr_account_metrics != None:
					for acc_metrics in arr_account_metrics:
						if acc_metrics['cost'] != 0:
							record_row = [campaignEID,campaign_name,acc_metrics['domain'],round(acc_metrics['cost'],2),acc_metrics['impressions'],acc_metrics['clicks'],acc_metrics['adjustedViewThroughs'],acc_metrics['adjustedClickThroughs']]
							csvwriter.writerow(record_row)
		except:
			print ("JSON response error")
	print (campaignEID + " complete")

# print complete
print ("done")

# close file
csv_file.close()
