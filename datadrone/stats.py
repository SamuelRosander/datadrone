import datetime

def get_days_since_last(entry):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    return (now - entry.timestamp).days

def get_all(entries):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    stats = {}

    stats["now"] = now
    stats["first"] = 0
    stats["last"] = 0
    stats["total"] = 0
    stats["average_a_day"] = 0
    stats["days_since_last"] = 0
    stats["max_in_a_day"] = 0
    stats["max_in_a_day-date"] = "0000-00-00"
    stats["longest_without"] = 0
    stats["longest_without_start"] = "0000-00-00"
    stats["longest_without_end"] = "0000-00-00"
    stats["total_today"] = 0

    if entries.count() > 0:
        stats["first"] = entries[0].timestamp
        stats["last"] = entries[entries.count()-1].timestamp
        stats["total"] = entries.count()
        stats["average_a_day"] = round(stats["total"]/(now - stats["first"]).days, 2)
        stats["days_since_last"] = (now - stats["last"]).days

        tempdate = 0
        temp_max_in_a_day = 0
        for i,entry in enumerate(entries):
            if entry.timestamp.date() == tempdate:
                temp_max_in_a_day += 1
            else:
                tempdate = entry.timestamp.date()
                temp_max_in_a_day = 1

            if temp_max_in_a_day > stats["max_in_a_day"]:
                stats["max_in_a_day"] = temp_max_in_a_day
                stats["max_in_a_day-date"] = tempdate

            if entry.timestamp.date() == now.date():
                stats["total_today"] += 1

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
