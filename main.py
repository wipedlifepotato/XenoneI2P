from TorrentWrapper import TorrentWrapper as TWrapper
import customtkinter
from customtkinter import filedialog
from tkinter import messagebox

APP_NAME = "XenoneI2P"

# Словарь локализации (i18n)
TRANSLATIONS = {
    "en": {
        "title": "XenoneI2P Torrent Client",
        "active_torrents": "Active Torrents",
        "placeholder": "Enter magnet link or .torrent URL...",
        "btn_file": "Add File",
        "btn_add": "Add URL",
        "error_title": "Error",
        "no_file": "No file selected",
        "not_torrent": "This is not a torrent file",
        "magnet_error": "Magnet links are not implemented yet!",
        "empty_url": "Please enter a URL or magnet.",
        "add_error": "Failed to add torrent: ",
        "progress": "Progress",
        "size": "Size"
    },
    "ru": {
        "title": "XenoneI2P Торрент Клиент",
        "active_torrents": "Активные торренты",
        "placeholder": "Введите magnet-ссылку или URL .torrent...",
        "btn_file": "Добавить файл",
        "btn_add": "Добавить URL",
        "error_title": "Ошибка",
        "no_file": "Файл не выбран",
        "not_torrent": "Это не .torrent файл",
        "magnet_error": "Magnet-ссылки пока не реализованы!",
        "empty_url": "Пожалуйста, введите URL или magnet.",
        "add_error": "Не удалось добавить торрент: ",
        "progress": "Прогресс",
        "size": "Размер"
    }
}

