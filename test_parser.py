#!/usr/bin/env python3
"""Test script for the CodeParser"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import CodeParser

# Test code
test_code = '''#!/usr/bin/env python3
"""
Generated GUI Application
Created with Professional Python GUI Builder MVP
"""

import customtkinter as ctk
import tkinter as tk

# Set appearance mode and color theme
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

class GeneratedApp(ctk.CTk):
    """Generated GUI Application"""
    
    def __init__(self):
        super().__init__()
        self.title('Test GUI')
        self.geometry('800x600')
        self.setup_ui()

    def setup_ui(self):
        # Button at (50, 50)
        self.button_1 = ctk.CTkButton(
            self, text='Click Me!', width=100, height=30
        )
        self.button_1.place(x=50, y=50)
        
        # Label at (200, 50)
        self.label_1 = ctk.CTkLabel(
            self, text='Hello World', width=200, height=30
        )
        self.label_1.place(x=200, y=50)

if __name__ == '__main__':
    app = GeneratedApp()
    app.mainloop()
'''

if __name__ == '__main__':
    print("Testing CodeParser...")
    widgets, window_properties = CodeParser.parse_code_to_widgets(test_code)
    
    print(f"Found {len(widgets)} widgets:")
    for widget_id, widget_data in widgets.items():
        print(f"  - {widget_id}: {widget_data.type} at ({widget_data.x}, {widget_data.y})")
        print(f"    Properties: {widget_data.properties}")
    
    print(f"\nWindow properties: {window_properties}")
