from tkinter import (
    filedialog,
    ttk,
    Label,
    Tk,
    Frame,
    Canvas,
    Scrollbar,
    Button,
    VERTICAL,
    HORIZONTAL,
    OptionMenu,
    StringVar,
    Text,
    INSERT,
    END,
)
from tkcalendar import Calendar, DateEntry
from time import sleep, time
from datetime import date, timedelta
from os import path
import threading
import event
import schedule

# Check if tracker for day exist and productivity files exist
if not path.exists(event.get_date(date.today()) + ".txt"):
    open(event.get_date(date.today()) + ".txt", "w")
if not path.exists("event_productivity.txt"):
    open("event_productivity.txt", "w")
if not path.exists("website_productivity.txt"):
    open("website_productivity.txt", "w")

# Schedule task of creating new file for next day in case someone uses the program from one day to the next
def make_day():
    open(event.get_date(date.today() + timedelta(days=1)) + ".txt", "w")
schedule.every().day.at("23:59").do(make_day)


# Setup window
today_date = event.get_date(date.today())
main = Tk()
main.title("Easy Track")
height = "1280"
width = "720"
main.geometry(str(height) + "x" + str(width))
main.configure(bg="gray87")
main.resizable(0, 0)
started = False
seconds = 0
last_app = event.current_app()
try:
    last_url = event.get_url(event.get_foreground_window())
except:
    last_url = ""
productive_color = StringVar(main, "Productive Color: green")
unproductive_color = StringVar(main, "Unproductive Color: red")
browser_list = ['mozilla firefox', 'google chrome', 'microsoft edge']


# clear all info from page for transitions
def clear_window():
    list_to_keep = [
        "label",
        "label2",
        "label2",
        "label3",
        "label4",
        "separator",
        "separator2",
        "separator3",
    ]
    for widget in main.winfo_children():
        if not str(widget).replace(".!", "") in list_to_keep:
            widget.destroy()


# Sets up menu labels
def Menu_Label(label_info, position, top_bar, bottom_bar):
    label = Label(main, text=label_info, bg="gray87", font=("Courier", 18))

    def change_menu(event=None):
        top_bar.place(x=0, y=30 + position * (120), relwidth=0.24)
        bottom_bar.place(x=0, y=80 + position * (120), relwidth=0.24)
        clear_window()
        if label_info == "Home":
            menu_home(today_date)
        elif label_info == "Add activity":
            menu_add_activity()
        elif label_info == "Productivity Settings":
            menu_productivity_settings()
        elif label_info == "Settings & Support":
            menu_settings_support()

    def default_menu_button_color(event=None):
        label.config(fg="gray50")

    def hover_menu_button_color(event=None):
        label.config(fg="black")

    label.bind("<Button-1>", change_menu)
    label.bind("<Enter>", default_menu_button_color)
    label.bind("<Leave>", hover_menu_button_color)
    if position == 0:
        top_bar.place(x=0, y=30, relwidth=0.24)
        bottom_bar.place(x=0, y=80, relwidth=0.24)
    return label


# pulls menu bar up on left side of screen
def menu_bar():
    top_bar = ttk.Separator(main, orient="horizontal")
    bottom_bar = ttk.Separator(main, orient="horizontal")
    ttk.Separator(main, orient=VERTICAL).place(x=310, y=0, relheight=1)
    menu_text = [
        "Home",
        "Add activity",
        "Productivity Settings",
        "Settings & Support",
    ]
    label_list = [
        Menu_Label(menu_text[i], i, top_bar, bottom_bar)
        if i < 3
        else Menu_Label(menu_text[i], i + 2, top_bar, bottom_bar)
        for i in range(0, 4)
    ]
    for i in range(0, len(label_list)):
        if i != len(label_list) - 1:
            label_list[i].place(x=5, y=120 * (i) + 40)
        else:
            label_list[i].place(x=5, y=120 * (i + 2) + 40)


