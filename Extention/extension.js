//Custom Icons
let StatusGreen = "StatusActive.png"
let StatusRed =	"StatusInactive.png"
let statusbarPulse;
let connectingToServer = false

const { debug } = require('console');
const vscode = require('vscode');
const fs = require('fs');
var net = require('net');
const { json } = require('stream/consumers');
var client = new net.Socket();

const SAMValence = [
	"https://i.imgur.com/hgjLFYE.png",
	"https://i.imgur.com/A8Ou2sB.png",
	"https://i.imgur.com/5R4oEDS.png",
	"https://i.imgur.com/4vKzBoP.png",
	"https://i.imgur.com/3RBGUOs.png"
]
const SAMArousal = [ //TODO: Add Arousal Icons
	"https://i.imgur.com/OBQHlEK.png",
	"https://i.imgur.com/d2OXaVz.png",
	"https://i.imgur.com/c2QTq2w.png",
	"https://i.imgur.com/AidtLz0.png",
	"https://i.imgur.com/Np92D15.png"
]

const DevicesStatus = {"E4":false,"Eyetracker":false,"EGG":false}
/**
 * @param {vscode.ExtensionContext} context
 */

class StatisticsDataProvider
{
	constructor()
	{
		this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
	getTreeItem(element){
		return element;
	}
	getChildren(element)
	{
       return element
	}
}

class DevicesDataProvider {
	constructor() {
	  // Define the items to display in the tree view
	  this.items = [
		{
		  id: 'E4',
		  label: 'Empatica E4',
		  active: false,
		  iconPath: "$(gear)"
		},
		{
			id: 'Eyetracker',
			label: 'eyeTracker thing',
			active: false,
			iconPath: "$(gear)"
		},
		{
			id: 'EEG',
			label: 'Brainscanner',
			active: false,
			iconPath: "$(gear)"
		}
	  ];
	  iconPath: "$(gear)"
	}
  
	getChildren(element) {
		return element
	}
  
	getTreeItem(element) {
		const treeItem = {
			id: element.id,
			label: element.label,
			collapsibleState: element.children ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None,
			command: {
				command: "EmoIDE.ConnectToDevice",
				title: "Connect to Device",
				arguments: [element.id]
			  },
			iconPath: element.iconPath
		  };
		// Determine which icon to use based on the item's state
		let selectedIcon = '';
		if (element.functional) {
			selectedIcon = StatusGreen;
		} else {
			selectedIcon = StatusRed;
		}
		  return treeItem;
		}
  }
  class SAMViewProvider {
	static get viewType() { return 'SAMView'; }

	constructor(_extensionUri) {
	  this._extensionUri = _extensionUri;
	  this._view = undefined;
	}
  
	resolveWebviewView(webviewView, context, _token) {
	  webviewView.webview.options = {
		// Allow scripts in the webview
		enableScripts: true,
  
		localResourceRoots: [
		  this._extensionUri
		]
	  };
  
	  webviewView.webview.html = this.GetSAMView(0,0);
	  this._view = webviewView;
	}
  
