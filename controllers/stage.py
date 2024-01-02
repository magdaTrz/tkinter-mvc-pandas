import time

from models.main import Model
from paths import path_support_files
from views.main import View
from tkinter import filedialog
from threading import Thread


class StageController:
    def __init__(self, model: Model, view: View) -> None:
        self.file_path = path_support_files
        self.model = model
        self.view = view
        self.frame = self.view.frames["stage"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.supportfile_btn.config(command=self.start_generating_support_files)
        self.frame.supportfile_filedialog_btn.config(command=self.choose_file)

        self.frame.reportload_btn.config(command=lambda: self.handle_selected_stage(stage='load'))
        self.frame.reportend_btn.config(command=lambda: self.handle_selected_stage(stage='end'))

        self.frame.back_btn.config(command=self.handle_back)

    def handle_back(self) -> None:
        self.model.report_model.report_clear()
        self.view.switch('start')

    def handle_selected_stage(self, stage: str) -> None:
        print(f'StageController: handle_selected_stage({stage=})')
        if stage == 'load':
            self.view.switch('flow_load')
        elif stage == 'end':
            self.view.switch('flow_end')

    def choose_file(self) -> None:
        """File selection dialog"""
        print(f'StageController: choose_file()')
        file_path = filedialog.askopenfilename(
            title='Wybierz plik',
            filetypes=[('Pliki tekstowe', '*.txt'), ('Wszsytkie pliki', '*.*')]
        )
        if file_path:
            self.file_path = file_path
            self.frame.supportfile_filedialog_label.config(text=f"Wybrano: {file_path}")

    def start_generating_support_files(self) -> None:
        self.frame.supportfile_btn.grid_forget()
        self.frame.supportfile_filedialog_btn.grid_forget()
        self.frame.progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        threat = Thread(target=self.handle_generate_support_files)
        threat.start()
        progress_threat = Thread(target=self.update_progress)
        progress_threat.start()

    def update_progress(self):
        while True:
            self.frame.progress_bar['value'] = self.model.support_files.progress_value
            self.frame.update_idletasks()
            time.sleep(0.1)

    def handle_generate_support_files(self) -> None:
        """"Handles a file load event."""
        print(f'StageController: handle_generate_support_files({self.file_path})')
        success = self.model.support_files.load_data_from_file(self.file_path)
        if success:
            data = self.model.support_files.get_data() # tak można zaciągnać dane.
            self.frame.supportfile_filedialog_label.config(text=f"Poprawnie zakończono tworzenie plików pomocniczych.")
        else:
            self.frame.supportfile_btn.grid(row=2, column=0, padx=10, pady=10)
            self.frame.supportfile_filedialog_btn.grid(row=2, column=1, padx=10, pady=10)
            self.frame.progress_bar.grid_forget()
            self.frame.supportfile_filedialog_label.config(text=f"Nie znaleziono pliku potrzebnego do wygenerowania "
                                                                f"plików pomocniczych. ")

