import tkinter as tk
from tkinter import ttk

##
#  General helper functions
##
def grid_layout(parent, children_grid, start_row = tk.END, **opt):
    """Put a set of children in a grid layout.
    
    Repeated elements implies span, None for empty cell. For example:
    
    [[a, a, b, c],
     [a, a, d, e],
     [None, None, f, g]]
     
    means a.grid(row=0, col=0, rowspan=2, columnspan=2), b.grid(row=0,col=2), ....
    
    if the rows have different length, the last element of the shorter rows will span over
    the rest of columns.
    """
    if start_row == tk.END:
        start_row = parent.grid_size()[1]

    seen = set()
    max_row_length = max(len(row) for row in children_grid)
    for row in children_grid:
        row.extend([row[-1]]*(max_row_length - len(row)))
        
    for r, row in enumerate(children_grid):
        for c, w in enumerate(row):
            if w is None or w in seen:
                continue
            row_span = 0
            while r + row_span < len(children_grid) and w == children_grid[r+row_span][c]:
                row_span += 1
            col_span = 0
            while c + col_span < len(row) and w == row[c+col_span]:
                col_span += 1
            
            w.grid(row=r+start_row, column = c, rowspan=row_span, columnspan=col_span, sticky=tk.N+tk.E+tk.S+tk.W, **opt)
            seen.add(w)
def text_field(master, prompt, initial):
    label = ttk.Label(master, text=prompt)
    var = tk.StringVar()
    var.set(initial)
    entry = ttk.Entry(master, textvariable=var)
    return [label, entry], var
    
def boolean_field(master, prompt, info, initial):
    label = ttk.Label(master, text=prompt)
    var = tk.BooleanVar()
    var.set(initial)
    button = ttk.Checkbutton(master, variable=var, text=info)
    return [label if prompt else button, button], var
    
def radio_field(master, prompt, options, initial):
    widgets = []
    label = ttk.Label(master, text=prompt)
    widgets.append(label)
    var = tk.StringVar()
    var.set(initial)
    if len(options[0]) == 1:
        options = [(opt, opt) for opt in options]
    for text, value in options:
        button = ttk.Radiobutton(master, text=text, value=value, variable=var)
        widgets.append(button)
    return widgets, var
    
def number_field(master, prompt, choices, initial):
    label = ttk.Label(master, text=prompt)
    var = tk.IntVar()
    var.set(initial)
    combbox = ttk.Combobox(master, values=choices, textvariable=var, width=4)
    return [label, combbox], var

def add_content_frame(toplevel: tk.Toplevel, **kw):
    """Add a tkk.Frame instance to `toplevel` as its only child.
    
    Tk root window and Toplevels are not themed. This function will add a ttk.Frame
    to the toplevel window, and config it to cover the whole area of the window. All 
    children's should be added to this frame. In this way, we can themerize all windows
    using ttk's style system.
    """
    frame = ttk.Frame(toplevel, **kw)
    frame.grid(row=0, column=0, sticky='news')
    toplevel.rowconfigure(0, weight=1)
    toplevel.columnconfigure(0, weight=1)
    return frame
    
def subscribe(observable, topic, callback, widget: tk.Widget):
    """Register `callback` for the `observable`'s `topic` event. 
    
    Also arrange to remove the callback when the related widget is destroyed.
    """
    observable.subscribe(topic, callback)
    widget.bind('<Destroy>', lambda e: observable.unsubscribe(topic, callback), add=True)

def trace(var, topic, callback, widget):
    """Register `callback` for the actions of the given `var`. 
    
    Also arrange to remove the callback when the related widget is destroyed.
    """
    cbname = var.trace_add(topic, callback)
    widget.bind('<Destroy>', lambda e: var.trace_remove(topic, cbname), add=True)