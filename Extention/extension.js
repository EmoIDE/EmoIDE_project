//Custom Icons
let StatusGreen = "StatusActive.png"
let StatusRed =	"StatusInactive.png"
let statusbarPulse;

const { debug } = require('console');
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */

class DataProvider {
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
			label: 'Eyetracker thing',
			active: false,
			iconPath: "Icons/Logo.png"
		},
		{
			id: 'BrainTracker',
			label: 'Brainscanner',
			active: false,
			iconPath: "Icons/Logo.png"
		}
	  ];
	  this.settingsItem = {
		id: 'settings',
		label: 'Settings',
		command: 'myExtension.showSettings'
	};
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
			command: element.command,
			iconPath: element.iconPath
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
			treeItem.iconPath = "Icons/Logo.png";
		}
		  return treeItem;
		}
  }
function activate(context) {

	statusbarPulse = vscode.window.createStatusBarItem(1, 2);
	statusbarPulse.command = "statusWindow.open";
	statusbarPulse.text = "$(pulse) 0";
	statusbarPulse.color = "#42f551";
	statusbarPulse.show();

	vscode.workspace.getConfiguration('')
	const dataProvider = new DataProvider();
	const treeView = vscode.window.createTreeView("Devices",{treeDataProvider:dataProvider})
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
		  panel.webview.html = getWebviewContent();
		  
		})
	  );
	context.subscriptions.push(
		vscode.commands.registerCommand('EmoIDE.showSettings', () => {
			// Open the settings editor
			vscode.commands.executeCommand('workbench.action.openSettings', '@ext:EmoIDETeam.EmoIDE');
		})
	);

	context.subscriptions.push(
		vscode.commands.registerCommand('EmoIDE.connectToServer', () => {
			connectToServer();
		})
	);
	context.subscriptions.push(
		vscode.commands.registerCommand('EmoIDE.requestEyeData', () => {
			const gettingEyeData = setInterval(getEyeData, 1000);
		})
	);

	let disposable = vscode.commands.registerCommand('emoide.BreakNotif', function () {
		// The code you place here will be executed every time your command is executed

		// Display a message box to the user
		vscode.window.showInformationMessage('We recommend taking a break ☕');
	});

	context.subscriptions.push(disposable);
}
function getWebviewContent() {
	return `<!DOCTYPE html>
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
  }
  
  function connectToServer(){
	client.connect(6969, '127.0.0.1', function() {
		console.log('Connected');
		var json_data = {"function": "ping"}
		client.write(JSON.stringify(json_data));
	});
};

function getEyeData(){
	var json_data = {"function": "getEyeData"}
	client.write(JSON.stringify(json_data));
}
client.on('data', function(data){
	var json_data = JSON.parse(data.toString());
	var type_of_data = json_data["function"]
	if (type_of_data == "eyeData") {
		//gör något med infon som servern skickar
		//sparar/visar data på något snyggt sätt
	}

});
client.on('close', function() {
	console.log('Connection closed');
});
// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
