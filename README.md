# ImagineSystems

## Build
```git clone https://github.com/aleccarruthers/ImagineSystems.git```

```cd ImagineSystems```   
<p align="center">
  <b>Virtual Environment</b><br>
</p>
 
 ```python -m venv [your_environment_name]```
 
 **Windows**
 
 ```
 .\myenv\bin\activate [your_environment_name]
 pip install -r requirements.txt
 ```
 
 **Linux**
 
 ```
 source myenv/bin/activate
 pip install -r requirements.txt
 ```
 
 <p align="center">
  <b>Anaconda Environment</b><br>
</p>
 
 ```
 conda env create -f environment.yml
 conda activate AnaImgSys
 ```
 
 ## Exectute

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

The error seems to be a failed connection between service delta and epsilon, as the unique request id found in alpha, beta, and delta, which should have been sent to epsilon, is not found. "When the problem first begins" can be interpreted in a couple of ways. First, one could argue that the problem begins at the same time as when service alpha has its first '500' value, i.e. an errored request. If that is the case, the problem first begins at: **2021-03-12T13:13:55.369835000**. Alternatively, the problems could have begun just after the timestamp in service epsilon that was closest to the timestamp of the first errored message at service A (what was shown previously). For example, if the first errored message in service A took place at 4:00 PM and the closest timestamp in service epsilon to this time was at 3:58 PM, one could argue that the problems arose at 3:58:01 PM because without addiditonal samples being sent to service E, it is hard to dermine the exact time the connection became faulty between 3:58 and 4:00 PM. With this approach, service epsilon could have become faulty immediately instantaneously after ***2021-03-12T13:13:14.142511000***.


### Interpretation of Output

The top line of the output states the likely cause of the problems if any:
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

- The "problems" began at or approximately near the first timestamp in service A with a code value of '500', i.e. an error.
- The error codes propagate back to parent services, i.e. an invalid request termination in service delta would cause the entire path of services used to get to service delta to have a code value of 500 for the errored request id.
- While not tested because of the datasets, if no code value equals 500 in service A, it is assumed that no errors occurred.
- A missing request ID is a faulty connection between the last service to have the request ID and the service missing it.
- A service intermittently failing occurrs when a service has a code value of 500 and a text value of 'request terminated'. This was not the first error, so it was not considered here


### Scalability Considerations

- Depending on the size of the computer/s used, storing each service's entire log may not be ideal, as it would result in additional memory complexity. I guess it really depends on all the possible use cases for the script. If valid request id's also need to be periodically queried, then all of the log should be stored in each 'logNode' object. However, if the logs only need to be checked for error codes, the entire log would not need to be stored indefinitely in the 'logNode' class. One could find all unique values for the 'code' column and if 500 exists, return the request id and if not, don't store the log.
- I added created classes for each log file and manually set their children, which would obviously not scale well when the number of devices increases. To resolve this issue, a dictionary could potentially be used to keep track of the different levels of the "graph" and the respective children/subsequent logs for each log.
- Another aspect that would need to be changed, which is related to the previous point, is a more robust way for structuring the relationships between each log. For this given problem, just a single node exists at the top level; however, if multiple nodes existed, each of them would need to be explored, along with their subsequent child nodes/logs, i.e. I would most likely not be able to just add alpha straght into the queue because other devices could exist at the same level as alpha, but error at an earlier time.
- Only serial computing was used here, but with hundres of logs, each with millions of parameters, it may be advantageous to implement parallel computing strategies, such that multiple logs could be analyzed at the same time.
