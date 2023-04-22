from datetime import timedelta

def missing_data(data: list):
    """
    Detects when there are data points missing.

    Arguments
    data: [[value, time]]

    Returns
    len_missing: total amount of time missing from data
    where_missing: [(s, t)], where s is missing period start, t is missing period end
    """
    dt = int(timedelta(hours=24).total_seconds()*1000)
    len_missing = 0
    where_missing = []
    total = int((data[len(data)-1][1] - data[0][1])/dt)
    for i in range(len(data) - 1):
        # print((data[i+1][1] - data[i][1])/dt)
        if data[i+1][1] - data[i][1] != dt:
            len_missing += int((data[i+1][1] - data[i][1])/dt)
            where_missing.append((data[i][1], data[i+1][1]))
    # percent_missing = int((num_missing / total)*100)
    return len_missing, where_missing

def clean_data(data: list):
    """
    Fills in missing data and orders data points by time.

    Arguments
    data: raw data

    Returns
    cleaned: (d x n)-dimensional ndarray, where series[0] is the time index, and there are d - 1 time-series
    """
    # TODO
    pass