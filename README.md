# pandaforce
A pandas based salesforce access module

### Setup
sfpack contains the following functions:
  - convertTo18:	Converts the passed Salesforce 15-digit ID to an 18-digit Id
  - isNull:		Returns boolean value for passed value indicating if it is a Null or NaN value
  - repairCasing:	Changes 18-digit IDs that have had all character's capitalized to a Salesforce viable 18-digit Id

It also contains a login class which initiates a connection to a Salesforce org. It contains the following methods:
  - checkObject:	Accepts string argument. Returns dict {'isObject':True/False,'Records':count_of_records_in_object}
  - getdf:		Returns pandas dataframe from passed SOQL query
  - getObjectFields:	Returns list of all field names in the passed Salesforce object name
  - getObjectFieldsDict:Returns all fields of passed Salesforce object name as {label:name} dictionary
  - getReport:		Returns pandas dataframe from passed Salesforce report Id (15 or 18 digit)

Type 'help(function_name)' or 'help(login.method_name)' for additional information on each function or method
