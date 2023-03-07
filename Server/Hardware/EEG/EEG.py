
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


    
  

    requestAccess_json ={
        "id": REQUEST_ACCESS_ID,
        "jsonrpc": "2.0",
        "method": "requestAccess",
        "params": {
            "clientId": "",
            "clientSecret": ""
        }
    } 

    hasAccessRightJson = {
        "id": HASACCESSRIGHT_ID,
        "jsonrpc": "2.0",
        "method": "hasAccessRight",
        "params": {
            "clientId": "",
            "clientSecret": ""
        }
    }
    queryHeadsets_json= {
        "id": QUERY_HEADSET_ID,
        "jsonrpc": "2.0",
        "method": "queryHeadsets"
    }
    controlDevice_json = {
        "id": CONTROL_HEADST_ID,
        "jsonrpc": "2.0",
        "method": "controlDevice",
        "params": {
            "command": "connect",
            "headset": ""
        }
    }
    authorize_json = {
        "id": AUTHORIZE_ID,
        "jsonrpc": "2.0",
        "method": "authorize",
        "params": {
            "clientId": "",
            "clientSecret": ""
        }   
    }
    hasAccessRightJson = {
        "id": HASACCESSRIGHT_ID,
        "jsonrpc": "2.0",
        "method": "hasAccessRight",
        "params": {
            "clientId": "",
            "clientSecret": ""
        }
    }
    createSession_json = {
        "id": CREATE_SESSION_ID,
        "jsonrpc": "2.0",
        "method": "createSession",
        "params": {
            "cortexToken": "",
            "headset": "",
            "status": "open"
        }
    }
    querySession_json = {
        "id": QUERY_SESSION_ID,
        "jsonrpc": "2.0",
        "method": "querySessions",
        "params": {
            "cortexToken": ""
        }
    }
    subscribe_json = {
        "id": SUBSCRIBE_ID,
        "jsonrpc": "2.0",
        "method": "subscribe",
        "params": {
            "cortexToken":"",
            "session": "",
            "streams": ["met"]
        }
    }


    def __init__(self, client_id="PdLqy2A8a5ukYTU6eaJki38hlZoVS5IzJaVi4G3p", client_secret="CeFlg0Hqd5QltDtdbDr78whwNJqG2oyblzsPSbR4gFZ6mFXwHwdgW7UthZSF2Dfacp4JMah5BrRLpJXQLwZvWsAdF59SsdhkriO8g157e5ghz4IPo8vsnqlWV5TNQ7rR"):
        self.client_id = "PdLqy2A8a5ukYTU6eaJki38hlZoVS5IzJaVi4G3p"
        self.client_secret = "CeFlg0Hqd5QltDtdbDr78whwNJqG2oyblzsPSbR4gFZ6mFXwHwdgW7UthZSF2Dfacp4JMah5BrRLpJXQLwZvWsAdF59SsdhkriO8g157e5ghz4IPo8vsnqlWV5TNQ7rR"
        self.cortex_token = ""
        self.session_id = ""
        self.headset_id =""
        self.socket_url = "wss://localhost:6868"
        #self.cortex = await websockets.connect(self.socket_url)



    async def connect(self):
        self.cortex = await websockets.connect(self.socket_url)




    async def setup(self):
        



        #check access rights
        hasAccessRightJson = {
        "id": self.HASACCESSRIGHT_ID,
        "jsonrpc": "2.0",
        "method": "hasAccessRight",
        "params": {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
            }
        }
        await self.cortex.send(json.dumps(hasAccessRightJson))
        msg = await self.cortex.recv()
        print("Access granted: " + (json.loads(msg)["result"]["message"]))

        #get headset id
        queryHeadsets_json= {
            "id": self.QUERY_HEADSET_ID,
            "jsonrpc": "2.0",
            "method": "queryHeadsets"
        }
        await self.cortex.send(json.dumps(queryHeadsets_json))
        msg = await self.cortex.recv()
        print("Headset ID: " + (json.loads(msg)["result"][0]["id"]))
        self.headset_id = json.loads(msg)["result"][0]["id"]




        #authorize(get token)
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


        #create session
        self.createSession_json["params"]["cortexToken"] = self.cortex_token
        self.createSession_json["params"]["headset"] = self.headset_id
        await self.cortex.send(json.dumps(self.createSession_json))
        msg = await self.cortex.recv()
        self.session_id = json.loads(msg)["result"]["id"]

        
        self.subscribe_json["params"]["cortexToken"] = self.cortex_token
        self.subscribe_json["params"]["session"] = self.session_id
        await self.cortex.send(json.dumps(self.subscribe_json))
        msg = await self.cortex.recv()
        print(json.loads(msg))

        print("Setup done")


    async def get_eeg_data(self):

        
        data = await self.cortex.recv()
        data_arr = json.loads(data)["met"]
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
        await cortex_api.get_eeg_data()




        




if __name__ == "__main__":
    asyncio.run(main())
    #main()
    