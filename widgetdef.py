# -*- encoding: utf-8 -*-
'''
customized tree widget and text edit widget definition
Author: Jared Yu
Contect: hfyu.hzcn@gmail.com
Version: 1.0
Update: 2023-2-22
Requires: PyQt5
'''
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTextEdit, QAction, QMenu, QAbstractItemView, QInputDialog, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDrag
import cipherdb
import logging

class TextEdit(QTextEdit):
    '''customized text edit widget
    save textid and folderid of the content'''
    def __init__(self, parent:QWidget=None):
        super(TextEdit, self).__init__(parent=parent)
        self.folderid = cipherdb.ID_ROOT
        self.textid = cipherdb.ID_ROOT
        self.ifTextChanged = False
        self.db = None
    def setDatabaseHandle(self, db) -> None:
        '''for the main window to pass the database handler'''
        self.db = db
    def setNewPlainText(self, folderid:int, textid:int, text:str) -> None:
        '''set new content with textid and folderid'''
        self.folderid, self.textid = folderid, textid
        self.setPlainText(text)
        self.ifTextChanged = False
    def setTextChangedFlag(self, bChanged) -> None:
        '''set a flag when the content is changed
        There supposed to be a better solution, to be optimized'''
        self.ifTextChanged = bChanged
    def getTextChangedFlag(self) -> bool:
        '''get the flag of if-changed of the content'''
        return self.ifTextChanged

class TreeWidget(QTreeWidget):
    '''This class is for categories, internal drag and drop supported.'''
    #define column of the folders TreeWidgetFolders
    COL_FOLDER_ID = 1
    COL_FOLDER_NAME = 0
    COL_FOLDER_PARENTID = 2
    def __init__(self, parent:QWidget=None):
        super(TreeWidget, self).__init__(parent=parent)
        self.db = None
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__openConextMenuForTree)
        self.setActiveStatus(False) #if true, ppup menu is enabled
    def setDatabaseHandle(self, db) -> None:
        '''for the main window to pass the database handler'''
        self.db = db
    def setActiveStatus(self, status:bool) -> None:
        '''set a flag which indicate weather self is active.
        if inactive, the context menu will not be showed when a right clicked issued'''
        self.status = status
    def getActiveStatus(self) -> bool:
        '''get the active status of self'''
        return self.status
    def __openConextMenuForTree(self, position) -> None:
        '''event handler for opening the context menu
        position: passed from Qt'''
        logging.debug('>>>TreeWidget.__openConextMenuForTree')
        item = self.itemAt(position)
        
        #if data loaded, enable the popup menu, otherwise, disable it
        if not self.getActiveStatus():
            logging.debug('context menu disabled')
            return
        logging.debug('context menu enabled')
        self.rightClickAtItem = self.itemAt(position)
        
        menu = QMenu()
        menuNew = QAction(self.tr('New'), self)
        menuNew.triggered.connect(lambda :self.__menuNewCategoryClick(item))
        menu.addAction(menuNew)

        #if right clicked on the blank area, no need to show menu "rename" and "delete"
        if item != None:
            menuEdit = QAction(self.tr('Rename'), self)
            menuEdit.triggered.connect(lambda: self.__menuRenameCategoryClick(item))
            menu.addAction(menuEdit)
            menuDelete = QAction(self.tr('Delete'), self)
            menuDelete.triggered.connect(lambda: self.__menuDelCategoryClick(item))
            menu.addAction(menuDelete)
        menu.exec_(self.viewport().mapToGlobal(position))

    def __menuNewCategoryClick(self, item:QTreeWidgetItem) -> None:
        '''handler of context menu command New Category'''
        logging.debug('>>>TreeWidget.__menuNewCategoryClick')
        if item == None:
            logging.debug('create a new root item')
        else:
            logging.debug(f'create a new folder with parentid = {item.text(TreeWidget.COL_FOLDER_PARENTID)}, parentname={item.text(TreeWidget.COL_FOLDER_NAME)}')
        foldername, ok = QInputDialog.getText(self, 'New category', 'Input a new category')
        if not ok:
            return False
        
        parentid = cipherdb.ID_ROOT if item == None else item.text(TreeWidget.COL_FOLDER_ID)
        
        folderid = self.db.insertFolders(foldername, parentid)
        self.selectionModel().clear()
        itemNew = QTreeWidgetItem(self.invisibleRootItem() if item==None else item)
        itemNew.setText(TreeWidget.COL_FOLDER_ID, str(folderid))
        itemNew.setText(TreeWidget.COL_FOLDER_NAME, foldername)
        itemNew.setText(TreeWidget.COL_FOLDER_PARENTID, str(parentid))
        itemNew.setSelected(True)

    def __menuRenameCategoryClick(self, item:QTreeWidgetItem) -> None:
        '''handler of context menu command Rename Category'''
        logging.debug('>>>TreeWidget.__menuRenameCategoryClick')
        if item == None:
            return
        foldername, ok = QInputDialog.getText(self, 'Rename the category', 'Please input a new category name')
        if not ok:
            return False
        folderid = item.text(TreeWidget.COL_FOLDER_ID)
        self.db.updateTableFoldersFoldernameByFolderid(folderid, foldername)
        item.setText(TreeWidget.COL_FOLDER_NAME, foldername)

    def __menuDelCategoryClick(self, item:QTreeWidgetItem) -> None:
        '''handler of context menu command Delete Category'''
        logging.debug('>>>TreeWidget.__menuDelCategoryClick')
        if item == None:
            return
        folderid = item.text(TreeWidget.COL_FOLDER_ID)
        self.db.updateTableFoldersDeleteFolder(folderid) #delete the record from the table
        root = self.invisibleRootItem() #delete the item from the tree widget
        ( item.parent() or root ).removeChild(item)

    def startDrag(self, supportedActions) -> None:
        '''event handler, called when a drag-and-drop starts, overwriting the handler of the parent class'''
        logging.debug('>>>TreeWidget.startDrag')
        self.dragedItem = self.currentItem()
        super().startDrag(supportedActions)
        # drag = QDrag(self)
        # drag.exec_(supportedActions)
    def dropEvent(self, event) -> None:
        '''event handler, called when a drag-and-drop ends, overwriting the handler of the parent class'''
        logging.debug('>>>TreeWidget.dropEvent')
        if event.source() != self:
            event.ignore()
        else:
            destItem = self.itemAt(event.pos())
            parentid = cipherdb.ID_ROOT if destItem == None else destItem.text(TreeWidget.COL_FOLDER_ID)
            event.setDropAction(Qt.MoveAction)
            QTreeWidget.dropEvent(self, event)
            #update the parentid of the draged item
            self.dragedItem.setText(TreeWidget.COL_FOLDER_PARENTID, str(parentid))
            #save to database
            folderid = self.dragedItem.text(TreeWidget.COL_FOLDER_ID)
            self.db.updateTableFoldersParentidByFolderid(folderid, parentid)
    