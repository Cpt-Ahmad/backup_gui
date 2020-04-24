
import os
import shutil
import time
import datetime
import tkinter as tk
import tkinter.scrolledtext as scrtxt
from tkinter.filedialog import askopenfilename, askdirectory


class Backup(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super(Backup, self).__init__(parent, *args, **kwargs)
        self.parent = parent

        button_add_file = tk.Button(root, text="Add File", command=self.add_file_to_backup)
        button_add_dir = tk.Button(root, text="Add Directory", command=self.add_dir_to_backup)
        button_backup = tk.Button(root, text="Start Backup", command=self.start_backup)
        button_show = tk.Button(root, text="Show Backup List", command=self.show_backup_list)
        button_remove = tk.Button(root, text="Remove", command=self.remove_from_backup_list)

        button_add_file.place(relx=0.1, rely=0.1)
        button_add_dir.place(relx=0.1, rely=0.2)
        button_backup.place(relx=0.1, rely=0.3)
        button_show.place(relx=0.1, rely=0.4)
        button_remove.place(relx=0.1, rely=0.5)

        self.console = scrtxt.ScrolledText(root, bg="white")
        self.console.place(relx=0.275, rely=0.1, relheight=0.8, relwidth=0.7)
        self.log("INFO", "Backup GUI v0.1")

        self.pack(side="top", fill="both", expand=True)

        self.backup_filename = "backup_list.txt"

    def log(self, level, msg):
        self.console.insert(tk.END, " ".join((level, msg, "\n")))
        self.console.see(tk.END)

    def add_file_to_backup(self):
        file_name = askopenfilename()
        self.add_to_backup(file_name)

    def add_dir_to_backup(self):
        dir_name = askdirectory()
        self.add_to_backup(dir_name)

    def add_to_backup(self, path):
        if path == "":
            return
        if os.path.exists(self.backup_filename):
            file_mode = "a"
        else:
            file_mode = "w"
        with open(self.backup_filename, file_mode) as backup_file:
            backup_file.write("{}\n".format(path))
        self.log("INFO", "Path succesfully added to backup list")

    def remove_from_backup_list(self):
        if not os.path.exists(self.backup_filename):
            self.log("WARNING", "Backup list does not exist -> first add a file or directory")
            return

        check_buttons = {}
        sub_window = tk.Toplevel(self)

        def get_objects_to_remove():
            new_list = ""
            for key in check_buttons:
                if not check_buttons[key].get():
                    new_list += "".join((key, "\n"))
            with open(self.backup_filename, "w") as backup_file_write:
                backup_file_write.write(new_list)
            sub_window.destroy()

        sub_window.wm_title("Remove")
        sub_window.resizable(width=False, height=False)
        sub_window.minsize(width=640, height=480)
        sub_window.protocol("WM_DELETE_WINDOW", get_objects_to_remove)

        with open(self.backup_filename, 'r') as backup_file:
            for i, line in enumerate(backup_file):
                button_text = line.rstrip()
                bv = tk.BooleanVar()
                bv.set(False)
                cb = tk.Checkbutton(sub_window, text=button_text, variable=bv)
                check_buttons[button_text] = bv
                cb.pack(anchor="w")

    def show_backup_list(self):
        if not os.path.exists(self.backup_filename):
            self.log("WARNING", "Backup list does not exist -> first add a file or directory")
            return

        with open(self.backup_filename, "r") as backup_file:
            string = "Current paths in backup list:\n" + "".join(backup_file.readlines())
        self.log("INFO", string.rstrip())

    def start_backup(self):
        if not os.path.exists(self.backup_filename):
            self.log("WARNING", "Backup list does not exist -> first add a file or directory")
            return

        destination = askdirectory()
        if destination == "":
            return

        before_time = time.perf_counter()
        is_empty = True
        with open(self.backup_filename, "r") as file:
            for line in file:
                src = line.rstrip()

                if not os.path.exists(src):
                    self.log("WARNING", "{} does not exist".format(src))
                    continue

                if not os.path.isdir("tmp"):
                    os.mkdir("tmp")

                if os.path.isfile(src):
                    shutil.copy2(src, "tmp")
                    is_empty = False
                    continue

                if os.path.isdir(src):
                    dir_name = os.path.basename(src)
                    shutil.copytree(src, os.path.join("tmp", dir_name))
                    is_empty = False
                    continue

        if is_empty:
            self.log("WARNING", "Backup has no valid files or directories -> first add a valid file or directory")
            return

        zip_name = "backup_{}".format(datetime.datetime.now().isoformat())
        zip_name = zip_name.replace(":", "-").replace(".", "-")
        zip_dest = os.path.join(destination, zip_name)

        shutil.make_archive(zip_dest, "zip", "tmp")
        shutil.rmtree("tmp")

        total_time = time.perf_counter() - before_time

        self.log("INFO", "Backup complete @ {}.zip".format(zip_dest))
        self.log("INFO", "Backup complete ({} sec)".format(total_time))


if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title("Backup GUI")
    root.minsize(width=800, height=400)
    root.resizable(width=False, height=False)
    Backup(root)
    root.mainloop()



