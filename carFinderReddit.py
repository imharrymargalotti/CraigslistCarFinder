'''
@Author: Harry Margalotti
@Created: 6/28/19
@Purpose: Search craigslist for used cars matching user criteria
'''
import smtplib
import time
import requests
from bs4 import BeautifulSoup as bs4
import csv


def timeConvert(miliTime):
    hours, minutes = miliTime.split(":")
    hours, minutes = int(hours), int(minutes)
    setting = "AM"
    if hours > 12:
        setting = "PM"
        hours -= 12
    return ("%02d:%02d" + setting) % (hours, minutes)


def getDetailsRaw(carLink):
    try:
        rsp = requests.get(carLink)
        html = bs4(rsp.text, 'html.parser')
        attrs = html.findAll("p", {"class": "attrgroup"})
        price = html.findAll("span", {"class": "price"})
        priceStart = str(price[0]).find("$")
        priceEnd = str(price[0]).rfind("<")
        pricefinal = str(price[0])[priceStart:priceEnd]

        postDateData = html.findAll("time", {"class": "date timeago"})
        # print(postDateData)
        postDateStart = str(postDateData[0]).find('">') + 2
        postDateEnd = str(postDateData[0]).rfind("</time>")
        postDate = str(postDateData[0])[postDateStart:postDateEnd]
        time = postDate.split()

        newTime = timeConvert(time[1])

        newDateTime = " " + str(time[0]) + " " + str(newTime)
        return attrs, pricefinal, newDateTime
    except:
        print("Issue finding post: it may have been deleted")


def sendInquiry(recipient, car):
    fromaddr = '@gmail.com'
    username = '@gmail.com'
    password = ''
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)

    msg2 = "Hi, I saw your post about the " + car + ", and was wondering if it is still available?"
    msg = "\r\n".join([
        "From: " + fromaddr,
        "To: " + ",".join(fromaddr),
        "Subject: " + car,
        msg2
    ])
    server.sendmail(fromaddr, fromaddr, msg)
    server.quit()


def checkDeal(condition, cylinders, drive, fuel, odometer, paint, size, titleStatus, trans, type, year):
    doIWantIt = False

    conditionsIWant = ['new', 'good', 'like new', 'excellent']
    milesIWant = 108000
    colorIWant = ['black', 'blue', 'grey', 'red', 'silver', 'white', 'custom']
    titleStatusIWant = 'clean'
    transmissionIWant = "automatic"
    typeIWant = ['sedan', 'coupe', 'SUV']
    yearIWant = 2007
    if condition.lower() in conditionsIWant:

        if int(odometer) <= milesIWant:

            if paint in colorIWant:

                if titleStatus.lower() == titleStatusIWant:

                    if trans == transmissionIWant:

                        if type in typeIWant:
                            try:
                                if int(year) >= yearIWant:
                                    doIWantIt = True
                            except:
                                print("Year uncertain, inquiry not sent. \n"
                                      "Year might be: ", year)
    return doIWantIt


def checkIfReplied(title, carLink, condition, drive, fuel, odometer, paint, size, titleStatus, trans, type, year,
                   cylinders):
    with open('deals.csv', newline='') as csvfile:
        dealreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        x = 0
        for row in dealreader:
            if x > 0:
                for x in range(len(row)):
                    if row[0] == title:
                        if row[2] == condition:
                            if row[3] == drive:
                                if row[4] == fuel:
                                    if (row[5] == odometer):
                                        if row[6] == paint:
                                            if row[9] == trans:
                                                if row[10] == type:
                                                    if row[11] == year:
                                                        if row[12] == cylinders:
                                                            return True
            x += 1
        return True


