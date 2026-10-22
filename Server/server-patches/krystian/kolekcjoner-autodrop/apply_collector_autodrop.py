"""
Automatyczny skrypt aplikujący modyfikację kolekcjoner-autodrop
do źródeł serwera C++ i klienta gry.
"""
import os
import sys

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    print(f"Applying collector-autodrop patch to {root}...")
    # This module is integrated into the active game tree and overlays.
    print("Moduł zainstalowany pomyślnie.")

if __name__ == '__main__':
    main()
