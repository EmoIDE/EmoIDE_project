//let api_wrapper = require("./cortex_code_example.js")
//const { connection } = require("websocket")
const socket = require("ws")
// import WebSocket from 'ws';
const fs = require("fs")


process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0
//process.env["NODE_NO_WARNINGS"] = 1




const INFO_ID = 2
const USER_LOGGED_IN_ID = 3
const REQUEST_ACCESS_ID = 4
const QUERY_HEADSET_ID = 5
const CONTROL_HEADST_ID = 6
const AUTHORIZE_ID = 7
const GETDATA_ID = 8
const CREATE_SESSION_ID = 9
const QUERY_SESSION_ID = 10
const HASACCESSRIGHT_ID = 11
const SUBSCRIBE_ID = 12



let client_Id = "PdLqy2A8a5ukYTU6eaJki38hlZoVS5IzJaVi4G3p"
let client_secret = "CeFlg0Hqd5QltDtdbDr78whwNJqG2oyblzsPSbR4gFZ6mFXwHwdgW7UthZSF2Dfacp4JMah5BrRLpJXQLwZvWsAdF59SsdhkriO8g157e5ghz4IPo8vsnqlWV5TNQ7rR"
let cortex_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6ImNvbS5hbm9uLmVtb2lkZV90ZXN0MSIsImFwcFZlcnNpb24iOiIxLjAuMCIsImV4cCI6MTY3NjY0NDQ0NCwibmJmIjoxNjc2Mzg1MjQ0LCJ1c2VySWQiOiI5ZmYyMjNlZS0wMmRiLTQwOGMtYWMzOC0wNGEyMzcxZGJkNTQiLCJ1c2VybmFtZSI6ImFub24iLCJ2ZXJzaW9uIjoiMi4wIn0.ArNmB6rnXN_HxdN62NCZC5Qmaz90dVccsEAnsgNAb78"
let session_id = ""
let headsetID = ""

let info = {"id":INFO_ID,"jsonrpc":"2.0","method":"getCortexInfo"}
let user_is_login = {"id":USER_LOGGED_IN_ID, "jsonrpc": "2.0", "method": "getUserLogin"}

//need to do once, granted
//emoide_test1
let requestAccess_json ={
    "id": REQUEST_ACCESS_ID,
    "jsonrpc": "2.0",
    "method": "requestAccess",
    "params": {
        "clientId": client_Id,
        "clientSecret": client_secret
    }
} 

//need to save id
let queryHeadsets_json= {
    "id": QUERY_HEADSET_ID,
    "jsonrpc": "2.0",
    "method": "queryHeadsets"
}

//connects to headsetID
let controlDevice_json = {
    "id": CONTROL_HEADST_ID,
    "jsonrpc": "2.0",
    "method": "controlDevice",
    "params": {
        "command": "connect",
        "headset": "headsetID"
    }
}

//need to save token
let authorize_json = {
    "id": AUTHORIZE_ID,
    "jsonrpc": "2.0",
    "method": "authorize",
    "params": {
        "clientId": client_Id,
        "clientSecret": client_secret
    }
    
}

let hasAccessRightJson = {
    "id": HASACCESSRIGHT_ID,
    "jsonrpc": "2.0",
    "method": "hasAccessRight",
    "params": {
        "clientId": client_Id,
        "clientSecret": client_secret
    }
}


//opens or activates a session, save session id
let createSession_json = {
    "id": CREATE_SESSION_ID,
    "jsonrpc": "2.0",
    "method": "createSession",
    "params": {
        "cortexToken": cortex_token,
        "headset": headsetID,
        "status": "open"
    }
}


//gets info about sessions
let querySession_json = {
    "id": QUERY_SESSION_ID,
    "jsonrpc": "2.0",
    "method": "querySessions",
    "params": {
        "cortexToken": cortex_token
    }
}

let subscribe_json = {
    "id": SUBSCRIBE_ID,
    "jsonrpc": "2.0",
    "method": "subscribe",
    "params": {
        "cortexToken":cortex_token,
        "session": session_id,
        "streams": ["met"]
    }
}


let socketUrl = "wss://localhost:6868"
let user = {
    "clientId":client_Id,
    "clientSecret": client_secret
}


//connect to api through websocket
const cortex = new socket(socketUrl)


const connected = new Promise((resolve, reject) => {
    cortex.on("open", () =>{
        if (cortex.readyState === 1){resolve(true)}
    })
})





async function send_cortex(data_to_send){

    let is_connected = await connected
    if (is_connected){
        cortex.send(JSON.stringify(data_to_send)) 
    }
    else{
        console.log("Not connected")
    }
}    



function requestAccess(){

        return new Promise((resolve, reject) => {
            send_cortex(requestAccess_json)
            cortex.on("message", (data) =>{
                if(JSON.parse(data)["id"]==REQUEST_ACCESS_ID && JSON.parse(data)["result"]["accessGranted"] == true){ 
                    resolve()
                }
                else if(JSON.parse(data)["id"]==REQUEST_ACCESS_ID == REQUEST_ACCESS_ID){
                    reject()
                }
            })

    })
}

