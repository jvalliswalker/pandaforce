import subprocess
import sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])
    
install('simple_salesforce')
install('salesforce_reporting')
install('pandas')

from simple_salesforce import Salesforce
from salesforce_reporting import Connection, ReportParser
import pandas as pd
import webbrowser

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# -----------------------------------------------------------------------------------------------

def init(username,password,orgid,securitytoken='',sandbox=False):
    global sf, sfr
    if sandbox == False:
        sf = Salesforce(password=password, username=username, organizationId=orgid)
    elif sandbox == True:
        sf = Salesforce(password=password, username=username, organizationId=orgid,domain='test')
    else:
        raise Exception('Invalid entry for argument \'sandbox\'. The \'sandbox\' argument can be {} (to access a Salesforce sandbox) or {} (the default value)'.format(colorIt('True','GREEN'),colorIt('False','GREEN')))
    sfr = Connection(username=username,password=password,security_token=securitytoken)
    return 'Initiation Successful'
    
def colorIt(text,colorType):
    col = ''
    if colorType.lower() == 'purple':
        return '{}{}{}{}{}'.format(color.PURPLE,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'cyan':
        return '{}{}{}{}{}'.format(color.CYAN,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'darkcyan':
        return '{}{}{}{}{}'.format(color.DARKCYAN,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'blue':
        return '{}{}{}{}{}'.format(color.BLUE,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'green':
        return '{}{}{}{}{}'.format(color.GREEN,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'yellow':
        return '{}{}{}{}{}'.format(color.YELLOW,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'red':
        return '{}{}{}{}{}'.format(color.red,color.BOLD,text,color.END,color.END)
    elif colorType.lower() == 'underline':
        return '{}{}{}{}{}'.format(color.UNDERLINE,color.BOLD,text,color.END,color.END)
    else:
        raise Exception('Please enter a valid color (purple, cyan, darkcyan, blue, green, yellow, red, or underline)')

        
def getdf(val):
    try:
        return pd.DataFrame(list(sf.query_all(val)['records'])).drop(columns=['attributes'])
    except (KeyError, NameError) as e:
        if str(e) == '"labels [\'attributes\'] not contained in axis"':
            print('No data found for query\n----------------------\n[{}]\n----------------------\nNull value returned'.format(val))
            return None
        elif str(e) == 'name \'sf\' is not defined':
            raise Exception('The sfpack variable \'sf\' has not been defined. ' +
                            'Please initiate sfpack using {} with your Salesforce login credentials. '.format(colorIt('sfpack.init()','BLUE')) +
                            'Run {} for more details on {}.'.format(colorIt('sfpack.packhelp(\'init\')','BLUE'),colorIt('init()','BLUE')))
        else:
            return e
    
def getReport(report_id):
    try:
        return pd.DataFrame(ReportParser(sfr.get_report(report_id)).records_dict())
    except (KeyError, NameError) as e:
        if str(e) == 'name \'sfr\' is not defined':
            raise Exception('The sfpack variable \'sfr\' has not been defined. ' +
                            'Please initiate sfpack using {} with your Salesforce login credentials. '.format(colorIt('sfpack.init()','BLUE')) +
                            'Run {} for more details on {}.'.format(colorIt('sfpack.packhelp(\'init\')','BLUE'),colorIt('init()','BLUE')))
        else:
            return e

def updatesf(obj='',uptype='',data=''):
    if uptype not in ['insert','update','delete','hard_delete','upsert']:
        raise Exception('No valid uptype selected. Please choose one of the folowing options: [insert, update, delete, hard_delte, upsert]')
    else:
        return(eval(f'sf.bulk.{obj}.{uptype}(data)'))        


def convertTo18(fifteenId):
    #check valid input
    if fifteenId is None:
        return fifteenId
    if len(fifteenId) < 15:
        return "not a valid 15 digit ID: " + fifteenId
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
    if len(x18DigitId) < 18:
        return 'Error'
    toUpper = []
    toUpper.append(getBitPatterns(x18DigitId[15:16]))
    toUpper.append(getBitPatterns(x18DigitId[16:17]))
    toUpper.append(getBitPatterns(x18DigitId[17:18]))
    toUpper = [item for sublist in toUpper for item in sublist]
    
    output = ''.join([x18DigitId[x].upper() if toUpper[x] else x18DigitId[x].lower() for x in range(0,15)]) + x18DigitId[15:].upper()
        
    return outputs

# Deprecated help function
def packhelp(*key):
    coloring = 'blue'
    if len(key) > 1:
        raise Exception('packhelp can accept 0 or 1 arguments. You entered {} arguments'.format(len(key)))
    if len(key) == 0:
        defList = sorted([
            colorIt('  -init',coloring),
            colorIt('  -getdf',coloring),
            colorIt('  -getReport',coloring),
            colorIt('  -convertTo18',coloring),
            colorIt('  -repairCasing',coloring),
            colorIt('  -massTask',coloring)])
        print('Fuctions available in sfpack:\n\n' + '\n'.join(defList) + '\n\nRun help(' + colorIt('function name','blue') +') for additional help on each function')
    elif key[0] == 'getdf':
        print('The ' + colorIt('getdf',coloring) + ' function returns a Pandas Dataframe based of of the SOQL query passed as an argument.\n\n'
              'Make sure your SOQL query is written in single quotes (' + colorIt("''",'yellow') + ').\n\n'
              'You can learn more about SOQL functions at: \nhttps://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm')
    elif key[0] == 'getReport':
        print('The {} function returns a Pandas DataFrame of the Salesforce Report whose Id you pass in as an argument.\n'.format(colorIt('getReport',coloring)) +
                'For example, getReport(\'00O1Y00000XXXXX\').')
    elif key[0] == 'updatesf':
        print('The {} function allows for bulk updates, inserts, and deletion of records in your org. '.format(colorIt('updatesf',coloring)) +
                'It requires three parameters: {}, {}, and {}'.format(colorIt('obj',coloring),colorIt('uptype',coloring),colorIt('data',coloring)))
    elif key[0] == 'convertTo18':
        print('The {} function returns the 18 digit ID version of the 15 digit ID passed as an argument.\n'.format(colorIt('convertTo18',coloring)) +
                'For example, convertTo18(\'003i000001IIGw7\') returns \'003i000001IIGw7AAH\'')
    elif key[0] == 'repairCasing':
        print('The {} function returns a correct 18 digit ID when passed a capitalized version\n'.format(colorIt('repairCasing()',coloring)) +
                'of an 18 digit Id. For example, repairCasing(\'003i000001IIGW7\') returns \'003i000001IIGw7\'')
    elif key[0] == 'massTask':
        print('The ' + colorIt('massTask()',coloring) + ' function returns a Data Frame of tasks ready to upload, based on the arguments passed in.\n'
              'The arguments are 1) ' + colorIt('baseTaskId',coloring) + ' and 2) ' + colorIt('populationQuery',coloring) + ':\n\n'
              '  -' + colorIt('baseTaskId',coloring) + ' is the Salesforce Id of a base task template existing in Salesforce.\n\n'
              '  -' + colorIt('populationQuery',coloring) + ' is the SOQL query used to select the Wave-Maker population who should receive this task.\n\n')
    elif key[0] == 'init':
        print('The {} function initiates your connection with your Salesforce database.\n'.format(colorIt('init()',coloring)) + 
              'The parameters are 1) {}, 2) {}, 3) {}, and the optional 4) {}.\n\n'.format(colorIt('Username',coloring),
                                                                                      colorIt('Password',coloring),
                                                                                      colorIt('OrgId',coloring),
                                                                                      colorIt('SecurityToken',coloring)) +
              '{} and {} are your Salesforce username and password respectively. '.format(colorIt('Username',coloring),
                                                                                      colorIt('Password',coloring)) +
              '{} is your Salesforce.com Organization ID. '.format(colorIt('OrgId',coloring)) + 
              '{} is only required if your Salesforce org uses a Security Token, and defaults to \'\' if not assigned.\n\n'.format(colorIt('SecurityToken',coloring)) +
              '\tEx: init(\n\t\tusername=\'myusername@myemail.com\',\n\t\tpassword=\'mySalesforceLoginPassword\',\n\t\tOrgId=\'myOrgId\',\n\t\tSecrityToken=\'mySecurityToken\')\n') 
    else:
        raise Exception('No such key. Type help() for general help or help(function name) for information on that function')