# Productivity event box
def load_day_productivity(date):
    frame_event = Frame(main)
    frame_event.place(x=800, y=200)
    event_list = Canvas(frame_event, width=370, height=350)
    scroll = Scrollbar(frame_event, orient=VERTICAL, command=event_list.yview)
    frame = Frame(event_list)
    events = event.load_day(date)
    if type(events) == bool:
        Label(frame, text="Nothing", font=("Helvetica", 16), anchor="w").pack(
            fill="both"
        )
    else:
        for i in events:
            current_event = i[0] + "\t\t\t\t\t"
            current_event_time = i[1] + "Hrs\t" + i[2].replace("\n", "") + "Mins\n"
            if int(i[2]) < 1 and int(i[1]) < 1:
                continue
            color = ""
            if event.is_productive("event", i[0]):
                color = productive_color.get().split(" ")[-1]
            else:
                color = unproductive_color.get().split(" ")[-1]
            Label(
                frame, text=current_event, font=("Helvetica", 20), anchor="w", bg=color
            ).pack(fill="both")
            Label(
                frame, text=current_event_time, font=("Helvetica", 14), anchor="w"
            ).pack(fill="both")
            # ttk.Separator(frame_event).place(x=0,y=0,relwidth=.94)
    event_list.create_window(0, 0, window=frame, anchor="nw")
    event_list.update_idletasks()
    event_list.configure(scrollregion=event_list.bbox("all"), yscrollcommand=scroll.set)
    event_list.pack(fill="both", expand=True, side="left")
    scroll.pack(fill="y", side="right")


# Place calendar in window
def place_calendar():
    cal = Calendar(main, font=("Helvetica", 15), selectmode="day", cursor="hand2")
    cal.place(x=350, y=250)
    Button(
        main,
        text="Load Day",
        command=lambda: load_day_productivity(event.get_date(cal.selection_get())),
    ).place(x=500, y=500)


# Update time for websites
def website_time_update(this_app, seconds, url):
    if this_app.lower() in browser_list:
        if event.is_productive("website", last_url):
            event.create_activity("Productive Website", seconds, today_date)
        else:
            event.create_activity("Unproductive Website", seconds, today_date)
    else:
        event.add_productivity(this_app, "event", "productive")
        event.create_activity(this_app, seconds, today_date)


# Update app activity
def tracker():
    global seconds, last_app, last_url
    schedule.run_pending()
    new_app = event.current_app()
    new_url = ""
    if new_app.lower() in browser_list:
        try:
            new_url = event.get_url(event.get_foreground_window())
        except:
            new_url = ""
    if new_app.lower() in browser_list:
        if new_url != "":
            event.add_productivity(new_url, "website", "productive")
            if last_app.lower() in browser_list:
                new_prod = event.is_productive("website", new_url)
                old_prod = event.is_productive("website", last_url)
                if new_prod != old_prod:
                    minutes = int(round(seconds / 60))
                    seconds %= 60
                    hours = int(round(minutes / 60))
                    minutes %= 60
                    if old_prod:
                        event.create_activity("Productive Website", seconds, today_date)
                    else:
                        event.create_activity(
                            "Unproductive Website", seconds, today_date
                        )
                    seconds = 0
                    last_url = new_url
    if not new_app == last_app:
        if seconds > 0:
            website_time_update(last_app, seconds, last_url)
        seconds = 0
    elif seconds % 30 == 0 and (seconds - 1) % 30 == 29:
        website_time_update(new_app, seconds, new_url)
        seconds = 0
    if started:
        seconds += 3
        last_app = event.current_app()
        if last_app.lower() in browser_list:
            try:
                last_url = event.get_url(event.get_foreground_window())
            except:
                last_url = last_url
        threading.Timer(3, tracker).start()
    else:
        if seconds > 10:
            website_time_update(new_app, seconds, new_url)


# Productivity tracker start
def tracker_start(start_button, stop_button):
    global started
    started = True
    start_button.place_forget()
    stop_button.place(x=365, y=100)
    tracker()


# Productivity tracker stop
def tracker_stop(start_button, stop_button):
    global started
    started = False
    start_button.place(x=365, y=100)
    stop_button.place_forget()


# load home page
def menu_home(date):
    start_button = Button(main, font=("Arial 15"), text="Start Tracker", width=30,)
    stop_button = Button(main, font=("Arial 15"), text="Stop Tracker", width=30,)
    start_button.config(command=lambda: tracker_start(start_button, stop_button))
    stop_button.config(command=lambda: tracker_stop(start_button, stop_button))
    if not started:
        start_button.place(x=365, y=100)
    else:
        stop_button.place(x=365, y=100)
    place_calendar()
    load_day_productivity(date)


# load Detailed Summary
def menu_detailed_summary(date):
    return


