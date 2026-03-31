"""
----------------------------------------------
cuhkit - A CLI-oriented Python package for handling cuhHub Stormworks projects (addons/mods).
https://github.com/cuhHub/cuhkit
----------------------------------------------

Copyright (C) 2026 cuhHub

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# // Imports
from __future__ import annotations

import time
from cuhkit.log import logger

# // Main
class TimeIt:
    """
    A class for conveniently timing code.
    """
    
    def __init__(self):
        """
        Initialises instances.
        """

        self.start_time = 0
        self.end_time = 0
        
    def get_elapsed(self) -> float:
        """
        Returns how long it took in seconds.
        
        Returns:
            float: How long it took in seconds.
        """
        
        return self.end_time - self.start_time

    def start(self):
        """
        Starts the timer.
        """
        
        self.start_time = time.perf_counter()
        
    def stop(self) -> float:
        """
        Stops the timer, returning how long it took in seconds.
        
        Returns:
            float: How long it took in seconds.
        """
        
        self.end_time = time.perf_counter()
        elapsed = self.get_elapsed()
        logger.info(f"Took: {elapsed:.4f} seconds.")
        
        return elapsed
    
    def __enter__(self) -> TimeIt:
        """
        Starts the timer.
        
        Returns:
            TimeIt: The timer.
        """

        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the timer.
        """

        self.stop()