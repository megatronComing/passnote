# -*- encoding: utf-8 -*-
'''
database manipalation
Author: Jared Yu
Contect: hfyu.hzcn@gmail.com
Version: 1.0
Update: 2023-2-20
Requires: PyQt5
'''
import os
import datetime
import sqlite3
import uuid
import encryption as ECP
import logging
import operator as OPT
DB_VERSION = '1.0'

TBL_FOLDERS = 'folders' #table name
#field names for table TBL_FOLDERS
TBL_FOLDERS_F_ID = 'folderid'
TBL_FOLDERS_F_NAME = 'name'
TBL_FOLDERS_F_PARENTID = 'parentid'

TBL_TEXT = 'texts' #table texts

#field names for table TBL_TEXT
TBL_TEXT_F_ID = 'textid'
TBL_TEXT_F_VALUE = 'textval'
TBL_TEXT_F_FOLDERID = 'folderid'
TBL_TEXT_F_DATE_C = 'dateCreate'
TBL_TEXT_F_DATE_E = 'dateLastEdit'

ID_ROOT = 0

TBL_SYS = 'sysinfo' #table which holds system info
#field names for table TBL_SYS
TBL_SYS_F_ID = 'itemindex'
TBL_SYS_F_ITEMVALUE = 'itemvalue'
TBL_SYS_V_IDX_VER = 1
TBL_SYS_V_IDX_SAMPLE = 2

DEFAULT_PASSWD = 'HiJared@2022' #default password used to encrypt the database
SAMPLE_TEXT = 'PasswordNotebookByJared@202212'

def getUniqueId() -> int:
    '''create a unique id for database records'''
    return int((''.join([x[:4] for x in str(uuid.uuid4()).split('-')])[:10]),16)