# load Add activity
def menu_add_activity():
    productive_list = ["productive", "unproductive"]
    activity_productivity = StringVar(main, "productive")
    productive_dropdown = OptionMenu(main, activity_productivity, *productive_list)
    productive_dropdown.config(width=20, font=("Helvetica", 14))

    title_lbl = Label(main, text="Activity Title:", font=("Helvetica", 20), bg="gray87")
    time_lbl = Label(main, text="Time Spent:", font=("Helvetica", 20), bg="gray87")
    min_lbl = Label(main, text="Minutes", font=("Helvetica", 20), bg="gray87")
    hr_lbl = Label(main, text="Hours", font=("Helvetica", 20), bg="gray87")
    date_lbl = Label(main, text="Date:", font=("Helvetica", 20), bg="gray87")

    error_label = Label(
        main, text="Incorrect Format", font=("Helvetica", 20), bg="gray87", fg="red"
    )

    activity_done = Text(main, width=30, height=1, font=("Helvetica", 20))
    minutes_spent = Text(main, width=5, height=1, font=("Helvetica", 20))
    minutes_spent.insert(INSERT, "10")
    hours_spent = Text(main, width=5, height=1, font=("Helvetica", 20))
    hours_spent.insert(INSERT, "0")

    title_lbl.place(x=480, y=100)
    activity_done.place(x=480, y=150)

    time_lbl.place(x=480, y=250)
    hours_spent.place(x=655, y=250)
    hr_lbl.place(x=740, y=250)
    minutes_spent.place(x=880, y=250)
    min_lbl.place(x=965, y=250)
    productive_dropdown.place(x=480, y=350)

    cal = DateEntry(
        main,
        font=("Helvetica", 15),
        wfont=("Helvetica", 15),
        selectmode="day",
        cursor="hand2",
        width=20,
    )
    cal.place(x=480, y=450)

    def upload_activity():
        list = [
            str(activity_done.get(1.0, END)).replace("\n", ""),
            str(hours_spent.get(1.0, END)).replace("\n", ""),
            str(minutes_spent.get(1.0, END)).replace("\n", ""),
            str(activity_productivity.get()),
            str(event.get_date(cal.get_date())),
        ]
        if list[0] == "" or list[1].isdigit == False or list[2].isdigit == False:
            error_label.place(x=900, y=550)
            return
        error_label.place_forget()
        if not path.exists(list[4] + ".txt"):
            open(list[4] + ".txt", "w")
        event.add_productivity(list[0], "event", list[3])
        event.create_activity(
            list[0], str(int(list[1]) * 3600 + int(list[2]) * 60), list[4]
        )

    submit = Button(
        main,
        text="Create Activity",
        font=("Helvetica", 15),
        width=20,
        command=lambda: upload_activity(),
    )
    submit.place(x=900, y=600)


# load Productivity Settings
def menu_productivity_settings():
    def test(button1, button2):
        button1.place_forget()
        button2.place_forget()
        if button1["text"] == "App/Activity Settings":
            app_activity_settings()
        else:
            web_page_settings()

    app_activity_set = Button(
        main, text="App/Activity Settings", font=("Helvetica", 20), width=50
    )
    web_page_set = Button(
        main, text="Web Page Settings", font=("Helvetica", 20), width=50
    )

    app_activity_set.config(command=lambda: test(app_activity_set, web_page_set))
    web_page_set.config(command=lambda: test(web_page_set, app_activity_set))

    app_activity_set.place(x=380, y=200)
    web_page_set.place(x=380, y=400)


# load app and activity settings
def app_activity_settings():
    frame_event = Frame(main)
    frame_event.place(x=380, y=100)
    event_list = Canvas(frame_event, width=800, height=500)
    scroll = Scrollbar(frame_event, orient=VERTICAL, command=event_list.yview)
    frame = Frame(event_list)
    events = event.get_productivity("event")
    if type(events) == bool:
        Label(frame, text="Nothing", font=("Helvetica", 16), anchor="w").pack(
            fill="both"
        )
    else:

        def set_buttons(i):
            tabs = "\t\t\t\t\t\t\t\t\t\t\t"
            current_event_productive = i[1]

            def change_prod(productive, ev):
                event.change_productivity(ev, "event", productive)
                clear_window()
                app_activity_settings()

            if current_event_productive.replace("\n", "") == "productive":
                Button(
                    frame,
                    font=("Helvetica", 16),
                    text="Mark Unproductive: " + i[0] + tabs,
                    anchor="w",
                    command=lambda: change_prod("unproductive", i[0]),
                ).pack(fill="both")
            else:
                Button(
                    frame,
                    font=("Helvetica", 16),
                    text="Mark Productive: " + i[0] + tabs,
                    anchor="w",
                    command=lambda: change_prod("productive", i[0]),
                ).pack(fill="both")

        for i in events:
            set_buttons(i)
    event_list.create_window(0, 0, window=frame, anchor="nw")
    event_list.update_idletasks()
    event_list.configure(scrollregion=event_list.bbox("all"), yscrollcommand=scroll.set)
    event_list.pack(fill="both", expand=True, side="left")
    scroll.pack(fill="y", side="right")


