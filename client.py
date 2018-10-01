import requests
import json
import pprint as pp

class Client():

    def __init__(self, url, key):
        self.url = url
        self.api = url+'/api'
        self.key = key
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def get_wid(self, name):
        req = self.session.get(self.api + "/histories?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        wid = None
        for w in data:
            if (w['name']==name):
                wid = w['id']
        return wid

    def upload_dataset(self, wid, filename):
        req = self.session.post(self.api + "/tools",
                                data={'key':self.key,'tool_id':'upload1','workspace_id':wid},
                                files={'files_0|file_data':open(filename, 'rb')})
        req.raise_for_status()
        data = json.loads(req.text)
        did=data['outputs'][0]['id']
        return did
    
    def get_dataset_state(self, did):
        req = self.session.get(self.api + "/datasets/"+did+"?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        return data['state']
        
    def get_workflow_name(self, workflow):
        req = self.session.get(self.url + "/workflow_name/"+workflow+"?key=" + self.key)
        req.raise_for_status()
        return req.text
    
    def start_job(self,wid,workflow,inputs):
        inputs = json.dumps(inputs)
        req = self.session.post(self.api + "/tools",data={'key':self.key,'tool_id':self.get_workflow_name(workflow),'workspace_id':wid,'inputs':inputs})
        req.raise_for_status()
        data = json.loads(req.text)
        jid=data['jobs'][0]['id']
        djid=str(data['decoded_job_id'])
        return jid,djid

    def get_job_state(self, jid):
        req = self.session.get(self.api + "/jobs/"+jid+"/state?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        return data['state'],data['status']

    def get_result_id(self, jid, name):
        req = self.session.get(self.api + "/jobs/"+jid+"?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        return data['outputs'][name]['id']

    def get_download_url(self, did):
        req = self.session.get(self.api + "/datasets/"+did+"?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        return self.url+data['download_url']

    def get_resources(self):
        req = self.session.get(self.api + "/resources?key=" + self.key)
        req.raise_for_status()
        data = json.loads(req.text)
        return data

    def get_resource(self, name):
        req = self.session.get(self.api + "/resources/list?key=" + self.key + "&name=" + name)
        req.raise_for_status()
        try:
            data = json.loads(req.text)
            return data
        except:
            return None
        
    def start_resource(self, name):
        req = self.session.get(self.api + "/resources/start?key=" + self.key + "&name=" + name)
        req.raise_for_status()
        return req.text

    def stop_resource(self, name):
        req = self.session.get(self.api + "/resources/stop?key=" + self.key + "&name=" + name)
        req.raise_for_status()
        return req.text

    def download_jobfile(self, djid, path):
        url=self.url + "/download/"+ str(int(round(int(djid)/1000))).zfill(3) + "/" + djid + "/" + path +"?key=" + self.key
        print(url)
        req = self.session.get(url)
        req.raise_for_status()
        return req.content
    
    def get_job_tail(self, jid, file, lastline):
        url = self.api + "/jobs/"+jid+"/tail?key=" + self.key + "&file=" + file + "&line="+str(lastline)
        try:
            req = self.session.get(url)
            req.raise_for_status()
            data = req.text
            return data
        except:
            data = ""
