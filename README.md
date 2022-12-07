# **OPC-UA Adapter**
Talian OPC-UA adapter is a python-based program used to integrate OPC-UA server with Maximo server using python.

## Architecture Design
![Architecture Design image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Architecture_Design2-removebg-preview.png)

## **Software Requirement**
For this procedure test, first you need an OPC-UA servers and a Maximo server already installed on your localhost / server.

1. OPC-UA server for Simulation is recommended, you can download from:
* [Integration Objects - Experts in Digital Transformation and Industry 4.0](https://integrationobjects.com/sioth-opc/sioth-opc-unified-architecture/opc-ua-server-simulator/)

* [Prosys OPC UA Simulation Server 5.2.2-9 Download](https://downloads.prosysopc.com/opc-ua-simulation-server-downloads.php)

2. The Maximo application we use is version 7.6.1, you can see the installation guide from:
* [Installing Maximo Asset Management 7.6.1 From Start to Finish (ibm.com)](https://www.ibm.com/support/pages/installing-maximo-asset-management-761-start-finish)

3. And next you need to download and install python 3.7 or higher	to develop the adaptor, you can download from:
* [Download Python | Python.org](https://www.python.org/downloads/)

4. After download and install python, you need to install some library using pip
* `pip install asyncua`
* `pip install requests`
* `pip install pywin32`
* `pip install autopylogger`

## Maximo Configuration
There are several processes that must be prepared in maximo before the integration starts

### Database Configuration
The first thing we have to do is create a new Object and Attribute in maximo, in this case we create 3 new objects OPCSERVER, OPCTAG, and OPCDATA.
#### Object and Atribute
* OPCSERVER

| Atribute | Atribute Type | Atribute Length | 
| ------------- | ------------- | ------------- |
| SERVERNAME | ALN | 20 |
| SERVERURL | ALN | 250 |
| TYPE | ALN   | 10 |
| READTYPE | ALN | 20 |
| USER | ALN | 20 |
| PASSWORD | CRYPTO  | 30 |
| INTERVAL | INT  | 12 |
| ORGID | UPPER | 8 |
| SITEID | UPPER | 8 |

* OPCTAG

| Atribute | Atribute Type | Atribute Length | 
| ------------- | ------------- | ------------- |
| TAG | ALN | 250 |
| SERVERNAME | ALN | 20 |
| ASSETNUM | UPPER   | 12 |
| METERNAME | UPPER | 10 |
| ORGID | UPPER | 8 |
| SITEID | UPPER | 8 |

* OPCDATA

| Atribute | Atribute Type | Atribute Length | 
| ------------- | ------------- | ------------- |
| TAG | ALN | 250 |
| VALUE | DECIMAL   | 16 |
| DATETIME | DATETIME | 10 |
| SERVERNAME | ALN | 20 |
| ORGID | UPPER | 8 |
| SITEID | UPPER | 8 |

#### Object Relationship
![DB relation image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/DB_relation-removebg-preview.png)

### Application Designer
After we create a new object, the next step is to create a new application inside Maximo. We made 2 applications, namely OPC Configuration and OPC Data Read which can be accessed in the Asset module.

The OPC Configuration application consists of 2 objects, namely OPCSERVER as the parent object and OPCTAG as a child object, in this application contains the OPC server configuration in the main table and the list of tags that we want to use is in the Tag List tab.

![OPC Configuration Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/OPC%20Configuration.png)

While the OPC Data Read application uses a single OPCDATA object, this application is useful for accommodating data sent from the OPC-UA server through integration using a python adapter.

![OPC Data Read Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/OPC%20Data%20Read.png)

#### Object Structure
An object structure is the common data layer that the integration framework components use for sending and receiving data in Maximo. An object structure consists of one or more related business objects that define the content of an integration message.

An object structure provides the message content for channels and services and enables application-based import and export. In addition, an object structure, on its own, can be called as a service, supporting the Create, Update, Delete, Sync, and Query operations.

![Object Structure](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Object%20Structure.png)

## Integration Process
The first step that must be ensured is that both OPC-UA and Maximo servers must be turned on. In the integration process using this python adapter, there will be 3 stages.
### Configuration File
This configuration file contains several links such as Maximo server URL, OPC server URL, Maximo OSLC URL, and several other configurations.

```
{
	"opc_servername": "opcuasimulator",
	"maximo_url": "http://147.139.132.238:9080/maximo",
	"enable_maximo": true,
	"headers_maximo": {
		"Content-Type": "application/json",
		"apikey":"8nmu3lb1bfm0bflugcqj08h48dc445tm5a8sq4bc",
		"properties" : "*"
	},
	"local_taglist" : false,
	"taglist" : []
}
```
opc_server name is the server name that we created earlier in the OPC Configuration application in Maximo, maximo url is the address of maximo server, headers_maximo is the configuration used in the process of sending data to the maximo server, api key data can be obtained using the Postman application in the following way

First open the Postman application and fill in the header as shown below
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/postman-1.png)

Use the POST method and enter the url address of the Maximo server, use maxauth that has been encoded, in this test we use baseencode64, we use the mxintadm user and password for this integration.
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/base64-encode.png)

Then fill in the body as shown below
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/postman-2.png)

Last click Send and we will get the apikey we need
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/postman-3.png)

### Get OPC Tag List
The first stage is the python adapter will retrieve data and a list of tags that are on the Maximo server using the OSLC API that has been configured in the Maximo Object Structure.

