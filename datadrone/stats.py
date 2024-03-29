import datetime
import calendar
from collections import defaultdict


def get_time_since_last(entry):
    now = datetime.datetime.utcnow()

    diff = now - entry.utc_timestamp
    diffs = diff.seconds
    diffd = diff.days

    # handling negative entries (entry is set in the future)
    if diffd < 0:
        diffs = diffs - 86400
        diffd = diffd + 1

    # abs() for handling negative entries
    # int() instead of floor() for correct rounding on negative entries
    if abs(diffd) < 1:
        if abs(diffs) == 1:
            return str(diffs) + " second ago"
        elif abs(diffs) < 60:
            return str(diffs) + " seconds ago"
        elif abs(diffs) < 120:
            return str(int(diffs/60)) + " minute ago"
        elif abs(diffs) < 3600:
            return str(int(diffs/60)) + " minutes ago"
        elif abs(diffs) < 7200:
            return str(int(diffs/3600)) + " hour ago"
        else:
            return str(int(diffs/3600)) + " hours ago"
    elif abs(diffd) < 2:
        return str(diffd) + " day ago"
    else:
        return str(diffd) + " days ago"


def get_all(entries, scope_from=None, scope_to=None, days=None):
    utcnow = datetime.datetime.utcnow()
    # hardcoded to CET
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    now_date = now.date()
    stats = dict()

    stats["first"] = 0  # first entry (in scope)
    stats["last"] = 0  # last entry (in scope)
    stats["total"] = 0  # total nr of entries (in scope)
    # average nr of entries per day, first and last days are inclusive
    stats["average_a_day"] = 0
    # nr of days since last. If scope it will use scope_to as last day
    stats["days_since_last"] = "-"
    stats["max_in_a_day"] = 0  # max numbers of entries in one day
    stats["max_in_a_day-date"] = "0000-00-00"  # date for max_in_a_day value
    stats["longest_without"] = 0  # longest nr of days without any entry
    # start date for longest_without
    stats["longest_without_start"] = "0000-00-00"
    stats["longest_without_end"] = "0000-00-00"  # end date for longest_without
    stats["total_today"] = 0  # total nr of entries today
    stats["total_nr_of_days"] = 0  # total nr of days in search scope
    # counting how many entries for each tag
    stats["nr_of_entrytags"] = defaultdict(int)
    # max nr of days in a row with at least 1 entry
    stats["longest_streak"] = 0
    # start date for longest_streak
    stats["longest_streak_start"] = "0000-00-00"
    stats["longest_streak_end"] = "0000-00-00"  # end date for longest_streak
    # counting how many entries for each day
    stats["weekday"] = {
        "Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0,
        "Saturday": 0, "Sunday": 0}
    # counting how many entries in each time slot
    stats["time_of_day"] = {"00-04": 0, "04-08": 0, "08-12": 0, "12-16": 0,
                            "16-20": 0, "20-24": 0}

    if entries:
        stats["first"] = entries[0]["timestamp"]
        stats["last"] = entries[-1]["timestamp"]
        stats["total"] = len(entries)
        if scope_from and scope_to:
            stats["total_nr_of_days"] = (
                scope_to - scope_from).days + 1
        elif days:
            stats["total_nr_of_days"] = days
        else:
            stats["total_nr_of_days"] = (
                now_date - stats["first"].date()).days + 1
        if stats["total_nr_of_days"] == 0:
            stats["total_nr_of_days"] = 1
        stats["average_a_day"] = round(
            stats["total"] / stats["total_nr_of_days"], 2)
        stats["longest_streak"] = 1
        stats["longest_streak_start"] = stats["first"].date()
        stats["longest_streak_end"] = stats["first"].date()
        if scope_to:
            scope_end_datetime = datetime.datetime.combine(
                scope_to, datetime.time(23, 59, 59))
            stats["days_since_last"] = (
                scope_end_datetime - entries[-1]["utc_timestamp"]).days
        else:
            stats["days_since_last"] = (
                utcnow - entries[-1]["utc_timestamp"]).days

        tempdate = 0
        temp_max_in_a_day = 0
        temp_longest_streak = 1
        temp_longest_streak_start = stats["longest_streak_start"]
        temp_longest_streak_end = stats["longest_streak_end"]

        for i, entry in enumerate(entries):
            entry_date = entry["timestamp"].date()

            # calculates nr_of_entrytags
            for entrytag in entry["entrytags"]:
                if not entrytag.tag.deleted and not entrytag.tag.archived:
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

            # calculates weekday
            stats["weekday"][calendar.day_name[entry_date.weekday()]] += 1

            # calculates time_of_day
            hour = entry["timestamp"].hour
            if hour >= 20:
                stats["time_of_day"]["20-24"] += 1
            elif hour >= 16:
                stats["time_of_day"]["16-20"] += 1
            elif hour >= 12:
                stats["time_of_day"]["12-16"] += 1
            elif hour >= 8:
                stats["time_of_day"]["08-12"] += 1
            elif hour >= 4:
                stats["time_of_day"]["04-08"] += 1
            else:
                stats["time_of_day"]["00-04"] += 1

            # calculations between 2 dates, skip 1st entry to be able to
            # compare with entry[i-1]
            if i > 0:
                prev_entry_date = entries[i - 1]["timestamp"].date()

                # calculates longest_without
                temp_date_diff = (entry["timestamp"] -
                                  entries[i - 1]["timestamp"]).days
                if temp_date_diff > stats["longest_without"]:
                    stats["longest_without"] = temp_date_diff
                    stats["longest_without_start"] = prev_entry_date
                    stats["longest_without_end"] = entry_date

                # calculates longest_streak
                if (entry_date - prev_entry_date).days == 1:
                    # if last entry was 1 day ago
                    temp_longest_streak += 1
                    temp_longest_streak_end = entry_date
                elif (entry_date - prev_entry_date).days != 0:
                    temp_longest_streak = 1
                    temp_longest_streak_start = entry_date

                if temp_longest_streak > stats["longest_streak"]:
                    stats["longest_streak"] = temp_longest_streak
                    stats["longest_streak_start"] = temp_longest_streak_start
                    stats["longest_streak_end"] = temp_longest_streak_end

        if stats["days_since_last"] > stats["longest_without"]:
            stats["longest_without"] = stats["days_since_last"]
            stats["longest_without_start"] = entries[-1]["timestamp"].date()
            if scope_to:
                stats["longest_without_end"] = scope_to
            else:
                stats["longest_without_end"] = now_date
    return stats
