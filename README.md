# ImagineSystems

## Build
**Step 1**

```git clone https://github.com/aleccarruthers/ImagineSystems.git```
   
   or
    
   Click on the green 'code' button next to the 'Add File' button >>> Download ZIP

**Step 2**

If the first option was used in Step 1:

```cd ImagineSystems```   

If the second option was used in Step 1:

```cd ImagineSystems-main```

**Step 3**
<p align="center">
  <b>Virtual Environment</b><br>
</p>
 
 ```python -m venv [your_environment_name]```
 
 **Windows**
 
 ```
 .\[your_environment_name]\Scripts\activate
 pip install -r requirements.txt
 ```
 
 **Linux**
 
 ```
 source [your_environment_name]/bin/activate
 pip install -r requirements.txt
 ```
 
 <p align="center">
  <b>Anaconda Environment</b><br>
</p>
 
 ```
 conda env create -n [your_environment_name] -f environment.yml
 conda activate [your_environment_name]
 ```
 
 ## Exectute

From the ```ImagineSystems``` (step 1: options 1) or ```ImagineSystems-main``` (step1: option 2) directory:

``` python main.py```

 ## Explanation
 
 
 ### Questions
The output of ```main.py``` is provided below:

```
Unique ID not found - Failed Connectivity

Request ID: 5cfdc1cb-576b-4171-b949-c11705cb60d9
Service: epsilon
Time of last message before error: 2021-03-12T13:13:14.142511000

Message Send Time:
Service: alpha,  Timestamp: 2021-03-12T13:13:55.369835000
Service: beta,  Timestamp: 2021-03-12T13:13:55.376835000
Service: delta,  Timestamp: 2021-03-12T13:13:55.383835000
```

The error seems to be a failed connection between service delta and epsilon because the unique request id found in alpha, beta, and delta, which should have been sent to epsilon, is not present in epsilon. "When the problem first begins" can be interpreted in a couple of ways. First, one could argue that the problem begins at the same time as when service alpha has its first '500' value, i.e. an errored request. If that is the case, the problem first begins at: **2021-03-12T13:13:55.369835000**. Alternatively, the problems could have begun just after the timestamp in service epsilon that was closest to the timestamp of the first errored message in service A (what was shown previously). For example, if the first errored message in service A took place at 4:00 PM and the closest valid timestamp in service epsilon to this time was at 3:58 PM, one could argue that the problems arose at 3:58:01 PM because without addiditonal samples being sent to service E, it is hard to dermine the exact time the connection became faulty between 3:58 and 4:00 PM. With this approach, service epsilon could have become faulty immediately instantaneously after ***2021-03-12T13:13:14.142511000*** in the worst case scenario. By worst case scenario I mean, the earliest possible time of problems beginning.


### Interpretation of Output

The top line of the output states the likely cause of the problems, if any:
- No Problems Exist: "No Errors in service"
- Invalid Termination of Request (a service intermittently
failing): "Invalid Request Termination"
- Missing Request ID (Failed Connectivity): "Unique ID not found - Failed Connectivity"

Lines 2 - 4:
- The request ID not found
- The service the request ID was not found in
- Last succesful message in service before failed connectivity

Lines 5 - 8:
- The timestamps of the missing request ID in all services that actually contained it

*Note: The output text will be different if either no errors were detected or the service intermittently failed. The former outputs nothing, while the latter outputs just the service having the invalid termination and the timestamp it occurred.*


### Assumptions of Approach

- The "problems" began at or approximately near the first timestamp in service alpha with a code value of '500', i.e. an error.
- The error codes propagate back to parent services, i.e. an invalid request termination in service delta would cause the entire path of services used to get to service delta to have a code value of 500 for the errored request id. 
- While not tested because of the datasets, if no code value equals 500 in service alpha, it is assumed that no errors occurred in the service.
- A missing request ID is a faulty connection between the last service to have the request ID and the service missing it.
- A service intermittently failing occurrs when a service has a code value of 500 and a text value of 'request terminated'. This was not the first error, so it was not encountered here.
- Any entry/row in the log is complete, i.e. each attribute of the dictionary has a value.
- The values for each entry in the dictionary agree with the provided possible values, i.e. a code value of 300 won't be found in any of the entries.


### Scalability Considerations

- Depending on the size of the computer/s used, storing each service's entire log may not be ideal, as it would increase the runtime memory needed for the script. I guess it really depends on all the possible use cases for the script. If valid request id's also need to be periodically queried, then all of the log should be stored in each 'logNode' object. However, if the logs only need to be checked for error codes, the entire log would not necessarily need to be stored in the 'logNode' class. One could find all unique values for the 'code' column and if 500 exists, return the request id and timestamp of the first 500 instance. If 500 is not present, the entire log does not need to be stored.
- I manually created classes for each log file and their corresponding children, which would obviously not scale well when the number of devices increases. To resolve this issue, a dictionary could potentially be used to keep track of the different levels of the service graph and the respective children/subsequent logs for each log.
- The code submitted assumed that there can only be one service/node as the first layer, but with hundreds of devices, I would imagine that at least a few services would exists in that first layer. Since there was only one root service here, I could get away with adding alpha directly to the queue; however, this process does not hold when multiple services exist at the top layer. What could be done to resolve this issue is a loop over all of the top layer nodes, only keeping the ones that have an error present. The top layer services/nodes with an error could then be added to an even higher level list such that each of them is put into the queue to determine the timestamp of the first errored request.
- Only serial computing was used here, but with hundres of logs, each with millions of parameters, it may be advantageous to implement parallel computing strategies, such that multiple logs could be analyzed at the same time.
- Another possible limitation, which is related to the first point, could be how the dataframes for each log are created. In the current design, lines of the log file are looped over, converted to a python dictionary using JSON, and appended to a list. The list is then concatenated to form the dataframe for the log. With the largest file having just 1234 entries, this approach is fast enough, but some alternate method may need to implemented such that multiple lines could be parsed at the same time while keeping their order in tact. 
- One of the biggest adjustments that would need to be made to handle hundreds of services would be the inclusion of unit tests. Here, it was not really necessary because the log files were all structured in a similar way, non-dynamic, and had no missing or faulty values. However, as the number of services increases and under the assumption that this script is working with dynamic data streams, the need for unit tests would increase. The unit tests I would include are:
   
   - Checking the keys of the log dataframe to make sure no keys are missing and or no keys have been mistakenly added to that piece of data.
  - Checking that the values of the log keys are consistent with their range of possible values.
  - Checking the log files exists when being read.
  - Checking the format of values in the log, i.e. the request id should be a string not a number.
  - Checking the exit status of all possible conditions: No errors found, invalid termination, and faulty connectivity.
  - Checking that adding an invalid child node/service to an existing node/service throws an error.  
