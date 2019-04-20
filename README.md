# PandaForce
A utility package utilizing [pandas](https://github.com/pandas-dev/pandas) and [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce)

## Overview
pandaforce contains the following general utility functions:
  - `convertTo18`:	Converts the passed Salesforce 15-digit ID to an 18-digit Id
  - `info` gives an overview of the functions and methods within the pandaforce package
  - `isNull`:		Returns boolean value for passed value indicating if it is a Null or NaN value
  - `repairCasing`:	Changes 18-digit IDs that have had all character's capitalized to a Salesforce viable 18-digit Id

It also contains a `login` class which initiates a connection to a Salesforce org. It contains the following methods:
  - `checkObject`: Accepts string argument. Returns dict {'isObject':True/False,'Records':count_of_records_in_object}
  - `dml`: Runs the specified bulk CRUD command with the passed data
  - `getdf`: Returns pandas dataframe from passed SOQL query
  - `getObjectFields`: Returns list of all field names in the passed Salesforce object name
  - `getObjectFieldsDict`: Returns all fields of passed Salesforce object name as {label:name} dictionary
  - `getReport`: Returns pandas dataframe from passed Salesforce report Id (15 or 18 digit)

## Connecting to a Salesforce Org
To connect to your Salesforce Org, create a `login` class instance with `var = pandaforce.login()`. `login` requires the following parameters:
  - `username` = string of your Salesforce login username
  - `password` = string of your Salesforce login password
  - `orgid` = string of your Salesforce organization id, as found on the **Company Information** setup page of your org

There are also two optional parameters, `securitytoken` and `sandbox`.
  - `securitytoken` defaults to a blank string (`''`), but can accept your login security token
  - `sandbox` defaults to `False`, but must be passed as `True` to access a sandbox within of your org. If you are accessing a sandbox, you must also append `'.your_sandbox_name'` to the end of your username, as you would when logging in to a normal Salesforce sandbox.
  
You can have any number of `login` instances running within a given script. Each instance should be assigned to a different variable. The default example login instance in this document will be `sf`.

## Login Class Methods (Details)

### checkObject
The `checkObject` method accepts one string parameter, and searches your Salesforce org for an object with a name matching that parameter. It is not case sensitive. The search is by object name, not object label, so make sure to inlude underscores (`_`) and to append `__c` for custom objects.

The method returns a dictionary formatted as `{'isObject':True/False,'Records':None or count of records in object}`.

### dml
The `dml` method evokes a bulk CRUD (Created, Update, Delete) command into your Salesforce org. These changes are permanent, so be cautious when using this method.

`dml` parameters are as follows:
  - `obj`: the name of the Salesforce object (not its label) as a string
  - `uptype`: the type of CRUD function to be executed. Options are `insert`, `update`, `delete`, and `hard_delete` as a string
  - `data`: this parameter must be a `list` of `dictionaries`. Each value in the list represents a record, and the dictionaries must be formatted as noted below:
    - `insert`: `{'field_names':field_values_as_type_in_salesforce}'
    - `update`: `{'Id':'15_or_18_digit_Id_as_String','field_names':field_values_as_type_in_salesforce}`
    - `delete` and `hard_delete`: `{'Id':'15_or_18_digit_Id_as_String'}

`dml` returns a list of dictionaries, as formatted in the example below:
```
[{'success': True, 'created': False, 'id': '0030v000000000000B', 'errors': []},
 {'success': True, 'created': False, 'id': '0030v000000000000N', 'errors': []},
 {'success': False,'created': False,'id': None,'errors': [{'message': 'Please update phone number format to: (XXX) XXX-XXXX',
    'fields': ['MobilePhone'],
    'statusCode': 'FIELD_CUSTOM_VALIDATION_EXCEPTION',
    'extendedErrorDetails': None}]},
```
To capture the `dml` results, assign a variable to the dml command. For example:

```r = sf.dml('Custom_Object__c','delete','myData')```

**Insert Example**
```
sf = login(login_criteria_here)

myData = [{'Name':'First Record','Field_A__c':'A value','Number_Field__c':123},
           'Name':'Second Record','Field_A__c':'Another value','Number_Field__c':456}]
           
sf.dml('Custom_Object__c','insert',myData)
```

**Update Example**

```
sf = login(login_criteria_here)

myData = [{'Id':'000000000000001','Name':'First Record','Field_A__c':'A value','Number_Field__c':123},
           'Id':'000000000000002','Name':'Second Record','Field_A__c':'Another value','Number_Field__c':456}]
           
sf.dml('Custom_Object__c','update',myData)
```

**Delete Example**
```
sf = login(login_criteria_here)

myData = [{'Id':'000000000000001'},
           'Id':'000000000000002'}]
           
sf.dml('Custom_Object__c','delete',myData)
```

**Dot Notation Example**
Because the `login` class initiates a `Salesforce` class from the [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce) package, you can also run a dml statement through dot notation. A dml statement in this fashion would look like the following:

```sf.Org.Custom_Object__c.update(myData)```

The `.Org` component between `sf.` and `.Custom_Object__c` is required as the Simple Salesforce `Salesforce` class is housed within the `login` class instance.

### getObjectFields
The `getObjectFields` method returns list of all field names in the passed Salesforce object name. The passed value must be a string, and be the name of the Salesforce object, not the label (i.e., `'Custom_Object__c'` rather than `'Custom Object'`)

### getObjectFieldsDict
The `getObjectFieldsDict` method returns all fields of passed Salesforce object name as dictionary, using a {label:name} format. Like `getObjectFields`, the passed string must be the name of the Salesforce object, not the label (i.e., `'Custom_Object__c'` rather than `'Custom Object'`)

### getReport
The `getReport` method returns a pandas dataframe from passed Salesforce report Id (15- or 18-digit). This method only works on tabular Salesforce reports, and will only return the text value of any hyperlinked text (i.e. The 'Name' field on the report will appear in the dataframe as the text of the name, not a link to the record or the record's 15- or 18-digit Id

## Pandaforce Inheritance
As its name implies, Pandaforce heavily utilizes [pandas](https://github.com/pandas-dev/pandas) and [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce), so any functionality of those packages will apply to this package as well. 

For example, dataframes returned from methods such as `getdf()` or `getReport` are pandas DataFrames, so all DataFrame methods from the pandas package will function on it. Likewise, the `Org` variable in each `login` instance is a simple-salesforce Salesforce class, and its methods are accessible as well.

