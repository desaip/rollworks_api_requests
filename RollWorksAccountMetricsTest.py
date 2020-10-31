# importing libraries
import requests 
import json
import csv
  
# set selected adv EID to Salesforce AMER Digital Marketing Account
advertisableEID = "BJ2LEY7ICBALDJY44RXUPT"

# set selected month to pull metrics by date 
month = "07"

# set selected year to pull metrics by date 
year = "2019"

# set your adroll login credentials
adroll_auth = ('LOGIN', 'PASSWORD')

# create a CSV file for writing
csv_file = open('CampaignAccountMetrics_'+year+'_'+month+'.csv', 'w')
csvwriter = csv.writer(csv_file)

# create a header row
header_row = ['campaignEID','campaignName','date','domain','cost','impressions','clicks','adjustedViewThroughs','adjustedClickThroughs']
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
		# loop through each date
		for d in range(1, 3):
			#set date range
			if d<10:
				str_start = '0'+str(d)
				if d!=9:
					str_end = '0'+str(d+1)
				else:
					str_end = str(d+1)
			else :
				str_start = str(d)
				str_end = str(d+1)
			date_string = 'start: "'+year+"-"+month+'-'+str_start+'", end: "'+year+'-'+month+'-'+str_end+'"'
			# query for graphQL 
			data = {
			         'query': '{accountMetrics {summary ('+ date_string +', advertisableEID: '+ advertisableEID +', campaignEIDs:["'+ campaignEID +'"]) { domain cost impressions clicks adjustedClickThroughs adjustedViewThroughs } } }'    
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
								record_row = [campaignEID,campaign_name,year+'-'+month+'-'+str_start,acc_metrics['domain'],round(acc_metrics['cost'],2),acc_metrics['impressions'],acc_metrics['clicks'],acc_metrics['adjustedViewThroughs'],acc_metrics['adjustedClickThroughs']]
								csvwriter.writerow(record_row)
			except:
				print ("JSON response error")
		print (campaignEID + " complete")

# print complete
print ("done")

# close file
csv_file.close()
