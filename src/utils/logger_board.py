import datetime
import queue
import threading
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject


'''
Instead of passing the QTextCursor object directly through the signal, pass a signal with a simple data type, 
such as a string, containing the information you need to manipulate the text cursor.
For example, you can send a signal with a string indicating the action to perform (e.g., "moveToEnd") or a position index.

In the slot that receives the signal, create a QTextCursor object based on the information provided in the signal 
and perform the desired action.

Use signal-slot to share data from logger dashboard
'''
class LogDashboard(QObject):
    log_signal = pyqtSignal(str, bool)  # Define a signal to emit log messages
    def __init__(self, log_object):
        super().__init__()
        # Log display
        self.log_display = log_object
        self.log_display.setReadOnly(True)

        # Create a queue for storing logs
        self.log_queue = queue.Queue()

        # Start a separate thread for handling logs
        self.log_thread = threading.Thread(target=self.log_consumer)
        self.log_thread.daemon = True  # Daemonize the thread (will exit when the main program exits)
        self.log_thread.start()

    def add_log(self, log_level, log_message):
        current_time = datetime.datetime.now().strftime('%d:%m:%y %H:%M')
        formatted_log = f"{current_time} - [{log_level}] {log_message}"

        ver_scroll_bar = self.log_display.verticalScrollBar()
        scroll_is_at_end = ver_scroll_bar.maximum() - ver_scroll_bar.value() <= 1

        # Put the log entry into the queue
        # self.log_queue.put(formatted_log)
        self.log_signal.emit(formatted_log, True)

    def log_consumer(self):
        while True:
            try:
                log_entry = self.log_queue.get()
                self.log_display.append(log_entry)
                self.log_display.moveCursor(QTextCursor.End)
                self.log_queue.task_done()
            except KeyboardInterrupt:
                break

    def clear_logs(self):
        self.log_display.clear()

    def save_logs(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(None, "Save Logs", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.log_display.toPlainText())
