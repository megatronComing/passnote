# -*- encoding: utf-8 -*-
'''
main window widget definition
Author: Jared Yu
Contect: hfyu.hzcn@gmail.com
Version: 1.0
Update: 2022-2-22
Requires: PyQt5
'''
from PyQt5.Qt import QMainWindow, QDesktopWidget, QIcon, QWidget, QHBoxLayout, QVBoxLayout, QAbstractItemView, QMenu, QAction, QTreeWidgetItem, QLineEdit, QMessageBox, QInputDialog,QFileDialog, QFont
from PyQt5.QtWidgets import QApplication
from widgetdef import TreeWidget, TextEdit
import logging
import sys
import os
import json
import cipherdb

DEFAULT_MAINWINDOW_WIDTH = 800
DEFAULT_MAINWINDOW_HEIGHT = 500

DEFALT_DB_NAME = 'cipherdb.db'
CONFIG_FILE = 'config.json'
CFG_DBFILE = 'database'
DEFAULT_DBFILE = 'cipherdb.db'
WINDOW_TITLE = 'Cipher notebook'

ABOUT_MSG = f"""Encrypted notebook V1.0
CAUTION: No recovery can be done in case of losing the password.
The initial password is: {cipherdb.DEFAULT_PASSWD}
Author: Jared Yu
email: hfyu.hzcn@gmail.com"""
class MainWindow(QMainWindow):
    def __init__(self, width:int = DEFAULT_MAINWINDOW_WIDTH, height:int = DEFAULT_MAINWINDOW_HEIGHT):
        '''create a main windows with the specified width and height'''
        super(MainWindow, self).__init__()
        self.db = None
        self.resize(width, height)
        self.__createMainWindow()
        self.__connectWidgetSignals()
        self.loadDatabase()
    
    def closeEvent(self, event):
        logging.debug('MainWindow.closeEvent()')
        self.__saveText2Database()


    def clearMainWindow(self) -> None:
        '''clear all display of the main window'''
        self.treeFolders.clear()
        self.textWidget.setPlainText('')
    def loadDatabase(self) -> None:
        '''load database, called when the class is initiated'''
        configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), CONFIG_FILE)
        logging.debug(f'config file {configfile}')
        config = self.__getConfig(configfile)
        if None == config:
            self.__showStatusMsg('No database found', 10000)
            return
        logging.info(f'config file read: ' + CONFIG_FILE)
        logging.debug(f'config:{config}')
        #print(type(config))
        if not self.__connectDatabase(config[CFG_DBFILE]):
            return
        self.__readAllFolders(cipherdb.ID_ROOT, None)
        self.__showStatusMsg(f'Database loaded: {config[CFG_DBFILE]}', 10000)

    def __getConfig(self, filename:str) -> dict:
        '''read configuration from the file'''
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            logging.info(f'config file loaded [{filename}]')
            return json.loads(data)
        except:
            logging.info(f'FAILED to read config file [{filename}]')
            return None
    def __saveConfig(self, configDict:dict, filename:str) -> bool:
        '''save the configuration to file'''
        jsonData = json.dumps(configDict)
        logging.debug(jsonData)
        try:
            with open(CONFIG_FILE, 'w') as json_file:
                json.dump(jsonData, json_file)
            return True
        except:
            return False
    def __createMainWindow(self) -> None:
        '''create all the widgets:TreeWidget, TextEdit, main menu'''
        self.setWindowIcon(QIcon('lock.png'))
        self.setFont(QFont('Times New Roman', 12))
        self.setWindowTitle(WINDOW_TITLE)
        self.__putWindowInCenterOfScreen()
        self.__createWidgets()
        self.__createMenu()
        #self.setSignalHandlers()
    def __putWindowInCenterOfScreen(self) -> None:
        '''put the main windows in the center of the screen'''
        #put the main windows in the center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
    def __createWidgets(self) -> None:
        '''create TreeWidget and TextEdit'''
        WIDTH_FOLDER = 200
        #create widgets for the main window
        #create widgets
        self.centralwidget = QWidget(self)
        self.centralwidgetLayout = QVBoxLayout(self.centralwidget)
        self.centralwidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.centralwidgetLayout.setSpacing(0)

        self.mainWidget = QWidget(self.centralwidget)
        self.mainLayout = QHBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.treeFolders = TreeWidget(self.centralwidget)
        self.treeFolders.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeFolders.setDragEnabled(True)
        self.treeFolders.viewport().setAcceptDrops(True)
        self.treeFolders.setDropIndicatorShown(True)
        self.treeFolders.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeFolders.setMaximumWidth(WIDTH_FOLDER)
        #self.treeFolders.header().setStyleSheet("QHeaderView{background-color:#E6E6E6;border:none;}")
        self.treeFolders.header().setStyleSheet("background-color: rgb(150,150,150)")

        #config widgets
        self.treeFolders.setColumnCount(3)
        self.treeFolders.setHeaderLabels(['Categories', 'folderid', 'parentid'])
        self.treeFolders.setColumnHidden(TreeWidget.COL_FOLDER_ID,True)
        self.treeFolders.setColumnHidden(TreeWidget.COL_FOLDER_PARENTID,True)
        self.treeFolders.setColumnHidden(TreeWidget.COL_FOLDER_NAME,False)

        self.textWidget = TextEdit(self.centralwidget)
        

        self.mainLayout.addWidget(self.treeFolders)
        self.mainLayout.addWidget(self.textWidget)

        #self.statusbar = QStatusBar(self)
        
        self.centralwidgetLayout.addWidget(self.mainWidget)
        #self.centralwidgetLayout.addWidget(self.statusbar)

        self.setCentralWidget(self.centralwidget)
        
    
    def __showStatusMsg(self, msg:str, timeout:int=0) -> None:
        '''display a message on the status bar of the main window'''
        #self.statusbar.showMessage(msg, timeout)
        self.statusBar().showMessage(msg, timeout)
    def __createMenu(self) -> None:
        '''create main menu for the main window'''
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        newDatabase = QAction("&New database", self)
        newDatabase.setShortcut("Ctrl+N")
        newDatabase.setStatusTip('Create a new database')
        newDatabase.triggered.connect(self.__menuNewDatabase)
        fileMenu.addAction(newDatabase)

        openDatabase = QAction("&Open database", self)
        openDatabase.setShortcut("Ctrl+O")
        openDatabase.setStatusTip('Select a database file')
        openDatabase.triggered.connect(self.__menuSelectDatabase)
        fileMenu.addAction(openDatabase)

        changePasswd = QAction("N&ew Password", self)
        changePasswd.setShortcut("Ctrl+E")
        changePasswd.setStatusTip('Set a new password')
        changePasswd.triggered.connect(self.__menuChangePasswd)
        fileMenu.addAction(changePasswd)

        aboutAction = QAction("&About", self)
        aboutAction.setShortcut("Ctrl+A")
        aboutAction.setStatusTip('Show about')
        aboutAction.triggered.connect(self.__menuAbout)
        fileMenu.addAction(aboutAction)

        aboutAction = QAction("E&xit", self)
        aboutAction.setShortcut("Ctrl+X")
        aboutAction.setStatusTip('Exit the program')
        aboutAction.triggered.connect(self.__menuExit)
        fileMenu.addAction(aboutAction)

    def __menuNewDatabase(self) -> None:
        '''handle of the menu command New Database'''
        dirname = QFileDialog.getExistingDirectory(self, 'Select a directory to create the new database')
        if dirname == '':
            return
        filename, ok = QInputDialog.getText(self, 'database file name', 'database file name')
        if not ok:
            return
        if filename[-3:].lower() != '.db':
            filename += '.db'
        fname = os.path.join(dirname, filename)
        logging.debug(f'New database file full path:{fname}')
        
        passwd, ok = QInputDialog.getText(self, 'Set password', 'Set password for the new database', QLineEdit.Password)
        if not ok:
            return
        passwdAgain, ok = QInputDialog.getText(self, 'Set password', 'Please input the password again', QLineEdit.Password)
        if not ok:
            return
        if passwd != passwdAgain:
            self.__showMessageBox(QMessageBox.Error, "Passwords don't match!", "Password mismatch", QMessageBox.Ok)
            return
        if self.db != None:
            del self.db
        self.db = cipherdb.CiperDatabase(fname)
        self.treeFolders.setDatabaseHandle(self.db)
        self.textWidget.setDatabaseHandle(self.db)
        if self.db.createDatabase(fname, passwd):
            logging.info(f'new database created [{fname}]')
            self.__showMessageBox(QMessageBox.Information, "Database created successfully", "New database", QMessageBox.Ok)

        else:
            logging.critical(f'FAILED to create a new database [{fname}]')
            self.__showMessageBox(QMessageBox.Error, "FAILED to create a new database", "New database", QMessageBox.Ok)
        #save config
        self.__saveConfig({CFG_DBFILE:fname}, CONFIG_FILE)
        #read table folders and set the data into the tree widget
        self.__readAllFolders(cipherdb.ID_ROOT, None)
        

    def __readAllFolders(self, parentid:int, parentWidget:QWidget) -> None:
        '''read folder data whose parentid is given, set the data to TreeWidget
        recursion is done to load all the children folders'''
        logging.debug('>>>MainWindow.__readAllFolders')
        if parentid == cipherdb.ID_ROOT:
            parentWidget = self.treeFolders
        records = self.db.readTableFolders(parentid)
        
        for row in records:
            rowFolderid, rowFoldername, rowParentid = row
            item = QTreeWidgetItem(parentWidget)
            item.setText(TreeWidget.COL_FOLDER_ID, str(rowFolderid))
            item.setText(TreeWidget.COL_FOLDER_NAME, rowFoldername)
            item.setText(TreeWidget.COL_FOLDER_PARENTID, str(rowParentid))
            self.__readAllFolders(rowFolderid, item) #recursion
        self.treeFolders.setActiveStatus(True)
        
    # def setSignalHandlers(self):
    #     pass
    def __menuChangePasswd(self) -> None:
        '''handler of the menu command New Password'''
        logging.debug('>>>MainWindow.__menuChangePasswd')
        passwd, ok = QInputDialog.getText(self, 'Change password', 'Please input a new password for the database', QLineEdit.Password)
        if not ok:
            return
        passwdAgain, ok = QInputDialog.getText(self, 'Change password', 'Please input the new password again', QLineEdit.Password)
        if not ok:
            return
        if passwd != passwdAgain:
            self.__showMessageBox(QMessageBox.Warning, "The password you inputed don't match, cancelled!", "Password mismatch", QMessageBox.Ok)
            return
        if self.db.changePasswd(passwd):
            self.__showMessageBox(QMessageBox.Information, "The new password was set to the database successfully", "Password changed", QMessageBox.Ok)
        else:
            self.__showMessageBox(QMessageBox.Critical, "FAILED to set the new password to the dataBASE", "Password UNCHANGED", QMessageBox.Ok)
        
    def __menuSelectDatabase(self) -> None:
        '''handler of the menu command Open Database'''
        logging.debug('>>>MainWindow.__menuSelectDatabase')
        filename = QFileDialog.getOpenFileName(self, 'Open an existing database file')[0]
        if filename == '':
            logging.debug('user cancled')
            return
        logging.debug(f'database file selected [{filename}]')
        if not self.__connectDatabase(filename):
            return
        self.__saveConfig({CFG_DBFILE:filename}, CONFIG_FILE)
        self.clearMainWindow()
        self.__readAllFolders(cipherdb.ID_ROOT, None)
        
    def __menuAbout(self) -> None:
        '''handler of the menu command About'''
        self.__showMessageBox(QMessageBox.Information, 
            ABOUT_MSG, 
            "About password notebook", QMessageBox.Ok)
    def __menuExit(self) -> None:
        '''handler of the menu command Exit, save changed data before exiting'''
        self.__saveText2Database() #save change
        exit(0)
    def __showMessageBox(self, iconType, text:str, title:str, buttons) -> None:
        '''show a message box window
        iconType: QMessageBox.Warning, QMessageBox.Information, QMessageBox.Error or QMessageBox.Critical
        buttons: combination of QMessageBox.Ok, QMessageBox.Cancel'''
        msgBox = QMessageBox()
        msgBox.setIcon(iconType) #Question,Information,Warning,Critical
        msgBox.setText(text)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(buttons)
        msgBox.exec_()
    
    def __connectDatabase(self, filename) -> bool:
        '''connect the sqlite3 database and save the handler'''
        logging.debug('>>>MainWindow.openDatabase')
        #input password
        passwd, ok = QInputDialog.getText(self, f'Open a database', f'Input password for the database {filename}', QLineEdit.Password)
        if not ok:
            return False
        logging.debug(f'{passwd=}')
        self.db = cipherdb.CiperDatabase(filename)
        self.treeFolders.setDatabaseHandle(self.db)
        self.textWidget.setDatabaseHandle(self.db)
        if not self.db.openDatabase(filename):
            logging.warning(f'FAILED to open database {filename}')
            self.__showStatusMsg(f'FAILED to open database {filename}', 5000)
            return False
        if not self.db.verifyPasswd(passwd):
            self.__showMessageBox(QMessageBox.Critical, "The password you inputed is incorrect!", "Password incorrect", QMessageBox.Ok)
            return False
        
        #set filename to window title
        basename = os.path.basename(filename)
        self.setWindowTitle(WINDOW_TITLE + ' - ' + basename)
        return True
    def __connectWidgetSignals(self) -> None:
        '''connect event handler of the widgets'''
        self.treeFolders.selectionModel().selectionChanged.connect(self.__folderSelectChange)
        self.textWidget.textChanged.connect(self.__textChange)
    def __folderSelectChange(self) -> None:
        '''event handler when selection of the TreeWidget changed
        refresh the content of the TextEdit when a new folder is selected'''
        logging.debug('>>>MainWindow.text __folderSelectChange')
        if len(self.treeFolders.selectedItems()) == 0:
            logging.debug('No current itm')
            return
        self.__saveText2Database()
        folderid = int(self.treeFolders.selectedItems()[0].text(TreeWidget.COL_FOLDER_ID))
        #read the text from database
        textid, text,dateCreate, dateEdit = self.db.readTextByFolderid(folderid)
        logging.debug(f'text for {folderid=} {dateCreate=} {dateEdit=}')
        
        self.textWidget.setNewPlainText(folderid, textid, text)
        msg = '' if cipherdb.ID_ROOT == textid else f'Created at {dateCreate}     Last edited at {dateEdit}'
        self.__showStatusMsg(msg, 10000)
    def __textChange(self) -> None:
        '''event handler of TextEdit, called when the content of TextEdit is changed, set a flag. 
        the data will be saved to database according to this flag'''
        logging.debug('>>>MainWindow.text changed')
        self.textWidget.setTextChangedFlag(True)

    def __saveText2Database(self) -> None:
        '''save the content of TextEdit to database'''
        if not self.textWidget.getTextChangedFlag():
            logging.debug('no need to save text')
            return
        #logging.debug(f'save text to db with textid {self.textWidget.textid}')
        folderid = self.textWidget.folderid
        if self.textWidget.textid == cipherdb.ID_ROOT:
            logging.debug(f'create a new text with {folderid=}')
            self.db.insertTexts(self.textWidget.toPlainText(), self.textWidget.folderid)
        else:
            
            logging.debug(f'update the text with {folderid=}')
            self.db.updateTextsTextByTextid(self.textWidget.textid, self.textWidget.toPlainText())
            #self.db.updateTextsTextByTextid(self.textWidget.textid, self.textWidget.toPlainText())
        self.textWidget.setTextChangedFlag(False)
