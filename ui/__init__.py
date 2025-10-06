#!/usr/bin/env python3
"""
UI components package for the GUI Builder application.
"""

from .widget_toolbox import WidgetToolbox
from .design_canvas import DesignCanvas
from .properties_editor import PropertiesEditor
from .code_editor import CodeEditor, PopOutCodeEditor
from .preferences_window import PreferencesWindow
from .window_properties_dialog import WindowPropertiesDialog

__all__ = [
    'WidgetToolbox',
    'DesignCanvas', 
    'PropertiesEditor',
    'CodeEditor',
    'PopOutCodeEditor',
    'PreferencesWindow',
    'WindowPropertiesDialog'
]
