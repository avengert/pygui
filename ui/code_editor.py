#!/usr/bin/env python3
"""
Code editor components for the GUI Builder application.
"""

import customtkinter as ctk
from typing import Optional, Callable


class CodeEditor(ctk.CTkFrame):
    """Code editor panel for editing generated Python code"""
    
    def __init__(self, parent, on_code_change: Optional[Callable] = None):
        super().__init__(parent)
        self.on_code_change = on_code_change
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the code editor UI"""
        self.configure(width=400, height=600)
        self.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(self, text="Code Editor", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)
        
        # Code text area with scrollbar
        self.code_text = ctk.CTkTextbox(
            self,
            width=380,
            height=500,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind text change events
        self.code_text.bind("<KeyRelease>", self.on_text_change)
        self.code_text.bind("<Button-1>", self.on_text_change)
    
    def set_code(self, code: str):
        """Set the code content"""
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
    
    def get_code(self) -> str:
        """Get the current code content"""
        return self.code_text.get("1.0", "end-1c")
    
    def on_text_change(self, event=None):
        """Handle text change events"""
        if self.on_code_change:
            self.on_code_change(self.get_code())
    
    def highlight_syntax(self):
        """Basic syntax highlighting (placeholder for future enhancement)"""
        # This could be enhanced with proper Python syntax highlighting
        pass


class PopOutCodeEditor(ctk.CTkToplevel):
    """Pop-out window for the code editor"""
    
    def __init__(self, parent_app, on_code_change: Optional[Callable] = None, on_close_callback: Optional[Callable] = None):
        super().__init__()
        self.parent_app = parent_app
        self.on_code_change = on_code_change
        self.on_close_callback = on_close_callback
        
        self.title("Code Editor - Pop-out")
        self.geometry("600x700")
        self.minsize(400, 300)
        
        # Make this window stay on top of the main window
        self.transient(parent_app)
        self.grab_set()
        
        # Setup the UI
        self.setup_ui()
        
        # Handle window close events
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def setup_ui(self):
        """Setup the pop-out code editor UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="Code Editor", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=10)
        
        # Code text area with scrollbar
        self.code_text = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Control buttons
        self.sync_button = ctk.CTkButton(
            controls_frame, text="🔄 Sync from Design", width=120, height=25,
            command=self.sync_from_design, font=ctk.CTkFont(size=10)
        )
        self.sync_button.pack(side="left", padx=5, pady=5)
        
        self.validate_button = ctk.CTkButton(
            controls_frame, text="✅ Validate", width=80, height=25,
            command=self.validate_code, font=ctk.CTkFont(size=10)
        )
        self.validate_button.pack(side="left", padx=5, pady=5)
        
        self.run_button = ctk.CTkButton(
            controls_frame, text="▶️ Run Code", width=80, height=25,
            command=self.run_code, font=ctk.CTkFont(size=10)
        )
        self.run_button.pack(side="left", padx=5, pady=5)
        
        self.export_button = ctk.CTkButton(
            controls_frame, text="💾 Export", width=80, height=25,
            command=self.export_code, font=ctk.CTkFont(size=10)
        )
        self.export_button.pack(side="right", padx=5, pady=5)
        
        # Pop-in button
        self.pop_in_button = ctk.CTkButton(
            controls_frame, text="📌 Pop Back In", width=100, height=25,
            command=self.pop_back_in, font=ctk.CTkFont(size=10)
        )
        self.pop_in_button.pack(side="right", padx=5, pady=5)
        
        # Bind text change events
        self.code_text.bind("<KeyRelease>", self.on_text_change)
        self.code_text.bind("<Button-1>", self.on_text_change)
    
    def set_code(self, code: str):
        """Set the code content"""
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
    
    def get_code(self) -> str:
        """Get the current code content"""
        return self.code_text.get("1.0", "end-1c")
    
    def on_text_change(self, event=None):
        """Handle text change events"""
        if self.on_code_change:
            self.on_code_change(self.get_code())
    
    def sync_from_design(self):
        """Sync code from the design canvas"""
        if hasattr(self.parent_app, 'sync_code_from_design'):
            self.parent_app.sync_code_from_design()
    
    def validate_code(self):
        """Validate the current code"""
        if hasattr(self.parent_app, 'validate_code'):
            self.parent_app.validate_code()
    
    def run_code(self):
        """Run the current code"""
        if hasattr(self.parent_app, 'run_generated_code'):
            self.parent_app.run_generated_code()
    
    def export_code(self):
        """Export the current code"""
        if hasattr(self.parent_app, 'export_edited_code'):
            self.parent_app.export_edited_code()
    
    def pop_back_in(self):
        """Pop the code editor back into the main window"""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
    
    def on_window_close(self):
        """Handle window close event"""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
