from TorrentWrapper import TorrentWrapper as TWrapper
import customtkinter
from customtkinter import filedialog
APP_NAME="XenoneI2P"

class GUI():
    def add_button_file(self):
        print("Add button clicked")
        filename = filedialog.askopenfilename()
        print(filename)
        if filename == ():
            print("No file selected")
            return False
        if filename.split('.')[-1] != 'torrent':
            print("This not torrent file")
            return False
        with open(filename, "rb") as f:
            content = f.read()
        pass
    def add_button_url(self):
        url = self.torrent_url.get("0.0", "end")
        print(url)
        pass
    def __init__(self, xsize: int=940, ysize: int =940):
        global APP_NAME
        self.app = customtkinter.CTk()
        self.app.title(APP_NAME)
        self.app.geometry(f"{xsize}x{ysize}")
        self.add_button_file = customtkinter.CTkButton(self.app, text="Add File", command=self.add_button_file)
        self.add_button_file.grid(row=0, column=0, padx=20, pady=20)
        self.t = TWrapper()

        self.torrent_url = customtkinter.CTkTextbox(self.app)
        self.add_button = customtkinter.CTkButton(self.app, text="Add by url", command=self.add_button_url)
        self.add_button.grid(row=0, column=1, padx=20, pady=20)
        self.torrent_url.grid(row=1, column=1, sticky="nsew")
    pass
def main():
    #t = TWrapper()
    #t.add('magnet:?xt=urn:btih:c8a431d53b00314211a78b6b8388ceb8dcbb3680&dn=Tetrazole.+Explosions+stuff.+&tr=http://tracker2.postman.i2p/announce.php', is_magnet=True)
    #t.add("http://tracker2.postman.i2p/index.php?action=Download&id=55406", is_magnet=False)
    #t.add("http://tracker2.postman.i2p/index.php?action=Download&id=102920")
    #torrents = t.get()
    #for torrent in torrents:
    #    print(torrent)
    #t.remove(1)
    g = GUI()
    g.app.mainloop()
    pass

if __name__ == "__main__":
	main()
