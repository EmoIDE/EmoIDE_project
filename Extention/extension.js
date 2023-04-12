//Custom Icons
let StatusGreen = "StatusActive.png"
let StatusRed =	"StatusInactive.png"
let statusbarPulse;

const { debug } = require('console');
const vscode = require('vscode');
const fs = require('fs');
var net = require('net');
var client = new net.Socket();
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
const DevicesStatus = {"wristBand":false,"eyeTracker":false,"brainTracker":false}
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
	getChildren(element)
	{

        if (element.label === 'Webview 1') {
            // Return webview node
            const panel = vscode.window.createWebviewPanel(
                'SAMStatus',
                'Emotional status',
                vscode.ViewColumn.One,
                {}
            );
			panel.webview.html = '<h1>Hello World from Webview 1!</h1>';

		}
	}
}

class DevicesDataProvider {
	constructor() {
	  // Define the items to display in the tree view
	  this.items = [
		{
		  id: 'wristBand',
		  label: 'Empatica E4',
		  active: false,
		  iconPath: "Icons/Logo.png"
		},
		{
			id: 'Eyetracker',
			label: 'eyeTracker thing',
			active: false,
			iconPath: "Icons/Logo.png"
		},
		{
			id: 'brainTracker',
			label: 'Brainscanner',
			active: false,
			iconPath: "Icons/Logo.png"
		}
	  ];
	  icon: "StatusGreen"
	}
  
	getChildren(element) {
	  if (!element) {
		// return top-level items
		return Promise.resolve(this.items);
	  } else {
		// return children of a given item
		const item = this.items.find(item => item.id === element.id);
		if (item && item.children) {
		  return Promise.resolve(item.children);
		} else {
		  return Promise.resolve([]);
		}
	  }
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

const devices = new DevicesDataProvider();
const stats = new StatisticsDataProvider();

function activate(context) {

	statusbarPulse = vscode.window.createStatusBarItem(1, 2);
	statusbarPulse.command = "statusWindow.open";
	statusbarPulse.text = "$(pulse) 0";
	statusbarPulse.color = "#42f551";
	statusbarPulse.show();

	vscode.workspace.getConfiguration('')
	const treeView = vscode.window.createTreeView("Devices",{treeDataProvider:devices})
	const treeViewStats = vscode.window.createTreeView("Stats",{treeDataProvider:stats})
	// The command has been defined in the package.json file
	// Now provide the implementation of the command with  registerCommand
	// The commandId parameter must match the command field in package.json

	context.subscriptions.push(
		vscode.commands.registerCommand('statusWindow.open', () => {
		  // Create and show a new webview
		  const panel = vscode.window.createWebviewPanel(
			'statusWindow.open', // Identifies the type of the webview. Used internally
			'Status', // Title of the panel displayed to the user
			vscode.ViewColumn.One, // Editor column to show the new webview panel in.
			{
				enableScripts: true
			} // Webview options. More on these later.
		  );
		  const onDiskPath = vscode.Uri.joinPath(context.extensionUri,"..","/Server/Dashboard/Saved_dashboards/dashboard.html");
		  const fileUri = vscode.Uri.file(onDiskPath.path);

		  panel.webview.html = fs.readFileSync(fileUri.fsPath, 'utf8');
		  
		}),

		vscode.commands.registerCommand('EmoIDE.showSettings', () => {
			// Open the settings editor
			vscode.commands.executeCommand('workbench.action.openSettings', '@ext:EmoIDETeam.EmoIDE');
		}),
	
		vscode.commands.registerCommand('EmoIDE.connectToServer', () => {
			connectToServer();
			const gettingEyeData = setInterval(getCurrentPulse, 1000);
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



		vscode.commands.registerCommand('emoide.BreakNotif', () =>{
		// The code you place here will be executed every time your command is executed

		// Display a message box to the user
		vscode.window.showInformationMessage('We recommend taking a break ☕');
	})
	);

	context.subscriptions.push();
}
function getWebviewContent() {
	return null
	//Andvänd som placeholder tillsvidare

	/*`<!DOCTYPE html>
  <html lang="en">
  <head>
	  <meta charset="UTF-8">
	  <meta name="viewport" co5ntent="width=device-width, initial-scale=1.0">
	  <title>Cat Coding</title>
  </head>
  <body>
	  <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
	  <h1>LOOK AT THIS CAT WOAW</h1>
  </body>
  </html>`;
  */
  }
  
  function connectToServer(){
	client.connect(6969, '127.0.0.1', function() {
		console.log('Connected');
		var json_data = {"function": "ping"}
		client.write(JSON.stringify(json_data));
		
	});
};



function getCurrentPulse(){
	var json_data = {"function": "getPulse"}
	client.write(JSON.stringify(json_data));
}
client.on('data', function(data){
	var json_data = JSON.parse(data.toString());
	var type_of_data = json_data["function"]
	if (type_of_data == "ping") {
		console.log("ping funka");
		//gör något med infon som servern skickar
		//sparar/visar data på något snyggt sätt
		//vscode.window.showInformation Message('received ping');
	}
	if (type_of_data == "getCurrentPulse") {
		//gör något med infon som servern skickar
		//sparar/visar data på något snyggt sätt
		console.log("ss");
		var pulse = json_data["data"]
		statusbarPulse.text = "$(pulse)" + pulse.toString();
	}


});
client.on('close', function() {
	vscode.window.showInformationMessage('Connection closed');
});
// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
