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
*Now that you’re in the environment, any dependencies you install with only be accessible within your virtual environment.

Example: (In this Test Case we will set [Your_Environment_Name] to TestTaskPriority<br/>
(base) C:Users/username> conda create -n [Your_Environment_Name] python=3.11<br/>
(base) C:Users/username> conda activate [Your_Environment_Name]<br/>
(Your_Environment_Name) C:Users/username><br/>

Now that you have a virtual environment set up, make sure you activate it before installing any dependencies or running your project. If you ever forget the name of you environment, run conda env list to get a full list of the environments you’ve created.

**Setting up Environment To Run the Test**<br/>
Now that we have set up our virtual environment in Conda we will need to select to use this environment inside VSCode.
Here is a link to a website to help explain how to set this up: https://inst.eecs.berkeley.edu/~cs188/fa24/projects/proj0/ide-workflow/ 
In this website you can focus on just setting up VSCode.

**How To Run the Test**<br/>
1.) Clone the repository into a folder to be able to download the code to test.<br/>
2.) Run the test_TaskPriority.py file in VSCode<br/>
Once the test is ran we shall see that for each test case there will be a corresponding true or false: <br/>
Test Case 1: Task Creation<br/>
This first test is seeing if a task can be created at all and that it was stored. Should see True as the output<br/>

Test Case 2: Prevent Empty Task<br/>
This test is seeing if you can create a blank task by entering just empty space. Should see true

Test Case 3: Due Date Change
This is to test that the function will allow you to update the due date of a task

Test Case 4: Testing Creation of Multiple Tasks
Checking that the function will create multiple different task and have them appropriately named. As well as stored in a list to be able to be called on later.

