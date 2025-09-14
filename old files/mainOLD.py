#!/usr/bin/env python3
"""
main.py - Clean interface that returns ONLY plain text
This is what Flask will call in the backend
"""

import os
import sys
from email_input_handler import EmailInputHandler


def main(file_path):#for YQ if you need to get your data, call it from here it will return the data
    """
    Main function that returns ONLY clean plain text.
    No print statements, no debug info, just the processed text.
    
    Args:
        file_path (str): Path to the email file
        
    Returns:
        str: Clean plain text or empty string if error
    """
    try:
        # Verify file exists
        if not os.path.exists(file_path):
            return ""
        
        # Process the file silently
        handler = EmailInputHandler()
        result = handler.process_input(file_path=file_path, debug=False)
        
        # Return only the clean text (no extra messages)
        return result if result else ""
        
    except Exception:
        # Silent error handling - return empty string
        return ""
