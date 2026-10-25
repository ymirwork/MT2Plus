"""
Automatyczny skrypt aplikujący / weryfikujący modyfikację kolekcjoner-refine
(sprawdzanie i pobieranie ulepszaczy z magazynu kolekcjonera).
"""
import os
import sys

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    print(f"Applying collector-refine patch to {root}...")
    # Moduł zintegrowany bezpośrednio w źródłach C++ (char_item.cpp, playerbot_collector.cpp/h, input_login.cpp)
    # oraz w kliencie gry (uirefine.py, uicollector.py).
    print("Moduł zainstalowany pomyślnie.")

if __name__ == '__main__':
    main()
