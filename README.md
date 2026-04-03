# CS3203-Productivity-App
GroupH_Ticket5PSprint1CodeReview_CS3203Spring2026

**Uncram**<br/>
Uncram is a productivity program that helps users manage tasks through time blocking, conflict detection, and a prioritization engine that tracks deadlines and progress. An analytics dashboard monitors task completion, while a collaboration hub enables team communication, file sharing, and shared scheduling. To support focus, the program includes a timer, distraction-blocking web extension, and ambient sounds to keep users engaged during work sessions.

Within UnCram we have the function of TaskPrioritizationEngine, this function is supposed to help select which task that need to be prioritized and how long that they should be focused on that task. Almost behaves like your own AI assistant to help you manage your workload. Actual AI incorporation will be coming in later.

This README will undergo several changes over the course of our product development. Anything that is currently a placeholder will be changed according to our progression. 

**Necessary Downloads to test TaskPrioritizationEngine**<br/>
We suggest using VSCode when running the test but any development tool that can run python will work.
VSCode Download Link: https://code.visualstudio.com/download
Will need to have python installed (at least version 3.11)
Methods to Install Python:
Setting up a Conda Environment (Recommended)
To avoid having conflicting dependencies between this class and any other projects you work on, we recommend setting up a virtual environment for this test. This makes installing dependencies easier, as well as prevents most common installation issues.

Install miniconda (https://www.anaconda.com/docs/getting-started/miniconda/install/overview):
Miniconda is a lightweight tool that allows you to make virtual environments, as well as gives you access to a few essential python packages.
Run conda create -n [your env name] python=3.11 in your terminal/Anaconda Prompt
Activate the environment with conda activate [your env name] *Now that you’re in the environment, any dependencies you install with only be accessible within your virtual environment.

Example: (In this example we will set [Your_Environment_Name] to TestTaskPriority
(base) C:Users/username> conda create -n [Your_Environment_Name] python=3.11
(base) C:Users/username> conda activate [Your_Environment_Name]
(Your_Environment_Name) C:Users/username>

Now that you have a virtual environment set up, make sure you activate it before installing any dependencies or running your project. If you ever forget the name of you environment, run conda env list to get a full list of the environments you’ve created.

**Setting up Environment To Run the Test**<br/>
Now that we have set up our virtual environment in Conda we will need to select to use this environment inside VSCode.
Here is a link to a website to help explain how to set this up: https://inst.eecs.berkeley.edu/~cs188/fa24/projects/proj0/ide-workflow/ 
In this website you can focus on just setting up VSCode.

**How To Run the Test**<br/>



