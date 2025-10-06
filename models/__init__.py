#!/usr/bin/env python3
"""
Data models package for the GUI Builder application.
"""

from .widget_types import WidgetType, WidgetProperty, WidgetData, WidgetGroup
from .preferences import AppPreferences, PreferencesManager

__all__ = [
    'WidgetType',
    'WidgetProperty', 
    'WidgetData',
    'WidgetGroup',
    'AppPreferences',
    'PreferencesManager'
]
