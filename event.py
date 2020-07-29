from win32gui import GetWindowText, GetForegroundWindow
from time import sleep, time
from os import fdopen
from uiautomation import ControlFromHandle

# insert activity for a day
def create_activity(activity, seconds, date):
    with open(date + ".txt", "a+") as f1:
        line = activity_exists(activity, date + ".txt")
        if type(line) == bool:
            minute = round(int(seconds) / 60)
            seconds = int(seconds) % 60
            hour = round(int(minute) / 60)
            minute %= 60
            f1.write(
                activity
                + ",-,"
                + str(hour)
                + ",-,"
                + str(minute)
                + ",-,"
                + str(seconds)
                + "\n"
            )
        else:
            new_line = line.split(",-,")
            new_line[3] = int(int(new_line[3].replace("\n", ""))) + int(seconds)
            new_line[2] = int(new_line[2]) + int(int(new_line[3]) / 60)
            new_line[3] = int(new_line[3]) % 60
            new_line[1] = int(new_line[1]) + int(int(new_line[2]) / 60)
            new_line[2] = int(new_line[2]) % 60
            replace = (
                str(new_line[0])
                + ",-,"
                + str(new_line[1])
                + ",-,"
                + str(new_line[2])
                + ",-,"
                + str(new_line[3])
                + "\n"
            )
            update_file(line, replace, date + ".txt")


# Used to update file if activity exists
def update_file(old_line, new_line, filename):
    with open(filename, "r+") as f1:
        copy = f1.readlines()
        f1.seek(0)
        f1.truncate(0)
        for i in range(0, len(copy)):
            if copy[i] != old_line:
                f1.write(copy[i])
            else:
                f1.write(new_line)


# Used to remove entry
def remove_entry(activity, filename):
    old_line = activity_exists(activity, filename)
    with open(filename, "r+") as f1:
        copy = f1.readlines()
        f1.seek(0)
        f1.truncate(0)
        for i in range(0, len(copy)):
            if copy[i] != old_line:
                f1.write(copy[i])


# Returns list of events from specfied day
def load_day(date):
    try:
        with open(date + ".txt", "r") as f1:
            return [i.split(",-,") for i in f1.readlines()]
    except:
        return False


# Return False if activity doesn't exist, otherwise returns activity
def activity_exists(activity, filename):
    with open(filename, "r+") as f1:
        for line in f1:
            if line.split(",-,")[0].lower() == activity.lower():
                return line
        return False


# Change whether evemt is productive
def change_productivity(event, event_type, productive):
    line = activity_exists(event, event_type + "_productivity.txt")
    update_file(
        line, event + ",-," + productive + "\n", event_type + "_productivity.txt"
    )


# add app as productive or unproductive
def add_productivity(event, event_type, productive):
    if type(activity_exists(event, event_type + "_productivity.txt")) == bool:
        with open(event_type + "_productivity.txt", "a+") as f1:
            f1.write(event + ",-," + productive + "\n")


# return whether event is productive
def is_productive(event_type, event):
    try:
        with open(event_type + "_productivity.txt", "r") as f1:
            for i in f1.readlines():
                if i.split(",-,")[0] == event and (
                    i.split(",-,")[1].replace("\n", "").lower() == "unproductive"
                ):
                    return False
            return True
    except:
        return ""


# returns list of productivity
def get_productivity(event_type):
    try:
        with open(event_type + "_productivity.txt", "r") as f1:
            return [i.split(",-,") for i in f1.readlines()]
    except:
        return False


# return foreground window
def get_foreground_window():
    return GetForegroundWindow()


# returns what window is currently focused
def current_app():
    return GetWindowText(GetForegroundWindow()).split("- ")[-1]


# returns current web page or file name that is being used in the currently focused window
def current_app_activity():
    try:
        return GetWindowText(GetForegroundWindow()).split("- ")[-2]
    except:
        return "None"


# return browser url
def get_url(window):
    windowControl = ControlFromHandle(window)
    edit = windowControl.EditControl()
    if 'firefox' in (GetWindowText(window)).lower() or 'edge' in (GetWindowText(window)).lower():
        return str(edit.GetValuePattern().Value).partition(".")[2].replace('www.', '').partition("/")[0]
    # Need to add solution in for using chrome
    return str(edit.GetValuePattern().Value).partition("/")[0]


# returns correctly formatted day from datetime package
def get_date(day):
    date = str(day).split("-")
    return date[1] + "_" + date[2] + "_" + date[0]
