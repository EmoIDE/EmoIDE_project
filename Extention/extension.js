// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
var net = require('net');
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */
var client = new net.Socket();
function activate(context) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "emoide" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with  registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('emoide.helloWorld', function () {
		// The code you place here will be executed every time your command is executed

		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from emoIDE!');
	});

	vscode.commands.registerCommand('emoide.connectToServer', () => {
		connect_to_server();
	})
	vscode.commands.registerCommand('emoide.requestEEGData', () => {

	});

	context.subscriptions.push(disposable);
}

function connect_to_server(){
	client.connect(6969, '127.0.0.1', function() {
		console.log('Connected');
		var json_data = {"function": "ping"}
		client.write(JSON.stringify(json_data));
	});
}

client.on('data', function(data){
	var json_data = JSON.parse(data.toString());
	var type_of_data = json_data["function"]
	if (type_of_data == "nånting") {
		//gör något med infon som servern skickar
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
