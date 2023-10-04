import datetime


# Wirte log in dir_file and save
log_file_path = "/srv/bench/frappe-bench/apps/frappe/frappe/API/TCTM/system_log.log"

def write_log(log_text):
    current_datetime = datetime.datetime.now()
    try:
        with open(log_file_path, "a") as f:
            f.write(f'{current_datetime} {log_text}\n')
            f.flush()
        return True
    except Exception as e:
        print(f"An error occurred while writing to the log file: {str(e)}")
        return False