==========
FAQ
==========

Question 1
-----------

**Q: What is the purpose of this tool?**

**A:** The purpose of this tool is to develop an emotionally-aware IDE plugin that leverages developers' emotions to improve their work in software development. The tool aims to integrate affective computing and biometric data analysis into the IDE, allowing developers to receive information about their emotional states. By being aware of their emotional states, developers can make informed decisions regarding code quality, productivity, and well-being. The tool's objectives include eliciting requirements, designing user interfaces, processing biometric data, developing a prototype plugin, and evaluating its effectiveness in collaboration with the customer and other developers.

Question 2
-----------

**Q: How do I get started with the tool?**

**A:** To get started with the tool, follow these steps:

1. Install the necessary Python modules
    To get started with the tool, you need to install the required Python modules. Follow these steps:
        1. Open the command prompt or terminal.
        2. Navigate to the project directory using the command:

.. code-block:: python

    cd {projectPath}/Server/

3. Install the required Python modules by running the following command:

.. code-block:: python

    pip install -r Requirements.txt

Make sure you have Python installed on your system before proceeding with the installation of the modules.

2. Start the server
    After installing the required modules, you can start the server. Follow these steps:
        1. Open the command prompt or terminal.
        2. Navigate to the project directory using the command:

.. code-block:: python

    cd {projectPath}/Server/

3. Run the following command to start the server:

.. code-block:: python

    python main.py

This will initiate the server, allowing it to listen for requests.

3. Start using the product
    Once the server is up and running, you can start using the product. This project aims at improving an early prototype of an IDE plugin that leverages developers' emotions to enhance their work. Here's how you can get started:

    a. Install the IDE plugin in the Visual Studio Code (IDE).
    b. Launch the IDE and open a project or create a new one.
    c. Use the plugin features to analyze and utilize emotional cues to enhance your programming experience. 
    
    Feel free to explore the various functionalities and features offered by the product.

Question 3
-----------

**Q: Can I customize the settings?**

**A:** Yes, you can customize the settings in the extension according to your preferences. The following are some of the settings that you can modify:

- Age: Specify your age.
- Gender: Choose your gender.
- RestingHeartRate: Set your resting heart rate.
- Glasses: Indicate whether you wear glasses or not.
- E4StreamingPort: Define the port for E4 streaming.
- EyeTrackerCalibration: Enable or disable eye tracker calibration.
- EEG: Enable or disable EEG functionality.
- E4: Enable or disable E4 device.
- Eyetracker: Enable or disable eye tracker.
- ServerPort: Set the port for the server.
- FileFormat: Choose the file format for data storage.
- SaveLocation: Specify the location where the output files will be saved.
- DonateData: Decide whether to donate data or not.
- Pop-ups: Enable or disable pop-up notifications.

These settings control various aspects of the extension, such as personal information, device configuration, communication ports, data file format, saving location, and specific features. Feel free to modify these settings in the provided JSON configuration file to tailor the extension to your specific needs.

Question 4
-----------

**Q: What are the supported operating systems for this tool?**

**A:** The tool currently only supports Windows 10 and above.

Please note that the tool has been tested and designed specifically for Windows 10 and higher versions. It may not be compatible with earlier versions of Windows or other operating systems such as macOS or Linux.

If you are using a different operating system, we recommend checking for any available updates or alternative versions of the tool that may be compatible with your specific platform. Our development team is constantly working to expand the supported operating systems, so please stay tuned for any future updates regarding additional platform support.

If you have any further questions or concerns regarding the tool's compatibility with your operating system, please don't hesitate to reach out to our support team for further assistance.

Question 5
-----------

**Q: How do I update the tool to the latest version?**

**A:** Updating the tool to the latest version is a straightforward process. Here's how you can do it:

1. Visit our GitHub repository to access the latest builds and updates. You can find the repository at the following link: `Link to GitHub Repo. <https://github.com/EmoIDE/EmoIDE_project>`_

2. Once you're on the GitHub repository page, navigate to the "Releases" section. This section contains all the available versions and updates for the tool.

3. Look for the latest release or version of the tool. Usually, the latest version will be listed at the top. Release versions are typically tagged with version numbers or release names for easy identification.

4. Click on the release or version you want to update to. This will take you to the release page, where you can find detailed information about the update, including any new features, bug fixes, or improvements.

