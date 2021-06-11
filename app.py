from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.font import BOLD
import requests, csv, re, sys
from datetime import date, datetime, timedelta
from tkinter.filedialog import asksaveasfile
from tkcalendar import *

### Global Variables ###
user_inputs = {
    'country': 'Not Selected',
    'city': 'Not Selected',
    'from_date': 'Not Selected',
    'to_date': 'Not Selected',
    'method': 'Not Selected'
}

### Main App Logic ###

# Helpers Functions:
def format_date(date):
    date = datetime.strptime(date, '%d-%m-%Y')
    date = date.strftime('%m/%d/%Y')
    return date

def format_time(time):
    time = re.search('(..:..) *', time).group(1)
    time = datetime.strptime(time, '%H:%M')
    time = time.strftime("%H:%M")
    return time

def row_creator(d, prayer):
    row = []
    row.append(prayer)
    start_date = d['date']['gregorian']['date']
    start_date = format_date(start_date)
    row.append(start_date)
    start_time = d['timings'][prayer]
    start_time = format_time(start_time)
    row.append(start_time)
    return row


# Creating csv file:
def create_csv_file(file_name, data):
    header = ['Subject', 'Start Date', 'Start Time']
    # header = ['Subject', 'Start Date', 'End Date', 'Start Time', 'End Time']

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
        from_date = user_inputs['from_date']
        to_date = user_inputs['to_date']
        method = int(user_inputs['method'].split(' -')[0])
        years = [*range(int(from_date.year), int(to_date.year)+1, 1)]
        prayer_times=[]
        for y in years:
            response = requests.get(f'http://api.aladhan.com/v1/calendarByCity?city={city}&country={country}&method={method}&year={y}&annual=true', timeout=5)
            response = response.json()['data']
            prayer_times.append(response)
        next_month = requests.get(f'http://api.aladhan.com/v1/calendarByCity?city={city}&country={country}&method={method}&year={to_date.year+1}&annual=true', timeout=5)
        next_month = next_month.json()
        last_prayer_time = next_month['data']['1'][0]['timings']['Fajr']
        data = structure_data(prayer_times, from_date, to_date, last_prayer_time)
        create_csv_file(file_name, data)
        messagebox.showinfo("Saved", f'File saved at\n{file_name.name}')
        sys.exit("File Saved")
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("Error", 'Check your internet connection\nthen try again.')
        return 

# Structuring data for csv file    
def structure_data(prayer_times, from_date, to_date, last_prayer_time):
    all_days_rows_list=[]
    prayers = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    def structure_month(prayer_times, from_date, to_date, last_prayer_time):
        for d in prayer_times:
            current_date = d['date']['gregorian']['date']
            current_date = datetime.strptime(current_date, '%d-%m-%Y').date()
            if current_date >= from_date and current_date <= to_date:
                for prayer in prayers:
                    all_days_rows_list.append(row_creator(d, prayer))

    monthes = [*range(1, 13, 1)]
    for p in prayer_times:
        for m in monthes:
            structure_month(p[str(m)], from_date, to_date, last_prayer_time)
    
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
root.title('Islamic Finder')
root.geometry('500x500')

def fetch_cities():
    try:
        user_inputs['country'] = countries_combo.get()
        url = 'https://countriesnow.space/api/v0.1/countries/cities'
        body = {
            "country": countries_combo.get()
        }
        cities_res = requests.post(url, data = body,timeout=5)
        cities_list = cities_res.json()['data']
        if len(cities_list) < 1:
            cities_combo['value'] = []
            cities_combo.set('')
            messagebox.showerror("Error", 'Sorry, No cities Found')
            return 
        cities_combo['value'] = cities_list
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("Error", 'Check your internet connection\nthen try again.')

def tab_change_handle(self):
    current_tab_index = main_container.index(main_container.select())
    if current_tab_index == 4:
        next_btn['state'] = 'disabled'
    else:
        next_btn['state'] = 'normal'
    if current_tab_index == 0:
        prev_btn['state'] = 'disabled'
    else:
        prev_btn['state'] = 'normal'

def next():
    current_tab_index = main_container.index(main_container.select())
    main_container.select(current_tab_index+1)

def prev():
    current_tab_index = main_container.index(main_container.select())
    main_container.select(current_tab_index-1)

# Header Elements
logoLabel = Label(root, text='Islamic Finder',font=("Arial", 30, BOLD), fg='brown')
logoLabel.pack()

sloganLabel = Label(root, text='Custom Prayer Times Calendar')
sloganLabel.pack()

# Tabs Container
main_container = ttk.Notebook(root,width=500,height=300)
main_container.bind("<<NotebookTabChanged>>", tab_change_handle)
main_container.pack(pady=20)
main_container.pack_propagate(0)

# Creating Tabs
countries_tab = Frame(main_container, width=500, height=500)
cities_tab = Frame(main_container, width=500, height=500)
period_tab = Frame(main_container, width=500, height=500)
method_tab = Frame(main_container, width=500, height=500)
download_tab = Frame(main_container, width=500, height=500)

