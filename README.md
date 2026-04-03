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
1.) Clone the repository into a folder to be able to download the code to test.
2.) Run the test_FocusModeTimer.py file in VSCode by using git bash terminal and putting in "python -m unittest test_FocusModeTimer.py". You will notice that all 6 tests pass.
