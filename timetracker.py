import datetime, json, psutil, sys, pygame as pg
from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId

# gets the name of the process ... (https://stackoverflow.com/questions/70574208/get-the-name-of-the-current-opened-application-in-python)
def get_process_name():
    hwnd = GetForegroundWindow()
    _,pid = GetWindowThreadProcessId(hwnd)
    if psutil.pid_exists(pid):
        process = psutil.Process(pid)
        process_name = process.name()
        return process_name
    else:
        return "sleep"
    
def timedelta_round_seconds(timedelta):
    timedelta_seconds = datetime.timedelta.total_seconds(timedelta)
    timedelta_full = datetime.timedelta(seconds=int(timedelta_seconds))
    return timedelta_full

# the timedeltas get converted to strings so they can be stored in the json file
def str_to_timedelta(str_of_timedelta): # input the value of the key and get out a timedelta
    converted_str = datetime.datetime.strptime(str_of_timedelta,"%H:%M:%S") # we specify the input and the format...
    converted_str = datetime.timedelta(hours=converted_str.hour, minutes=converted_str.minute, seconds=converted_str.second) # ...and use datetime's hour, min and sec properties to build a timedelta
    return converted_str

def add_to_total(old_time_val, segment_to_add): #gets the string from both dictionaries, converts to timedelta, and outputs the total time as timedelta
    new_segment = str_to_timedelta(segment_to_add)
    old_time = str_to_timedelta(old_time_val)
    total_time = new_segment + old_time
    return total_time

# set up for pygame
pg.init()
clock = pg.time.Clock()
screenx = 400
screeny = 400
screen = pg.display.set_mode((screenx, screeny))
text_font = pg.font.SysFont(None, 24) # loads default pygame font

def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour) # boolean gives text characters edges and looks nicer
    screen.blit(img, (x,y))

st = datetime.datetime.now() # START TIME 
tickspeed = 1 # 1 FPS 

#gets the data for python to read from the JSON
f =open("data_file.json")
string = f.read() 
f.close()

timers = {} # define it in case the data_file.json is empty

current_date = str(datetime.date.today())
print("current date is: " + current_date)

with open("all_times.json") as f:
    all_times_str = json.load(f)

for date in all_times_str:
    if date == current_date:
        timers = all_times_str[date]
    else:
        timers = {}

for app, timer in timers.items(): # convert the times to timedelta for calculations while the program is running
    timers.update({app: str_to_timedelta(timer)})

display_clock = datetime.timedelta(0)

for app, timer in timers.items():
    display_clock += timer

while True:
    for event in pg.event.get():
        if (event.type == pg.QUIT):

            timers_str = timers # before manipulating string create another version for the all_times stuff
            for app, timer in timers_str.items():
                timers_str.update({app : str(timer)}) # need to convert timedelta to string for it to be JSON'ed

            date_in_all_times = False
            for date in all_times_str:
                if current_date == date:
                    date_in_all_times = True
                    all_times_str.update({date: timers})
            
            if date_in_all_times == False:
                all_times_str.update({current_date: timers})
                print("yues")
            
            json_object = json.dumps(all_times_str, indent=4)
            with open("all_times.json", "w") as f:
                f.write(json_object)

            print('quit')
            pg.quit()
            sys.exit() 
    
    y_offset = 0 # so we can list the timers underneath each other
    active_window = get_process_name()

    if active_window not in timers:
        timers.update({active_window: datetime.timedelta(0)}) # so for a new window it still works, just treats it as having a total time of 0 before the sum

    tt_old = timers[active_window] # un-updated time spent on this app
    tt = tt_old + datetime.timedelta(seconds=(1/tickspeed)) # total time overall = total time stored + the time between one "frame" and the next
    timers.update({active_window : tt}) # updates the timer for this particular app with the new overall total time calculated
    
    # this is for the overall timer
    display_clock = display_clock + datetime.timedelta(seconds=(1/tickspeed)) # TOTAL TIME = CURRENT TIME - START TIME
    
    screen.fill((108, 230, 199)) # set the background
    draw_text("Total: " + str(timedelta_round_seconds(display_clock)), text_font, (0, 0, 0), screenx-150, 10)
    
    for app, timer in timers.items():
        str_timer = str(timedelta_round_seconds(timer))
        draw_text(app + " : " + str_timer, text_font, (0,0,0), 10, 10+y_offset)
        y_offset += 20

    pg.display.update()
    clock.tick(tickspeed)