class CiperDatabase():
    '''a sqlite3 based database, with the main content encryped by AES'''
    def __init__(self, strFileName:str):
        self.passwdVerified = False #when a password is validated, set to True
        self.aes = None #encryption handle
        self.dbConn = None
        
    def __del__(self):
        '''destructor'''
        if self.dbConn:
            self.dbConn.commit()
            self.dbConn.close()
        

    def openDatabase(self, filename) -> bool:
        '''connect a database'''
        try:
            #when a new instance is implemented, all tables will be created if not exist
            self.dbConn = sqlite3.connect(filename)
            
        except:
            logging.debug(f'ERROR connecting database {filename}')
            return False
        
        return True
    def createDatabase(self, filename, passwd) -> bool:
        '''create a new database
        return True if successful, otherwise False'''
        if None != self.dbConn:
            self.dbConn.close()
            self.dbConn = None
        try:
            #when a new instance is implemented, all tables will be created if not exist
            self.dbConn = sqlite3.connect(filename)
            sqlCreateTableFolders = f""" CREATE TABLE IF NOT EXISTS {TBL_FOLDERS} (
                                        {TBL_FOLDERS_F_ID} integer PRIMARY KEY,
                                        {TBL_FOLDERS_F_NAME} text NOT NULL,
                                        {TBL_FOLDERS_F_PARENTID} integer NOT NULL
                                    ); """
            sqlCreateTableTexts = f""" CREATE TABLE IF NOT EXISTS {TBL_TEXT} (
                                        {TBL_TEXT_F_ID} integer PRIMARY KEY,
                                        {TBL_TEXT_F_VALUE} text NOT NULL,
                                        {TBL_TEXT_F_FOLDERID} integer NOT NULL,
                                        {TBL_TEXT_F_DATE_C} text,
                                        {TBL_TEXT_F_DATE_E} text
                                    ); """
            sqlCreateTableSys = f""" CREATE TABLE IF NOT EXISTS {TBL_SYS} (
                                        {TBL_SYS_F_ID} integer PRIMARY KEY,
                                        {TBL_SYS_F_ITEMVALUE} text NOT NULL
                                    ); """
            #insert sample text record if not exists
            self.aes = ECP.AESCipher(passwd)
            sqlCreateSampleText = f"""INSERT INTO {TBL_SYS} ( {TBL_SYS_F_ID}, {TBL_SYS_F_ITEMVALUE} ) 
                                SELECT {TBL_SYS_V_IDX_SAMPLE}, \"{self.aes.encrypt(SAMPLE_TEXT)}\"
                                WHERE NOT EXISTS (SELECT * FROM {TBL_SYS} WHERE {TBL_SYS_F_ID}={TBL_SYS_V_IDX_SAMPLE});"""
            print(sqlCreateSampleText)
            sqlCreateVersion = f"""INSERT INTO {TBL_SYS} ( {TBL_SYS_F_ID}, {TBL_SYS_F_ITEMVALUE} ) 
                                SELECT {TBL_SYS_V_IDX_VER}, \"{DB_VERSION}\"
                                WHERE NOT EXISTS (SELECT * FROM {TBL_SYS} WHERE {TBL_SYS_F_ID}={TBL_SYS_V_IDX_VER});"""
            for sql in [sqlCreateTableFolders, sqlCreateTableTexts, sqlCreateTableSys, sqlCreateSampleText, sqlCreateVersion]:
                self.__executeSqlWithoutReturn(sql)
        except Error as e:
            logging.critical(e)
            return False
        
        return True
    def verifyPasswd(self, passwd:str) -> bool:
        '''verity password
        return True if password is correct, otherwise False
        By decrypting the sample text to determine weather the password is correct'''
        #set user inputed password for decrypting, verify it
        #return True if the password is correct, otherwise return False
        
        data = self.__executeSqlWithFetchall(f'SELECT {TBL_SYS_F_ITEMVALUE} FROM {TBL_SYS} WHERE {TBL_SYS_F_ID}={TBL_SYS_V_IDX_SAMPLE}')
        if len(data) != 1:
            logging.critical('SYSTEM PANIC: password table wrong')
            return False
        sampleTextEncrypted = str(data[0][0])
        try:
            aes = ECP.AESCipher(passwd)
            if aes.decrypt(sampleTextEncrypted) != SAMPLE_TEXT:
                return False
            self.passwdVerified = True
            self.aes = aes
            return True
        except:
            logging.critical(f'ERROR decrypting sample text, cipher text = {sampleTextEncrypted}')
            return False
        
    def __executeSqlWithoutReturn(self, sql:str) -> None:
        '''execute a sql which insert new data or update a record in a table, commit() will be called after the execution of the sql'''
        cursor = self.dbConn.cursor()
        cursor.execute(sql)
        self.dbConn.commit()
    def __executeSqlWithFetchall(self, sql:str) -> list:
        '''execute a sql which reads data from database, return the result by fetchall()'''
        cursor = self.dbConn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    def insertFolders(self, foldername:str, parentid:int) -> int:
        '''insert a new record into the table folders, return the unique folderid'''
        if not self.aes:
            return
        folderid = getUniqueId()
        foldername = self.aes.encrypt(foldername)
        sql = f"INSERT INTO {TBL_FOLDERS} ({TBL_FOLDERS_F_ID}, {TBL_FOLDERS_F_NAME}, {TBL_FOLDERS_F_PARENTID}) VALUES ({folderid}, \"{foldername}\", {parentid});"
        self.__executeSqlWithoutReturn( sql )
        return folderid
    def readTableFolders(self, parentId:int=ID_ROOT) -> list:
        '''read records from table folders whose parentid is given by parameter parentId'''
        records = self.__executeSqlWithFetchall( f"SELECT {TBL_FOLDERS_F_ID},{TBL_FOLDERS_F_NAME},{TBL_FOLDERS_F_PARENTID} FROM {TBL_FOLDERS} WHERE {TBL_FOLDERS_F_PARENTID}={parentId}" )
        ret = []
        for record in records:
            ret.append([record[0], self.aes.decrypt(str(record[1])), record[2]])
        logging.debug(f'{len(ret)} records read from table {TBL_FOLDERS_F_ID}.')
        #return sorted(ret, key=OPT.itemgetter(1))
        ret.sort(key = lambda x:x[1])   #sort the records by foldername in ascending order
        return ret
    
    def readTextByFolderid(self, folderid:int) -> list:
        '''query table texts, read records whose folderid is given by the parameter folderid'''
        records = self.__executeSqlWithFetchall( f"SELECT {TBL_TEXT_F_ID},{TBL_TEXT_F_VALUE},{TBL_TEXT_F_DATE_C},{TBL_TEXT_F_DATE_E} FROM {TBL_TEXT} WHERE {TBL_TEXT_F_FOLDERID}={folderid}" )
        if len(records) > 1:
            logging.critical(f'ERROR: {len(records)} records of text found for folderid {folderid}')
            return ID_ROOT, '', '', ''
        elif len(records) != 1:
            return ID_ROOT, '', '', ''
        return (records[0][0], self.aes.decrypt(str(records[0][1])), records[0][2], records[0][3])
        
    def insertTexts(self, textname:str, folderid:int) -> int:
        '''insert a new record into the table texts, return the unique textid'''
        if not self.aes:
            return
        textid = getUniqueId()
        nowstr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        textname = self.aes.encrypt(textname)
        sql = f"""INSERT INTO {TBL_TEXT} ({TBL_TEXT_F_ID},{TBL_TEXT_F_VALUE},{TBL_TEXT_F_FOLDERID},{TBL_TEXT_F_DATE_C},{TBL_TEXT_F_DATE_E})
            VALUES ({textid},\"{textname}\",{folderid},\"{nowstr}\",\"{nowstr}\"); """
        self.__executeSqlWithoutReturn( sql )
        return textid
    def updateTextsTextByTextid(self, textid:int, text:str) -> None:
        '''update the text of a record of table texts by textid'''
        encText = self.aes.encrypt(text)
        nowstr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = f'UPDATE {TBL_TEXT} SET {TBL_TEXT_F_VALUE}=\"{encText}\",{TBL_TEXT_F_DATE_E}=\"{nowstr}\"  WHERE {TBL_TEXT_F_ID}={textid}'
        self.__executeSqlWithoutReturn( sql )
        
    def updateTableFoldersParentidByFolderid(self, folderid:int, parentid:int) -> None:
        '''update the parentid of a record of table folders by folderid'''
        self.__executeSqlWithoutReturn( f"UPDATE {TBL_FOLDERS} SET {TBL_FOLDERS_F_PARENTID}={parentid} WHERE {TBL_FOLDERS_F_ID}={folderid}")
        
    def updateTableFoldersFoldernameByFolderid(self, folderid:int, foldername:str) -> None:
        '''update the foldername of a record of table folders by folderid'''
        if not self.aes:
            return
        foldername = self.aes.encrypt(foldername)
        self.__executeSqlWithoutReturn(f"UPDATE {TBL_FOLDERS} SET {TBL_FOLDERS_F_NAME}=\"{foldername}\" WHERE {TBL_FOLDERS_F_ID}={folderid}")
        
    def updateTableFoldersDeleteFolder(self, folderid:int) -> None:
        '''remove a record from the folders table'''
        self.__executeSqlWithoutReturn( f"DELETE FROM {TBL_FOLDERS} WHERE {TBL_FOLDERS_F_ID}={folderid}" )
        self.__executeSqlWithoutReturn( f"DELETE FROM {TBL_TEXT} WHERE {TBL_TEXT_F_FOLDERID}={folderid}" )
            
    
    def changePasswd(self, newPasswd:str) -> bool:
        """
        when a new password is set, read all the data, decrypt it with the old password, 
        encrypt it with new password and update the database
        return True if successful
        """
        newAes = ECP.AESCipher(newPasswd)
        #re-encrypt table folders
        records = self.__executeSqlWithFetchall( f"SELECT {TBL_FOLDERS_F_ID},{TBL_FOLDERS_F_NAME} FROM {TBL_FOLDERS}" )
        for record in records:
            folderid = record[0]
            foldername = self.aes.decrypt(str(record[1]))
            sql = f"UPDATE {TBL_FOLDERS} SET {TBL_FOLDERS_F_NAME}=\"{newAes.encrypt(foldername)}\" WHERE {TBL_FOLDERS_F_ID}={folderid}"
            cursor = self.dbConn.cursor()
            cursor.execute(sql)
        
        #re-encrypt table texts
        records = self.__executeSqlWithFetchall( f"SELECT {TBL_TEXT_F_ID},{TBL_TEXT_F_VALUE} FROM {TBL_TEXT}" )
        for record in records:
            textid = record[0]
            text =self.aes.decrypt(str(record[1])) 
            sql = f"UPDATE {TBL_TEXT} SET {TBL_TEXT_F_VALUE}=\"{newAes.encrypt(text)}\" WHERE {TBL_TEXT_F_ID}={textid}"
            cursor = self.dbConn.cursor()
            cursor.execute(sql)

        #re-encrypt sample text
        sql = f"UPDATE {TBL_SYS} SET {TBL_SYS_F_ITEMVALUE}=\"{newAes.encrypt(SAMPLE_TEXT)}\" WHERE {TBL_SYS_F_ID}={TBL_SYS_V_IDX_SAMPLE}"
        cursor = self.dbConn.cursor()
        cursor.execute(sql)

        #commit the modification
        try:
            self.dbConn.commit()
            self.aes = newAes
            return True
        except:
            return False


