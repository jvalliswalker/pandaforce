
# coding: utf-8

# In[97]:


pth = [
'C:\\Users\\jvallis-walker\\AppData\\Local\\Programs\\Python\\Python37-32\\python36.zip',
'C:\\Users\\jvallis-walker\\AppData\\Local\\Programs\\Python\\Python37-32\\DLLs',
'C:\\Users\\jvallis-walker\\AppData\\Local\\Programs\\Python\\Python37-32\\lib',
'C:\\Users\\jvallis-walker\\AppData\\Local\\Programs\\Python\\Python37-32',
'C:\\Users\\jvallis-walker\\AppData\\Local\\Programs\\Python\\Python37-32\\lib\\site-packages'
]

import sys, json
for i in pth:
    sys.path.append(i)

userName = 'autoadmin@making-waves.org'
userPassword = 'Koef99**1'
    
from simple_salesforce import Salesforce, exceptions
sf = Salesforce(password=userPassword, username=userName, organizationId='00Di0000000cNQu')

from salesforce_reporting import Connection, ReportParser
sfr = Connection(username=userName,password=userPassword,security_token='')

import pandas as pd
import os

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

class HoldToTaskMatcher:
    '''A class for creating Financial Holds for Tasks'''
    
    def __init__(self):
        '''Initialize self. Variables initiated: Tasks, Budgets, Holds, Updates, and UpdateStatus'''
        self.Tasks = pd.DataFrame()
        self.Budgets = pd.DataFrame()
        self.Holds = []
        self.Updates = []
        self.UpdateStatus = False
        
    def createHolds(self, hold_reason=None,task_query='',budget_query=''):
        '''Create Financial Hold records based on passed arguments, and assign records to the Tasks, Budgets, and Holds variables.'''
        if (any(i not in task_query.lower() for i in [' id,','task','whatid','whoid']) 
            and any(i not in task_query.lower() for i in [',id','task','whatid','whoid'])):
            raise Exception('task_query parameter must query the \'task\' object, and include the Id, WhatId, and WhoId fields')
        else:
            tasks = getdf(task_query)

        if (any(i not in budget_query.lower() for i in [' id,','budget__c','wave_maker__c'])
            and any(i not in budget_query.lower() for i in [',id','budget__c','wave_maker__c'])):
            raise Exception('budget_query parameter must query the \'budget__c\' object, and include the Id and Wave_Maker__c fields')
        else:
            fps = getdf(budget_query)
        
        hold_reasons = []
        for i in sf.Financial_Hold__c.describe()['fields']:
            if i['name'] == 'Reason__c':
                for val in i['picklistValues']:
                    hold_reasons.append(val['value'])
                    
        if hold_reason not in hold_reasons:
            raise Exception('hold_reason argument invalid; please choose a hold reason from the following list: {}'.format(', '.join(hold_reasons)))
        else:
            hold_reason = hold_reason

        fpdict = {}

        for i in fps.index:
            fpdict[fps.at[i,'Wave_Maker__c']] = fps.at[i,'Id']

        fholds = []

        for i in tasks.index:
            try:
                fholds.append({'Financial_Plan__c':fpdict[tasks.at[i,'WhoId']],'Reason__c':hold_reason,'Start_Date__c':'2019-04-10'})
            except:
                None

        self.Tasks = tasks
        self.Budgets = fps
        self.Holds = fholds
    
    def insertHolds(self):
        '''Insert the Financial Hold records created from createHolds() into Salesforce'''
        r = sf.bulk.Financial_Hold__c.insert(self.Holds)
        self.Holds = [i['id'] for i in r]
    
    def matchHoldsToTasks(self):
        '''Assign the inserted Financial Holds from insertHolds() to the WhatId task fields of Tasks'''
        holds = getdf('SELECT ID, Financial_Plan__r.Wave_Maker__c FROM Financial_Hold__c WHERE Id IN (\'{}\')'.format('\',\''.join(self.Holds)))
        holds['Wavemaker'] = [i['Wave_Maker__c'] for i in holds.Financial_Plan__r]
        hdict = {}
        for i in holds.index:
            hdict[holds.at[i,'Wavemaker']] = holds.at[i,'Id']
        tmpTasks = self.Tasks
        for i in tmpTasks.index:
            tmpTasks.at[i,'WhatId'] = hdict[tmpTasks.at[i,'WhoId']]
            tmpTasks.at[i,'Auto_Update_Record_Process__c'] = 'Resolve Financial Hold'
