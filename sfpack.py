import subprocess
import sys

def install(package):
    """Runs pip installation on passed package name"""
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def __init__():
    hard_dependencies = ("simple_salesforce", "salesforce_reporting", "pandas")
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
            install('simple_salesforce')
            install('salesforce_reporting')
            install('pandas')
        else:
            raise Exception('sfpack cannot run without required packages {}'.format(missing_dependencies))

__init__()
            
from simple_salesforce import Salesforce
from salesforce_reporting import Connection, ReportParser
from re import sub
import pandas as pd

# Utility functions within sfpack
def addColor(text):
    """Provides blue-color formatting for passed string"""
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    return ('{}{}{}{}{}'.format(BLUE,BOLD,text,END,END))

def expectString(val):
    """Raises standard Exception message if passed value is not a string"""
    if type(val) != str:
        raise Exception('Expected string, received {}'.format(type(val)))

def functions():
    """Displays list of primary sfpack functions"""
    print('sfpack contains the following functions:\n\t-' +
    addColor('checkSalesforceObject') + '\n\t-' +
    addColor('convertTo18') + '\n\t-' +
    addColor('getdf') + '\n\t-' +
    addColor('getreport') + '\n\t-' +
    addColor('getObjectFields') + '\n\t-' +
    addColor('getObjectFieldsDict') + '\n\t-' +
    addColor('isNull') + '\n\t-' +
    addColor('login') + '\n\t-' +
    addColor('repairCasing') + '\ntype \'help(function_name)\' for additional information on each function')
          
          
# -----------------------------------------------------------------------------------------------
# Primary sfpack functions

class login():
    """Initiates Salseforce connection objects sf (simple-salesforce) and sfr (salesforce-reporting)"""
    
    def __init__(self,username,password,orgid,securitytoken='',sandbox=False,include_reports=False):
        self.Username = username
        self.Password = password
        self.OrgId = orgid
        self.SecurityToken = securitytoken
        self.Sandbox = sandbox
        self.IncludeReports = include_reports
        self.Org = self.connectToSalesforceOrg()
    
    def connectToSalesforceOrg(self):
        if self.Sandbox == False:
            sf = Salesforce(password=self.Password, username=self.Username, security_token=self.SecurityToken,organizationId=self.OrgId)
        elif self.Sandbox == True:
            sf = Salesforce(password=self.Password, username=self.Username, organizationId=self.OrgId,security_token=self.SecurityToken,domain='test')
        else:
            raise Exception('Invalid entry for argument \'sandbox\'. Argument must be True, False, or Null')
        if self.IncludeReports:
            sfr = Connection(username=self.Username,password=self.Password,security_token=self.SecurityToken)
        try:
            return {'sf':sf,'sfr':sfr}
        except UnboundLocalError as e:
            return sf
            

# def login(username,password,orgid,securitytoken='',sandbox=False,include_reports=False):
#     """Initiates Salseforce connection objects sf (simple-salesforce) and sfr (salesforce-reporting)"""
#     global sf, sfr
#     if sandbox == False:
#         sf = Salesforce(password=password, username=username, security_token=securitytoken,organizationId=orgid)
#     elif sandbox == True:
#         sf = Salesforce(password=password, username=username, organizationId=orgid,security_token=securitytoken,domain='test')
#     else:
#         raise Exception('Invalid entry for argument \'sandbox\'. Argument must be True, False, or Null')
#     if include_reports:
#         sfr = Connection(username=username,password=password,security_token=securitytoken)
#     
#     return 'Login Successful'

    def getdf(self,val):
        """Accepts string SOQL query, returns Pandas dataframe of the queried data"""
        expectString(val)
        try:
            return pd.DataFrame(list(self.Org.query_all(val)['records'])).drop(columns=['attributes'])
        except (KeyError, NameError) as e:
            if str(e) == '"labels [\'attributes\'] not contained in axis"':
                raise Exception('No data found for query [{}]'.format(val))
            elif str(e) == 'name \'sf\' is not defined':
                raise Exception('The sfpack variable \'sf\' has not been defined. ' +
                                'Please initiate sfpack using {} with your Salesforce login credentials. '.format(colorIt('sfpack.login()','BLUE')) +
                                'Run {} for more details on {}.'.format(colorIt('sfpack.packhelp(\'login\')','BLUE'),colorIt('login()','BLUE')))
            else:
                return e

    def getReport(self,report_id):
        """Accepts string Salesforce Report ID, returns Pandas dataframe of queried data"""
        expectString(report_id)
        try:
            return pd.DataFrame(ReportParser(sfr.get_report(report_id)).records_dict())
        except (KeyError, NameError) as e:
            if str(e) == 'name \'sfr\' is not defined':
                raise Exception('The sfpack variable \'sfr\' has not been defined. ' +
                                'Please initiate sfpack using {} with your Salesforce login credentials. '.format(colorIt('sfpack.login()','BLUE')) +
                                'Run {} for more details on {}.'.format(colorIt('sfpack.packhelp(\'login\')','BLUE'),colorIt('login()','BLUE')))
            else:
                return e

    def updatesf(self,obj='',uptype='',data=''):
        if uptype.lower() not in ['insert','update','delete','hard_delete','upsert']:
            raise Exception('No valid uptype selected. Please choose one of the folowing options: [insert, update, delete, hard_delte, upsert]')
        else:
            return(eval(f'sf.bulk.{obj}.{uptype}(data)'))        

    def convertTo18(self,fifteenId):
        """Converts passed Salesforce 15-digit ID to an 18-digit Id"""
        expectString(fifteenId)
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

    def repairCasing(self,x18DigitId):
        """Changes 18-digit IDs that have had all character's capitalized to a Salesforce viable 18-digit Id"""
        def getBitPatterns(c):
            CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
            index = CHARS.find(c)
            result = []
            for bitNumber in range(0,5):
                result.append((index & (1 << bitNumber)) != 0)
            return result

        expectString(x18DigitId)
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

    def isNull(self,val):
        """Returns boolean value for passed value indicating if it is or is not a Null value. Works for both None and NaN data."""
        if val == None:
            return True
        elif val != val:
            return True
        else:
            return False

    def getObjectFields(self,obj):
        """Returns list of all field names in the passed Salesforce object name"""
        expectString(obj)
        isObject = checkSalesforceObject(obj)['IsObject']
        if isObject == False:
            raise Exception('Invalid Salesforce object name. If this is a custom object, make sure to include \'__c\' to the end of the object name')
        fields = getattr(sf,obj).describe()['fields']
        flist = [i['name'] for i in fields]
        return flist

    def getObjectFieldsDict(self,obj):
        """Returns dictionary of all field labels (keys) and corresponding field names (values) of passed Salesforce object name"""
        expectString(obj)
        fields = getattr(sf,obj).describe()['fields']
        fdict = {}
        for i in fields:
            fdict[i['label']] = i['name']
        return fdict

    def checkSalesforceObject(self,objName):
        """Accepts string argument. Returns dict {'isObject':True/False,'Records':count_of_records_in_object}"""
        expectString(objName)
        try:
            getattr(sf,objName).metadata()
            a = sf.query_all('SELECT count(Id) FROM {}'.format(objName))['records'][0]['expr0']
            return {'IsObject':True,'Records':a}
        except:
            a = sys.exc_info()
            return {'IsObject':not("Resource {} Not Found".format(objName) in str(a[1])),'Records':None}
