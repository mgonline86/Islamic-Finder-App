from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.font import BOLD
import requests, csv, re, sys
from datetime import datetime, timedelta
from tkinter.filedialog import asksaveasfile
from tkcalendar import *

### Global Variables ###
user_inputs = {
    'country': 'Not Selected',
    'city': 'Not Selected',
    'from_date': datetime.today().date(),
    'to_date': datetime.today().date() + timedelta(days=365),
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
        country_search_result_box.delete(0, END)
        for i in sorted_countries_list:
            country_search_result_box.insert(END, i)
        return sorted_countries_list
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("Error", 'Check your internet connection\nthen start the app.')
        sys.exit("No internet connection")


root = Tk()
root.title('Islamic Finder')

# Gets the requested values of the height and widht.
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
 
# Gets both half the screen width/height and window width/height
positionRight = int(root.winfo_screenwidth()/2.5 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/5 - windowHeight/2)
 
# Positions the window in the center of the page.
root.geometry("+{}+{}".format(positionRight, positionDown))

def fetch_cities():
    try:
        # user_inputs['country'] = countries_combo.get()
        url = 'https://countriesnow.space/api/v0.1/countries/cities'
        body = {
            "country": user_inputs['country']
        }
        cities_res = requests.post(url, data = body,timeout=5)
        cities_list = cities_res.json()['data']
        if len(cities_list) < 1:
            cities_combo['value'] = []
            cities_combo.set('')
            messagebox.showerror("Error", 'Sorry, No cities Found')
            return 
        cities_combo['value'] = cities_list
        city_search_result_box.delete(0, END)
        for i in cities_list:
            city_search_result_box.insert(END, i)

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
main_container = ttk.Notebook(root,width=500,height=400)
main_container.bind("<<NotebookTabChanged>>", tab_change_handle)
main_container.pack(pady=20)
main_container.pack_propagate(0)

# Creating Tabs
countries_tab = Frame(main_container)
cities_tab = Frame(main_container)
period_tab = Frame(main_container)
method_tab = Frame(main_container)
download_tab = Frame(main_container)

countries_tab.pack(fill='both', expand=True)
cities_tab.pack(fill='both', expand=True)
period_tab.pack(fill='both', expand=True)
method_tab.pack(fill='both', expand=True)
download_tab.pack(fill='both', expand=True)

main_container.add(countries_tab, text='Countries')
main_container.add(cities_tab, text='Cities')
main_container.add(period_tab, text='Period')
main_container.add(method_tab, text='Methods')
main_container.add(download_tab, text='Download')

def countries_handle(self):
    if len(country_search_result_box.curselection()) > 0:
        curent_selection_index = int(country_search_result_box.curselection()[0])
        country_name = country_search_result_box.get(curent_selection_index)
        country_search_entry.delete(0, END)
        country_search_entry.insert(0, country_name)
        print(country_name)
        user_inputs['country']= country_name
        country_input_label['text'] =f'Country--> {user_inputs["country"]}'
        user_inputs['city']= 'Not Selected'
        city_search_entry.delete(0, END)
        city_input_label['text'] =f'City--> {user_inputs["city"]}'
        fetch_cities()   
    
def cities_handle(self):
    if len(city_search_result_box.curselection()) > 0:
        curent_selection_index = int(city_search_result_box.curselection()[0])
        city_name = city_search_result_box.get(curent_selection_index)
        city_search_entry.delete(0, END)
        city_search_entry.insert(0, city_name)
        print(city_name)
        user_inputs['city']= city_name
        city_input_label['text'] =f'City--> {user_inputs["city"]}'

def from_date_handle(self):
    user_inputs['from_date']= from_date_entry.get_date()
    from_date_input_label['text'] =f'From--> {user_inputs["from_date"]}'

def to_date_handle(self):
    user_inputs['to_date']= to_date_entry.get_date()
    to_date_input_label['text'] =f'To--> {user_inputs["to_date"]}'

def method_handle(e):
    print(e)
    user_inputs['method']= e
    method_input_label['text'] =f'Method--> {user_inputs["method"]}'

# Countries Tab Elements
def countries_search(var):
    content= var.get()
    filtered_country_list = filter(lambda country: content.lower() in country.lower(), countries_combo['value'])
    filtered_country_list = list(filtered_country_list)
    def sort_list(i):
       order = i.lower().find(content.lower())
       order = 1000 if order == -1 else order
       return order
    filtered_country_list.sort(key=sort_list)
    country_search_result_box.delete(0, END)
    for i in filtered_country_list:
        country_search_result_box.insert(END, i)
countries_label = Label(countries_tab, text='Choose Your Country',font=("Arial", 18), fg='blue')
countries_label.pack()
country_search_var = StringVar()
country_search_var.trace("w", lambda name, index,mode, var=country_search_var: countries_search(var))
country_search_entry = Entry(countries_tab, textvariable=country_search_var)
country_search_entry.pack(pady=30)
country_search_result_box = Listbox(countries_tab, cursor='hand2', selectmode=SINGLE)
country_search_result_box.bind('<<ListboxSelect>>', countries_handle)
country_search_result_box.pack(side = LEFT, fill = BOTH, expand=True)
scrollbar = Scrollbar(countries_tab)
scrollbar.pack(side = RIGHT, fill = BOTH)
country_search_result_box.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = country_search_result_box.yview)
countries_combo = ttk.Combobox(countries_tab, value=fetch_countries(), state='readonly')

