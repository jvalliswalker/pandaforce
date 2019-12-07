import subprocess
import sys

def __install(package):
    """Runs pip installation on passed package name"""
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def __init__():
    hard_dependencies = ("simple_salesforce", "salesforce_reporting", "pandas","requests")
    missing_dependencies = []

    for dependency in hard_dependencies:
        try:
            __import__(dependency)
        except ImportError as e:
            print(dependency,'failed')
            missing_dependencies.append(dependency)

    if len(missing_dependencies) > 0:
        print("Missing required packages {}".format(missing_dependencies))
        response = input('Would you like to install these packages? y/n')
        if response == 'y':
            __install('simple_salesforce')
            __install('salesforce_reporting')
            __install('pandas')
        else:
            raise Exception('sfpack cannot run without required packages {}'.format(missing_dependencies))

__init__()
            
from simple_salesforce import Salesforce
from salesforce_reporting import Connection, ReportParser
from re import sub
import pandas as pd
import requests

# Utility functions within sfpack
def __addColor(text):
    """Provides blue color and bold formatting for passed string"""
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    return ('{}{}{}{}{}'.format(BLUE,BOLD,text,END,END))

def __expectString(val):
    """Raises standard Exception message if passed value is not a string"""
    if type(val) != str:
        raise Exception('Expected string, received {}'.format(type(val)))
        
def info():
    """Displays list of primary sfpack functions"""
    print('sfpack contains the following functions:\n' +
        '  - {}:\t{}\n'.format(__addColor('convertTo18'),convertTo18.__doc__) + 
        '  - {}:\t\t{}\n'.format(__addColor('isNull'),isNull.__doc__) +
        '  - {}:\t{}'.format(__addColor('repairCasing'),repairCasing.__doc__))
    print('\nIt also contains a '+ __addColor('login') +
        ' class which initiates a connection to a Salesforce org. It contains the following methods:\n' +
        '  - {}:\t\t{}\n'.format(__addColor('getdf'),login.getdf.__doc__) + 
        '  - {}:\t\t{}\n'.format(__addColor('getFields'),login.getFields.__doc__) +
        '  - {}:\t\t{}\n'.format(__addColor('getReport'),login.getReport.__doc__) +
        '  - {}:\t\t{}\n'.format(__addColor('isObject'),login.isObject.__doc__) + 
        '  - {}:\t{}'.format(__addColor('recordCount'),login.recordCount.__doc__))
 
    print('\nType \'help(function_name)\' or \'help(login.method_name)\' for additional information on each function or method')

def convertTo18(fifteenId):
    """Converts the passed Salesforce 15-digit ID to an 18-digit Id"""
    __expectString(fifteenId)
    if len(fifteenId) != 15:
        raise Exception('Expected 15 character string, received {} character string'.format(len(fifteenId)))
    elif len(sub('[a-zA-z0-9]','',fifteenId)) > 0:
        raise Exception('Passed string cannot contain any special characters (i.e. "!","@","#")')
    suffix = ''
    for i in range(0, 3):
        flags = 0
        for x in range(0,5):
            c = fifteenId[i*5+x]
            #add flag if c is uppercase
            if c.upper() == c and c >= 'A' and c <= 'Z':
                flags = flags + (1 << x)
        if flags <= 25:
            suffix = suffix + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[flags]
        else:
            suffix = suffix + '012345'[flags - 26]
    return fifteenId + suffix

def repairCasing(x18DigitId):
    """Changes 18-digit IDs that have had all character's capitalized to a Salesforce viable 18-digit Id"""
    def getBitPatterns(c):
        CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
        index = CHARS.find(c)
        result = []
        for bitNumber in range(0,5):
            result.append((index & (1 << bitNumber)) != 0)
        return result

    __expectString(x18DigitId)
    if len(x18DigitId) != 18:
        raise Exception('Expected 18 character string, received {} character string'.format(len(x18DigitId)))
    elif len(sub('[a-zA-z0-9]','',x18DigitId)) > 0:
        raise Exception('Passed string cannot contain any special characters (i.e. "!","@","#")')

    toUpper = []
    toUpper.append(getBitPatterns(x18DigitId[15:16]))
    toUpper.append(getBitPatterns(x18DigitId[16:17]))
    toUpper.append(getBitPatterns(x18DigitId[17:18]))
    toUpper = [item for sublist in toUpper for item in sublist]

    output = ''.join([x18DigitId[x].upper() if toUpper[x] else x18DigitId[x].lower() for x in range(0,15)]) + x18DigitId[15:].upper()

    return output

def isNull(val):
    """Returns boolean value for passed value indicating if it is a Null or NaN value"""
    if val == None:
        return True
    elif val != val:
        return True
    else:
        return False
        
        
# -----------------------------------------------------------------------------------------------
# Primary sfpack functions