# load web page settings
def web_page_settings():
    title_lbl = Label(
        main, text="Add Unproductive Website:", font=("Helvetica", 20), bg="gray87"
    )
    title_lbl.place(x=480, y=150)

    web_page = Text(main, width=30, height=1, font=("Helvetica", 20))
    web_page.place(x=480, y=200)

    def upload_website():
        site = str(web_page.get(1.0, END)).replace("\n", "")
        for i in event.get_productivity("website"):
            if str(i[0]).lower() == site.lower():
                event.change_productivity(site, "website", "unproductive")
                return
        site = str(site).replace('www.','')
        event.add_productivity(site, "website", "unproductive")

    submit = Button(
        main,
        text="+ Add",
        font=("Helvetica", 14),
        width=5,
        command=lambda: upload_website(),
    )
    submit.place(x=950, y=200)

    def website_list():
        web_list = Tk()
        web_list.wm_title("Website Productivity List")
        frame_event = Frame(web_list)
        frame_event.pack()
        event_list = Canvas(frame_event, width=800, height=500)
        scroll = Scrollbar(frame_event, orient=VERTICAL, command=event_list.yview)
        frame = Frame(event_list)
        events = event.get_productivity("website")
        if type(events) == bool:
            Label(frame, text="Nothing", font=("Helvetica", 16), anchor="w").pack(
                fill="both"
            )
        else:

            def set_buttons(i):
                tabs = "\t\t\t\t\t\t\t\t\t\t\t"
                current_event_productive = i[1]

                def change_prod(productive, ev):
                    event.change_productivity(ev, "website", productive)
                    clear_window()
                    web_list.destroy()
                    web_page_settings()

                if current_event_productive.replace("\n", "") == "productive":
                    Button(
                        frame,
                        font=("Helvetica", 16),
                        text="Mark Unproductive: " + i[0] + tabs,
                        anchor="w",
                        command=lambda: change_prod("unproductive", i[0]),
                    ).pack(fill="both", expand=True)
                else:
                    Button(
                        frame,
                        font=("Helvetica", 16),
                        text="Mark Productive: " + i[0] + tabs,
                        anchor="w",
                        command=lambda: change_prod("productive", i[0]),
                    ).pack(fill="both", expand=True)

            for i in events:
                set_buttons(i)
        event_list.create_window(0, 0, window=frame, anchor="nw")
        event_list.update_idletasks()
        event_list.configure(
            scrollregion=event_list.bbox("all"), yscrollcommand=scroll.set
        )
        event_list.pack(fill="both", expand=True, side="left")
        scroll.pack(fill="y", side="right")
        web_list.mainloop()

    # add button to make list pop up
    web_page_but = Button(
        main, text="Change Website productivity", font=("Helvetica", 20), width=30
    )
    web_page_but.config(command=lambda: website_list())
    web_page_but.place(x=500, y=400)


# load Settings & Support
def menu_settings_support():

    productive_color_list = [
        "Productive Color: red",
        "Productive Color: blue",
        "Productive Color: green",
    ]
    color_productive_dropdown = OptionMenu(
        main, productive_color, *productive_color_list
    )
    color_productive_dropdown.config(width=20, font=("Helvetica", 14))
    color_productive_dropdown.place(x=390, y=400)

    unproductive_color_list = [
        "Unproductive Color: red",
        "Unproductive Color: blue",
        "Unproductive Color: green",
    ]
    color_unproductive_dropdown = OptionMenu(
        main, unproductive_color, *unproductive_color_list
    )
    color_unproductive_dropdown.config(width=20, font=("Helvetica", 14))
    color_unproductive_dropdown.place(x=860, y=400)

    text = Text(main, width=61, height=9, font=("Helvetica", 16))
    text.place(x=390, y=40)
    text.insert(
        INSERT,
        "\n The home page gives a short summary of producitvity day to day\n\n"
        + " Detailed summary gives some graphical representations of productivity\n\n"
        + " Add activity lets you add an activity your device won't or can't track\n\n"
        + " Productivity settings lets you adjust settings for apps, activites, and websites\n\n",
    )
    text.config(state="disabled")


menu_bar()
menu_home(today_date)
main.mainloop()
