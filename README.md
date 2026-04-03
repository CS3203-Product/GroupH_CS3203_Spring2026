# CS3203-Productivity-App
GroupH_Ticket5PSprint1CodeReview_CS3203Spring2026

**Uncram**<br/>
Uncram is a productivity program that helps users manage tasks through time blocking, conflict detection, and a prioritization engine that tracks deadlines and progress. An analytics dashboard monitors task completion, while a collaboration hub enables team communication, file sharing, and shared scheduling. To support focus, the program includes a timer, distraction-blocking web extension, and ambient sounds to keep users engaged during work sessions.

Within UnCram we have the function of TaskPrioritizationEngine, this function is supposed to help select which task that need to be prioritized and how long that they should be focused on that task. Almost behaves like your own AI assistant to help you manage your workload. Actual AI incorporation will be coming in later.

This README will undergo several changes over the course of our product development. Anything that is currently a placeholder will be changed according to our progression. 

**Necessary Downloads to test TaskPrioritizationEngine**<br/>
Recommend having git installed to make downloading the files easier. <br/>
We suggest using VSCode when running the test but any development tool that can run python will work. <br/>
VSCode Download Link: https://code.visualstudio.com/download <br/>
Will need to have python installed (at least version 3.11) <br/>
Methods to Install Python: <br/>
Setting up a Conda Environment (Recommended)
To avoid having conflicting dependencies between this class and any other projects you work on, we recommend setting up a virtual environment for this test. This makes installing dependencies easier, as well as prevents most common installation issues.<br/>

Install miniconda (https://www.anaconda.com/docs/getting-started/miniconda/install/overview):
Miniconda is a lightweight tool that allows you to make virtual environments, as well as gives you access to a few essential python packages.<br/>
Run conda create -n [your env name] python=3.11 in your terminal/Anaconda Prompt<br/>
Activate the environment with conda activate [your env name]<br/>
*Now that you’re in the environment, any dependencies you install with only be accessible within your virtual environment. <br/>
You will need to run the code: pip install nicegui pytest <br/>

Example: (In this Test Case we will set [Your_Environment_Name] to TestTaskPriority<br/>
(base) C:Users/username> conda create -n [Your_Environment_Name] python=3.11<br/>
(base) C:Users/username> conda activate [Your_Environment_Name]<br/>
(Your_Environment_Name) C:Users/username>pip install nicegui pytest<br/>

Now that you have a virtual environment set up, make sure you activate it before installing any dependencies or running your project. If you ever forget the name of you environment, run conda env list to get a full list of the environments you’ve created.

**Setting up Environment To Run the Test**<br/>
Now that we have set up our virtual environment in Conda we will need to select to use this environment inside VSCode.
Here is a link to a website to help explain how to set this up: https://inst.eecs.berkeley.edu/~cs188/fa24/projects/proj0/ide-workflow/ 
In this website you can focus on just setting up VSCode.

**How To Run the Test**<br/>
1.) Clone the repository into a folder to be able to download the code to test.<br/>
2.) Run git clone -b Test_TaskPriority https://github.com/CS3203-Product/GroupH_CS3203_Spring2026.git to access this test case
3.) Run the test_TaskPriority.py file in VSCode by using git bash terminal and putting in "pytest -v". You will notice only the update_day_selection will pass the test<br/>