	UpdateSAMIndex(valence,arousal) {
	  if (this._view) {
		this._view.webview.html = this.GetSAMView(Math.max(0,valence),Math.max(0,arousal));
	  	}
	}
	GetSAMView(indexVal,indexAro) {

		return `<!DOCTYPE html>
		  <html lang="en">
		  <head>
			  <meta charset="UTF-8">
		  </head>
		  <body>
			<div id=arousal align = "left">
				<p>Arousal</p>
				<img  id="SAMArousal" src="${SAMArousal[indexAro]}"/>
			</div>
		
			<div id=valence align = "left">
				<p>Valence</p>
				  <img id="SAMValence" src="${SAMValence[indexVal]}"/>
			</div>
			<script>
				const imgAro = document.getElementById('SAMArousal');
				const vscode = acquireVsCodeApi();
				window.addEventListener('message', event => {
					const imgVal = document.getElementById('SAMValence');
					
					switch (message.command) {
						case 'Valence':
							imgVal.src = message.data.SAMVal;
							break;
						case 'Arousal':
							imgAro.src = message.data.SamAro;
							break;
					}
				});
			</script>
			</body>
			</html>`;
		}
}
function RequestclientData(sentMessage)
{
	client.write(sentMessage+"|");
}
function StartDataInterval()
{
	client.write("get_data");
}
function activate(context) {
	var SAMProv = new SAMViewProvider(context.extensionUri);
	const devices = new DevicesDataProvider();
	const stats = new StatisticsDataProvider();
	vscode.workspace.getConfiguration('')
	vscode.window.createTreeView("Devices",{treeDataProvider:devices})
	vscode.window.createTreeView("SAMView",{treeDataProvider:stats})

	vscode.workspace.getConfiguration('')
	
	statusbarPulse = vscode.window.createStatusBarItem(1, 2);
	statusbarPulse.command = "statusWindow.open";
	statusbarPulse.text = "$(pulse) 0";
	statusbarPulse.color = "#42f551";
	statusbarPulse.show();

	vscode.workspace.onDidChangeConfiguration( () =>{

		//get all settings
		const user_settings = vscode.workspace.getConfiguration().get("User");
		const hardware_settings = vscode.workspace.getConfiguration().get("Hardware");
		const extension_settings = vscode.workspace.getConfiguration().get("Extension");
		//
		//merge json
		const merge_json = Object.assign(user_settings, hardware_settings, extension_settings);
		
		// merge_json["EEG"] = devices["EEG"]
		// merge_json["Eyetracker"] = devices["Eyetracker"]
		// merge_json["E4"] = devices["E4"]
		// merge_json["extension"] = true
		// merge_json["training"] = false

		vscode.window.showInformationMessage("trying to write settings");

		const onDiskPath = vscode.Uri.joinPath(context.extensionUri,"..","/Server/settings.json");
		const fileUri = vscode.Uri.file(onDiskPath.path);
		fs.writeFileSync(fileUri.fsPath, JSON.stringify(merge_json, null, 4));
		
		client.write("settings_update");
		vscode.window.showInformationMessage("settings updated");

	})
	
	context.subscriptions.push(

		vscode.window.registerWebviewViewProvider("SAMView", SAMProv),
		//Registering all commands
		vscode.commands.registerCommand('statusWindow.open', () => {
			// Create and show a new webviewtpulse
			const panel = vscode.window.createWebviewPanel(
			  'statusWindow.open', // Identifies the type of the webview. Used internally
			  'Status', // Title of the panel displayed to the user
			  vscode.ViewColumn.One, // Editor column to show the new webview panel in.
			  {
				  enableScripts: true
			  } // Webview options. More on these later.
			);
			const onDiskPath = vscode.Uri.joinPath(context.extensionUri,"..","/Server/Dashboard/Saved_dashboards/combined_dashboard.html");
			const fileUri = vscode.Uri.file(onDiskPath.path);
  
			panel.webview.html = fs.readFileSync(fileUri.fsPath, 'utf8');
			
		}),
		vscode.commands.registerCommand('EmoIDE.showSettings', () => {
			// Open the settings editor
			vscode.commands.executeCommand('workbench.action.openSettings', '@ext:EmoIDETeam.EmoIDE');
		}),
	
		vscode.commands.registerCommand('EmoIDE.connectToServer', () => {
			connectingToServer = !connectingToServer
			const pulseInterval = setInterval(StartDataInterval, 1000);
			if (connectingToServer)
			{
				connectToServer();
			}
			else
			{
				client.write("disconnect")
			}
			
		}),

		vscode.commands.registerCommand("EmoIDE.ConnectToDevice",(deviceId) =>	{
			//Insert command for connecting to server here
			
			//If connection sucessfull, set value to True
			if (devices[deviceId] == true)
			{
				vscode.window.showInformationMessage('Device "'+deviceId+'"Is now off');
				devices[deviceId] = false
			}
			else
			{
				//Try connection through server
				devices[deviceId] = true
				//If connection was successful:
				if (devices[deviceId] == true)
				{
					vscode.window.showInformationMessage('Device "'+deviceId+'"Sucessfully connected!')
				}
				else
				{
					//if connection has failed
					vscode.window.showInformationMessage('Device "'+deviceId+'"failed to connect');
				}
			}
		}),
		vscode.commands.registerCommand('EmoIDE.toggleRecording', () =>{
			client.write("toggle_session");
			vscode.window.showInformationMessage('session toggled');

		}),
		vscode.commands.registerCommand('emoide.BreakNotif', () =>{
		vscode.window.showInformationMessage('We recommend taking a break ☕');
	})
	);
function connectToServer(){
	client.connect(6969, '127.0.0.1', function() {
		console.log('Connected');
		client.write("Ping");
	});
};

// TCP communication
client.on('data', function(data){
	var dataResponse = JSON.parse(data.toString());
	switch(dataResponse["TypeOfData"])
	{
		case "Hardware":
		{
			//Pulse
			var pulse = dataResponse["Pulse"]
			statusbarPulse.text = "$(pulse)" + pulse.toString();
			//SAM
			SAMProv.UpdateSAMIndex(dataResponse["Emotion"][1]-1,dataResponse["Emotion"][0]-1);
			
			const popup_setting = vscode.workspace.getConfiguration().get("Extension.Pop-ups");

			console.log(popup_setting)

			if (Boolean(popup_setting)){
				//send notif
				//check if valence and arousal first
				//[0] = Arousal, [1] = Valence
				if (dataResponse["Emotion"][0]-1 * dataResponse["Emotion"][0]-1 >= 15) {
					vscode.window.showInformationMessage('We recommend taking a break ☕')
				}
			}
			


			
			break;
		}
		case "Ping":
		{
			vscode.window.showInformationMessage(dataResponse["Ping"]);
		}
	}

});
client.on('close', function() {
	vscode.window.showInformationMessage('Connection to server closed');
});
}


// This method is called when your extension is deactivated
function deactivate() 
{}

module.exports = {
	activate,
	deactivate
}
