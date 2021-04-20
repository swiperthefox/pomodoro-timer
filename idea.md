1. [ ] system tray
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
  
10. [x] disable start button when a session is running

11. sub task 
  * use "a sub task @mai" to create a subtask who parent is the task in the list that starts with "mai".
  * or the charactor "@" will pop a list 
  
## MISC task

1. a special kind of task
2. can't mark as done
3. todos are in a seperate table "todo"
4. 

## Text Entry Task Specification

Use text string to specify properties of a task.

- text: Pay the bill
  This is the task description
- Show (@): @04-15, @Mon (Tue, Wed, Thu, Fri, Sat, Sun), @+1, @+1w, @+1m
  The day to start showing this task.
- repeat (*): *w, *m, *y, *Mon, *m12, *y04-13
  repeated task
  * for *w, *m, *y, the date to repeat is the show date or today if there is no show date.
  * for *Mon, *m12, *y04-13, the task will relisted on the next occurance of such date
      if this date does not match the `show date`, then both of them will take effect.  
- session type(==): == =
  == for a long session, = for short session, =. for todo items
- parent task (^): ^Other task^
  the parent is the first task that is on current list, whose title matches the given text.
  if repeat field exists, then this field is ignored. 

## add command line interface:

1. add "task description string"
2. list
3. start tid
4. done tid
5. history tid

