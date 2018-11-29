import datetime

def get_days_since_last(entry):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # hardcoded to CET

    return (now - entry.timestamp).days

def get_all(entries, scope_from=None, scope_to=None):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1) # hardcoded to CET
    stats = {}

    stats["now"] = now  # current datetime
    stats["first"] = 0  # first entry (in scope)
    stats["last"] = 0   # last entry (in scope)
    stats["total"] = 0  # total nr of entries (in scope)
    stats["average_a_day"] = 0  # average nr of entries per day, first and last days are inclusive
    stats["days_since_last"] = 0    # nr of days since last. Only relevant if no scope is set
    stats["max_in_a_day"] = 0   # max numbers of entries in one day
    stats["max_in_a_day-date"] = "0000-00-00"   # date for max_in_a_day value
    stats["longest_without"] = 0    # longest nr of days without any entry
    stats["longest_without_start"] = "0000-00-00"   # start date for longest_without
    stats["longest_without_end"] = "0000-00-00" # end date for longest_without
    stats["total_today"] = 0    # total nr of entries today
    stats["total_nr_of_days"] = 0   # total nr of days in search scope

    if entries.count() > 0:
        stats["first"] = entries[0].timestamp
        stats["last"] = entries[entries.count()-1].timestamp
        stats["total"] = entries.count()
        if scope_from and scope_to:
            stats["total_nr_of_days"] = (scope_to - scope_from).days + 1 # +1 to include scope_to
        else:
            stats["total_nr_of_days"] = (now.date() - stats["first"].date()).days + 1 # +1 to iunclude current day
        print(stats["total_nr_of_days"])
        if stats["total_nr_of_days"] == 0:
            stats["total_nr_of_days"] = 1   # set nr of days to 1 to prevent division by 0
        stats["average_a_day"] = round(stats["total"]/stats["total_nr_of_days"], 2)
        stats["days_since_last"] = (now - stats["last"]).days

        tempdate = 0
        temp_max_in_a_day = 0
        for i,entry in enumerate(entries):
            # calculates max_in_a_day
            if entry.timestamp.date() == tempdate:
                temp_max_in_a_day += 1
            else:
                tempdate = entry.timestamp.date()
                temp_max_in_a_day = 1
            # sets max_in_a_day and max_in_a_day-date
            if temp_max_in_a_day > stats["max_in_a_day"]:
                stats["max_in_a_day"] = temp_max_in_a_day
                stats["max_in_a_day-date"] = tempdate

            # calculates total_today
            if entry.timestamp.date() == now.date():
                stats["total_today"] += 1

            # calculates longest_without, skipping the first entry to be able to use i-1
            if i > 0:
                temp_date_diff = (entry.timestamp - entries[i-1].timestamp).days
                if temp_date_diff > stats["longest_without"]:
                    stats["longest_without"] = temp_date_diff
                    stats["longest_without_start"] = entries[i-1].timestamp.date()
                    stats["longest_without_end"] = entry.timestamp.date()

        # if the current streak is longer than the longest streak between two entries
        if stats["days_since_last"] > stats["longest_without"]:
            stats["longest_without"] = stats["days_since_last"]
            stats["longest_without_start"] = entries[entries.count()-1].timestamp.date()
            stats["longest_without_end"] = now.date()

    return stats
