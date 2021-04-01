from tkinter import PhotoImage, BitmapImage

class AssetPool:
    COLOR = PhotoImage
    BW = BitmapImage
     
    def __init__(self, root):
        self.img_assets = {}
        self.font_assets = {}
        self.__img_cache = {}
        
    def get_image(self, name):
        if name in self.__img_cache:
            return self.__img_cache[name]
        elif name in self.img_assets:
            loader, filepath = self.img_assets[name]
            try:
                self.__img_cache[name] = img = loader(file=filepath)
                return img
            except:
                return None
        else:
            return None
    
    def add_img(self, name, loader, filepath):
        if loader != AssetPool.BW and loader != AssetPool.COLOR:
            return False
        else:
            self.img_assets[name] = (loader, filepath)
    
    def get_font(self, name):
        return self.font_assets.get(name, None)
    
    def add_font(self, name, font):
        self.font_assets[name] = font

def get_root(w):
    root = w.winfo_toplevel()
    if root.master:
        root = root.master
    return root
    
# An AssetPool instance is attached to the root window.
def get_asset_pool(w):
    return get_root(w).asset_pool
