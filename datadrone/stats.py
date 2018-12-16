import datetime
import calendar
from collections import defaultdict

def get_days_since_last(entry):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # hardcoded to CET

    return (now - entry.timestamp).days

def get_all(entries, scope_from=None, scope_to=None, days=None):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1) # hardcoded to CET
    now_date = now.date()
    stats = {}

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
    stats["nr_of_entrytags"] = defaultdict(int) # dictionary of all tags and how many of each of them
    stats["longest_streak"] = 0 # max nr of days in a row with at least 1 entry
    stats["longest_streak_start"] = "0000-00-00" # start date for longest_streak
    stats["longest_streak_end"] = "0000-00-00" # end date for longest_streak
    stats["weekday"] = { "Monday":0, "Tuesday":0, "Wednesday":0, "Thursday":0, "Friday":0, "Saturday":0, "Sunday":0 } # dictinoary of all weekdays and how many of each of them

    if entries.count() > 0:
        stats["first"] = entries[0].timestamp
        stats["last"] = entries[entries.count()-1].timestamp
        stats["total"] = entries.count()
        if scope_from and scope_to:
            stats["total_nr_of_days"] = (scope_to - scope_from).days + 1 # +1 to include scope_to
        elif days:
            stats["total_nr_of_days"] = days
        else:
            stats["total_nr_of_days"] = (now_date - stats["first"].date()).days + 1 # +1 to iunclude current day
        if stats["total_nr_of_days"] == 0:
            stats["total_nr_of_days"] = 1   # set nr of days to 1 to prevent division by 0
        stats["average_a_day"] = round(stats["total"]/stats["total_nr_of_days"], 2)
        stats["longest_streak"] = 1
        stats["longest_streak_start"] = stats["first"].date()
        stats["longest_streak_end"] = stats["first"].date()
        stats["days_since_last"] = (now - stats["last"]).days

        tempdate = 0
        temp_max_in_a_day = 0
        temp_longest_streak = 1
        temp_longest_streak_start = stats["longest_streak_start"]
        temp_longest_streak_end = stats["longest_streak_end"]

        for i,entry in enumerate(entries):
            entry_date = entry.timestamp.date()
            prev_entry_date = entries[i-1].timestamp.date()

            # calculates nr_of_entrytags
            for entrytag in entry.entrytags:
                if not entrytag.tag.deleted:
                    stats["nr_of_entrytags"][entrytag.tag.name] += 1

            # calculates max_in_a_day
            if entry_date == tempdate:
                temp_max_in_a_day += 1
            else:
                tempdate = entry_date
                temp_max_in_a_day = 1
            # sets max_in_a_day and max_in_a_day-date
            if temp_max_in_a_day > stats["max_in_a_day"]:
                stats["max_in_a_day"] = temp_max_in_a_day
                stats["max_in_a_day-date"] = tempdate

            # calculates total_today
            if entry_date == now_date:
                stats["total_today"] += 1

            # calculates weekday average
            print()
            stats["weekday"][calendar.day_name[entry_date.weekday()]] += 1

            if i > 0:
                # calculates longest_without
                temp_date_diff = (entry.timestamp - entries[i-1].timestamp).days
                if temp_date_diff > stats["longest_without"]:
                    stats["longest_without"] = temp_date_diff
                    stats["longest_without_start"] = prev_entry_date
                    stats["longest_without_end"] = entry_date

                # calculates longest_streak
                if (entry_date - prev_entry_date).days == 1:  # if last entry was 1 day ago
                    temp_longest_streak += 1
                    temp_longest_streak_end = entry_date
                elif (entry_date - prev_entry_date).days != 0:    # resets streak unless its multiple entries the same day
                    temp_longest_streak = 1
                    temp_longest_streak_start = entry_date

                if temp_longest_streak > stats["longest_streak"]:
                    stats["longest_streak"] = temp_longest_streak
                    stats["longest_streak_start"] = temp_longest_streak_start
                    stats["longest_streak_end"] = temp_longest_streak_end

        # if the current streak is longer than the longest streak between two entries
        if stats["days_since_last"] > stats["longest_without"]:
            stats["longest_without"] = stats["days_since_last"]
            stats["longest_without_start"] = entries[entries.count()-1].timestamp.date()
            stats["longest_without_end"] = now_date
    return stats
