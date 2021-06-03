from tkinter import ttk

from asset import get_asset_pool
from .simpledialog import Dialog

class HelpWindow(Dialog):
    def body(self, master):
        asset_pool = get_asset_pool(master)
        title = ttk.Label(master, text="Hello, here is a quick start map.")
        content = ttk.Label(master, image=asset_pool.get_image('doc'))
        title.pack()
        content.pack()
        self.transient(self.master.winfo_toplevel())
        