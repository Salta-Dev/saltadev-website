"""Common CSS classes for form widgets.

This module provides consistent styling constants for Django form widgets,
avoiding code duplication across forms.
"""

# Base styles for dark-themed form inputs
INPUT_BASE = (
    "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl "
    "text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
)

# Input with placeholder styling
INPUT_CLASS = f"{INPUT_BASE} placeholder-[#6b605f]"

# Textarea styling (adds resize-none)
TEXTAREA_CLASS = f"{INPUT_CLASS} resize-none"

# Select/dropdown styling (different padding for arrow space)
SELECT_CLASS = (
    "w-full pl-4 pr-10 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl "
    "text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary "
    "cursor-pointer appearance-none"
)

# Date/time input styling (no placeholder needed)
DATE_TIME_CLASS = INPUT_BASE
