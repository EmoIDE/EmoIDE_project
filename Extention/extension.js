//Custom Icons
let StatusGreen = "StatusActive.png"
let StatusRed =	"StatusInactive.png"
let statusbarPulse;

const { debug } = require('console');
const vscode = require('vscode');
const fs = require('fs');

const DevicesStatus = {"wristBand":false,"Eyetracker":false,"BrainTracker":false}
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */


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
			contextValue: "Eyetracker",
			label: 'Eyetracker thing',
			active: false,
			iconPath: "Icons/Logo.png"
		},
		{
			id: 'BrainTracker',
			contextValue: "BrainTracker",
			label: 'Brainscanner',
			active: false,
			iconPath: "Icons/Logo.png"
		}
	  ];

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
			  }
		  };

		if (!element) {
			treeItem.description = 'settings';
			treeItem.contextValue = 'header';
		  }
		  else {
			// Determine which icon to use based on the item's state
			let selectedIcon = '';
			if (element.functional) {
			  selectedIcon = StatusGreen;
			} else {
			  selectedIcon = StatusRed;
			}
		}
		  return treeItem;
		}
  }

const devices = new DevicesDataProvider();
function activate(context) {

	statusbarPulse = vscode.window.createStatusBarItem(1, 2);
	statusbarPulse.command = "statusWindow.open";
	statusbarPulse.text = "$(pulse) 0";
	statusbarPulse.color = "#42f551";
	statusbarPulse.show();

	vscode.workspace.getConfiguration('')
	
	const devicesTreeView = vscode.window.createTreeView("Devices",{treeDataProvider:devices})
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
			{} // Webview options. More on these later.
		  );
			
		  //Local file path converted to Uri
		  const onDiskPath = vscode.Uri.joinPath(context.extensionUri,"..","/Server/Output/output_data.html");
		  const fileUri = vscode.Uri.file(onDiskPath.path);

		  panel.webview.html = fs.readFileSync(fileUri.fsPath, 'utf8');
		}),

		vscode.commands.registerCommand('EmoIDE.showSettings', () => {
			// Open the settings editor
			vscode.commands.executeCommand('workbench.action.openSettings', '@ext:EmoIDETeam.EmoIDE');
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

		vscode.commands.registerCommand("EmoIDE.BreakNotif",() =>	{
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
	  <meta name="viewport" content="width=device-width, initial-scale=1.0">
	  <title>Cat Coding</title>
  </head>
  <body>
	  <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
	  <h1>LOOK AT THIS CAT WOAW</h1>
  </body>
  </html>`;
  */
  }
  
// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
