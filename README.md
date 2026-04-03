 HEAD
 HEAD
# CS3203-Productivity-App

**Uncram**<br/>
UnCram is a productivity program that helps users manage tasks through time blocking, conflict detection, and a prioritization engine that tracks deadlines and progress. An analytics dashboard monitors task completion, while a collaboration hub enables team communication, file sharing, and shared scheduling. To support focus, the program includes a timer, distraction-blocking web extension, and ambient sounds to keep users engaged during work sessions.

**Breakdown of UnCram:**
+ Language: Python
+ API(s) used: FastAPI,
+ Development Tools: Visual Studio Code
  
This README will undergo several changes over the course of our product development. Anything that is currently a placeholder will be changed according to our progression. 

**Installation Method**<br/>
At this time, an installation for the program is currently unavailable as it is currently in early stages of development.

**Current Status**<br/>
The program is currently in early stages of development. Changes and updates on progression of our development will be stated explicitly here.

**Usage**<br/>
Access and availability to the program is unavailable as the development is in its early stages. However, upon development completion, the program will be accessible on a public domain through the web included with all features.

**Development Roadmap**

***Phase 1: Task Concentration***

**Focus Timer**
+ Implement a focus timer that turns on when focus sessions begin.
+ Test UI of the focus timer to ensure it displays focus time remaining.
  
**Distraction Blocker**
+ Create a web-based extension that will prevent other programs from being browsed.
  
**Ambient Focus Aids**
+ Design sounds and small tunes that best aid concentration during focus sessions.

***Phase 2: Task Progression***

**Task Prioritization Engine**
+ Build an accessible page with an engine that stores task information, deadlines, calendar with scheduled tasks, along with providing small details about task completion.
+ Develop a dashboard category where task completion and progress can be viewed, indicating amount of work done and time spent on completion.
+ Construct a collaboration hub that allows communication with other users using the program, file sharing, and project management to track task progression.

**Task Analytics Dashboard**
+ Design a dashboard that collects task completion progress, records time spent on task completion, and how many tasks are being completed on a daily bais
+ Provides task completion and analytics data based on daily progression, weekly progression, etc.

**Collaboration Hub**
+ Develop a collaborative tool that allows for file sharing, communication, and managing projects and tasks.
+ Ensure tasks within a group can undergo changes by group members, tasks can be completed and submitted individually, and users can communicate task completion progress with others in their groups. 

**Development Team**<br/>
To reach developers on the team about product inquires, discord usernames are listed below:<br/>

[dopc]<br/>
[thesilverback4521]<br/>
[cindaman]<br/>
[yoghurtboy]<br/>
[nguyetng]<br/>
[onejosh]<br/>
[crazinessjoy]<br/>
=======
test
>>>>>>> 0d0ffcf (Update README.md)
=======
**Uncram** is a productivity program that helps users manage tasks through time blocking, conflict detection, and a prioritization engine that tracks deadlines and progress. An analytics dashboard monitors task completion, while a collaboration hub enables team communication, file sharing, and shared scheduling. To support focus, the program includes a timer, distraction-blocking web extension, and ambient sounds to keep users concentrated and free of distraction during work sessions.

Within Uncram, the DistractionBlocker feature blocks access to other websites when a task session begins based on blocks of time scheduled and opens access to those select websites when the task session ends. 

As the product is still undergoing development, changes will be made to this read me to clearly state what this feature will do and its effectiveness towards our final product.

**Steps to Test DistractionBlocker**

1) Make sure git is installed so downloading and accessing files is convenient
   
2) As Visual Studio Code is the base our where our code is stored, it is best to download VS Code to run the test.
Visual Studio Code Download https://code.visualstudio.com/download

3) Python is the programming language used for our project so you MUSt have it installed through your terminal before you can test the file.
   Steps to install Python:
   - Follow the link to download Python: Windows: (https://www.python.org/downloads/windows/) macOS: https://www.python.org/downloads/macos/
   - When you run the . exe file, on the first screen, check the box "Add python.exe to path" and click install now
   - Once finished downloading, open the command prompt and type "python --version" or "python3 --version" to verify installation

4) Install pip in your terminal for accessing using the Python GUI and pytest
   Steps to install pip:
   - In your terminal, type "pip --version" or "py -m pip --version" for Windows users, type "pip3 --version" or "python3 -m pip --version". If pip is not installed on your computer, follow the next steps.
   - Download the get-pip.py script from the following link: https://pip.pypa.io/en/latest/installation/
   Steps to install pytest:
   - Once installed, go to your terminal and type "python get-pip.py" for Windows and "python3 get-pip.py" for macOS.
   - Once pip is installed, install pytest by typing in the terminal "pip install pytest" (Windows) or "pip3 install pytest" (macOS)
   - To confirm pytest is installed, type "pytest --version" in your terminal.
   Steps to install NiceGUI:
   - pip install nicegui
  
   Now that you have the necessary installations, here are the steps to test the file:
   - Clone the group repository using typing "git clone https://github.com/CS3203-Product/GroupH_CS3203_Spring2026"
   - Clone the feature code by typing "git clone -b DistractionBlocker --single-branch [repostiory link]"
   - 
>>>>>>> bc84cef (Update README with Uncram program details and setup steps)
