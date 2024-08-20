# PyAutoGuiRecord
recorder for PyAutoGui, inspired by AutoIt's AU3Record

For example if you record yourself pressing Windows button + R -> notepad -> enter -> test, you should get:
```
(...)
------OPTIMIZED VERSION:
while not pyautogui.getActiveWindowTitle() == 'recorder.py - Visual Studio Code':
    time.sleep(0.1)
pyautogui.keyDown('win')
pyautogui.press('r')
pyautogui.keyUp('win')
while not pyautogui.getActiveWindowTitle() == 'Run':
    time.sleep(0.1)
pyautogui.write('notepad')
pyautogui.keyDown('Key.enter')
while not pyautogui.getActiveWindowTitle() == '':
    time.sleep(0.1)
pyautogui.keyUp('Key.enter')
while not pyautogui.getActiveWindowTitle() == 'Untitled - Notepad':
    time.sleep(0.1)
pyautogui.keyDown('t')
while not pyautogui.getActiveWindowTitle() == '*Untitled - Notepad':
    time.sleep(0.1)
pyautogui.keyUp('t')
pyautogui.write('est')
pyautogui.keyDown('esc')
```