class GUI():
    def __init__(self, xsize: int = 940, ysize: int = 940):
        global APP_NAME
        self.current_lang = "en"

        self.app = customtkinter.CTk()
        self.app.title(APP_NAME)
        self.app.geometry(f"{xsize}x{ysize}")

        self.t = TWrapper()
        self.torrent_widgets = {}

        self.app.grid_rowconfigure(2, weight=1)
        self.app.grid_columnconfigure(0, weight=1)

        # Верхняя панель управления
        self.top_frame = customtkinter.CTkFrame(self.app, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.btn_file = customtkinter.CTkButton(
            self.top_frame,
            text=self.tr("btn_file"),
            command=self.add_button_file
        )
        self.btn_file.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.lang_menu = customtkinter.CTkOptionMenu(
            self.top_frame,
            values=["EN", "RU"],
            command=self.change_language,
            width=70
        )
        self.lang_menu.grid(row=0, column=1, sticky="e")

        # Панель ввода URL
        self.url_frame = customtkinter.CTkFrame(self.app, fg_color="transparent")
        self.url_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.torrent_url = customtkinter.CTkEntry(
            self.url_frame,
            placeholder_text=self.tr("placeholder")
        )
        self.torrent_url.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.add_button = customtkinter.CTkButton(
            self.url_frame,
            text=self.tr("btn_add"),
            command=self.add_button_url,
            fg_color="#27ae60",
            hover_color="#219653"
        )
        self.add_button.grid(row=0, column=1)

        # Скролл-контейнер со списком торрентов
        self.scroll_frame = customtkinter.CTkScrollableFrame(
            self.app,
            label_text=self.tr("active_torrents")
        )
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Патчим баг со скроллом в customtkinter, если он вылетает по строкам
        self._patch_scroll_bug()

        self.update_torrent_list()
        self.periodic_update()

    def _patch_scroll_bug(self):
        """Патч против AttributeError: 'str' object has no attribute 'master' в CTkScrollableFrame"""
        old_check = getattr(self.scroll_frame, "_check_if_valid_scroll", None)
        if old_check:
            def safe_check(widget):
                if isinstance(widget, str):
                    return False
                try:
                    return old_check(widget)
                except Exception:
                    return False
            self.scroll_frame._check_if_valid_scroll = safe_check

    def tr(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"]).get(key, key)

    def change_language(self, choice):
        self.current_lang = choice.lower()
        self.app.title(self.tr("title"))
        self.btn_file.configure(text=self.tr("btn_file"))
        self.add_button.configure(text=self.tr("btn_add"))
        self.torrent_url.configure(placeholder_text=self.tr("placeholder"))
        self.scroll_frame.configure(label_text=self.tr("active_torrents"))

    def show_error(self, message):
        messagebox.showerror(self.tr("error_title"), message)

    def add_button_file(self):
        filename = filedialog.askopenfilename()
        if not filename or filename == ():
            return False

        if not filename.endswith('.torrent'):
            self.show_error(self.tr("not_torrent"))
            return False

        try:
            with open(filename, "rb") as f:
                content = f.read()

            # Вызываем твой метод для сырых байтов
            self.t.add_raw(content)
            self.update_torrent_list()
        except Exception as e:
            self.show_error(self.tr("add_error") + str(e))

    def add_button_url(self):
        url = self.torrent_url.get().strip()
        if not url:
            self.show_error(self.tr("empty_url"))
            return

        if url.startswith("magnet:"):
            self.show_error(self.tr("magnet_error"))
            return

        try:
            # Если для URL используется стандартный add
            self.t.add(url, is_magnet=False)
            self.torrent_url.delete(0, customtkinter.END)
            self.update_torrent_list()
        except Exception as e:
            self.show_error(self.tr("add_error") + str(e))

    def remove_torrent(self, t_id):
        print(f"Remove torrent ID: {t_id}")
        self.t.remove(t_id)
        self.update_torrent_list()

    def update_torrent_list(self):
        try:
            torrents = self.t.get()
        except Exception as e:
            return

        current_ids = [t['id'] for t in torrents]

        for t_id in list(self.torrent_widgets.keys()):
            if t_id not in current_ids:
                self.torrent_widgets[t_id]["frame"].destroy()
                del self.torrent_widgets[t_id]

        for torrent in torrents:
            t_id = torrent['id']
            name = torrent.get('name', 'Unknown')
            size_mb = torrent.get('total_size', 0) / (1024 * 1024)
            percent = torrent.get('percent_done', 0.0)
            if percent > 100:
                percent = 100.0

            progress_val = percent / 100.0
            down_speed = torrent.get('rate_download', 0) / 1024
            up_speed = torrent.get('rate_upload', 0) / 1024

            if t_id not in self.torrent_widgets:
                row_frame = customtkinter.CTkFrame(self.scroll_frame)
                row_frame.pack(fill="x", pady=5, padx=5)
                row_frame.grid_columnconfigure(0, weight=1)

                lbl_name = customtkinter.CTkLabel(row_frame, text=name, anchor="w", font=("Arial", 13, "bold"))
                lbl_name.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))

                p_bar = customtkinter.CTkProgressBar(row_frame)
                p_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
                p_bar.set(progress_val)

                lbl_info = customtkinter.CTkLabel(row_frame, text="", anchor="w", font=("Arial", 11))
                lbl_info.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

                btn_action = customtkinter.CTkButton(
                    row_frame, text="X", width=30, fg_color="#b33939", hover_color="#ff5252",
                    command=lambda id=t_id: self.remove_torrent(id)
                )
                btn_action.grid(row=0, column=1, rowspan=3, padx=10)

                self.torrent_widgets[t_id] = {
                    "frame": row_frame,
                    "progress_bar": p_bar,
                    "label_info": lbl_info
                }

            widgets = self.torrent_widgets[t_id]
            widgets["progress_bar"].set(progress_val)
            info_text = (
                f"{self.tr('progress')}: {percent:.2f}%  |  "
                f"{self.tr('size')}: {size_mb:.1f} MB  |  "
                f"↓ {down_speed:.1f} KB/s  |  "
                f"↑ {up_speed:.1f} KB/s"
            )
            widgets["label_info"].configure(text=info_text)

    def periodic_update(self):
        self.update_torrent_list()
        self.app.after(2000, self.periodic_update)

def main():
    g = GUI()
    g.app.mainloop()

if __name__ == "__main__":
    main()