if __name__ == '__main__':
    def setDebugData(w):
        treedata = {'Diary':
            {'2021':
                {'2021/01':
                    {'2021/01/01':
                        '''line 11
                        line 12
                        line 13
                        lin3 14''', 
                    '2021/01/02':
                        '''line 21
                        line 22
                        line 23
                        lin3 24'''},
                '2021/02':
                    {'2021/02/05':
                        '''line 51
                        line 52
                        line 53
                        lin3 54''', 
                    '2021/02/06':
                        '''line 61
                        line 62
                        line 63
                        lin3 64'''}},
            '2022':
                {'2022/01':
                    {'2022/01/01':
                        '''line 11
                        line 12
                        line 13
                        lin3 14''', 
                    '2022/01/02':
                        '''line 21
                        line 22
                        line 23
                        lin3 24'''},
                '2022/02':
                    {'2022/02/05':
                        '''line 51
                        line 52
                        line 53
                        lin3 54''', 
                    '2022/02/06':
                        '''line 61
                        line 62
                        line 63
                        lin3 64'''}}}}
        
        def add2tree(parent, treedata):
            for key,value in treedata.items():
                item = QTreeWidgetItem(parent)
                item.setText(0,key)
                if isinstance( value, dict ):
                    add2tree(item, value)
        add2tree(w.treeFolders, treedata)

    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    setDebugData(mainwindow)
    msg = '''
    line 1
    line 2
    line 3
    '''
    mainwindow.textWidget.setPlainText(msg)
    mainwindow.show()
    app.exec()