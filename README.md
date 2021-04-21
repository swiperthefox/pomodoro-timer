# Yet Another Pomodoro Timer

## Features:

* A simple task manager.
* Start a session timer for a given task.
* (Optionally) Add a short note after a session ends.
* Show session history for a task.
* A "Todo task" that captures small things which do not worth a whole session.

## Quick Start

1. Download the files, extract the contents.
2. Run the `main.py` file using python 3.

The program requires the `tkinter` module, which may not be installed with python by default on some systems.

## Usage

The following diagram shows the main features of the app.

![main feature](doc.png)

The rest of the user interfaces are self-explaining.

## Some Notes:

1. A task is not "a task for today", it's "a task for every day" as long as it's not marked as done. 

2. A task is assigned a certain number of sessions for each day. The start button will be disabled after all the assigned sessions had been used.

3. Tasks marked as done will stay in the task list for the rest of day, to show some progress of the day.

4. The task list will be reloaded when the app is restarted or when the date change.

5. There are two types of sessions for different tasks: long (50 minutes of work plus 10 minutes of rest) and short (25m plus 5m). The lengths of the sessions can be changed in settings.

## Feedbacks, issue reports, and suggestions are welcome.