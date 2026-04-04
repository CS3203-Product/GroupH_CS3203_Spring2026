# CS3203-Productivity-App
GroupH_Ticket5PSprint1CodeReview_CS3203Spring2026

Uncram
Uncram is a productivity program that helps users manage tasks through time blocking, conflict detection, and a prioritization engine that tracks deadlines and progress. An analytics dashboard monitors task completion, while a collaboration hub enables team communication, file sharing, and shared scheduling. To support focus, the program includes a timer, distraction-blocking web extension, and ambient sounds to keep users engaged during work sessions.

Within UnCram, we have the function of FocusModeTimer. This function is responsible for representing a focus mode timer to help users stay focused on their tasks
    # We are creating a Pomodoro-style timer
    # It breaks work into 25-minute "work" intervals with 5-minute breaks in between. 
    # As for the unit test, we set the timer for work to 1 minute.
    # After four "Pomodoros", the user takes a longer break of 15-30 minutes.

This README will undergo several changes over the course of our product development. Anything that is currently a placeholder will be changed according to our progression.

Necessary Downloads to test FocusModeTimer
Recommend having git installed to make downloading the files easier.
We suggest using VSCode when running the test, but any development tool that can run Python will work.
VSCode Download Link: https://code.visualstudio.com/download
Will need to have Python installed (at least version 3.11)
Then, you will need to run the code: pip install nicegui

How To Run the Test
1. For a smooth experience, you can download GitHub Desktop instead of using the terminal to clone the repository. https://desktop.github.com/download/
2. After downloading, in the top left of GitHub Desktop, you can clone the repository into a folder to be able to download the code to test. Then it will appear as the main branch, switch to the FocusModeTimer branch.
3. Install Python https://www.python.org/downloads/. When the installer opens, you MUST check the box at the bottom that says:
☑ Add Python.exe to PATH
(If you miss this, pip won't work later!) Then, in the VS Code extension, install Python again to trigger the PATH.
4. In the center of the GitHub Desktop, you will see "Open the repo in your external editor." Choose "Open in VS Code."
5. GIT BASH type "python -m pip install nicegui." Then, "python -m unittest test_FocusModeTimer.py"