### Read Tag List
The second stage of the python adapter will process the data taken from Maximo and then make a connection to the OPC-UA server as a client, after the connection is successfully made the next stage the python adapter will take the value from the tag list that have been processed previously.

### Send to Maximo
And the third stage is to process the data that we got from the OPC-UA server and then send it to the Maximo server via the OSLC API that we have created in the Object Structure.

### Schedule
The next stage after the Python Adapter has successfully performed its function, which is to repeat the 3 stages above according to the intervals that have been specified in the OPC Configuration application in Maximo, we can determine in how many seconds or minutes the script will run repeatedly.

## Maximo Data Processing
After Maximo receives the data sent by the Python Adapter, the next process is managing the data. The data will go through several processes below

### Asset Configuration
Before we start the process of sending data from OPC Data into the Asset Meter, we have to prepare some configurations in the Asset application.

#### Conditional Monitoring
Condition monitoring involves using measurement points to determine an acceptable range for meters at an asset or location. When the meter reading exceeds the acceptable range, then you can create a work order to address the situation.

The first step in this process is to create a new Measurement Point, we have to fill in some required fields and of course choose the Asset to be used

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Conditional%20Monitoring.png)

#### Asset Meter
After we create a new measure point in the Condition Monitoring application, Maximo will automatically create a new Meter in the Asset that we specified earlier.

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Asset%20Meter.png)

### Automation Script
An automation script consists of a launch point, variables with corresponding binding values, and the source code. You use wizards to create the components of an automation script. You create scripts and launch points, or you create a launch point and associate the launch point with an existing script.

You can also create library scripts, which are reusable pieces of programming language that automation scripts can invoke from the body their code. Library scripts must be hosted on the same system.

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/automation%20script.png)

The script that we created will process the data that is in the OPCDATA object and will send its value into the ASSETMETER object through the relationship we created earlier.

### BIRT Reporting
Business Intelligence and Reporting Tools (BIRT) is an open source, based on Eclipse system for designing, developing, and running reports. You can develop BIRT reports for TADDM, designing them to use JDBC data sources and SQL queries of predefined database views.

The BIRT system includes two major components:
* The BIRT designer, a graphical tool for designing and developing new reports
* The BIRT runtime engine, which provides support for running reports and rendering published report output

#### Measurement History Report
In this report we can see the result of the data sent from the OPC-UA Server to Maximo about the measurement value of the Asset.

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Run%20Report.png)

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/BIRT%20Measurment.png)

## Maximo Functional Process
In this process, we will explain the use of the data that has been received by Maximo from the previous integration process

### Condition Monitoring
In Maximo you can use the Condition Monitoring application to define acceptable upper and lower limits for meter measurement readings that can help you to decide when preventive or emergency maintenance should be initiated for your assets.

Condition Monitoring allows you to set upper / lower warning limits, upper / lower action limits, and PM limits which you can then associate with a specific PM and or job plan. These limits will be associated with a specific asset and meter type which you will record measurements against.

Once you have defined your limits for the asset / location you can then begin entering measurement points which will document meter readings at a specific time in the asset's history. These measurement points will then be used to decide whether or not work should be done on your asset.

#### Generate Work Order 
After it is determined that the meter readings are outside of your predefined limits, you can use the Condition Monitoring application to generate work orders against your asset using the "Generate Work Orders" option from the application's Select Action menu. 

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/ConMon%20Generate%20WO.png)

#### Setting up Measure Point Wogen Crontask
Cron tasks are behind-the-scene jobs set to run automatically and on a fixed schedule.
Maximo contains a set of default cron tasks, but you can also create custom cron tasks to fit your business needs.
Cron tasks include activities like generating preventive maintenance work orders and reordering inventory items on a schedule.
*	Go To Cron Task Setup Application.
* From the List Tab, select the Cron Task definition you want to work with is this MeasurePointWoGenCronTask
*	Enter a name in the Cron Task Instance Name field.
*	Click Set Schedule to open the Set Schedule dialog
*	Setup the appropriate interval.
*	Check the Active? field.
*	Click Save Cron Task Definition From the Select Action menu, select Reload Request.
*	Select the instance, then click OK.

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Cron%20Task.png)

*	In Organization. Select Actions, PM Options
*	"Automatic MeasurePoint WO generation?" Check box must be checked for the Site you choose to run.
*	Use Action Limits as Work Order Generation Criteria? Check box must be checked for the Site you choose to run.


![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Organization%20Action.png)
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Organization%20Action2.png)

### How to change the colour of a field using conditional expressions
Here is a step-by-step guide about how to dynamically highlight measurement that have a Upper Warning Limit, Upper Action Limit, Lower Warning Limit, Lower Action Limit, in the Condition Monitoring application.

#### Define conditional expression
Open Administration – Conditional Expression Manager application. Create the following conditional expression.

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/Conditional%20Expression.png)

#### Configure COND application
follow the steps below to edit the application
* Open System configuration – Platform Configuration – Applications Designer application 
* Select and edit the COND application. 
 
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/App%20Design%20COND.png)

*	Select the Measurement Field and open the properties window (Right Click). 
*	Click on Configure Conditional Properties button the Advanced tab. 
	
![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/App%20Design%20COND2.png)

*	Use READ as Signature Option and EVERYONE as the security group. 
*	Select all the Conditional Expressions that you have made 

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/App%20Design%20COND3.png)

*	Enter the defined condition with Property=cssclass and Value=txtred or txtorange

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/App%20Design%20COND4.png)

*	And the result will look like this

![Image](https://github.com/adi-rowi/tal-opc-ua/blob/main/images/App%20Design%20COND5.png)