countries_tab.pack(fill='both', expand=True)
cities_tab.pack(fill='both', expand=True)
period_tab.pack(fill='both', expand=True)
method_tab.pack(fill='both', expand=True)
download_tab.pack(fill='both', expand=True)

main_container.add(countries_tab, text='Countries')
main_container.add(cities_tab, text='Cities')
main_container.add(period_tab, text='Period')
main_container.add(method_tab, text='Method')
main_container.add(download_tab, text='Download')

def countries_handle(self):
    user_inputs['country']= countries_combo.get()
    country_input_label['text'] =f'Country--> {user_inputs["country"]}'
    fetch_cities()   
    
def cities_handle(self):
    user_inputs['city']= cities_combo.get()
    city_input_label['text'] =f'City--> {user_inputs["city"]}'

def from_date_handle(self):
    user_inputs['from_date']= from_date_entry.get_date()
    from_date_input_label['text'] =f'From--> {user_inputs["from_date"]}'

def to_date_handle(self):
    user_inputs['to_date']= to_date_entry.get_date()
    to_date_input_label['text'] =f'To--> {user_inputs["to_date"]}'

def method_handle(self):
    user_inputs['method']= method_combo.get()
    method_input_label['text'] =f'Method--> {user_inputs["method"]}'

# Countries Tab Elements
countries_label = Label(countries_tab, text='Choose Your Country',font=("Arial", 18), fg='blue')
countries_label.pack()
countries_combo = ttk.Combobox(countries_tab, value=fetch_countries(), state='readonly')
countries_combo.current()
countries_combo.bind('<<ComboboxSelected>>', countries_handle)
countries_combo.pack()

# Cities Tab Elements
cities_label = Label(cities_tab, text='Choose Your City',font=("Arial", 18), fg='blue')
cities_label.pack()
cities_combo = ttk.Combobox(cities_tab, state='readonly')
cities_combo.current()
cities_combo.bind('<<ComboboxSelected>>', cities_handle)
cities_combo.pack()

# Period Tab Elements
period_label = Label(period_tab, text='Choose The Period',font=("Arial", 18), fg='blue')
period_label.pack()
period_left_frame = Frame(period_tab, padx=30)
period_left_frame.pack(side=LEFT)
from_label = Label(period_left_frame, text='From',font=("Arial", 18), fg='blue')
from_label.pack()
from_date_entry = DateEntry(period_left_frame)
from_date_entry.bind('<<DateEntrySelected>>', from_date_handle)
from_date_entry.pack()
period_right_frame = Frame(period_tab, padx=30)
period_right_frame.pack(side=RIGHT)
to_label = Label(period_right_frame, text='To',font=("Arial", 18), fg='blue')
to_label.pack()
to_date_entry = DateEntry(period_right_frame)
to_date_entry.bind('<<DateEntrySelected>>', to_date_handle)
to_date_entry.pack()

# Method Tab Elements
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
method_label = Label(method_tab, text='Choose The Method',font=("Arial", 18), fg='blue')
method_label.pack()
method_combo = ttk.Combobox(method_tab, values=method_list, state='readonly', width=45)
method_combo.current()
method_combo.bind('<<ComboboxSelected>>', method_handle)
method_combo.pack()

# Download Tab Elements
inputs_frame = Frame(download_tab, bg='red')
inputs_frame.pack()
country_input_label = Label(inputs_frame, text=f'Country--> {user_inputs["country"]}', justify=LEFT, font=("Arial", 12), width=500, anchor='w', padx=30)
country_input_label.pack()
city_input_label = Label(inputs_frame, text=f'City--> {user_inputs["city"]}', justify=LEFT, font=("Arial", 12), width=500, anchor='w', padx=30)
city_input_label.pack()
from_date_input_label = Label(inputs_frame, text=f'From--> {user_inputs["from_date"]}', justify=LEFT, font=("Arial", 12), width=500, anchor='w', padx=30)
from_date_input_label.pack()
to_date_input_label = Label(inputs_frame, text=f'To--> {user_inputs["to_date"]}', justify=LEFT, font=("Arial", 12), width=500, anchor='w', padx=30)
to_date_input_label.pack()
method_input_label = Label(inputs_frame, text=f'Method--> {user_inputs["method"]}', justify=LEFT, font=("Arial", 12), width=500, anchor='w', padx=30)
method_input_label.pack()
downloadBtn = Button(download_tab, bg="green", fg="white", height=1, width=10, font=("Arial", 15), text='Download',command=main)
downloadBtn.pack()

left_frame = Frame(root)
left_frame.pack(side=LEFT)
right_frame = Frame(root)
right_frame.pack(side=RIGHT)
prev_btn = Button(left_frame, text='Previous', command=prev, state='disabled')
prev_btn.pack(pady=10, padx=50)
next_btn = Button(right_frame, text='Next', command=next)
next_btn.pack(pady=10, padx=50)

root.resizable(0, 0)
root.mainloop()