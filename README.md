# Yet Another Pomodoro Timer

## Features:

* A simple task manager.
* Start a session timer for a given task.
* (Optionally) Add a short note after a session ends.
* Show session history for a task.
* A "Todo task" that captures small things which do not worth a whole session.
* Quickly define a task with [text format](#text-format)

## Quick Start

1. Download the files, extract the contents.
2. Run the `main.py` file using python 3.

The program requires the `tkinter` module, which may not be installed with python by default on some systems.

## Usage

The following diagram shows the main features of the app.

![main feature](doc.png)

The rest of the user interfaces are self-explaining.

## Text Format<a name="text-format"></a>

New tasks are created in the new task dialog. The task field of dialog also accept an "extended task description" format. The format is as follows:
    
    task title. [#n] [@show_time] [*repeat_pattern] [=duration_type] [^parent title^]
    
The task title is the leading text before the first period, followed by some options.
    
The optional fields are some fields that start with a few special characters. The fields could
appear in any order.

- @show_time: When to add the task to the task list.

  Possible format: 
  1. @04-15: show at the given date. If the date is not valid, use the latest valid date that is prior
  to the given date (for example, @4-32 is converted to the last day of April.)
  2. @Mon (Tue, Wed, Thu, Fri, Sat, Sun): show at the upcoming given day of the week.
  3. @+10, @+2w, @+1m: a day relative to today.

- *repeat_pattern: Repeatedly show the task in the given pattern.

  Possible format:
  1. *w, *m, *y: repeat every week, month, or year, start from today.
  2. *Mon, *m12, *y04-13: these formats combine the date to show with repeat pattern (Monday on every week,
  on 12th of every month, or April 13 of every year.).

- =duration: The duration type of session. The default value is short session.

  Possible format:
  "==" for long session, "=-" for short session, and "=." for todos.

- ^parent_title^: specifies the parent task. 
  The first task in the current task list that matches the given
  `parent_title` will be the parent of this task. A Repeated task can't have parent task: If `*` field
  is given, this field will be ignored.

-!deadline: the deadline of the task
  deadline has the same format as @show_time. It's ignored for repeated tasks.

## Some Notes:

1. A task is not "a task for today", it's "a task for every day" as long as it's not marked as done. 

2. A task is assigned a certain number of sessions for each day. The start button will be disabled after all the assigned sessions had been used.

3. Tasks marked as done will stay in the task list until the task list is reloaded, to show the "progress of the day".

4. The task list will be reloaded when the app is restarted or when the date change.

5. There are two types of sessions for different tasks: long (50 minutes of work time plus 10 minutes of rest time) and short (25m plus 5m) ones. These times can be customized in settings.

## Feedbacks, issue reports, and suggestions are welcome.
