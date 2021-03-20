import os
import json
import pandas as pd
import numpy as np
class logNode:
    def __init__(self,log_path):
        if os.path.exists(log_path):
            
            # Create list of dictionaries using each line of the log file
            list_of_dicts = []
            with open(log_path) as log:
                for lines in log:
                    list_of_dicts.append(json.loads(lines))
                    
            # Convert List of dictionaries to a pandas dataframe and set datetime
            self.log_data = pd.DataFrame(list_of_dicts)
            self.log_size = len(self.log_data)
            self.log_data['ts'] = pd.to_datetime(self.log_data['ts'],format='%Y-%m-%dT%H:%M:%S')
            self.name = self.log_data.source.values[0]
            self.log_data.set_index(self.log_data.ts,inplace=True)
            
            # Checking for an error in the log using the 500 error code
            # If an error code exists, get earliest error message and set
            # class attributes for:
            #         - Time of first Error
            #         - Text of first Error
            #         - Unique ID of first Error
            #         - Error code of first Error (500)
            if 500 in self.log_data.code.values:
                errors_in_log = self.log_data.loc[self.log_data.code==500]
                self.first_error_time = errors_in_log['ts'].values[0]
                self.first_error_text = errors_in_log['text'].values[0]
                self.first_error_id = errors_in_log['id'].values[0]
                self.first_error_code = errors_in_log['code'].values[0]
            else: # If an error does not exist, set all four previous class attributes to a value of 'None'
                self.first_error_time = None
                self.first_error_text = None
                self.first_error_id = None
                self.first_error_code = None
            self.children = None
        else:
            raise ValueError('File does not exist')
            
    # Add child nodes as a list of strings
    # The string should equal the logfile/child nodes name, i.e. ['beta','gamma',...]
    def add_child(self,children):
        if len(children)>0:
            self.children=children
        else:
            raise ValueError("Missing node")
            
    # Check whether a unique request id exists in this log
    # Does not exist: text = 0
    # Exists: text = text attribute of log file for specific index where the unique id exists 
    def id_code_check(self,unique_id):
        df_unique_id = self.log_data.loc[self.log_data.id==unique_id]
        if len(df_unique_id)==0:
            text = 0
        else:
            text = df_unique_id['text'].values[0]
        return len(df_unique_id), text

# Create classes for each file in '.\log' directory and assign children
def log_file_parse(log_path):
    alpha = logNode(log_path[0])
    beta = logNode(log_path[1])
    gamma = logNode(log_path[4])
    delta = logNode(log_path[2])
    epsilon = logNode(log_path[3])
    
    alpha.add_child(['beta','gamma'])
    beta.add_child(['delta','epsilon'])
    gamma.add_child(['delta','epsilon'])
    delta.add_child(['epsilon'])
    
    return alpha, beta, gamma, delta, epsilon


##### Checking if the root node even has any errors #####
# It is assumed an error in any branch of the service tree will create an error in the root service
def no_error_check(log,visited_logs):
    
    # If no error exists in the root service: 
    #     - check_val = 0 (break out of loop)
    if len(visited_logs)<1 and log.first_error_id is None:
        check_val = 0
    
    # If an error exists:
    #     - return the request id of the first errored entry
    else: 
        check_val = log.first_error_id
    visited_logs.append(log)
    
    return check_val



# Function is called if an error exists in the root service
def error_check(log,visited_logs,error_ids,service_dict):
    
    # Invalid termination of root server
    if len(visited_logs)==1 and log.first_error_text=='request terminated':
        check = 1
        next_iter = None
    
    # Error does not end in root service, so a message is sent to at least one other service
    else:
        # Get earliest error id from root service and find the 
        # child service that the message was sent to
        unique_error_id = error_ids[-1]
        next_node_name = log.first_error_text.split(' ')[-1]
        next_node = service_dict[next_node_name]
        
        # Check if error code exists in child service
        errorID_in_next_node, text = next_node.id_code_check(error_ids[-1])
        
        # Error id missing from child
        if errorID_in_next_node==0:
            check = 2
            visited_logs.append(next_node)
            next_iter = None
            
        # Error id in child
        else:
            # Error ends at the child node
            if text=='request terminated':
                check = 3
                next_iter = None
                visited_logs.append(next_node)
                
            # Error does not end at this child node. Thus, it must be added to the queue.
            else:
                check = next_node
                next_iter = 1
                
    return check, next_iter



def print_error(error_not_found,check_val,visited_logs,error_ids):
    
    # No error exists in root service, so it is assumed no error exists in any service
    if error_not_found == 1:
        print("No Errors in service")
    
    else:
        # Retrieve first error id and last service visited
        unique_error_id = error_ids[-1]
        error_service = visited_logs[-1]
        
        # Invalid termination error - a service  intermittently failing
        # 1: Invalid termination at root service
        # 3: Invalid termination at a non-root service
        if check_val==1 or check_val==3:
            error_time = error_service.log_data.loc[error_service.log_data.id==unique_error_id]
            error_time = error_time['ts'].values[0]
            print("Invalid Request Termination")
            print(" ")
            print(f"Service: {error_service.name}")
            print(f"ID: {unique_error_id}")
            print(f"Time: {error_time}")
            
        # Unique Request ID not in a service - failed connectivity between services
        else:
            # Last service with request id and the time that message was received
            last_valid_service = visited_logs[-2]
            time_last_valid = last_valid_service.log_data.loc[last_valid_service.log_data.id==unique_error_id]
            time_last_valid = time_last_valid['ts'].values[0]
            
            # Find the last time the errored service received a message before the errors occurred.
            # This involves finding the closest time in the errored service to the 'time_last_valid' value
            # Basically, at what time did the service start functioning improperly
            ind_before_errors = error_service.log_data.index.get_loc(time_last_valid,method='nearest')
            closest_times = error_service.log_data.iloc[ind_before_errors-1:ind_before_errors+1]['ts'].values
            if closest_times[1]<time_last_valid:
                close_time = closest_times[1]
            else:
                close_time = closest_times[0]
                
            print("Unique ID not found - Failed Connectivity")
            print(" ")
            print(f"Request ID: {error_ids[-1]}")
            print(f"Service: {error_service.name}")
            print(f"Time of last message before error: {close_time}")
            print(" ")
            print("Message Send Time:")
            for i in visited_logs[:-1]:
                message_time = i.log_data.loc[i.log_data.id==unique_error_id]
                message_time = message_time['ts'].values[0]
                print(f"Service: {i.name},  Timestamp: {message_time}")
            print(" ")