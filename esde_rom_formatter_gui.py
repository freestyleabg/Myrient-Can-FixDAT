#!/usr/bin/env python3
"""GUI for creating ES-DE .m3u directory structures for multi-disc ROM sets."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore

from esde_rom_formatter_core import process_library


class QtLogger:
    def __init__(self, emit: QtCore.pyqtSignal, verbose: bool) -> None:
        self._emit = emit
        self.verbose = verbose

    def info(self, message: str) -> None:
        self._emit.emit(message)

    def debug(self, message: str) -> None:
        if self.verbose:
            self._emit.emit(message)

    def warn(self, message: str) -> None:
        self._emit.emit(f"WARN: {message}")


class Worker(QtCore.QObject):
    log = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(bool, str)

    def __init__(
        self,
        root: Path,
        recursive: bool,
        dry_run: bool,
        verbose: bool,
        extract_archives: bool,
        delete_archives: bool,
        postprocess_single_disc: bool,
    ) -> None:
        super().__init__()
        self.root = root
        self.recursive = recursive
        self.dry_run = dry_run
        self.verbose = verbose
        self.extract_archives = extract_archives
        self.delete_archives = delete_archives
        self.postprocess_single_disc = postprocess_single_disc

    @QtCore.pyqtSlot()
    def run(self) -> None:
        try:
            logger = QtLogger(self.log, verbose=self.verbose)
            logger.info(f"Scanning: {self.root}")
            logger.info(f"Recursive: {'yes' if self.recursive else 'no'}")
            logger.info(f"Mode: {'dry-run' if self.dry_run else 'apply'}")
            logger.info(f"Extract archives: {'yes' if self.extract_archives else 'no'}")
            logger.info(f"Post-process single-disc: {'yes' if self.postprocess_single_disc else 'no'}")

            result = process_library(
                root=self.root,
                recursive=self.recursive,
                dry_run=self.dry_run,
                logger=logger,
                extract_archives_first=self.extract_archives,
                delete_archives_after_extract=self.delete_archives,
                postprocess_single_disc=self.postprocess_single_disc,
            )

            summary = (
                f"Done. Groups processed: {result.groups_processed} | "
                f"Files moved: {result.files_moved} | Files skipped: {result.files_skipped} | "
                f"Archives extracted: {result.archives_extracted} | Archive failures: {result.archives_failed}"
            )
            self.finished.emit(True, summary)
        except Exception as exc:  # noqa: BLE001
            self.finished.emit(False, f"Run failed: {exc}")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._thread: QtCore.QThread | None = None
        self._worker: Worker | None = None

        self.setWindowTitle("ESDE ROM Formatter")
        self.resize(900, 620)

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)

        layout = QtWidgets.QVBoxLayout(root)

        path_row = QtWidgets.QHBoxLayout()
        path_label = QtWidgets.QLabel("ROM Folder")
        self.path_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_folder)

        path_row.addWidget(path_label)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse_btn)

        opt_row = QtWidgets.QHBoxLayout()
        self.recursive_cb = QtWidgets.QCheckBox("Scan subfolders (--recursive)")
        self.dry_run_cb = QtWidgets.QCheckBox("Dry run (no file changes)")
        self.dry_run_cb.setChecked(True)
        self.verbose_cb = QtWidgets.QCheckBox("Verbose logs")
        self.extract_cb = QtWidgets.QCheckBox("Extract .zip/.7z archives first")
        self.delete_archives_cb = QtWidgets.QCheckBox("Delete archives after successful extraction")
        self.postprocess_single_disc_cb = QtWidgets.QCheckBox("Post-process single-disc folders (Game -> Game.cue)")
        self.extract_cb.setChecked(False)
        self.delete_archives_cb.setEnabled(False)
        self.postprocess_single_disc_cb.setEnabled(False)
        self.extract_cb.stateChanged.connect(self._on_extract_toggle)
        opt_row.addWidget(self.dry_run_cb)
        opt_row.addWidget(self.recursive_cb)
        opt_row.addWidget(self.extract_cb)
        opt_row.addWidget(self.delete_archives_cb)
        opt_row.addWidget(self.postprocess_single_disc_cb)
        opt_row.addWidget(self.verbose_cb)
        opt_row.addStretch(1)

        button_row = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("Run")
        self.clear_btn = QtWidgets.QPushButton("Clear Log")
        self.run_btn.clicked.connect(self._start_run)
        button_row.addWidget(self.run_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addStretch(1)

        self.log_edit = QtWidgets.QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QtGui.QFont("Consolas", 10))
        self.clear_btn.clicked.connect(self.log_edit.clear)

        self.status_label = QtWidgets.QLabel("Ready")

        layout.addLayout(path_row)
        layout.addLayout(opt_row)
        layout.addLayout(button_row)
        layout.addWidget(self.log_edit, 1)
        layout.addWidget(self.status_label)

    def _browse_folder(self) -> None:
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select ROM folder")
        if folder:
            self.path_edit.setText(folder)

    def _append_log(self, text: str) -> None:
        self.log_edit.appendPlainText(text)
        scrollbar = self.log_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _set_running(self, running: bool) -> None:
        self.run_btn.setEnabled(not running)
        self.path_edit.setEnabled(not running)
        self.recursive_cb.setEnabled(not running)
        self.dry_run_cb.setEnabled(not running)
        self.verbose_cb.setEnabled(not running)
        self.extract_cb.setEnabled(not running)
        self.delete_archives_cb.setEnabled(not running and self.extract_cb.isChecked())
        self.postprocess_single_disc_cb.setEnabled(not running and self.extract_cb.isChecked())

    def _on_extract_toggle(self, state: int) -> None:
        self.delete_archives_cb.setEnabled(state == QtCore.Qt.Checked and self.run_btn.isEnabled())
        self.postprocess_single_disc_cb.setEnabled(state == QtCore.Qt.Checked and self.run_btn.isEnabled())

    def _start_run(self) -> None:
        raw = self.path_edit.text().strip()
        if not raw:
            QtWidgets.QMessageBox.warning(self, "Missing Folder", "Please select a ROM folder.")
            return

        root = Path(raw).expanduser()
        if not root.exists() or not root.is_dir():
            QtWidgets.QMessageBox.warning(self, "Invalid Folder", f"Folder not found:\n{root}")
            return

        self.log_edit.clear()
        self.status_label.setText("Running...")
        self._set_running(True)

        self._thread = QtCore.QThread(self)
        self._worker = Worker(
            root=root.resolve(),
            recursive=self.recursive_cb.isChecked(),
            dry_run=self.dry_run_cb.isChecked(),
            verbose=self.verbose_cb.isChecked(),
            extract_archives=self.extract_cb.isChecked(),
            delete_archives=self.delete_archives_cb.isChecked(),
            postprocess_single_disc=self.postprocess_single_disc_cb.isChecked(),
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._append_log)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_finished(self, ok: bool, message: str) -> None:
        self._append_log("")
        self._append_log(message)
        self.status_label.setText(message)
        self._set_running(False)
        if not ok:
            QtWidgets.QMessageBox.critical(self, "Error", message)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())

