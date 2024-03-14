import threading, msvcrt
def take_key():
    global key_GL, command_mode_GL
    while True:
        if not command_mode_GL:
            key_GL = msvcrt.getwch()
        if key_GL == "Q":
            break
        elif key_GL == "/":
            command_mode_GL = True

global key_GL, command_mode_GL
key_GL, command_mode_GL = None, False
threading.Thread(target=take_key, daemon=True).start()