# Cities Tab Elements
def search(var):
    content= var.get()
    filtered_city_list = filter(lambda city: content.lower() in city.lower(), cities_combo['value'])
    filtered_city_list = list(filtered_city_list)
    def sort_list(i):
       order = i.lower().find(content.lower())
       order = 1000 if order == -1 else order
       return order
    filtered_city_list.sort(key=sort_list)
    city_search_result_box.delete(0, END)
    for i in filtered_city_list:
        city_search_result_box.insert(END, i)

cities_label = Label(cities_tab, text='Choose Your City',font=("Arial", 18), fg='blue')
cities_label.pack()
cities_combo = ttk.Combobox(cities_tab, state='readonly', value=[])
city_search_var = StringVar()
city_search_var.trace("w", lambda name, index,mode, var=city_search_var: search(var))
city_search_entry = Entry(cities_tab, textvariable=city_search_var)
city_search_entry.pack(pady=30)
city_search_result_box = Listbox(cities_tab, cursor='hand2', selectmode=SINGLE)
city_search_result_box.bind('<<ListboxSelect>>', cities_handle)
city_search_result_box.pack(side = LEFT, fill = BOTH, expand=True)
scrollbar = Scrollbar(cities_tab)
scrollbar.pack(side = RIGHT, fill = BOTH)
city_search_result_box.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = city_search_result_box.yview)


# Period Tab Elements
period_label = Label(period_tab, text='Choose The Period',font=("Arial", 18), fg='blue')
period_label.pack()
period_left_frame = Frame(period_tab, padx=30, width=250, height=250)
period_left_frame.pack(side=LEFT)
period_left_frame.pack_propagate(0)
from_label = Label(period_left_frame, text='From',font=("Arial", 18), fg='blue')
from_label.pack()
from_date_entry = DateEntry(period_left_frame)
from_date_entry.bind('<<DateEntrySelected>>', from_date_handle)
from_date_entry.pack()
from_date_entry.set_date(datetime.today().date())
period_right_frame = Frame(period_tab, padx=30, width=250, height=250)
period_right_frame.pack(side=RIGHT)
period_right_frame.pack_propagate(0)
to_label = Label(period_right_frame, text='To',font=("Arial", 18), fg='blue')
to_label.pack()
to_date_entry = DateEntry(period_right_frame)
to_date_entry.bind('<<DateEntrySelected>>', to_date_handle)
to_date_entry.pack()
to_date_entry.set_date(datetime.today().date() + timedelta(days=365))

# Method Tab Elements
methods_list = [
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
method_variable = StringVar()
for m in methods_list:
    Radiobutton( method_tab, text=m, value=m, variable=method_variable, tristatevalue="x", cursor='hand2', command= lambda: method_handle(method_variable.get())).pack(anchor=W)

# Download Tab Elements
inputs_frame = Frame(download_tab, bg='red')
inputs_frame.pack()
country_input_label = Label(inputs_frame, text=f'Country--> {user_inputs["country"]}', font=("Arial", 12), width=500, padx=30)
country_input_label.pack()
city_input_label = Label(inputs_frame, text=f'City--> {user_inputs["city"]}', font=("Arial", 12), width=500, padx=30)
city_input_label.pack()
from_date_input_label = Label(inputs_frame, text=f'From--> {user_inputs["from_date"]}', font=("Arial", 12), width=500, padx=30)
from_date_input_label.pack()
to_date_input_label = Label(inputs_frame, text=f'To--> {user_inputs["to_date"]}', font=("Arial", 12), width=500, padx=30)
to_date_input_label.pack()
method_input_label = Label(inputs_frame, text=f'Method--> {user_inputs["method"]}', font=("Arial", 12), width=500, padx=30)
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