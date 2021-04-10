1. More detectable notification

It's hard (need more dependency) to create a system tray. Here is a work around:

create a window that only shows a small icon, indicating that a session is going on. We can make it
stay on top all the time, and place it in a corner.

If a user want to interact with it, he can hover over the icon, then a full window 
(the task name, progress bar, along with the title bar) will show, so that the user could
move it, click it, etc.

2. [ ] system tray
2. [x]setting window:

  * session time pattern, 
  * long rest time, 
  * show note editor, 
  * progress window stay on top, 
  * main window stay on top
  * font
  
3. [x]sound alert

4. make a package

5. proper detection of screen size

6. [x] Observable property

7. A special "Misc" task, which captures the small, trivial things to do.
  - click on the task to pop an todo list editor 
  - repeated events
  - also can be created in the normal task editor dialog
  
8. repeated events: tasks are set to repeat every week, month or year.
  - no "repeat every day", since such tasks can stay on the task list, as long as it is not done.
  - if we want an event to repeat every week, the we don't want it to stay there for the whole week.

9. Anti procrastination by ugly!
  - show rotten tomato on the day of deadline
  
10. [] disable start button when a session is running

11. sub task 
  * use "a sub task @mai" to create a subtask who parent is the task in the list that starts with "mai".
  * or the charactor "@" will pop a list 