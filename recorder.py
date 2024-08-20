import pynput
import threading
import pyautogui
import time

_is_shutting_down = threading.Event()

_log = list()
def log(msg: str)->None:
    _log.append(msg)
    print(msg)


def bin2hex(string: str|bytes|bytearray) -> str:
    if isinstance(string, str):        
        return string.encode("utf-8").hex()
    if isinstance(string, (bytes, bytearray)):
        return string.hex()
    raise ValueError("bin2hex: string must be str, bytes or bytearray")

def optimizer(log: list) -> list:
    # change pyautogui.keyDown("a");pyautogui.keyUp("a") to pyautogui.press("a")
    # change pyautogui.pres("a");pyautogui.press("b"); to pyautogui.write("ab")
    optimized = True
    while optimized:
        optimized = False
        index = len(log) - 1
        while index > 0:
            current_line = log[index]
            previous_line = log[index - 1]
            if current_line.startswith("pyautogui.keyUp(") and previous_line.startswith("pyautogui.keyDown("):
                key_up_key = current_line[len("pyautogui.keyUp('"):-len("')")]
                key_down_key = previous_line[len("pyautogui.keyDown('"):-len("')")]
                if key_up_key == key_down_key:
                    log[index] = "pyautogui.press('" + key_up_key + "')"
                    del log[index - 1]
                    optimized = True
            elif current_line.startswith("pyautogui.press(") and previous_line.startswith("pyautogui.press("):
                current_press = current_line[len("pyautogui.press('"):-len("')")]
                previous_press = previous_line[len("pyautogui.press('"):-len("')")]
                log[index] = "pyautogui.write('" + previous_press + current_press + "')"
                del log[index - 1]
                optimized = True
            elif current_line.startswith("pyautogui.write(") and previous_line.startswith("pyautogui.write("):
                current_write = current_line[len("pyautogui.write('"):-len("')")]
                previous_write = previous_line[len("pyautogui.write('"):-len("')")]
                log[index -1] = "pyautogui.write('" + previous_write + current_write + "')"
                del log[index]
                optimized = True
            elif current_line.startswith("pyautogui.write(") and previous_line.startswith("pyautogui.press("):
                current_write = current_line[len("pyautogui.write('"):-len("')")]
                previous_press = previous_line[len("pyautogui.press('"):-len("')")]
                log[index - 1] = "pyautogui.write('" + previous_press + current_write + "')"
                del log[index]
                optimized = True
            elif current_line.startswith("pyautogui.mouseUp(") and previous_line.startswith("pyautogui.mouseDown("):
                current_mouse_up = current_line[len("pyautogui.mouseUp("):-1]
                previous_mouse_down = previous_line[len("pyautogui.mouseDown("):-1]
                if current_mouse_up == previous_mouse_down:
                    log[index - 1] = "pyautogui.click(" + previous_mouse_down + ")"
                    del log[index]
                    optimized = True
            index -= 1
    return log

debug_optimizer = False
#debug_optimizer = True
if debug_optimizer:
    log = [
        "pyautogui.keyDown('T')",
        "pyautogui.keyUp('T')",
        "pyautogui.keyDown('e')",
        "pyautogui.keyUp('e')",
        "pyautogui.keyDown('s')",
        "pyautogui.keyUp('s')",
        "pyautogui.keyDown('t')",
        "pyautogui.keyUp('t')",
    ]
    optimized_log = optimizer(log)
    print("Optimized log:")
    print(optimized_log) # should print ["pyautogui.write('Test')"]
    exit(0)


def record_mouse_and_keyboard_events():
    def translate_button(button):
        if button == pynput.mouse.Button.left:
            return "'left'"
        elif button == pynput.mouse.Button.middle:
            return "'middle'"
        elif button == pynput.mouse.Button.right:
            return "'right'"
        elif button == pynput.keyboard.Key.ctrl_l:
            return "'ctrl_l'"
        elif button == pynput.keyboard.Key.esc:
            return "'esc'"
        else:
            # ???
            ret = str(button)
            if ret == 'Key.cmd':
                return "'win'" # windows key... idk why str(button) returns "Key.cmd"
            if ret.startswith("'"):
                return ret
            return "'" + ret + "'"
    def on_click(x, y, button, pressed):
        if pressed:
            #print(f"Mouse clicked at ({x}, {y}) with {button}")
            log("pyautogui.mouseDown(" + str(x) + ", " + str(y) + ", button=" + translate_button(button) + ")")
        else:
            #print(f"Mouse released at ({x}, {y}) with {button}")
            log("pyautogui.mouseUp(" + str(x) + ", " + str(y) + ", button=" + translate_button(button) + ")")
        if _is_shutting_down.is_set():
            return False
    
    def on_scroll(x, y, dx, dy):
        #print(f"Mouse scrolled at ({x}, {y}) with ({dx}, {dy})")
        log("pyautogui.scroll(" + str(dx) + ", " + str(dy) + ")")
        if _is_shutting_down.is_set():
            return False
    
    def on_press(key):
        try:
            #print(f"Key pressed: {key.char}")
            log("pyautogui.keyDown(" + translate_button(key.char) + ")")
        except AttributeError:
            #print(f"Special key pressed: {key}")
            log("pyautogui.keyDown(" + translate_button(key) + ")")
            if key == pynput.keyboard.Key.esc:
                # Stop both listeners when ESC is pressed
                _is_shutting_down.set()
                print("Shutting down...")
        if _is_shutting_down.is_set():
            return False
    def on_release(key):
        #print(f"Key released: {key}")
        log("pyautogui.keyUp(" + translate_button(key) + ")")
        if key == pynput.keyboard.Key.esc:
            # Stop both listeners when ESC is pressed
            _is_shutting_down.set()
            print("Shutting down...")
        if _is_shutting_down.is_set():
            return False
    with pynput.mouse.Listener(on_click=on_click, on_scroll=on_scroll) as mouse_listener:
        with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
            keyboard_listener.join()

def record_active_window():
    pass
    old_title = None
    while True:
        title = pyautogui.getActiveWindowTitle()
        # idk why but it returns None sometimes, sporadically
        if title is not None and title != old_title:
            #print(title)
            # todo: proper python quoting of title..

            log("while not pyautogui.getActiveWindowTitle() == '" + title + "':")
            log("    time.sleep(0.1)")
            old_title = title
        else:
            pass
            #print("No change")
        if _is_shutting_down.is_set():
            break
        pyautogui.sleep(0.1)



if __name__ == "__main__":
    mouse_and_keyboard_recorder_thread = threading.Thread(target=record_mouse_and_keyboard_events)
    mouse_and_keyboard_recorder_thread.start()
    record_active_window_thread = threading.Thread(target=record_active_window)
    record_active_window_thread.start()
    record_active_window_thread.join()
    mouse_and_keyboard_recorder_thread.join()
    print("------OPTIMIZED VERSION:")
    optimized_log = optimizer(_log)
    for line in optimized_log:
        print(line)