#         self.Tasks = tmpTasks # Unnecessary because tmpTasks is ref to self.Tasks, not a self.Tasks.copy()
        self.Tasks = json.loads(tmpTasks[['Id','WhatId','Auto_Update_Record_Process__c']].to_json(orient='records'))
        self.Updates = sf.bulk.Task.update(self.Tasks)
        if any([self.Updates[i]['success'] == False for i in range(0,len(self.Updates))]):
            self.UpdateStatus = False
        else:
            self.UpdateStatus = True
            
    def __run(self, hold_reason=None,task_query='',budget_query=''):
        '''Hidden query to run createHolds(), insertHolds(), and matchHoldsToTasks() in a single command. Recommended for testing only.'''
        self.createHolds(hold_reason=hold_reason,task_query=task_query,budget_query=budget_query)
        self.insertHolds()
        self.matchHoldsToTasks()
        return 'run successful'
    
# -----------------------------------------------------------------------------------------------

def help(*key):
    coloring = 'blue'
    if len(key) > 1:
        raise Exception('packhelp can accept 0 or 1 arguments. You entered {} arguments'.format(len(key)))
    if len(key) == 0:
        print('Type help(' + colorIt('\'functions\'','yellow') + ') to learn about the different functions in sfpack.\n'
                'Type help(' + colorIt('\'the name of the function\'','yellow') + ') to learn about that function')
    elif key[0].lower() == 'classes':
        defList = sorted([
            colorIt('  -HoldToTaskMatcher',coloring)])
        print('Classes available in sfpack:\n\n' + '\n'.join(defList))
    elif key[0].lower() == 'functions':
        defList = sorted([
            colorIt('  -getdf',coloring),
            colorIt('  -getReport',coloring),
            colorIt('  -convertTo18',coloring),
            colorIt('  -repairCasing',coloring),
            colorIt('  -getSchoolNamesDf',coloring),
            colorIt('  -getSchoolNamesDict',coloring),
            colorIt('  -massTask',coloring),
            colorIt('  -isNull',coloring),
            colorIt('  -getObjectFields',coloring),
            colorIt('  -getObjectFieldsDict',coloring),
            colorIt('checkSalesforceObject',colorit)])
        print('Fuctions available in sfpack:\n\n' + '\n'.join(defList) + '\n\nRun help(' + colorIt('function name','blue') +') for additional help on each function')
    elif key[0] == 'getdf':
        print('The ' + colorIt('getdf',coloring) + ' function returns a Pandas Dataframe based of of the SOQL query passed as an argument.\n\n'
              'Make sure your SOQL query is written in single quotes (' + colorIt("''",'yellow') + ').\n\n'
              'You can learn more about SOQL functions at: \nhttps://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm')
    elif key[0] == 'getReport':
        print('The \'getReport\' function returns a Pandas DataFrame of the Salesforce Report whose Id you pass in as an argument.\n'
                'For example, getReport(\'00O1Y00000XXXXX\').')
    elif key[0] == 'convertTo18':
        print('The \'convertTo18\' function returns the 18 digit ID version of the 15 digit ID passed as an argument.\n'
                'For example, convertTo18(\'003i000001IIGw7\') returns \'003i000001IIGw7AAH\'')
    elif key[0] == 'repairCasing':
        print('The \'repairCasing\' function returns a correct 18 digit ID when passed a capitalized version\n'
                'of an 18 digit Id. For example, repairCasing(\'003i000001IIGW7\') returns \'003i000001IIGw7\'')
    elif key[0] == 'getSchoolNamesDf':
        print('The \'getSchoolNamesDf\' function returns a DataFrame of all \'Schools\' and \'Other School Names\' from the CAP Salesforce org.',
             '\nDoes not accept an argument.')
    elif key[0] == 'getSchoolNamesDict':
        print('The \'getSchoolNamesDf\' function returns a Dictionary of all \'Schools\' and \'Other School Names\' from the CAP Salesforce org.',
             '\nDoes not accept an argument.')
    elif key[0] == 'massTask':
        print('The ' + colorIt('massTask()',coloring) + ' function returns a Data Frame of tasks ready to upload, based on the arguments passed in.\n'
              'The arguments are 1) ' + colorIt('baseTaskId',coloring) + ' and 2) ' + colorIt('populationQuery',coloring) + ':\n\n'
              '  -' + colorIt('baseTaskId',coloring) + ' is the Salesforce Id of a base task template existing in Salesforce.\n\n'
              '  -' + colorIt('populationQuery',coloring) + ' is the SOQL query used to select the Wave-Maker population who should receive this task.\n\n')
    else:
        raise Exception('Key "{}" does not exist. Type help() for general help or help(function name) for information on that function'.format(key[0]))
        
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
    except KeyError as e:
        if str(e) == '"labels [\'attributes\'] not contained in axis"':
            print('No data found for query\n----------------------\n[{}]\n----------------------\nNull value returned'.format(val))
            return None
        else:
            return e

