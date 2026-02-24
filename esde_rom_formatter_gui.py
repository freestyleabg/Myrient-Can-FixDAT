#!/usr/bin/env python3
"""GUI for creating ES-DE .m3u directory structures for multi-disc ROM sets."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore

from esde_rom_formatter_core import process_library

TITLE_BAR_HEIGHT = 32
USE_FRAMELESS_WINDOWS = sys.platform.startswith("win")

APP_STYLESHEET = """
QWidget#titleBar { background-color: #1f2027; }
QLabel#titleText { color: #e6e6eb; font-weight: 600; }
QPushButton#titleButton, QPushButton#titleButtonClose {
    background-color: transparent; border: none; border-radius: 0; color: #e0e0e5;
}
QPushButton#titleButton:hover { background-color: #3b3d4a; }
QPushButton#titleButtonClose:hover { background-color: #e81123; color: #ffffff; }
QWidget { color: #e6e6eb; }
QLineEdit, QPlainTextEdit {
    background-color: #18181f; border: 1px solid #444454; border-radius: 4px; padding: 3px; color: #f0f0f5;
}
QPushButton {
    background-color: #2f3645; border: 1px solid #4a5265; border-radius: 4px; padding: 4px 12px; color: #f0f0f5;
}
QPushButton:hover { background-color: #3a4356; }
QCheckBox { color: #e6e6eb; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px; border: 2px solid #4a5265; border-radius: 3px; background-color: #18181f;
}
QCheckBox::indicator:checked { background-color: #5aa0ff; border-color: #7ab3ff; }
"""


class TitleBar(QtWidgets.QWidget):
    def __init__(self, window: QtWidgets.QWidget) -> None:
        super().__init__(window)
        self._window = window
        self._drag_pos: QtCore.QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(TITLE_BAR_HEIGHT)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 8, 4)
        layout.setSpacing(8)

        title_label = QtWidgets.QLabel("ESDE ROM Formatter")
        title_label.setObjectName("titleText")
        layout.addWidget(title_label)
        layout.addStretch(1)

        self.min_button = QtWidgets.QPushButton("−")
        self.min_button.setObjectName("titleButton")
        self.min_button.setFixedSize(28, 22)
        self.min_button.clicked.connect(self._window.showMinimized)  # type: ignore[attr-defined]

        self.max_button = QtWidgets.QPushButton("□")
        self.max_button.setObjectName("titleButton")
        self.max_button.setFixedSize(28, 22)
        self.max_button.clicked.connect(self._toggle_max_restore)

        self.close_button = QtWidgets.QPushButton("×")
        self.close_button.setObjectName("titleButtonClose")
        self.close_button.setFixedSize(28, 22)
        self.close_button.clicked.connect(self._window.close)  # type: ignore[attr-defined]

        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

    def _toggle_max_restore(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
            self.max_button.setText("□")
        else:
            self._window.showMaximized()
            self.max_button.setText("❐")

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self._window.frameGeometry().topLeft()  # type: ignore[attr-defined]
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        if self._drag_pos is not None and (event.buttons() & QtCore.Qt.LeftButton):
            if self._window.isMaximized():
                self._window.showNormal()
                self.max_button.setText("□")
                self._drag_pos = event.globalPos() - self._window.frameGeometry().topLeft()  # type: ignore[attr-defined]
            self._window.move(event.globalPos() - self._drag_pos)  # type: ignore[attr-defined]
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:  # type: ignore[override]
        if event.button() == QtCore.Qt.LeftButton:
            self._toggle_max_restore()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


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
        self._title_bar: TitleBar | None = None

        self._apply_dark_theme()

        if USE_FRAMELESS_WINDOWS:
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint
                | QtCore.Qt.Window
                | QtCore.Qt.WindowSystemMenuHint
                | QtCore.Qt.WindowMinimizeButtonHint
                | QtCore.Qt.WindowMinMaxButtonsHint
                | QtCore.Qt.WindowCloseButtonHint
            )

        self.setWindowTitle("ESDE ROM Formatter")
        self.resize(760, 560)

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        if USE_FRAMELESS_WINDOWS:
            self._size_grip = QtWidgets.QSizeGrip(self)
            self._size_grip.setFixedSize(18, 18)
            self._size_grip.raise_()

        layout = QtWidgets.QVBoxLayout(root)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        if USE_FRAMELESS_WINDOWS:
            self._title_bar = TitleBar(self)
            layout.addWidget(self._title_bar)

        path_row = QtWidgets.QHBoxLayout()
        path_label = QtWidgets.QLabel("ROM Folder")
        self.path_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_folder)

        path_row.addWidget(path_label)
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse_btn)

        opt_container = QtWidgets.QVBoxLayout()
        opt_container.setSpacing(4)
        opt_row_top = QtWidgets.QHBoxLayout()
        opt_row_bottom = QtWidgets.QHBoxLayout()
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
        opt_row_top.addWidget(self.dry_run_cb)
        opt_row_top.addWidget(self.recursive_cb)
        opt_row_top.addWidget(self.extract_cb)
        opt_row_top.addStretch(1)
        opt_row_bottom.addWidget(self.delete_archives_cb)
        opt_row_bottom.addWidget(self.postprocess_single_disc_cb)
        opt_row_bottom.addWidget(self.verbose_cb)
        opt_row_bottom.addStretch(1)
        opt_container.addLayout(opt_row_top)
        opt_container.addLayout(opt_row_bottom)

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
        layout.addLayout(opt_container)
        layout.addLayout(button_row)
        layout.addWidget(self.log_edit, 1)
        layout.addWidget(self.status_label)

    def _apply_dark_theme(self) -> None:
        self.setStyleSheet(APP_STYLESHEET)
        palette = self.palette()
        bg = QtGui.QColor(30, 30, 36)
        panel = QtGui.QColor(40, 40, 48)
        text = QtGui.QColor(230, 230, 235)
        accent = QtGui.QColor(90, 160, 255)
        palette.setColor(QtGui.QPalette.Window, bg)
        palette.setColor(QtGui.QPalette.WindowText, text)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(20, 20, 26))
        palette.setColor(QtGui.QPalette.AlternateBase, panel)
        palette.setColor(QtGui.QPalette.Text, text)
        palette.setColor(QtGui.QPalette.Button, panel)
        palette.setColor(QtGui.QPalette.ButtonText, text)
        palette.setColor(QtGui.QPalette.Highlight, accent)
        self.setPalette(palette)

    def changeEvent(self, event: QtCore.QEvent) -> None:  # type: ignore[override]
        super().changeEvent(event)
        if not USE_FRAMELESS_WINDOWS:
            return
        if event.type() == QtCore.QEvent.WindowStateChange:
            if hasattr(self, "_size_grip"):
                self._size_grip.setVisible(not self.isMaximized())
            if self._title_bar is not None:
                self._title_bar.max_button.setText("❐" if self.isMaximized() else "□")

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if USE_FRAMELESS_WINDOWS and hasattr(self, "_size_grip"):
            margin = 2
            self._size_grip.setVisible(not self.isMaximized())
            self._size_grip.move(
                max(margin, self.width() - self._size_grip.width() - margin),
                max(margin, self.height() - self._size_grip.height() - margin),
            )

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
    app_icon_path: Path | None = None
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            p = Path(meipass) / ".github" / "icon_white.png"
            if p.exists():
                app_icon_path = p
    if app_icon_path is None:
        p = Path(__file__).resolve().parent / ".github" / "icon_white.png"
        if p.exists():
            app_icon_path = p
    if app_icon_path and app_icon_path.exists():
        app.setWindowIcon(QtGui.QIcon(str(app_icon_path)))
    window = MainWindow()
    if app_icon_path and app_icon_path.exists():
        window.setWindowIcon(QtGui.QIcon(str(app_icon_path)))
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())

