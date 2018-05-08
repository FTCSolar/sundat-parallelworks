#!/usr/bin/env python

import time,json,requests,sys 
from client import Client

# inputs
pw_url = "https://go.parallel.works"
api_key = "<APIKEY>"
workflow_name = "sundat_runner_v1_single_layout_coordinates"
workspace_name = "sundat_runner_v1"
resource_name = "sundat_linux"

inputs = {
    "jsonin": {
        "src": "hda",
        "id": "sample_inputs/sample-single-long-lat.json"
    }
}

print("Running workflow",workspace_name,"in workspace",workspace_name,"on resource",resource_name,"...")

# create a new Parallel Works client
c = Client(pw_url,api_key)

# check if resource exists and is on
resource=c.get_resource(resource_name)
if resource:
    if resource['status'] == "off":
        # if resource not on, start it
        print("Starting",resource_name,"...")
        print(c.start_resource(resource_name))
    else:
        print(resource_name,"already running...")
else:
    print("No resource found.")
    sys.exit(1)

# get workspace id from workspace name
wid = c.get_wid(workspace_name)
if wid == None:
    print("No workspace found.")
    sys.exit(1)

# upload the dataset(s)
for i in inputs:
    try:
        if 'id' in inputs[i]:
            print("Uploading dataset",inputs[i]['id'],"...")
            did = c.upload_dataset(wid,inputs[i]['id'])
            # poll file upload state until complete
            while True:
                time.sleep(1)
                state = c.get_dataset_state(did)
                print(state)
                if state == 'ok':
                    # replace the input id value with the successfully uploaded did
                    inputs[i]['id'] = did
                    break
    except:
        pass

# start the pw job (djid=decoded_job_id)
jid,djid = c.start_job(wid,workflow_name,inputs)

print("Submitted Job: "+jid)

# write the jid to a file for later stop/kill
f = open('out.job','w')
f.write(jid+","+djid)
f.close()

lastline=0
laststatus=""
while True:
    time.sleep(1)
    
    try:
        state,status = c.get_job_state(jid)
    except:
        state="starting"
        status=""
    if laststatus!=status:
        print(status)
    laststatus=status
    
    if state == 'ok':
        rid = c.get_result_id(jid,"htmlout")
        jsonid = c.get_result_id(jid,"jsonout")
        break
    elif (state == 'deleted' or state == 'error'):
        raise Exception('Simulation had an error. Please try again')

# get the JSON result dataset url
jsonurl = c.get_download_url(jsonid)
print("")

# save the JSON result to a file
req = requests.get(jsonurl)
req.raise_for_status()
print("Final Result Written to out.json")
f = open('out.json','w')
f.write(req.text)
f.close()

print("Workflow Complete.")
print("")


# download any result file by using the /download endpoint
#print("Fetching example individual result file to out.png...")
#f = open('out.png','wb')
#f.write(c.download_jobfile(djid,"output/case_0/out.png"))
#f.close()

#print("Fetching example individual result file to out.skp...")
#f = open('out.skp','wb')
#f.write(c.download_jobfile(djid,"output/case_0/out.skp"))
#f.close()


# turn off the computing resources
# print c.stop_resource(resource_name)