def debugInsertData():
    '''insert some data into database for debuging'''
    filename = 'passnote.db'
    db = CiperDatabase(filename)
    
    db.createDatabase(filename, DEFAULT_PASSWD)
    conn = db.dbConn
    debugData = {}
    aes = ECP.AESCipher(DEFAULT_PASSWD)
    ids = [getUniqueId() for i in range(0,100)]
    folders = [[ids[0], 'Websites', 0], 
        [ids[1], 'Music', ids[0]], 
        [ids[2], 'Movies', ids[0]], 
        [ids[3], 'R&D', ids[0]],
        [ids[4], 'Cuisine', ids[0]],
        [ids[5], 'Finance', 0],
        [ids[6], 'Banks', ids[5]],
        [ids[7], 'Stocks', ids[5]],
        [ids[8], 'Reading', 0],
        [ids[9], 'Chinese cuisine', ids[4]],
        [ids[10], 'Canadien cuisine', ids[4]],
        [ids[11], 'C language', ids[3]],
        [ids[12], 'python', ids[3]],
        [ids[13], 'javascript', ids[3]],
        [ids[14], 'Social', 0]]
    for folder in folders:
        folderid = folder[0]
        foldername = aes.encrypt(folder[1])
        parentid = folder[2]
        sql = f"INSERT INTO folders (folderid, name, parentid) VALUES ({folderid}, \"{foldername}\", {parentid});"
        conn.cursor().execute(sql)
    
    texts = [ids[12], '''A list comprehension returns a list while a generator expression returns a generator object.
It means that a list comprehension returns a complete list of elements upfront. However, a generator expression returns a list of elements, one at a time, based on request.

A list comprehension is eager while a generator expression is lazy.

In other words, a list comprehension creates all elements right away and loads all of them into the memory.''']
    textid = ids[30]
    textname = aes.encrypt(texts[1])
    folderid = ids[12]
    sql = f'INSERT INTO {TBL_TEXT} ({TBL_TEXT_F_ID},{TBL_TEXT_F_VALUE},{TBL_TEXT_F_FOLDERID}) VALUES ({textid},\"{textname}\",{folderid}); '
    #print(sql)
    conn.cursor().execute(sql)
    conn.commit()


if __name__ == '__main__':
    #db = CiperDatabase('passnote.db')
    debugInsertData()

    # for i in range(0,20):
    #     db.insertFolder({'name':f'folder{i}','parentid':0})
    #print(getUniqueId())
    #debugReadFolders(db)
