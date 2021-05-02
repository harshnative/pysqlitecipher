import sqlite3
from cryptography.fernet import Fernet


# main class containing all the main methods
class SqliteCipher:

    # constructor for the object
    def __init__(self , dataBasePath="pysqlitecipher.db" , checkSameThread=False , password=None):
        
        # main sqlite3 connection object
        self.sqlObj = sqlite3.connect(dataBasePath , check_same_thread=checkSameThread)

        # storing into object
        self.password = password

        if(password != None):
            self.passwordTableExist = self.checkTableExist("authenticationTable")

            if(self.passwordTableExist == False):
                pass    
        


    
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

        # checking if table name exist or not
        result = self.sqlObj.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(tablename))

        exist = False

        # if the table exist then a list will be returned and for loop we run at least once
        for i in result:
            exist = True

        return exist



    def createTable(self , tableName , colList , makeSecure=False):
        
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

        example  = [
            ["rollno" , "INT"],
            ["name" , "TEXT"],
        ]
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

        # if check table initiales with SECURED
        if(tableName[:7] == "SECURED"):
            raise ValueError("tableName should not start with SECURED")

        # if the table needs to be encrypted then add a SECURED tag to table name
        if(makeSecure):
            tableName = "SECURED_" + tableName


        # init string to execute in sqlite connector
        stringToExecute = "CREATE TABLE {}".format(tableName) + " ( "


        # traverse col list to add colname and data types to stringToExecute
        for i in colList:
            # i[0] = colname
            # i[1] = datatype

            colname = i[0]


            # add data type tages to the col names
            if(i[1] == "INT"):
                colname = colname + "_I"

            elif(i[1] == "REAL"):
                colname = colname + "_R"

            else:
                colname = colname + "_T"


            # only TEXT data type is allowed as encryptor only returns string type
            stringToExecute = stringToExecute + colname + " TEXT"
        
            stringToExecute = stringToExecute + " , "

        
        stringToExecute = stringToExecute[:-3] + ");"

        print(stringToExecute)










if __name__ == "__main__":
    obj = SqliteCipher()

    colList = [
            ["rollno" , "INT"],
            ["name" , "TEXT"],
        ]

    obj.createTable("testTable" , colList , makeSecure=True)

    

