import datetime

def timestamp():
    """
    function produces an actual timestamp
    :return: timestamp as String
    """
    current_time = datetime.datetime.now()
    time_stamp = current_time.strftime("%d-%m-%y_%H-%M-%S")
    return_time = "%s" % time_stamp
    return time_stamp

print(timestamp())