5. On the release page, you'll find the necessary files or installation instructions to update the tool. Follow the provided instructions to download and install the latest version on your system.

6. If the tool requires any specific installation steps or dependencies, make sure to follow those instructions as well. This ensures a smooth update process without any compatibility issues.

7. Once the update is successfully installed, you can launch the tool with the latest version and enjoy the new features and improvements it offers.

Remember to check the GitHub repository periodically for new releases and updates to stay up to date with the latest enhancements and bug fixes. It's always recommended to back up your data before performing any updates to avoid potential data loss.

If you encounter any issues during the update process, refer to the documentation provided with the tool or consult the support resources available on our GitHub repository for assistance.

Feel free to reach out if you have any further questions or concerns.

Question 6
-----------

**Q: What are the main features of the tool?**

**A:** The tool offers several main features to enhance the software development process. These features include:

Emotion Monitoring: The tool incorporates affective computing techniques to monitor developers' emotional states during their work. It analyzes physiological signals such as eye movements (saccades), blood volume pulse (BVP), galvanic skin response (GSR), and electroencephalography (EEG) to identify and correlate specific emotions.

Emotional Feedback: Based on the analysis of developers' emotional states, the tool provides real-time feedback and notifications within the Integrated Development Environment (IDE). This feedback helps developers become aware of their emotional well-being, enabling them to make informed decisions about their work patterns and productivity.

Code Quality Suggestions: The tool leverages emotional data to make suggestions regarding the quality of code written in different emotional states. It can identify code segments at the monitor that were looked at while the developer was in a distracted or stressed state, highlighting the need for special attention before integration into the system or product.

Work Break Recommendations: By recognizing when a developer has been working in an apprehensive state for an extended period, the tool can suggest the need for a break. This feature promotes a healthy work-life balance and helps prevent burnout by encouraging developers to take breaks when necessary.

Flow State Preservation: The tool recognizes when a developer is in a "flow" state, characterized by high focus and productivity. It provides notifications to minimize interruptions, ensuring that developers can maintain their optimal performance and creativity during these periods.

Integration with Existing IDEs: The tool is designed to be integrated as a plugin in the Visual Studio Code Integrated Development Environments (IDEs). This allows developers to leverage its features seamlessly within their preferred development environment.

Please note that these are the main features of the tool, and there may be additional functionalities and capabilities depending on the specific implementation and version of the IDE plugin.

Question 7
-----------

**Q: Are there any known limitation or known issues with the tool?**

**A:** While using the tool, there are a few known limitations and issues to be aware of:

- The tool may have limitations in accurately capturing a wide range of emotions. It might primarily focus on specific emotions like arousal and valence which can be translated into stress and flow. Therefore, it is important to understand the specific emotional dimensions the tool measures and interpret the results accordingly.

- Greater amount of sensor provides greater accuracy in response: The accuracy of the tool's response may vary depending on the number and quality of sensors used. Using a greater number of sensors can potentially provide more precise and reliable measurements. It is advisable to consider the sensor setup and configuration to optimize the accuracy of the tool's readings.

- Data recordings over longer periods and multiple sessions may clutter up the drive: If the tool records data over extended periods or multiple sessions, it can result in a significant amount of data being stored locally. This accumulation of data may consume storage space and potentially clutter the drive. It is recommended to regularly review and manage the stored data, ensuring sufficient disk space is available and organizing the data files to maintain a well-structured record.

It's important to keep these limitations and issues in mind when using the tool, as they can impact the accuracy and usability of the recorded data. Understanding these factors will help you make informed decisions and effectively interpret the results obtained from the tool.

Question 8
-----------

**Q: If I want to dive deeper about the data being recorded, where should I look?**

**A:** To explore the recorded data in more detail, you can refer to the locally saved files located in the folder named **Server/Output/**. Within this folder, you will find dataframes that contain the recorded data. These dataframes provide a structured representation of the data, allowing for further analysis and exploration.


Question 9
-----------

**Q: Does the tool have any built-in security measures to protect my data?**

**A:** The tool's security is solely reliant on the user, as all recordings and communications are performed and saved locally. It is essential for the user to ensure appropriate security measures are in place to protect their data.

Since the tool operates locally, the responsibility of securing the data rests with the user. It is recommended to follow best practices for securing your computer and the storage location where the data is saved. This may include using strong passwords, encrypting the storage device, implementing firewall and antivirus protection, and regularly updating your system and security software.