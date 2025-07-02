import inspect
import os

def printErr(err=''):
    # Get the caller's frame (the function that called printerror)
    caller_frame = inspect.currentframe().f_back  # or inspect.stack()[1][0]
    
    # Get the file name (with full path) and extract only the base file name
    file_path = caller_frame.f_code.co_filename
    file_name = os.path.basename(file_path)
    
    # Get the calling function's name
    function_name = caller_frame.f_code.co_name
    
    # Get the module name from the frame. This might return None if not found.
    module = inspect.getmodule(caller_frame)
    module_name = module.__name__ if module else "Unknown"
    
    # Print (or log) the error context
    print(f"Error occurred in module: {module_name}, file: {file_name}, function: {function_name}")
    print(err)