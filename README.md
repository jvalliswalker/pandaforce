# pandaforce
A pandas based salesforce access module

### Overview
pandaforce contains the following functions:
  - `convertTo18`:	Converts the passed Salesforce 15-digit ID to an 18-digit Id
  - `isNull`:		Returns boolean value for passed value indicating if it is a Null or NaN value
  - `repairCasing`:	Changes 18-digit IDs that have had all character's capitalized to a Salesforce viable 18-digit Id

It also contains a `login` class which initiates a connection to a Salesforce org. It contains the following methods:
  - `checkObject`:	Accepts string argument. Returns dict {'isObject':True/False,'Records':count_of_records_in_object}
  - `getdf`:		Returns pandas dataframe from passed SOQL query
  - `getObjectFields`:	Returns list of all field names in the passed Salesforce object name
  - `getObjectFieldsDict`:Returns all fields of passed Salesforce object name as {label:name} dictionary
  - `getReport`:		Returns pandas dataframe from passed Salesforce report Id (15 or 18 digit)

### Connect to Salesforce Org
To connect to your Salesforce Org, create a `login` class instance with `var = pandaforce.login()`. `login` requires the following parameters:
  - `username` = string of your Salesforce login username
  - `password` = string of your Salesforce login password
  - `orgid` = string of your Salesforce organization id, as found on the **Company Information** setup page of your org

There are also two optional parameters, `securitytoken` and `sandbox`.
  - `securitytoken` defaults to a blank string (`''`), but can accept your login security token
  - `sandbox` defaults to `False`, but must be passed as `True` to access a sandbox within of your org. If you are accessing a sandbox, you must also append `'.your_sandbox_name'` to the end of your username, as you would when logging in to a normal Salesforce sandbox.
  
You can have any number of `login` instances running within a given script. Each instance should be assigned to a different variable. The default example login instance in this document will be `sf`.
