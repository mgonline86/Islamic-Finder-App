from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.font import BOLD
import requests, csv, re, sys
from datetime import date, datetime, timedelta
from tkinter.filedialog import asksaveasfile

### Global Variables ###
user_inputs = {}

### Main App Logic ###

# Helpers Functions:
def format_date(date, value):
    date = datetime.strptime(date, '%d-%m-%Y')
    if value == 'last_end_date':
        date = date + timedelta(days=1)
    date = date.strftime('%m/%d/%Y')
    return date

def format_time(time, value):
    time = re.search('(..:..) *', time).group(1)
    time = datetime.strptime(time, '%H:%M')
    if value == 'end_time':
        time = time - timedelta(hours=0, minutes=1)
    time = time.strftime("%H:%M")
    return time

# Creating csv file:
def create_csv_file(file_name, data):
    header = ['Subject', 'Start Date', 'End Date', 'Start Time', 'End Time']

    with open(file_name.name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

# Getting Data from API
def main():
    try:
        # Getting filepath from user
        files = [('Comma-separated values', '*.csv')]
        file_name = asksaveasfile(filetypes=files, defaultextension=files)

        country = user_inputs['country']
        city = user_inputs['city']
        period = user_inputs['period']
        method = int(user_inputs['method'])
        year = int(user_inputs['year'])
        month = int(user_inputs['month']) if period == 'For one Month' else 1
        if period == 'For one Month':
            annual = 'false'
            if month == 12:

                next_month = requests.get(f'http://api.aladhan.com/v1/calendarByCity?city={city}&country={country}&method={method}&month=1&year={year+1}&annual={annual}', timeout=5)
            else:

                next_month = requests.get(f'http://api.aladhan.com/v1/calendarByCity?city={city}&country={country}&method={method}&month={month+1}&year={year}&annual={annual}', timeout=5)       
            next_month = next_month.json()
            last_prayer_time = next_month['data'][0]['timings']['Fajr']
        else:
            annual = 'true'
            next_month = requests.get(f'http://api.aladhan.com/v1/calendarByCity?city={city}&country={country}&method={method}&month={method}&month={month}&year={year+1}&annual={annual}', timeout=5)
            next_month = next_month.json()
            last_prayer_time = next_month['data']['1'][0]['timings']['Fajr']

        response = requests.get(f'http://api.aladhan.com/v1/calendarByCity?city={city}&country={country}&method={method}&month={month}&year={year}&annual={annual}', timeout=5)
        response = response.json()
        prayer_times = response['data']
        data = structure_data(prayer_times, annual, last_prayer_time)
        create_csv_file(file_name, data)
        messagebox.showinfo("Saved", f'File saved at\n{file_name.name}')
        sys.exit("File Saved")
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("Error", 'Check your internet connection\nthen try again.')
        return 

# Structuring data for csv file    
def structure_data(prayer_times, annual, last_prayer_time):
    all_days_rows_list=[]
    def structure_month(prayer_times, last_prayer_time):
        for i, d in enumerate(prayer_times):
            #Fajr
            row = []
            row.append('Fajr')
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_time = d['timings']['Fajr']
            start_time = format_time(start_time, 'start_time')
            end_time = d['timings']['Sunrise']
            end_time = format_time(end_time, 'end_time')
            row.append(start_time)
            row.append(end_time)
            all_days_rows_list.append(row)
            
            #Sunrise
            row = []
            row.append('Sunrise')
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_time = d['timings']['Sunrise']
            start_time = format_time(start_time, 'start_time')
            end_time = d['timings']['Dhuhr']
            end_time = format_time(end_time, 'end_time')
            row.append(start_time)
            row.append(end_time)
            all_days_rows_list.append(row)
            
            #Dhuhr
            row = []
            row.append('Dhuhr')
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_time = d['timings']['Dhuhr']
            start_time = format_time(start_time, 'start_time')
            end_time = d['timings']['Asr']
            end_time = format_time(end_time, 'end_time')
            row.append(start_time)
            row.append(end_time)
            all_days_rows_list.append(row)
            
            #Asr
            row = []
            row.append('Asr')
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_time = d['timings']['Asr']
            start_time = format_time(start_time, 'start_time')
            end_time = d['timings']['Maghrib']
            end_time = format_time(end_time, 'end_time')
            row.append(start_time)
            row.append(end_time)
            all_days_rows_list.append(row)
            
            #Maghrib
            row = []
            row.append('Maghrib')
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            start_time = d['timings']['Maghrib']
            start_time = format_time(start_time, 'start_time')
            end_time = d['timings']['Isha']
            end_time = format_time(end_time, 'end_time')
            row.append(start_time)
            row.append(end_time)
            all_days_rows_list.append(row)
            
            #Isha
            row = []
            row.append('Isha')
            start_date = d['date']['gregorian']['date']
            start_date = format_date(start_date, 'start_date')
            row.append(start_date)
            last_end_date = d['date']['gregorian']['date']
            last_end_date = format_date(last_end_date, 'last_end_date')
            row.append(last_end_date)
            start_time = d['timings']['Isha']
            start_time = format_time(start_time, 'start_time')
            if i+1 < len(prayer_times):
                end_time = prayer_times[i+1]['timings']['Fajr']
            else:    
                end_time = last_prayer_time
            end_time = format_time(end_time, 'end_time')
            row.append(start_time)
            row.append(end_time)

            all_days_rows_list.append(row)

    if annual == 'false':
        structure_month(prayer_times, last_prayer_time)
    if annual == 'true':
        monthes = [*range(1, 13, 1)]
        for m in monthes:
            structure_month(prayer_times[str(m)], last_prayer_time)
    
    return(all_days_rows_list)


### Tkinter GUI Logic ###

# Fetching countries List
def fetch_countries():
    try: 
        countries_res = requests.get('https://countriesnow.space/api/v0.1/countries/flag/unicode', timeout=5)
        countries_res = countries_res.json()['data']

        countries_list = []

        for country in countries_res:
            countries_list.append(country['name'])

        sorted_countries_list = sorted(countries_list, key=str.lower)
        return sorted_countries_list
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("Error", 'Check your internet connection\nthen start the app.')
        sys.exit("No internet connection")


root = Tk()
root.title('Mawakeet')
root.geometry('400x400')

def fetch_cities():
    try:
        user_inputs['country'] = myCombo.get()
        url = 'https://countriesnow.space/api/v0.1/countries/cities'
        body = {
            "country": myCombo.get()
        }
        cities_res = requests.post(url, data = body,timeout=5)
        cities_list = cities_res.json()['data']
        if len(cities_list) < 1:
            messagebox.showerror("Error", 'Sorry, No cities Found')
            return 
        mainLabel['text'] = 'Choose Your City'
        myCombo['value'] = cities_list
        myCombo.current(0)
        nextBtn['command'] = set_period
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("Error", 'Check your internet connection\nthen try again.')

def set_period():
    user_inputs['city'] = myCombo.get()
    period_list = ['For one Month', 'For one Year']
    mainLabel['text'] = 'Choose Period'
    myCombo['value'] = period_list
    myCombo.current(0)
    nextBtn['command'] = set_month

def set_month():
    user_inputs['period'] = myCombo.get()
    if myCombo.get() == 'For one Month':
        monthes_list = [*range(1, 13, 1)]
        mainLabel['text'] = 'Choose Month'
        myCombo['value'] = monthes_list
        myCombo.current(0)
        nextBtn['command'] = set_year
    else:
        user_inputs['month'] = 'all'
        set_year()  

def set_year():
    if user_inputs['period'] == 'For one Month':
        user_inputs['month'] = myCombo.get()
    current_year = date.today().year
    year_list = [*range(int(current_year) - 50, int(current_year) + 50, 1)]
    mainLabel['text'] = 'Choose Year'
    myCombo['value'] = year_list
    myCombo.current(year_list.index(int(current_year)))
    nextBtn['command'] = set_method

def set_method():
    user_inputs['year'] = myCombo.get()
    method_list = [
        "1 - University of Islamic Sciences, Karachi",
        "2 - Islamic Society of North America",
        "3 - Muslim World League",
        "4 - Umm Al-Qura University, Makkah",
        "5 - Egyptian General Authority of Survey",
        "7 - Institute of Geophysics, University of Tehran",
        "8 - Gulf Region",
        "9 - Kuwait",
        "10 - Qatar",
        "11 - Majlis Ugama Islam Singapura, Singapore",
        "12 - Union Organization islamic de France",
        "13 - Diyanet İşleri Başkanlığı, Turkey",
        "14 - Spiritual Administration of Muslims of Russia",
        "0 - Shia Ithna-Ansari"
    ]
    mainLabel['text'] = 'Choose Method'
    myCombo['width'] = 45
    myCombo['value'] = method_list
    myCombo.current(0)
    nextBtn['command'] = download_prayer_times

def download_prayer_times():
    user_inputs['method'] = myCombo.get().split(' -')[0]
    myCombo.forget()
    mainLabel['text'] = 'Download Prayer Times'
    nextBtn.forget()
    dataLabel = Label(
        root,
        text=f'\
            Country--> {user_inputs["country"]}\n\
            City-------> {user_inputs["city"]}\n\
            Period----> {user_inputs["period"]}\n\
            Month----> {user_inputs["month"]}\n\
            Year------> {user_inputs["year"]}\n\
            Method---> {user_inputs["method"]}\n\
                ',
        pady= 5,
        justify=LEFT,
        font=("Arial", 12)
    )
    dataLabel.pack()
    downloadBtn = Button(root, bg="green", fg="white", height=1, width=10, font=("Arial", 15), text='Download',command=main)
    downloadBtn.pack(pady=30)

logoLabel = Label(root, text='Mawakeet',font=("Arial", 30, BOLD), fg='brown')
logoLabel.pack()

sloganLabel = Label(root, text='Custom Prayer Times Calendar')
sloganLabel.pack(pady=(0,30))

mainLabel = Label(root, text='Choose Your Country',font=("Arial", 18), fg='blue')
mainLabel.pack()

myCombo = ttk.Combobox(root, value=fetch_countries(), state='readonly')
myCombo.current(0)
myCombo.bind('<<ComboboxSelected>>')
myCombo.pack()

nextBtn = Button(root, bg="#0492c2", fg="white", height=1, width=10, font=("Arial", 15), text='Next',command=fetch_cities)
nextBtn.pack(pady=30)

root.mainloop()