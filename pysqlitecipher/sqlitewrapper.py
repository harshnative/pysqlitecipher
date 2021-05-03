import sqlite3
from cryptography.fernet import Fernet
import hashlib
import onetimepad

# main class containing all the main methods
class SqliteCipher:

    # constructor for the object
    def __init__(self , dataBasePath="pysqlitecipher.db" , checkSameThread=False , password=None):
        
        # main sqlite3 connection object
        self.sqlObj = sqlite3.connect(dataBasePath , check_same_thread=checkSameThread)

        # password is essential , so it should not be None
        if(password == None):
            raise RuntimeError("password is not passed")

        # storing into object
        self.password = str(password)

        # check if the tableNames table exist in data base if not exist create one and insert it into tableNames table to know that this table exist
        self.sqlObj.execute("CREATE TABLE IF NOT EXISTS tableNames (tableName TEXT , secured INT);")
        self.sqlObj.commit()

        if(self.checkTableExist2("tableNames") == False):
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ('tableNames' , 0);")
            self.sqlObj.commit()

        # check if the authenticationTable exist , if not create table
        if(self.checkTableExist2("authenticationTable") == False):
            self.sqlObj.execute("CREATE TABLE authenticationTable (SHA512_pass TEXT , encryptedKey TEXT);")
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ('authenticationTable' , 0);")
            self.sqlObj.commit()
            
            # converting password to SHA512
            sha512Pass = hashlib.sha512(self.password.encode()).hexdigest()
            
            # converting password to SHA256
            sha256Pass = hashlib.sha512(self.password.encode()).hexdigest()
            
            # getting a random key from fernet
            stringKey = Fernet.generate_key().decode("utf-8")
            
            # encrypting this key
            encryptedKey = onetimepad.encrypt(stringKey , sha256Pass)
            
            
            # adding sha512 password and encrypted key to data base
            self.sqlObj.execute("INSERT INTO authenticationTable (SHA512_pass , encryptedKey) VALUES ({} , {})".format("'" + sha512Pass + "'" , "'" + encryptedKey + "'"))
            self.sqlObj.commit()
        
        else:

            # validate the password passed to password stored in data base
            
            # converting password to SHA512
            sha512Pass = hashlib.sha512(self.password.encode()).hexdigest()
        
            # getting the password from data base
            cursorFromSql = self.sqlObj.execute("SELECT * FROM authenticationTable")
            for i in cursorFromSql:
                sha512PassFromDB = i[0]


            # validating and raising error if not match
            if(sha512PassFromDB != sha512Pass):
                raise RuntimeError("password does not match to password used to create data base")

        
        # getting the encrypted key from db
        cursorFromSql = self.sqlObj.execute("SELECT * FROM authenticationTable")
        for i in cursorFromSql:
            encryptedKey = i[1]

        # generating key to decrypt key
        sha256Pass = hashlib.sha512(self.password.encode()).hexdigest()

        # decrypting key
        decryptedKey = onetimepad.decrypt(encryptedKey , sha256Pass)

        # initialising fernet module
        self.stringKey = decryptedKey
        self.key = bytes(self.stringKey , "utf-8")
        self.cipherSuite = Fernet(self.key)
        




    
    # function to check if a table exist or not
    def checkTableExist(self , tableName):

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in checkTable method")
        else:
            try:
                tableName = str(tableName)
            except ValueError:
                raise ValueError("Table name passed in check table function cannot be converted to string")

        # getting all tablenames in data base
        result = self.sqlObj.execute("SELECT * FROM tableNames")

        exist = False

        tableList = []

        # if the table exist then a list will be returned and for loop we run at least once
        for i in result:
            if(i[1] == 1):
                tableList.append(self.decryptor(i[0]))
            if(i[1] == 0):
                tableList.append(i[0])

        for i in tableList:
            if(i == tableName):
                exist = True
                break

        return exist

    
    # function to check if a table exist or not
    # this method does not match name with secured table
    def checkTableExist2(self , tableName):

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in checkTable method")
        else:
            try:
                tableName = str(tableName)
            except ValueError:
                raise ValueError("Table name passed in check table function cannot be converted to string")

        # getting all tablenames in data base
        result = self.sqlObj.execute("SELECT * FROM tableNames")

        exist = False

        # if the table exist then a list will be returned and for loop we run at least once
        for i in result:
            if(i[1] == 0):
                if(i[0] == tableName):
                    exist = True
                    break

        return exist



    # function to encrypt the passed string
    def encryptor(self , string):
        stringToPass = bytes(string , "utf-8")
        encodedText = self.cipherSuite.encrypt(stringToPass)
        return encodedText.decode("utf-8")

    
    # function to decrypt the passed string
    def decryptor(self , string):
        stringToPass = bytes(string , "utf-8")
        decodedText = self.cipherSuite.decrypt(stringToPass)
        return decodedText.decode("utf-8")



    # function to create a table
    def createTable(self , tableName , colList , makeSecure=False , commit=True):
        
        """
        colList should be like this -
        [
            [colname , datatype] , 
            [colname2 , datatype] , 
        ]

        dataType allowed = TEXT , REAL , INT

        tags for data type
        TEXT - T
        REAL - R
        INT - I
        JSON - J
        LIST - L

        example  = [
            ["rollno" , "INT"],
            ["name" , "TEXT"],
        ]

        if makeSecure is True table name , col list should be encrypted before add to data base
        this time while adding created table to tableNames table make secure = 1 to know that this table as to deal with encryption before performing any operation
        """

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in createTable method")
        else:
            try:
                tableName = str(tableName)
            except ValueError:
                raise ValueError("Table name passed in createTable function cannot be converted to string")

        # collist should not be empty
        if(len(colList) < 1):
            raise ValueError('col list contains no value in createTable method')

        # table should not exist in database already
        if(self.checkTableExist(tableName)):
            raise ValueError("table name already exist in data base")


        # if table has to be secured , encrypt table name
        if(makeSecure):
            tableName = self.encryptor(tableName)
            tableName = "'" + tableName + "'"
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ({} , 1);".format(tableName))
        else:
            tableName = "'" + tableName + "'"
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ({} , 0);".format(tableName))


        # init string to execute in sqlite connector
        stringToExecute = "CREATE TABLE {}".format(tableName) + " ( "


        # traverse col list to add colname and data types to stringToExecute
        for i in colList:
            # i[0] = colname
            # i[1] = datatype

            colname = i[0]

            if(makeSecure):
                colname = self.encryptor(colname)


            # add data type tages to the col names
            if(i[1] == "INT"):
                colname = colname + "_I"

            elif(i[1] == "REAL"):
                colname = colname + "_R"

            elif(i[1] == "JSON"):
                colname = colname + "_J"

            elif(i[1] == "LIST"):
                colname = colname + "_L"

            # TEXT will be default data type
            else:
                colname = colname + "_T"

            # converting colname to 'colname'
            colname = "'" + colname + "'"

            # only TEXT data type is allowed as encryptor only returns string type
            stringToExecute = stringToExecute + colname + " TEXT"
        
            stringToExecute = stringToExecute + " , "

        # remove extra , at the back
        stringToExecute = stringToExecute[:-3] + ");"

        # creating the table using sql connector
        self.sqlObj.execute(stringToExecute)

        if(commit):
            self.sqlObj.commit()

    
    # def insertIntoTable()



# TODO : def to check if table is secured






if __name__ == "__main__":
    obj = SqliteCipher(password="helloboi")

    colList = [
            ["rollno" , "INT"],
            ["name" , "TEXT"],
        ]

    obj.createTable("testTable" , colList , makeSecure=True)


    