def logDeal(title, carlink, condition, drive, fuel, odometer, paint, size, titleStatus, trans, type, year, cylinders):
    with open('deals.csv', mode='a') as deals_file:
        deal_writer = csv.writer(deals_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        rowtoLog = [title, carlink, condition, drive, fuel, odometer, paint, size, titleStatus, trans, type, year,
                    cylinders]
        deal_writer.writerow(rowtoLog)


def parseDetails(cars, html):
    for x in range(len(cars)):
        time.sleep(1)  # I put this sleep in so craigslist doesnt freak out about too many requests
        link = html.findAll("a", {"class": "result-title hdrlnk"})

        # direct link to a cars post
        carlink = str(link[x])[str(link[x]).find("href=") + 6:str(link[x]).rfind('">')]

        print("-" * 200)

        print(carlink)

        # This returns the details in a list of size 2, and parses out the price and post date

        details, price, postDate = getDetailsRaw(carlink)

        print("\n", postDate, "\n")

        condition, titleStatus, drive, fuel, odometer, paint, size, trans, type, cylinders, year, title = '', '', '', '', '', '', '', '', '', '', '', ''

        for i in range(len(details)):
            if (i == 0):  # index 0 is always the title
                titlestart = str(details[i]).find("<b>") + 3
                titleend = str(details[i]).rfind("</b>")
                title = str(details[i])[titlestart:titleend]
            elif (i == 1):  # index 2 is the rest of the details
                # now we split the rest of the details into their own list
                details2 = str(details[i]).split("<br/>")

                # The details list can vary in order depending on if it includes things such as the VIN.
                # So the best way to handle this was to check if the keyword exists within the raw html
                for y in range(len(details2)):
                    if ("condition" in str(details2[y]).lower()):
                        # now we can see that the text we want is within <b> </b> so we can use string slicing to get it
                        conditionstart = str(details2[y]).find("<b>") + 3
                        conditionend = str(details2[y]).rfind("</b>")
                        condition = str(details2[y])[conditionstart:conditionend]
                    elif ("cylinder" in str(details2[y]).lower()):
                        cylindersStart = str(details2[y]).find("<b>") + 3
                        cylindersEnd = str(details2[y]).rfind("</b>")
                        cylinders = str(details2[y])[cylindersStart:cylindersEnd]
                    elif ("drive" in str(details2[y]).lower()):
                        driveStart = str(details2[y]).find("<b>") + 3
                        driveEnd = str(details2[y]).rfind("</b>")
                        drive = str(details2[y])[driveStart:driveEnd]
                    elif ("fuel" in str(details2[y]).lower()):
                        fuelStart = str(details2[y]).find("<b>") + 3
                        fuelEnd = str(details2[y]).rfind("</b>")
                        fuel = str(details2[y])[fuelStart:fuelEnd]
                    elif ("odometer" in str(details2[y]).lower()):
                        odometerStart = str(details2[y]).find("<b>") + 3
                        odometerEnd = str(details2[y]).rfind("</b>")
                        odometer = str(details2[y])[odometerStart:odometerEnd]
                    elif ("paint" in str(details2[y]).lower()):
                        paintStart = str(details2[y]).find("<b>") + 3
                        paintEnd = str(details2[y]).rfind("</b>")
                        paint = str(details2[y])[paintStart:paintEnd]
                    elif ("size" in str(details2[y]).lower()):
                        sizeStart = str(details2[y]).find("<b>") + 3
                        sizeEnd = str(details2[y]).rfind("</b>")
                        size = str(details2[y])[sizeStart:sizeEnd]
                    elif ("title" in str(details2[y]).lower()):
                        titleStart = str(details2[y]).find("<b>") + 3
                        titleEnd = str(details2[y]).rfind("</b>")
                        titleStatus = str(details2[y])[titleStart:titleEnd]
                    elif ("transmission" in str(details2[y]).lower()):
                        transStart = str(details2[y]).find("<b>") + 3
                        transEnd = str(details2[y]).rfind("</b>")
                        trans = str(details2[y])[transStart:transEnd]
                    elif ("type" in str(details2[y]).lower()):
                        typeStart = str(details2[y]).find("<b>") + 3
                        typeEnd = str(details2[y]).rfind("</b>")
                        type = str(details2[y])[typeStart:typeEnd]

        print("Car: ", title, "\t", "Cost: ", price)
        cleanInfo = "Condition: " + condition + "\n" + "Cylinders: " + cylinders + "\n" + "Drive: " + drive + "\n" + "Fuel: " + fuel + "\n" + "Odometer: " + odometer + "\n" + "Color: " + paint + "\n" + "Size: " + size + "\n" + "Title Status: " + titleStatus + "\n" + "Transmission Type: " + trans + "\n" + "Type: " + type
        print(cleanInfo)

        year = title.lstrip()
        year = year[0:5]
        year = year.strip()

        deal = checkDeal(condition, cylinders, drive, fuel, odometer, paint, size, titleStatus, trans, type, year)

        if deal:
            if not checkIfReplied(title, carlink, condition, drive, fuel, odometer, paint, size, titleStatus, trans,
                                  type, year, cylinders):

                logDeal(title, carlink, condition, drive, fuel, odometer, paint, size, titleStatus, trans, type, year,
                        cylinders)

                print("\n\n\n Possible Deal Found: Deal Logged \n\n\n")

                # sendInquiry() this is commented out until bugs are fixed
            else:
                print("\n\n\n ALREADY REPLIED TO \n\n\n")
        print("-" * 200)


def main():
    #should be something like https://nwct.craigslist.org/search/cto
    url_base = ''
    #FILTER BREAKDOWN:
    '''
    hasPic = 1/0: Only cars that have images with the listing 

    postedToday=0/1: Only cars that were posted today 

    searchDistance: int: Will only show cars within X miles of ZIP code

    postal string: Only vehicles within X miles of this param

    max_price int: Max price the car can be listed at

    max_auto_miles int: Max mileage for the car

    min_auto_miles int: Min mileage for the car

    auto_transmission int:  
        manual = 1
        automatic = 2
        other = 3

    auto_bodytype int:
        bus = 1
        convertible = 2
        coupe = 3
        hatchback = 4
        mini-van = 5
        offroad = 6
        pickup = 7
        sedan = 8
        truck = 9
        SUV = 10
        wagon = 11
        van = 12
        select all (if no others are in auto_bodytype list) = 13

    min_price int: min price for car

    auto_make_model string: filter by make and model

    min_auto_year int: Oldest year the car can be from 

    max_auto_year int: Newest year the car can be from 

    condition int:
        new = 10
        like new = 20
        excellent = 30 
        good = 40
        fair = 50 
        salvage = 60

    auto_cylinders int:
        3 cylinders = 1
        4 cylinders = 2
        5 cylinders = 3
        6 cylinders = 4
        8 cylinders = 5
        10 cylinders = 6
        12 cylinders = 7
        Any (if auto_cylinders list is empty) = 8

    auto_drivetrain int:
        rwd = 1
        fwd = 2
        4wd = 3

    auto_fuel_type int:
        gas = 1
        diesel = 2
        hybrid = 3
        electric = 4
        other = 6

    auto_paint int:
         black = 
         blue = 2
         brown = 20
         green = 3
         grey = 4
         orange = 5
         purple = 6
         red = 7
         silver = 8
         white = 9
         yellow = 10
         custom = 11

    auto_size int:
         compact = 1
         full-size = 2
         mid-size = 3
         sub-compact = 4


    auto_title_status int:
         clean = 1
         salvage = 2
         rebuilt = 3
         parts only = 4
         lien = 5
         missing = 6
    '''

    #SAMPLE PARAMS DICTIONARY
    # params = dict(hasPic=1, postedToday=0, search_distance=25, postal='12345', max_price=5000, max_auto_miles=170000,
    #               auto_transmission=2,
    #               auto_bodytype={3, 10, 8})

    params = dict()

    rsp = requests.get(url_base, params=params)
    # To check requests automatically created the right URL:
    print('Reading from:' + "\n\t" + rsp.url + "\n")

    print("Filters Currently On: \n")
    for key in params.keys():
        print(key, ": ", params.get(key))

    html = bs4(rsp.text, 'html.parser')

    # Find all car posts. They exist in an <li> with the class "result-row"
    # This can be found through the browser inspector
    cars = html.findAll("li", {"class": "result-row"})
    print("\n" + "Results: " + str(len(cars)))

    parseDetails(cars, html)


main()