#!/usr/bin/env python3
"""
Demo of generated GUI code from the Python GUI Builder
This file demonstrates the output of the code generation feature.
"""

import customtkinter as ctk
import tkinter as tk

# Set appearance mode and color theme
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

class GeneratedApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Generated GUI')
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
            self, text='Welcome to the GUI Builder', width=200, height=30,
            font=ctk.CTkFont(size=14)
        )
        self.label_1.place(x=200, y=50)
        
        # Entry at (50, 100)
        self.entry_1 = ctk.CTkEntry(
            self, placeholder_text='Enter your name...', width=200, height=30
        )
        self.entry_1.place(x=50, y=100)
        
        # Checkbox at (50, 150)
        self.checkbox_1 = ctk.CTkCheckBox(
            self, text='I agree to the terms', width=200, height=30
        )
        self.checkbox_1.place(x=50, y=150)
        
        # Combobox at (50, 200)
        self.combobox_1 = ctk.CTkComboBox(
            self, values=['Option 1', 'Option 2', 'Option 3'], width=200, height=30
        )
        self.combobox_1.place(x=50, y=200)
        
        # Slider at (50, 250)
        self.slider_1 = ctk.CTkSlider(
            self, from_=0, to=100, width=200, height=20
        )
        self.slider_1.set(50)
        self.slider_1.place(x=50, y=250)
        
        # Progressbar at (50, 300)
        self.progressbar_1 = ctk.CTkProgressBar(
            self, width=200, height=20
        )
        self.progressbar_1.set(0.5)
        self.progressbar_1.place(x=50, y=300)

if __name__ == '__main__':
    app = GeneratedApp()
    app.mainloop()
