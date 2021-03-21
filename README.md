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

One can see that the error seems to a failed connection between service delta and epsilon, as the unique request id found in alpha, beta, and delta, which should have been sent to epsilon, is not found. "When the problem first begins" can be interpreted in a couple of ways. First, one could argue that the problem begins when service alpha has its first '500' value, i.e. an errored request. If that is the case, the problem first begins at: **2021-03-12T13:13:55.369835000**. Alternatively, the problem could be thought to have begun as early as the last valid message sent to service E before the problem arises. To do this, the timestamp closest in service epsilon that was closest to the timestamp of the first errored request in service D was found. With this approach, service epsilon could have become faulty immediately after ***2021-03-12T13:13:14.142511000***.
