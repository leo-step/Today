from bs4 import BeautifulSoup
import requests

def get_menus():
    dining_halls = {
        "Whitman College": 8,
        "Butler College": 2,
        "Rockefeller and Mathey Colleges": 1,
        "Forbes College": 3,
        "Center for Jewish Life": 5,
        "Yeh West College": 6
    }
    result = {}
    for dhall, index in dining_halls.items():
        dhall_result = {}
        url = "https://menus.princeton.edu/dining/_Foodpro/online-menu/menuDetails.asp?locationNum={:02d}".format(index)
        text = requests.get(url).text
        soup = BeautifulSoup(text, features="lxml")
        menus = soup.findAll("div", {"class" : "card mealCard"})
        
        for menu in menus:
            text = menu.text.replace("Nutrition", '').replace('\r', '')
            items = [item.strip() for item in text.split("\n") if item.strip()]
            subitems = {}
            category = None
            for i in range(1, len(items)):
                if items[i][0] == '-':
                    key = items[i].replace('-- ', '').replace(' --', '')
                    subitems[key] = []
                    category = key
                else:
                    subitems[category].append(items[i])
            dhall_result[items[0]] = subitems
        result[dhall] = dhall_result
    return result

print(get_menus())
