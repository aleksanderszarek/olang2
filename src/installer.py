import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import os, shutil, json, subprocess, sys, ctypes
from pathlib import Path


def run_as_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()


run_as_admin()


class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OLang Installer")
        self.root.geometry("700x550")
        self.root.iconbitmap("olang.ico")
        self.pages = []
        self.config_data = {
            "interpreterVer": "0.1.0",
            "preprocessorDebug": False,
            "returnOnFatal": True,
            "generalLibraryLocation": "libraries",
            "includeLibraries": [],
            "installDir": r"C:\Program Files\OLang",
            "addToPath": True,
            "associateFiles": True
        }
        self.available_libs = self.find_libraries()
        self.setup_pages()
        self.show_page(0)

    def find_libraries(self):
        lib_dir = os.path.join(os.getcwd(), "source", "libraries")
        if not os.path.exists(lib_dir): return []
        return [f[:-3] for f in os.listdir(lib_dir) if f.endswith(".py")]

    def setup_pages(self):
        self.pages = [self.page_terms(), self.page_config(), self.page_options(), self.page_progress(), self.page_done()]

    def show_page(self, index):
        for page in self.pages:
            page.pack_forget()
        self.pages[index].pack(fill="both", expand=True)
        self.current_page = index

    def next_page(self):
        self.show_page(self.current_page + 1)

    def prev_page(self):
        self.show_page(self.current_page - 1)

    def page_terms(self):
        frame = ttk.Frame(self.root)
        ttk.Label(frame, text="Terms of Service", font=("Arial", 16)).pack(pady=10)
        text = ttk.Text(frame, height=15, wrap="word")
        try:
            with open("TOS.txt", "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except:
            text.insert("1.0", "No Terms of Service file found.")
        text.config(state="disabled")
        text.pack(padx=20, pady=10, fill="both", expand=True)

        self.agree_var = ttk.IntVar()
        ttk.Checkbutton(frame, text="I accept the Terms of Service", variable=self.agree_var).pack()

        ttk.Button(frame, text="Next", command=lambda: self.next_page() if self.agree_var.get() else Messagebox.show_warning("Please accept the terms")).pack(pady=10)
        return frame

    def page_config(self):
        frame = ttk.Frame(self.root)
        ttk.Label(frame, text="Configure OLang", font=("Arial", 16)).pack(pady=10)
        self.debug_var = ttk.BooleanVar(value=False)
        self.fatal_var = ttk.BooleanVar(value=True)

        options_frame = ttk.Frame(frame)
        options_frame.pack(anchor="w", padx=20, pady=(0, 10))

        ttk.Checkbutton(options_frame, text="Enable preprocessor debugging", variable=self.debug_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Exit on fatal errors", variable=self.fatal_var).pack(anchor="w", pady=2)
        
        ttk.Label(frame, text="Select which libraries you want to include by default in your project.\nThose libraries' instructions will be available in all your OLang projects even if you don't use them!", wraplength=660, justify="left").pack(padx=10, pady=5)


        lib_frame_outer = ttk.Frame(frame)
        lib_frame_outer.pack(fill="both", expand=True, padx=20, pady=5)

        canvas = ttk.Canvas(lib_frame_outer)
        scrollbar = ttk.Scrollbar(lib_frame_outer, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.check_vars = {}
        default_selected = {"arrays", "convert", "mainlib", "varlib"}

        for lib in self.available_libs:
            var = ttk.BooleanVar(value=(lib in default_selected))
            self.check_vars[lib] = var
            ttk.Checkbutton(scrollable_frame, text=lib, variable=var).pack(anchor="w", pady=1)

        nav = ttk.Frame(frame)
        nav.pack(side="bottom", fill="x", pady=10)
        ttk.Button(nav, text="Back", command=self.prev_page).pack(side="left", padx=20)
        ttk.Button(nav, text="Next", command=self.save_config_page).pack(side="right", padx=20)

        return frame

    def save_config_page(self):
        self.config_data["includeLibraries"] = [lib for lib, var in self.check_vars.items() if var.get()]
        self.config_data["preprocessorDebug"] = self.debug_var.get()
        self.config_data["returnOnFatal"] = self.fatal_var.get()
        self.next_page()

    def page_options(self):
        frame = ttk.Frame(self.root)
        ttk.Label(frame, text="Installation Options", font=("Arial", 16)).pack(pady=10)

        path_frame = ttk.Frame(frame)
        path_frame.pack(pady=10)
        ttk.Label(path_frame, text="Install Directory:").pack(side="left")
        self.path_var = ttk.StringVar(value=self.config_data["installDir"])
        ttk.Entry(path_frame, textvariable=self.path_var, width=40).pack(side="left", padx=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_dir).pack(side="left")

        self.path_check = ttk.BooleanVar(value=True)
        self.file_assoc = ttk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Add OLang to system PATH", variable=self.path_check).pack(anchor="w", padx=20)
        ttk.Checkbutton(frame, text="Associate .olang files with OLang", variable=self.file_assoc).pack(anchor="w", padx=20)

        nav = ttk.Frame(frame)
        nav.pack(side="bottom", fill="x", pady=10)
        ttk.Button(nav, text="Back", command=self.prev_page).pack(side="left", padx=20)
        ttk.Button(nav, text="Install", command=self.start_install).pack(side="right", padx=20)
        return frame

    def browse_dir(self):
        selected = filedialog.askdirectory()
        if selected:
            self.path_var.set(selected)

    def start_install(self):
        self.config_data["installDir"] = self.path_var.get()
        self.config_data["addToPath"] = self.path_check.get()
        self.config_data["associateFiles"] = self.file_assoc.get()
        self.show_page(3)
        self.root.after(500, self.run_installation)

    def page_progress(self):
        frame = ttk.Frame(self.root)
        ttk.Label(frame, text="Installing OLang...", font=("Arial", 16)).pack(pady=10)
        self.status = ttk.StringVar(value="Starting installation...")
        ttk.Label(frame, textvariable=self.status).pack(pady=20)
        return frame

    def run_installation(self):
        try:
            target = Path(self.config_data["installDir"])
            source = Path(os.getcwd()) / "source"

            self.status.set("Copying files...")
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)

            self.status.set("Creating config.json...")
            with open(target / "config.json", "w", encoding="utf-8") as f:
                json.dump({
                    "interpreterVer": self.config_data["interpreterVer"],
                    "preprocessorDebug": self.config_data["preprocessorDebug"],
                    "returnOnFatal": self.config_data["returnOnFatal"],
                    "generalLibraryLocation": "libraries",
                    "includeLibraries": self.config_data["includeLibraries"]
                }, f, indent=4)

            if self.config_data["addToPath"]:
                self.status.set("Adding to PATH...")
                current_path = os.environ["PATH"]
                if str(target) not in current_path:
                    subprocess.run(f'setx PATH "{current_path};{target}"', shell=True)

            if self.config_data["associateFiles"]:
                self.status.set("Associating .olang files...")
                exe_path = target / "olang.exe"
                subprocess.run(f'reg add HKCR\\.olang /ve /d "OLangFile" /f', shell=True)
                subprocess.run(f'reg add HKCR\\OLangFile /ve /d "OLang Script" /f', shell=True)
                subprocess.run(f'reg add HKCR\\OLangFile\\shell\\open\\command /ve /d "\\"{exe_path}\\" \\"%1\\"" /f', shell=True)

            self.status.set("Installation complete.")
            self.root.after(1000, lambda: self.show_page(4))

        except Exception as e:
            Messagebox.show_error("Installation Failed", str(e))
            self.root.quit()

    def page_done(self):
        frame = ttk.Frame(self.root)
        ttk.Label(frame, text="OLang Installed!", font=("Arial", 16)).pack(pady=20)
        ttk.Button(frame, text="Open Online Docs", command=lambda: os.startfile("https://your-docs-url.com")).pack(pady=10)
        ttk.Button(frame, text="Finish", command=self.root.quit).pack(pady=10)
        return frame


if __name__ == "__main__":
    app = InstallerApp(ttk.Window(themename="darkly"))
    app.root.mainloop()
