# PandaForce
A utility package utilizing pandas and simple-salesforce

### Overview
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

### Connecting to a Salesforce Org
To connect to your Salesforce Org, create a `login` class instance with `var = pandaforce.login()`. `login` requires the following parameters:
  - `username` = string of your Salesforce login username
  - `password` = string of your Salesforce login password
  - `orgid` = string of your Salesforce organization id, as found on the **Company Information** setup page of your org

There are also two optional parameters, `securitytoken` and `sandbox`.
  - `securitytoken` defaults to a blank string (`''`), but can accept your login security token
  - `sandbox` defaults to `False`, but must be passed as `True` to access a sandbox within of your org. If you are accessing a sandbox, you must also append `'.your_sandbox_name'` to the end of your username, as you would when logging in to a normal Salesforce sandbox.
  
You can have any number of `login` instances running within a given script. Each instance should be assigned to a different variable. The default example login instance in this document will be `sf`.

### Login Class Methods (Details)

#### checkObject()
The `checkObject` method accepts one string parameter, and searches your Salesforce org for an object with a name matching that parameter. It is not case sensitive. The search is by object name, not object label, so make sure to inlude underscores (`_`) and to append `__c` for custom objects.

The method returns a dictionary formatted as `{'isObject':True/False,'Records':None or count of records in object}`.

#### dml()
The `dml` method evokes a bulk CRUD (Created, Update, Delete) command into your Salesforce org. These changes are permanent, so be cautious when using this method.

`dml` parameters are as follows:
  - `obj`: the name of the Salesforce object (not its label) as a string
  - `uptype`: the type of CRUD function to be executed. Options are `insert`, `update`, `delete`, and `hard_delete` as a string
  - `data`: this parameter must be a `list` of `dictionaries`. Each value in the list represents a record, and the dictionaries must be formatted as noted below:
    - `insert`: `{'field_names':field_values_as_type_in_salesforce}'
    - `update`: `{'Id':'15_or_18_digit_Id_as_String','field_names':field_values_as_type_in_salesforce}`
    - `delete` and `hard_delete`: `{'Id':'15_or_18_digit_Id_as_String'}
    
**Insert Example**
```
myData = {'Id':'000000000000000',
```

**Update Example**

```
myData = {'Id':'000000000000000',
```

**Delete Example**

