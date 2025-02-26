import time

def get_current_timestamp():
    """Returns the current timestamp in a readable format."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
