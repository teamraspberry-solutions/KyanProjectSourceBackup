import traceback
import time

class ErrorHandler:
    def __init__(self, log_file="error_log.txt"):
        """Initializes the error handler with a log file."""
        self.log_file = log_file

    def log_error(self, error):
        """Logs an error to a file with traceback details."""
        error_message = f"[{self.get_timestamp()}] {str(error)}\n{traceback.format_exc()}\n"
        with open(self.log_file, "a") as f:
            f.write(error_message)
        print(f"Error logged: {error}")

    def get_timestamp(self):
        """Returns the current timestamp."""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
