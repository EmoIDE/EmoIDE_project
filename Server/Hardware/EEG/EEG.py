
import json
import websockets

class EEG:
    """
    Class representing an EEG object that connects to the Emotiv Cortex API and retrieves EEG data.
    """
    
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
        """
        Initializes the EEG object with the specified client ID and client secret.

        Args:
            client_id (str): The client ID for accessing the Emotiv Cortex API.
            client_secret (str): The client secret for accessing the Emotiv Cortex API.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.cortex_token = ""
        self.session_id = ""
        self.headset_id =""
        #6868 is cortex api port
        self.socket_url = "wss://localhost:6868"

    async def connect(self):
        """
        Tries to connect to the Cortex API.

        This function establishes a connection to the Cortex API using the specified socket URL.
        It relies on the Emotiv launcher being running on the computer to establish the connection.
        If the connection fails, an error message is displayed.

        Raises:
            Exception: If the connection to the Cortex API fails.
        
        Notes:
            -   Emotiv lanucher must be running on the computer.
        """

        try:
            self.cortex = await websockets.connect(self.socket_url)
        except:
            print("[ERROR] - EEG connection failed. Check if application is running on the computer")

    async def request_access(self):
        """
        Requests access to the Cortex API.

        This function sends a request to the Cortex API to check if access rights are granted.
        If access is already granted, the function returns.
        Otherwise, it sends a request to the Cortex API to request access.
        The user is prompted to accept the access request in the Emotiv launcher.
        The function waits until access is granted before returning.

        Raises:
            Exception: If the access request fails or if access is not granted within a reasonable timeframe.
        """
        
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
            print("[ERROR] - EEG request_access")

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
        """
        Connects to the headset and retrieves the headset ID.

        This function sends a request to the Cortex API to query the available headsets.
        If at least one headset is found, it retrieves the ID of the first headset and sets it as the headset ID.
        If no headset is found, the function waits until a headset is connected and retrieves its ID.
        """
        
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
        """
        Retrieves the Cortex token needed for starting a session.

        This function sends an authorization request to the Cortex API using the client ID and client secret.
        It retrieves the Cortex token from the response and stores it in the object for future use.
        """

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
        """
        Starts a new session.

        This function sends a request to the Cortex API to create a new session using the Cortex token and the headset ID.
        The session is set to "open" status, indicating that it is active and ready to receive data.
        The session ID is retrieved from the response and stored in the object for future use.
        """

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
        """
        Subscribes to the EEG met data stream.

        This function sends a subscription request to the Cortex API.
        """

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

    async def end_session(self):
        """
        Ends the current session and disconnects from the Cortex API.

        This function sends an update session request to the Cortex API to change the status of the current session to "close".
        It then closes the connection to the Cortex API.
        """

        end_session_json = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "updateSession",
            "params": {
                "cortexToken": self.cortex_token,
                "session": self.session_id,
                "status": "close"
            }
        }

        await self.cortex.send(json.dumps(end_session_json))
        msg = await self.cortex.recv()

        await self.cortex.close() 

    async def setup(self):
        """
        Sets up the EEG object before retrieving EEG data.

        This function performs the necessary setup steps in sequence:
        1. Checks access rights by calling the request_access() function.
        2. Retrieves the headset ID by calling the get_headset_id() function.
        3. Authorizes the EEG object by calling the authorize() function.
        4. Creates a new session by calling the create_session() function.
        5. Subscribes to the EEG data stream by calling the subscribe() function.

        Notes:
            -   Need to run this before 'get__eeg_data()' function.
        """

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

    async def get_eeg_data(self):
        """
        Retrieves EEG data from the Cortex API.

        This function listens for EEG data from the Cortex API and returns a dictionary with the following metrics:
        [Engagement, Excitement, Long-term Excitement, Stress/Frustration, Relaxation, Interest/Affinity, Focus].
        The EEG data is updated every tenth of a second.

        Returns:
            dict: A dictionary containing the EEG metrics.

        Raises:
            Exception: If there is an error in receiving or parsing the EEG data.
        """
        
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

        return EEG_data_dict