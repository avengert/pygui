#!/usr/bin/env python3
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
        self.title('Generated GUI')
        self.minsize(400, 300)
        self.geometry('900x680')
        self.update_idletasks()  # Force window to update
        self.state('normal')  # Ensure window is not minimized
        self.geometry('900x680')  # Set size again
        self.update_idletasks()
        self.setup_ui()
        # Use after to delay size enforcement
        self.after(100, self.enforce_window_size)
        self.after(200, self.center_window)

    def enforce_window_size(self):
        """Aggressively enforce the window size"""
        self.geometry('900x680')
        self.update_idletasks()
        self.tk.call('wm', 'geometry', self._w, '900x680')
        self.update_idletasks()
        self.state('normal')
        self.geometry('900x680')
        self.update_idletasks()
        try:
            self.configure(width=900, height=680)
            self.update_idletasks()
        except:
            pass
        self.geometry('900x680')
        self.update_idletasks()

    def setup_ui(self):
        """Setup the user interface"""
        # Center window on screen after UI is set up
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        # Force window to correct size multiple times to ensure it sticks
        self.geometry('900x680')
        self.update_idletasks()
        self.geometry('900x680')  # Set again to ensure it sticks
        self.update_idletasks()
        
        # Get actual dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        
        # If window is still too small, force it again
        if width < 800 or height < 580:
            self.geometry('900x680')
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
        
        # Center the window
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        # Button at (740, 590)
        self.button__67cb4eb3_1bd3_4b29_b6f7_aebe5087a36d = ctk.CTkButton(
            self, text='Button', width=100, height=30
        )
        self.button__67cb4eb3_1bd3_4b29_b6f7_aebe5087a36d.place(x=740, y=590)
        # Label at (80, 180)
        self.label__36d37a3c_e5bc_4b50_90a9_cdc1d96242b5 = ctk.CTkLabel(
            self, text='Username', width=100, height=30,
            font=ctk.CTkFont(size=12)
        )
        self.label__36d37a3c_e5bc_4b50_90a9_cdc1d96242b5.place(x=80, y=180)
        # Label at (210, 180)
        self.label__48f6eabc_6989_4bfc_a43b_ecbf07ea6b4c = ctk.CTkLabel(
            self, text='Password', width=100, height=30,
            font=ctk.CTkFont(size=12)
        )
        self.label__48f6eabc_6989_4bfc_a43b_ecbf07ea6b4c.place(x=210, y=180)
        # Entry at (210, 220)
        self.entry__6c90e046_b21e_4fdf_a3c3_e567745a83c3 = ctk.CTkEntry(
            self, placeholder_text='Enter text...', width=100, height=30
        )
        self.entry__6c90e046_b21e_4fdf_a3c3_e567745a83c3.place(x=210, y=220)
        # Entry at (80, 220)
        self.entry__45b57342_1abd_4b21_941f_3dd27cb6a7f8 = ctk.CTkEntry(
            self, placeholder_text='Enter text...', width=100, height=30
        )
        self.entry__45b57342_1abd_4b21_941f_3dd27cb6a7f8.place(x=80, y=220)

if __name__ == '__main__':
    app = GeneratedApp()
    app.mainloop()