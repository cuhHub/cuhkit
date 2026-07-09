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
import time

from cuhkit.libs.timeit import TimeIt

# // Main
def test_timeit_start_and_stop():
    timer = TimeIt()
    timer.start()
    timer.stop()

    elapsed = timer.get_elapsed()
    assert elapsed >= 0

def test_timeit_context_manager():
    with TimeIt() as timer:
        time.sleep(0.01)

    elapsed = timer.get_elapsed()
    assert elapsed >= 0.01

def test_timeit_elapsed_accuracy():
    timer = TimeIt()
    timer.start()
    time.sleep(0.05)
    timer.stop()

    elapsed = timer.get_elapsed()
    assert elapsed >= 0.04
    assert elapsed < 0.5

def test_timeit_stop_returns_elapsed():
    timer = TimeIt()
    timer.start()
    time.sleep(0.01)

    elapsed = timer.stop()
    assert elapsed >= 0.01