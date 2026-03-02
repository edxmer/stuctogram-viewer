from py.stuctogram_generator import generate_structogram_html
from sys import argv
import threading
from os.path import abspath
from pathlib import Path
import webview

UPDATE_DELAY = 0.2
stuki_path = ""
prev_code = ""
html_file_path = Path(".") / "html" / "index.html"
html_file_path = abspath(html_file_path)
base_html_file_path = Path(".") / "html" / "base.html"
window = None

stop_event = threading.Event()

def check_for_update() -> bool:
    try:
        with open(stuki_path, "r", encoding="utf-8") as f:
            stuki_code = f.read()
        return stuki_code != prev_code
    except:
        return False

def update() -> None:
    global prev_code
    try:
        with open(base_html_file_path, "r", encoding="utf-8") as f:
            base_html = f.read() # replace @body to actual body

        with open(stuki_path, "r", encoding="utf-8") as f:
            stuki_code = f.read()
        
        prev_code = stuki_code

        stuki_html = generate_structogram_html(stuki_code)
        index_html = base_html.replace("@body", stuki_html)

        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(index_html)
    except Exception:
        print("Error updating")

    scroll_y = window.evaluate_js('window.scrollY')
    zoom_amount = window.evaluate_js('document.getElementById(\'zoomSlider\').value')

    def on_load():
        nonlocal zoom_amount
        if scroll_y is not None:
            window.evaluate_js(f'window.scrollTo(0, {scroll_y})')
        if zoom_amount is not None:
            window.evaluate_js(f'updateZoom({zoom_amount})')
            window.evaluate_js(f'document.getElementById(\'zoomSlider\').value = {zoom_amount}')

        window.events.loaded -= on_load

    try:
        window.load_url(f"file://{html_file_path}")
        window.events.loaded += on_load
    except Exception:
        pass

def on_closed():
    stop_event.set()

def main(_):
    
    while not stop_event.is_set():
        if check_for_update():
            update()
        
        if stop_event.wait(UPDATE_DELAY):
            break


if __name__ == '__main__':
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write("loading...")
    if 2 <= len(argv):
        stuki_path = Path(argv[1])

        if not stuki_path.is_file():
            raise Exception("The stuctogram's path is not found.")

        window = webview.create_window(
            'Structogram viewer',
            url=f"file://{html_file_path}",
            width=850, 
            height=1000,
        )

        window.events.closed += on_closed

        webview.start(main, window)
        
