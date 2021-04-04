import tkinter as tk
from tkinter import font
import random

N = 8

def on_button_toggle(k):
    s = state_vars[k].get()
    current = current_var.get()
    current += (s*2 - 1) * (1<<k)
    current_var.set(current)
    diff = target_var.get() - current
    diff_var.set(diff)
    if diff == 0:
        app.title("Great, you made it.")

def main(n):
    root = tk.Tk()
    tk.Button(root, text="Start", command=start_game).grid(row=10, column=0)
    tk.Button(root, text="Quit", command=root.quit).grid(row=10, column=1)
    btn_frame = tk.Frame(root)
    bit_states = []
    for i in range(n):
        state_var = tk.IntVar()
        btn = tk.Checkbutton(btn_frame, textvariable=state_var, indicatoron=0, 
            font=('monosapce', 48), width=2, anchor=tk.CENTER,
            variable=state_var, command=lambda k=i: on_button_toggle(k)
        )
        btn.pack(side=tk.RIGHT)
        bit_states.append(state_var)
        
    btn_frame.grid(row=0, column=0, sticky='snew', columnspan=2)
    current_var = tk.IntVar()
    target_var = tk.IntVar()
    diff_var = tk.IntVar()
    tk.Label(text="Target =", anchor=tk.W).grid(row=1, column=0, sticky='we')
    tk.Label(textvariable=target_var).grid(row=1, column=1, sticky='we')
    tk.Label(text="Current =", anchor=tk.W).grid(row=2, column=0, sticky='we')
    tk.Label(textvariable=current_var).grid(row=2, column=1, sticky='we')
    tk.Label(text="Diffence =", anchor=tk.W).grid(row=3, column=0, sticky='we')
    tk.Label(textvariable=diff_var).grid(row=3, column=1, sticky='we')
    return root, target_var, current_var, diff_var, bit_states
    
def start_game():
    app.title("Toggle the switches to represent the target number.")
    for v in state_vars:
        v.set(0)
    target = random.randint(0, (1<<N)-1)
    print(target)
    target_var.set(target)
    current_var.set(0)
    diff_var.set(target)
    app.update_idletasks()
    
app, target_var, current_var, diff_var, state_vars = main(8)
normal = font.nametofont('TkDefaultFont')
normal['size'] = 24
start_game()
app.mainloop()