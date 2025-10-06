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
        self.geometry('800x600')
        self.update_idletasks()  # Force window to update
        self.state('normal')  # Ensure window is not minimized
        self.geometry('800x600')  # Set size again
        self.update_idletasks()
        self.setup_ui()
        # Use after to delay size enforcement
        self.after(100, self.enforce_window_size)
        self.after(200, self.center_window)

    def enforce_window_size(self):
        """Aggressively enforce the window size"""
        self.geometry('800x600')
        self.update_idletasks()
        self.tk.call('wm', 'geometry', self._w, '800x600')
        self.update_idletasks()
        self.state('normal')
        self.geometry('800x600')
        self.update_idletasks()
        try:
            self.configure(width=800, height=600)
            self.update_idletasks()
        except:
            pass
        self.geometry('800x600')
        self.update_idletasks()

    def setup_ui(self):
        """Setup the user interface"""
        # Center window on screen after UI is set up
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        # Force window to correct size multiple times to ensure it sticks
        self.geometry('800x600')
        self.update_idletasks()
        self.geometry('800x600')  # Set again to ensure it sticks
        self.update_idletasks()
        
        # Get actual dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        
        # If window is still too small, force it again
        if width < 700 or height < 500:
            self.geometry('800x600')
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
        
        # Center the window
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        # Button at (470, 390)
        self.button__5d14f92b_e96f_41be_b6c4_21c501cb8cfc = ctk.CTkButton(
            self, text='Button', width=100, height=30
        )
        self.button__5d14f92b_e96f_41be_b6c4_21c501cb8cfc.place(x=470, y=390)

if __name__ == '__main__':
    app = GeneratedApp()
    app.mainloop()