<h1>Emotionally-Aware IDE</h1>
Welcome to the Emotionally-Aware IDE GitHub repository! This plugin is designed to increase productivity and quality in software development by leveraging developers' emotions to enhance their work. By integrating affective computing and biometric data analysis into the IDE, developers can receive valuable insights into their emotional states, enabling them to make informed decisions regarding code quality, productivity, and well-being.

<h2>Purpose</h2>
The purpose of this tool is to develop an emotionally-aware IDE plugin that empowers developers to improve their software development process. The key objectives of this tool include:

- **Emotion Monitoring**
- **Emotional Feedback**
- **Code Qualtiy Suggestions**
- **Work break recommendations**
- **Flow State Preservation**
- **Integration with Visual Studio Code (IDE)**

<h2>Requirements</h2>
Before running this tool to its full extent, make sure you meet the following necessary requirements:

1. **Python Server**:
  Install the necessary requirements for the Python server. Refer to the **Getting Started** section for detailed instructions.
2. **Gazepoint Control**:
  The [Gazepoint Control](https://www.gazept.com/downloads/) provided by Gazepoint must be active during a session to record data from the eye tracker. Calibrating the eye tracker is recommended to enhance gaze accuracy.
3. **E4 Streaming Service**:
  The [E4 Streaming Service](https://developer.empatica.com/windows-streaming-server-usage.html) provided by Empatica must be active and connected during a session to record data from the wristband.
4. **EEG Launcher**:
  The [EEG Launcher](https://www.emotiv.com/emotiv-launcher/) provided by Emotiv must be active and connected during a session to record data from the EEG device.


<h2>Getting Started</h2>
To get started with the Emotionally-Aware IDE Plugin, follow these steps:

1. **Install the necessary Python modules**:
Open the command prompt or terminal.
Install the required Python modules by running the following command:
```
pip install -r Requirements.txt
```
> Note: Ensure that Python is installed on your system before proceeding with the installation of the modules.

2. **Start the server**:
  After installing the required modules, you can start the server and pen the command prompt or terminal and then run the following command to start the server:
```
python main.py
```
> Note: This will initiate the server, enabling it to listen for extension connection

3. **Start using the product**:
  - Once the server is up and running, you can start utilizing the Emotionally-Aware IDE Plugin.
  - Follow these steps to integrate and utilize the plugin within Visual Studio Code (IDE):
    - Install the IDE plugin in Visual Studio Code.
    - Launch the IDE and open an existing project or create a new one.
    - Utilize the plugin features to analyze and leverage emotional cues to enhance your programming experience.
  - Feel free to explore the various functionalities and features offered by the product.

We hope that this tool significantly improves your software development process by incorporating emotions as a valuable asset. Should you encounter any issues, have suggestions please don't hesitate to create an issue or pull request on this repository. Happy coding!