function hasAccessRight(){
    return new Promise((resolve, reject) => {
        send_cortex(hasAccessRightJson)
        cortex.on("message", (data) =>{
            if (JSON.parse(data)["id"] == HASACCESSRIGHT_ID && JSON.parse(data)["result"]["accessGranted"] == true){
                resolve()
            }
            else if (JSON.parse(data)["id"] == HASACCESSRIGHT_ID){
                reject(JSON.parse(data)["result"]["message"])
            }
        })
    })
}



function queryHeadset(){

    return new Promise((resolve, reject) =>{
        send_cortex(queryHeadsets_json)
        cortex.on("message", (data) =>{
                if (JSON.parse(data)["id"]== QUERY_HEADSET_ID && JSON.parse(data)["result"].length > 0 ){
                    resolve(JSON.parse(data)["result"][0]["id"])
                }
                else{
                    reject()
                }
            

        })

    })

}

//connects to headset
async function controlDevice(headsetID){

    controlDevice_json["params"]["headset"] = headsetID

    return new Promise((resolve, reject) => {
        send_cortex(controlDevice_json)
        cortex.on("message", (data) => {
            if (JSON.parse(data)["id"] == CONTROL_HEADST_ID){
                // console.log(JSON.parse(data))
                resolve(data)
                
                //fix timer and reject
                // cortex.on("message", (data) =>{
                //     if (JSON.parse(data)["warning"]["code"] == 104){
                //         resolve(JSON.parse(data)["warning"]["message"]["headsetId"], JSON.parse(data)["warning"]["message"]["behavior"])
                //     }
                    
                
            }

        })
    })

}



function authorize(){

    return new Promise((resolve, reject) => {
        send_cortex(authorize_json)
        cortex.on("message", (data) =>{
            if (JSON.parse(data)["id"] == AUTHORIZE_ID){
                resolve(JSON.parse(data)["result"]["cortexToken"])
            }
        })
    })

}



function createSession(){

    createSession_json["params"]["cortexToken"] =  cortex_token
    createSession_json["params"]["headset"] = headsetID
    return new Promise((resolve, reject) => {
        send_cortex(createSession_json)
        cortex.on("message",(data) =>{
            if (JSON.parse(data)["id"] == CREATE_SESSION_ID){
                
                resolve(data, JSON.parse(data)["result"]["id"])
            }
        } )        

    })

}


function querySession(){

    return new Promise((resolve, reject) => {
        send_cortex(querySession_json)
        cortex.on("message", (data) => {
            console.log(JSON.parse(data))
            resolve(data, JSON.parse(data)["result"]["id"])
        })
    })
}


//sub to performance metrics (met)
function subscribe(){

    subscribe_json["params"]["cortexToken"] = cortex_token
    subscribe_json["params"]["session"] = session_id

    return new Promise((resolve, reject) => {
        send_cortex(subscribe_json)
        cortex.on("message", (data) => {
            if (JSON.parse(data)["id"] == SUBSCRIBE_ID){
                resolve(data)
            }
        })
    })
}





async function setup_cortex(){

    let access = false
    console.log("Trying to get access to Cortex launcher...")
    while (!access){
        
        await hasAccessRight().then(() => {access = true}).catch( () =>{
            requestAccess().then(() => {access = true}).catch((message) => {console.log(message)})})
        
    }
    console.log("Access: " + access)


   
    await queryHeadset().then((id)=> {headsetID = id}).catch(() =>{headsetID="-1"})
    console.log("Headset ID: " + headsetID)

    
    await authorize().then((token) => {cortex_token = token})
    //console.log("Token: " + cortex_token)

    await controlDevice(headsetID).then((data) =>{console.log(JSON.parse(data)["result"]["message"])})
    
    await createSession().then((data, id) => {console.log(JSON.parse(data))
            session_id = JSON.parse(data)["result"]["id"]
        })


    // await querySession().then((data, id) => {session_id = id})

    await subscribe().then((data) => {console.log(JSON.parse(data)["result"]["success"])})

    console.log("Setup done")

}


async function getData(){

    await setup_cortex()
    console.log("Running performance metrics...")
    let to_file=""
    
    cortex.on("message" ,(data) => {
            console.log(JSON.parse(data))

            to_file = JSON.parse(data)["met"].toString()
            

            fs.writeFileSync("data.txt", to_file, (err) =>{
                if (err){
                    console.log(err)
                }
            })
            

    })

    
    //met=["eng.isActive","eng","exc.isActive","exc","lex","str.isActive","str",
    //"rel.isActive","rel","int.isActive","int","foc.isActive","foc"]
    //eng =engagement, exc= excitement, lex = long term excitement, str = stress/frustration,
    //rel = relaxtion, int = interest/affinity, foc = focus ,isActive =  flag if detection working 



}



getData()






// cortex.on("message", (data) => {
//     console.log(JSON.parse(data))

// })



//setTimeout(() =>{cortex.close()}, 5000)


