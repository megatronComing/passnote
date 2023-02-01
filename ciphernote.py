# -*- encoding: utf-8 -*-
'''
the main entry for cipher notebook
Author: Jared Yu
Contect: hfyu.hzcn@gmail.com
Version: 1.0
Update: 2023-2-28
Requires: PyQt5, cryptography
Tested with: PyQt5 5.15.2.2.2, cryptography 2.9.2
Tested in: Windows 11, MacOS
'''
import sys
from PyQt5.QtWidgets import QApplication
import logging
import window as GUI
import cipherdb as DB

def main() -> None:
    '''main entry'''
    logging.basicConfig(level=logging.DEBUG)
    
    app = QApplication(sys.argv)
    mainwindow = GUI.MainWindow()
    mainwindow.show()
    app.exec()

if __name__ == '__main__':
    main()