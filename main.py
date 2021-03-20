import numpy as np
import queue
import os
import pandas as pd
import glob
import json
from log_classes import error_check, no_error_check, log_file_parse,print_error
from log_classes import logNode
def main():
    # File Path Setup
    log_path = os.path.join(os.getcwd(),'logs','*.log')
    log_path = glob.glob(log_path)
    log_path.sort()

    # Parse and create 'logNode' classes for logs
    alpha, beta, gamma, delta, epsilon = log_file_parse(log_path)
    service_dict = {'alpha':alpha,'beta':beta,'gamma':gamma,
                   'delta':delta,'epsilon':epsilon}
    
    # Add root log to queue
    q = queue.Queue(0)
    q.put(alpha)
    error_not_found = 0
    visited_logs = []
    error_ids = []
    while error_not_found==0:
        current_log = q.get()
        unique_error_id = no_error_check(current_log,visited_logs)

        # Check for no errored entries
        if unique_error_id == 0:
            error_not_found=1
            check_val = None
            break
        else:
            if unique_error_id not in error_ids:
                error_ids.append(unique_error_id)

            # Determine if the error occurs at the current service or if at a service further downstream.
            check_val, next_iter = error_check(current_log,visited_logs,
                                               error_ids,service_dict)
            # Error Downstream, so add the next node
            if next_iter is not None:
                q.put(check_val)

            # Error in current node, so break
            else:
                error_not_found=2
                break

    print_error(error_not_found,check_val,visited_logs,error_ids)


if __name__=="__main__":
    main()