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
        "size": "Size",
        "settings_title": "RPC Settings",
        "btn_apply": "Apply RPC",
        "success_rpc": "RPC configuration updated successfully!"
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
        "size": "Размер",
        "settings_title": "Настройки RPC",
        "btn_apply": "Применить RPC",
        "success_rpc": "Настройки RPC успешно обновлены!"
    }
}

class GUI():
    def __init__(self, xsize: int = 940, ysize: int = 980,
                 rpchost="127.0.0.1", rpcport=9191, rpcpath="mytorrents",
                 rpcuser="", rpcpassword=""):
        global APP_NAME
        self.current_lang = "en"

        self.app = customtkinter.CTk()
        self.app.title(APP_NAME)
        self.app.geometry(f"{xsize}x{ysize}")

        # Начальные параметры
        self.init_host = rpchost
        self.init_port = rpcport
        self.init_path = rpcpath
        self.init_user = rpcuser
        self.init_pass = rpcpassword

        # Передаем настройки подключения в обертку торрента
        self.t = TWrapper(
            rpchost=self.init_host,
            rpcport=int(self.init_port),
            rpcuser=self.init_user,
            rpcpassword=self.init_pass,
            path=self.init_path
        )
        self.torrent_widgets = {}

        self.app.grid_rowconfigure(3, weight=1)
        self.app.grid_columnconfigure(0, weight=1)

        # 1. Верхняя панель управления (Файл + Язык)
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

        # 1.5 Панель настроек RPC (Host, Port, Path)
        self.rpc_frame = customtkinter.CTkFrame(self.app)
        self.rpc_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.rpc_frame.grid_columnconfigure(6, weight=1)

        # Label/Entry для Host
        self.lbl_host = customtkinter.CTkLabel(self.rpc_frame, text="Host:", font=("Arial", 11, "bold"))
        self.lbl_host.grid(row=0, column=0, padx=(10, 2), pady=10)
        self.entry_host = customtkinter.CTkEntry(self.rpc_frame, width=120)
        self.entry_host.insert(0, str(self.init_host))
        self.entry_host.grid(row=0, column=1, padx=(0, 10), pady=10)

        # Label/Entry для Port
        self.lbl_port = customtkinter.CTkLabel(self.rpc_frame, text="Port:", font=("Arial", 11, "bold"))
        self.lbl_port.grid(row=0, column=2, padx=(0, 2), pady=10)
        self.entry_port = customtkinter.CTkEntry(self.rpc_frame, width=70)
        self.entry_port.insert(0, str(self.init_port))
        self.entry_port.grid(row=0, column=3, padx=(0, 10), pady=10)

        # Label/Entry для Path
        self.lbl_path = customtkinter.CTkLabel(self.rpc_frame, text="Path:", font=("Arial", 11, "bold"))
        self.lbl_path.grid(row=0, column=4, padx=(0, 2), pady=10)
        self.entry_path = customtkinter.CTkEntry(self.rpc_frame, width=130)
        self.entry_path.insert(0, str(self.init_path))
        self.entry_path.grid(row=0, column=5, padx=(0, 10), pady=10)

        # Кнопка применения RPC
        self.btn_apply_rpc = customtkinter.CTkButton(
            self.rpc_frame,
            text=self.tr("btn_apply"),
            command=self.apply_rpc_settings,
            fg_color="#2980b9",
            hover_color="#1f618d",
            width=110
        )
        self.btn_apply_rpc.grid(row=0, column=6, padx=10, pady=10, sticky="e")

        # 2. Панель ввода URL
        self.url_frame = customtkinter.CTkFrame(self.app, fg_color="transparent")
        self.url_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
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

        # 3. Скролл-контейнер со списком торрентов
        self.scroll_frame = customtkinter.CTkScrollableFrame(
            self.app,
            label_text=self.tr("active_torrents")
        )
        self.scroll_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Патчим баг со скроллом в customtkinter
        self._patch_scroll_bug()

        self.update_torrent_list()
        self.periodic_update()

    def apply_rpc_settings(self):
        """Метод для применения новых параметров RPC на лету"""
        try:
            new_host = self.entry_host.get().strip()
            new_port = int(self.entry_port.get().strip())
            new_path = self.entry_path.get().strip()

            # Обновляем поля в объекте-обертке
            self.t.rpchost = new_host
            self.t.rpcport = new_port
            self.t.path = new_path.strip("/")

            # Сразу проверяем подключение / обновляем список
            self.update_torrent_list()
            messagebox.showinfo("Success", self.tr("success_rpc"))
        except Exception as e:
            self.show_error(self.tr("add_error") + str(e))

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
        self.btn_apply_rpc.configure(text=self.tr("btn_apply"))
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

        if torrents is None:
            torrents = []

        current_ids = [t['id'] for t in torrents]

        for t_id in list(self.torrent_widgets.keys()):
            if t_id not in current_ids:
                self.torrent_widgets[t_id]["frame"].destroy()
                del self.torrent_widgets[t_id]

        for torrent in torrents:
            t_id = torrent['id']
            name = torrent.get('name', 'Unknown')
            size_mb = torrent.get('totalSize', 0) / (1024 * 1024)
            percent = torrent.get('percentDone', 0.0)
            if percent > 100:
                percent = 100.0

            progress_val = percent / 100.0
            down_speed = torrent.get('rateDownload', 0) / 1024
            up_speed = torrent.get('rateUpload', 0) / 1024

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
