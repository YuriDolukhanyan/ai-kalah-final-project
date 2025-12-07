"""Main entry point for Kalah game application."""

import os
# Suppress Tk deprecation warning on macOS
os.environ['TK_SILENCE_DEPRECATION'] = '1'

from src.gui.main_window import MainWindow


def main():
    """Run the GUI application."""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

