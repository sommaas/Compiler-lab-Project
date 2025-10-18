import tkinter as tk
from gui import CompilerInterface


def main():
    """Initialize and run the compiler GUI"""
    app_window = tk.Tk()
    compiler_ui = CompilerInterface(app_window)
    app_window.mainloop()


if __name__ == "__main__":
    main()