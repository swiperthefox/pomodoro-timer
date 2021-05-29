from tkinter import ttk
import tkinter as tk

class TomatoBox(ttk.Frame):
    """Render a list of images into a row of buttons.
    
    When one button is clicked, the `click_handler` will be called with its index
    as parameter.
    """
    def __init__(self, parent, tomato_config, click_handler=None, **keywords):
        ttk.Frame.__init__(self, parent, takefocus=1, **keywords)
        self.tomatoes = []
        self.handler = click_handler
        for i, tomato in enumerate(tomato_config):
            self.create_tomato(tomato, i, click_handler)
        self.bind("<KeyPress>", self.keypress_handler)
        
    def keypress_handler(self, e):
        keysym_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5":5,
            "KP_1": 1, "KP_2": 2, "KP_3": 3, "KP_4": 4, "KP_5": 5}
        if e.keysym in keysym_map:
            self.handler(keysym_map[e.keysym])

    def configure(self, cnf={}, **kw):
        kwargs = cnf.copy()
        kwargs.update(kw)
        if 'tomatoes' in kwargs:
            tomato_config = kwargs.pop('tomatoes')
            min_l = min(len(self.tomatoes), len(tomato_config))
            for button in self.tomatoes[min_l:]: # remove the extra ones
                button.destroy()
            self.tomatoes = self.tomatoes[:min_l]
            for tomato, button in zip(tomato_config, self.tomatoes): # update the existing ones
                button.config(image=tomato)
            for j, tomato in enumerate(tomato_config[min_l:]): # add more if needed
                self.create_tomato(tomato, min_l + j, self.handler)
        super().configure(cnf=kwargs)
        
    config = configure
    
    def create_tomato(self, img, idx, handler):
        tomato = ttk.Label(self, image=img)
        if handler is not None:
            tomato.bind('<Button-1>', lambda e: handler(idx+1))
        self.tomatoes.append(tomato)
        tomato.pack(side=tk.LEFT)
        return tomato
