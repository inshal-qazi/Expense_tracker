# only have to push on github
import json
gc = gspread.service_account(filename="Tracker.json")
spreadsheet = gc.open_by_key("enter a sheets ink your working on)
worksheet = spreadsheet.sheet1

#another  json file where all api of sheets are can get google cloud store in json

i = input("press (start or stop) to allow application to run: ").lower()

if i == "start":
    pass
elif i == "stop":
    print("no problem enter the expense when you remember")
else:
    print("invalid input enter again")

data = {
    "food": [],
    "shopping": [],
    "transportation": [],
    "education": [],
    "others" : []
}

with ("data.json","r") as file:
    data = json.load(file)

while i == "start":
    catagory = input("enter on what category you expand: ").lower()
    if catagory == "stop":
        print("Thanks for telling expense")
        break

    item = input("enter the name of thing: ")
    price = int(input("enter the price of thing: "))

    if catagory in data:
        data[catagory].append({"item": item, "price": price})
        
    else:
        print("invalid category")
        
with open("data.json","w") as file:
 json.dump(data,file,indent=4)
    

        
        


 












