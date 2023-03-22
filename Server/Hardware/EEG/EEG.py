
import asyncio
import json
import time

import websockets



class EEG:


    INFO_ID = 2
    USER_LOGGED_IN_ID = 3
    REQUEST_ACCESS_ID = 4
    QUERY_HEADSET_ID = 5
    CONTROL_HEADST_ID = 6
    AUTHORIZE_ID = 7
    GETDATA_ID = 8
    CREATE_SESSION_ID = 9
    QUERY_SESSION_ID = 10
    HASACCESSRIGHT_ID = 11
    SUBSCRIBE_ID = 12


    def __init__(self, client_id="PdLqy2A8a5ukYTU6eaJki38hlZoVS5IzJaVi4G3p", client_secret="CeFlg0Hqd5QltDtdbDr78whwNJqG2oyblzsPSbR4gFZ6mFXwHwdgW7UthZSF2Dfacp4JMah5BrRLpJXQLwZvWsAdF59SsdhkriO8g157e5ghz4IPo8vsnqlWV5TNQ7rR"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cortex_token = ""
        self.session_id = ""
        self.headset_id =""
        self.socket_url = "wss://localhost:6868"
        #self.cortex = await websockets.connect(self.socket_url)



    async def connect(self):
        try:
            self.cortex = await websockets.connect(self.socket_url)
        except:
            print("[ERROR] EEG connection failed. Check if application is running on the computer")


    async def request_access(self):
        has_access_rights_json = {
        "id": self.HASACCESSRIGHT_ID,
        "jsonrpc": "2.0",
        "method": "hasAccessRight",
        "params": {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }
        }

        request_access_json ={
            "id": self.REQUEST_ACCESS_ID,
            "jsonrpc": "2.0",
            "method": "requestAccess",
            "params": {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
                }
            }


        try:
            await self.cortex.send(json.dumps(has_access_rights_json))
            msg = await self.cortex.recv()
        except:
            print("[ERROR] EEG request_access")

        if (json.loads(msg)["result"]["accessGranted"] == True):
            return
        else:
            print("Accept in Emotiv Launcher")
            access_granted = False
            while not access_granted:
                await self.cortex.send(json.dumps(request_access_json))
                msg = await self.cortex.recv()
                if (json.loads(msg)["result"]["accessGranted"] ==  True):
                    access_granted = True
            return


    async def get_headset_id(self):
        query_headsets_json= {
            "id": self.QUERY_HEADSET_ID,
            "jsonrpc": "2.0",
            "method": "queryHeadsets"
        }

        await self.cortex.send(json.dumps(query_headsets_json))
        msg = await self.cortex.recv()
        
        if (len(json.loads(msg)["result"]) >0):
            
            self.headset_id = json.loads(msg)["result"][0]["id"]
            return
        else:
            print("Connect the headset")
            headset_ok = False
            while not headset_ok:
                
                await self.cortex.send(json.dumps(query_headsets_json))
                msg = await self.cortex.recv()
                if (json.dumps(msg)["result"].length() >0):
                    self.headset_id = json.loads(msg)["result"][0]["id"]
                    headset_ok = True

            return
        
    async def authorize(self):
        authorize_json = {
            "id": self.AUTHORIZE_ID,
            "jsonrpc": "2.0",
            "method": "authorize",
            "params": {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            }   
        }

        await self.cortex.send(json.dumps(authorize_json))
        msg = await self.cortex.recv()
        self.cortex_token = json.loads(msg)["result"]["cortexToken"]
        

    async def create_session(self):
        create_session_json = {
            "id": self.CREATE_SESSION_ID,
            "jsonrpc": "2.0",
            "method": "createSession",
            "params": {
                "cortexToken": self.cortex_token,
                "headset": self.headset_id,
                "status": "open"
                }
            }
        await self.cortex.send(json.dumps(create_session_json))
        msg = await self.cortex.recv()
        self.session_id = json.loads(msg)["result"]["id"]
        
        
    async def subscribe(self):
        subscribe_json = {
            "id": self.SUBSCRIBE_ID,
            "jsonrpc": "2.0",
            "method": "subscribe",
            "params": {
                "cortexToken":self.cortex_token,
                "session": self.session_id,
                "streams": ["met"]
                }
            }
        await self.cortex.send(json.dumps(subscribe_json))
        msg = await self.cortex.recv()
        #print(json.loads(msg))

    async def end_session(self):
       pass 



    async def setup(self):
        try:
            #check access rights
            await self.request_access()

            #get headset id
            await self.get_headset_id()

            #authorize(get token)
            await self.authorize()

            #create session
            await self.create_session()

            #subscribe to data stream        
            await self.subscribe()

            #print("Setup done")
        except:
            print("[ERROR] EEG setup")


    async def get_eeg_data(self):
        data_arr = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        try:
            data = await self.cortex.recv()
            data_arr = json.loads(data)["met"]
        except:
            pass
            
        EEG_data_dict = {
            "Engagement": data_arr[1],
            "Excitement": data_arr[3],
            "Long term excitement": data_arr[4],
            "Stress/Frustration" : data_arr[6],
            "Relaxation": data_arr[8],
            "Interest/Affinity": data_arr[10],
            "Focus": data_arr[12]
        }

        #print(EEG_data_dict)
        return EEG_data_dict
            




async def main():

    client_id = "PdLqy2A8a5ukYTU6eaJki38hlZoVS5IzJaVi4G3p"
    client_secret = "CeFlg0Hqd5QltDtdbDr78whwNJqG2oyblzsPSbR4gFZ6mFXwHwdgW7UthZSF2Dfacp4JMah5BrRLpJXQLwZvWsAdF59SsdhkriO8g157e5ghz4IPo8vsnqlWV5TNQ7rR"

    cortex_api = EEG(client_id, client_secret)
    await cortex_api.connect()        
    await cortex_api.setup()
    
    while True:
        try:
            await cortex_api.get_eeg_data()
        except:
            print("[ERROR] EEG main - get_eeg_data")
            break



        




if __name__ == "__main__":
    asyncio.run(main())
    
    