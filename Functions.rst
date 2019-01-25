*****************
Functions
*****************

Fuctions available in sfpack:

* convertTo18()
* getReport()
* getdf()
* init()
* massTask()
* repairCasing()

  
Init()
======

The **init()** function initiates your connection with your Salesforce database.
The parameters are **username**, **password**, **orgid**, and the optional **securitytoken**.

Username and Password are your Salesforce username and password respectively.
OrgId is your Salesforce.com Organization ID, which can be found on the `Company Information`__ section of your Salesforce org. 
SecurityToken is only required if your Salesforce org uses a Security Token, and defaults to '' if not assigned.

Example:

.. code-block:: python

  init(username='myusername@myemail.com',password='mySalesforceLoginPassword',
      OrgId='myOrgId',SecrityToken='mySecurityToken')

test


.. _CompanyInformationLookupHelp: https://help.salesforce.com/articleView?id=000006019&type=1
__ CompanyInformationLookupHelp_