class login:
    """Initiates Salseforce connection and is used for subsequent access methods"""
    
    def __init__(self,username,password,orgid,securitytoken='',sandbox=False):
        self.Username = username
        self.Password = password
        self.OrgId = orgid
        self.SecurityToken = securitytoken
        if sandbox==True:
            self.Sandbox = 'test'
        else:
            self.Sandbox = 'login'
        self.Org = Salesforce(username=self.Username, password=self.Password,
                              security_token=self.SecurityToken,organizationId=self.OrgId,
                             domain=self.Sandbox)

    def __expectString(self,val,argName=None):
        """Raises standard Exception message if passed value is not a string"""
        if argName == None:            
            if type(val) != str:
                raise Exception('Expected string, received {}'.format(type(val)))
        elif type(argName) != str:
            raise Exception('Expected string for argument \'argName\', received {}'.format(type(val)))
        else:
            if type(val) != str:
                raise Exception('Expected string for argument \'{}\', received {}'.format(argName,type(val)))
        
    def getdf(self,query):
        """Returns pandas dataframe from passed SOQL query"""
        self.__expectString(query)
        try:
            return pd.DataFrame(list(self.Org.query_all(query)['records'])).drop(columns=['attributes'])
        except (KeyError, NameError) as e:
            if str(e) == '"labels [\'attributes\'] not contained in axis"':
                raise Exception('No data found for query [{}]'.format(query))
            else:
                return e
            
    def getReport(self,reportId):
        """Returns pandas dataframe from passed Salesforce report Id (15 or 18 digit)"""
        self.__expectString(reportId)
        if len(reportId) != 15 and len(reportId) != 18:
            raise Exception('Expected 15 character or 18 character string, received {} character string'.format(len(reportId)))
        elif len(sub('[a-zA-z0-9]','',reportId)) > 0:
            raise Exception('Passed string cannot contain any special characters (i.e. "!","@","#")')
        with requests.session() as s:
            response = s.get("https://{}/{}?export".format(self.Org.sf_instance,reportId), headers=self.Org.headers, cookies={'sid': self.Org.session_id})
        
        def parseReponse(responseObject):
            # Separate trailing report data from regular data
            # then split remaining data by '\n'
            bigList = responseObject.text.split('\n\n\n')[0].split('\n')

            # Pull headers from first split group
            headers = bigList[0].split(',')

            #Crop off extra ""
            for i in range(0,len(headers)):
                headers[i] = headers[i][1:-1]

            # Initialize dictionary
            bigDict = {}
            for i in headers:
                bigDict[i] = []

            indexKeyMatcher = {}
            for i in range(0,len(headers)):
                indexKeyMatcher[i] = headers[i]

            # Separate header data from bigList
            bigList = bigList[1:]

            # Comma separate each sub-list
            # and add to dictionary
            for i in range(0,len(bigList)):
                data = bigList[i].split('",')
                #Crop off extra ""
                for subIndex in range(0,len(data)):
                    if subIndex == len(data)-1:
                        data[subIndex] = data[subIndex][1:-1]
                    else:
                        data[subIndex] = data[subIndex][1:]
                for col in range(0,len(data)):
                    bigDict[indexKeyMatcher[col]].append(data[col])
        #         bigDict[i] = data
            return bigDict
        
        return pd.DataFrame(parseReponse(response))

    def dml(self,obj='',uptype='',data=None):
        """Runs the specified bulk CRUD command with the passed data"""
        self.__expectString(obj,'obj')
        if self.isObject(obj) == False:
            raise Exception('\'{}\' is not a Salesforce object in this org'.format(obj))
        self.__expectString(uptype,'uptype')
        if uptype not in ['insert','update','delete','hard_delete','upsert']:
            raise Exception('No valid uptype selected. Please choose one of the folowing options: [insert, update, delete, hard_delete, upsert]')
        if type(data) != list:
            raise Exception('Expected list for argument \'data\', received {}'.format(type(data)))
        uptype = uptype.lower()
        return(eval(f'self.Org.bulk.{obj}.{uptype}(data)'))    

    def getFields(self,obj,returnDict=False):
        """Returns list or dictionary of all field names in the passed Salesforce object name."""
        self.__expectString(obj)
        if self.isObject(obj) == False:
            raise Exception('Invalid Salesforce object name. If this is a custom object, make sure to append \'__c\' to the end of the object name')
        fields = getattr(self.Org,obj).describe()['fields']
        if returnDict:
            fdict = {}
            for i in fields:
                fdict[i['label']] = i['name']
            return fdict
        else:
            flist = [i['name'] for i in fields]
            return flist

    def isObject(self,obj):
        """Accepts string argument as api name of object. Returns boolean"""
        self.__expectString(obj)
        try:
            eval('self.Org.{}.metadata()'.format(obj))['objectDescribe']['label']
            return True
        except:
            a = sys.exc_info()
            return False
        
    def recordCount(self,obj):
        """Accepts string argument. Returns integer count_of_records_in_object"""
        self.__expectString(obj)
        try:
            eval('self.Org.{}.metadata()'.format(obj))['objectDescribe']['label']
            try:
                return self.getdf('SELECT count(Id) FROM {}'.format(obj)).at[0,'expr0']
            except:
                return sf.Org.query_all('SELECT ID FROM {}'.format(obj))['totalSize']
        except:
            a = sys.exc_info()
            return {'IsObject':False,'Records':None}