def getReport(report_id):
    return pd.DataFrame(ReportParser(sfr.get_report(report_id)).records_dict())
        
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

def getBitPatterns(c):
    CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
    index = CHARS.find(c)
    result = []
    for bitNumber in range(0,5):
        result.append((index & (1 << bitNumber)) != 0)
    return result

def repairCasing(x18DigitId):
    if len(x18DigitId) < 18:
        return 'Error'
    toUpper = []
    toUpper.append(getBitPatterns(x18DigitId[15:16]))
    toUpper.append(getBitPatterns(x18DigitId[16:17]))
    toUpper.append(getBitPatterns(x18DigitId[17:18]))
    toUpper = [item for sublist in toUpper for item in sublist]
    
    output = ''.join([x18DigitId[x].upper() if toUpper[x] else x18DigitId[x].lower() for x in range(0,15)]) + x18DigitId[15:].upper()
        
    return output

def getSchoolNamesDf():
    alt_name_schools = getdf(
    'SELECT Name, School__c FROM Other_School_Names__c'
    )

    schools = getdf(
    'SELECT Name, Id FROM Account'
    )
    schools.rename(columns={'Id':'School__c'},inplace=True)

    df = pd.concat([schools,alt_name_schools]).reset_index(drop=True)
    return df

def getSchoolNamesDict():
    df = getSchoolNamesDf()
    dfdic = {}
    for i in df.index:
        dfdic[df.at[i,'Name'].lower()] = df.at[i,'School__c']
    return dfdic

def massTask(baseTaskId,populationQuery):

    task_fields = ['Priority','Assignee__c','ActivityDate','Status','Subject','Description',
                   'Auto_Publish_to_Portal_on__c','Student_Portal_Ready__c']

    taskInfo = getdf('SELECT Id, {} FROM Task WHERE Id = \'{}\''.format(', '.join(task_fields),baseTaskId))

    # Get student population
    pop = getdf(populationQuery)
    pop = list(pop.Id)

    # Get Users of student population
    users = getdf('SELECT Id, ContactId FROM User WHERE Profile.Name = \'Wavemaker\'')
    userdict = {}
    for i in users.index:
        userdict[users.at[i,'ContactId']] = users.at[i,'Id']    
    
    # Create new df
    tasksDf = pd.DataFrame()

    tasksDf['WhoId'] = pop
    try:
        tasksDf['OwnerId'] = [userdict[i] for i in tasksDf.WhoId]
    except:
        for i in tasksDf.index:
            try:
                tasksDf.at[i,'OwnerId'] = userdict[tasksDf.at[i,'WhoId']]
            except:
                tasksDf.at[i,'OwnerId'] = ''

    for i in task_fields:
        tasksDf[i] = taskInfo.at[0,i]

    replaceUs = ['“','”']
    for i in range(0,len(replaceUs)):
        tasksDf['Description'] = tasksDf['Description'].str.replace(replaceUs[i],'"')
    
    return tasksDf

def isNull(val):
    if val == None:
        return True
    elif val != val:
        return True
    else:
        return False

def getObjectFields(obj):
    fields = getattr(sf,obj).describe()['fields']
    flist = [i['name'] for i in fields]
    return flist

getObjectFields('Contact')


def getObjectFieldsDict(obj):
    fields = getattr(sf,obj).describe()['fields']
    fdict = {}
    for i in fields:
        fdict[i['label']] = i['name']
    return fdict

getObjectFields('Contact')

def checkSalesforceObject(objName):
    try:
        getattr(sf,objName).metadata()
        a = len(sf.query_all('SELECT Id FROM {}'.format(objName))['records'])
        return {'IsObject':True,'Records':a}
    except:
        a = sys.exc_info()
        return {'IsObject':not("Resource {} Not Found".format(objName) in str(a[1])),'Records':None}
