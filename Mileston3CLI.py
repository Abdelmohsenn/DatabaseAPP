import mysql.connector
import flask
import tkinter as tk
from tkinter import *
import tkinter.messagebox as MessageBox
from colorama import init, Fore, Back, Style
import pyfiglet
import pandas as pd
from tabulate import tabulate

#Start the event loop


mydb = mysql.connector.connect(
    host="db4free.net",
    user="abdelmohsen",
    password="Pigasis12",
    database="olxserverremote"
)
print(mydb)

"""Register a user
"""
# get user input
def Registration():
    cursor = mydb.cursor()

    while True:
        username = input("Enter your username: ")

        # Check if the username already exists in the database
        sql = "SELECT * FROM Users WHERE Username = %s"
        value = (username,)
        cursor.execute(sql, value)
        result = cursor.fetchone()
        if result:
            print("Username already exists. Please try another username.")
        else:
            break

    Email = input("Enter your Email: ")
    gender = input("Enter your gender: ")
    Age = input("Enter your Age: ")
    Birthdate = input("Enter Your Birthdate in format yyyy-mm-dd: ")

    sql = "INSERT INTO Users (Username, EMAIL, Age, Birthdate, Gender) VALUES (%s, %s, %s, %s, %s)"
    values = (username, Email, Age, Birthdate, gender)
    cursor.execute(sql, values)
    mydb.commit()
    cursor.close()

    print("You are successfully registered")
    return username, Email, gender, Age, Birthdate

def inserting():
    cursor = mydb.cursor()
    Username = input("Please enter Your Username:")
    # Check if the username exists in the database
    sql = "SELECT * FROM Users WHERE Username = %s"
    value = (Username,)
    cursor.execute(sql, value)
    result = cursor.fetchone()
    if not result:
        print("Username does not exist, please register first")
        Registration()
        return
    AdID = input("Please Provide The AdID of the Ad you Purchased the car from: ")
    # Check if the AdID exists in the database
    while True:
        sql = "SELECT * FROM AD WHERE AdID = %s"
        value = (AdID,)
        cursor.execute(sql, value)
        result = cursor.fetchone()
        if result:
            break
        else:
            print("AdID is not valid, please try again")
            AdID = input("Please Provide The AdID of the Ad you Purchased the car from: ")
    # Check if the car has already been sold
    sql = "SELECT * FROM Purchase WHERE AdID = %s"
    value = (AdID,)
    cursor.execute(sql, value)
    result = cursor.fetchone()
    if result:
        print(Fore.RED + "This car was already sold, please make sure of the ID and try again" + Style.RESET_ALL)
        return

    Rate = input("What Rate Would you give to the ad's seller from 1-5? ")
    Review = input("Please Write a Textual Review of the ad -> ")

    # Insert the data into the Purchase table
    sql = "INSERT INTO Purchase (Rate, Review, USERNAME, AdID) VALUES (%s, %s, %s, %s)"
    values = (Rate, Review, Username, AdID)
    cursor.execute(sql, values)
    mydb.commit()
    cursor.close()
    print("Purchase information is successfully added to the database")

def Reviews():
    ad_id = input("Enter the ad ID: ")
    print("\n")

    # Execute the SQL query
    mycursor = mydb.cursor()
    mycursor.execute("SELECT Review, USERNAME FROM Purchase WHERE AdID = %s", (ad_id,))

    # Print the results
    results = mycursor.fetchall()
    if not results:
        print("No reviews found.")
    else:
        for (review, username) in results:
            print(Fore.GREEN + "Review Given: " + Style.RESET_ALL, review)
            print(Fore.GREEN + "Reviewed By:" + Style.RESET_ALL, username)
            print("\n")
    mycursor.fetchall() # clear any remaining results
    mycursor.close()



def Agreggated_Rating():
    mycursor = mydb.cursor()

    # Take input from the user
    seller_name = input("Enter the name of the seller: ")

    # Execute the SQL query
    query = """SELECT AVG(p.Rate) FROM Purchase p INNER JOIN AD a 
    ON p.AdID = a.AdID 
    INNER JOIN Seller s 
    ON a.SellerLink = s.SellerLink 
    WHERE s.Namee = %s"""
    mycursor.execute(query, (seller_name,))

    # Fetch the result
    result = mycursor.fetchone()

    # Print the result
    if result[0]:
        print("The aggregated rating of the seller chosen is:", result[0])
    else:
        print("No ratings found for this seller.")
# insert the new user into the database

# get user input


def ADSSHOW():
    SubCity = input("Enter the subcity location of the cars you want: ")
    location2 = input("Enter the city location of the cars you want: ")
    City = location2.rjust(6, ' ')
    brand = input("Enter the Car Brand you are looking for: ")
    body_type = input("Enter the body type of the car: ")
    year_start = int(input("Enter the start year of the car range: "))
    year_end = int(input("Enter the end year of the car range: "))

    # execute the query for main table
    cursor = mydb.cursor()
    sql = """
            SELECT a.AdID, a.SUBCITY, a.CITY, a.CreationDate, c.Model, c.Price, a.SellerLink, AVG(c.Price) AS AveragePrice, COUNT(*) AS NumOfListings
            FROM AD a
            INNER JOIN Car c ON a.AdID = c.AdID
            WHERE a.SUBCITY = %s AND a.CITY = %s AND c.Brand = %s AND c.BodyType = %s AND c.Yearr BETWEEN %s AND %s
            GROUP BY a.AdID, a.SUBCITY, a.CITY, a.CreationDate, c.Model, a.SellerLink
        """
    values = (SubCity, City, brand, body_type, year_start, year_end)
    cursor.execute(sql, values)
    result_main = cursor.fetchall()
    result_main = pd.DataFrame(result_main, columns=['AdID', 'Area', 'City', 'CreationDate', 'Model', 'Price', 'SellerLink', 'AveragePrice', 'NumOfListings'])
    # Strip the "Ad Id" prefix from the AdID column
    result_main['AdID'] = result_main['AdID'].str.replace('Ad id ', '')

    # execute the query for model table
    cursor = mydb.cursor()
    sql = """
            SELECT c.Model, COUNT(*) AS NumOfListings, AVG(c.Price) AS AveragePrice
            FROM AD a
            INNER JOIN Car c ON a.AdID = c.AdID
            WHERE a.SUBCITY = %s AND a.CITY = %s AND c.Brand = %s AND c.BodyType = %s AND c.Yearr BETWEEN %s AND %s
            GROUP BY c.Model
        """
    values = (SubCity, City, brand, body_type, year_start, year_end)
    cursor.execute(sql, values)
    result_model = cursor.fetchall()
    result_model = pd.DataFrame(result_model, columns=['Model', 'NumOfListings', 'AveragePrice'])

    # print the main table
    print("\nThe ADS:")
    print(tabulate(result_main[['AdID', 'Area', 'City', 'CreationDate', 'Model', 'Price', 'SellerLink']], headers='keys', tablefmt='pretty', showindex=False))
    print("\n")
    print("The Model count and their Average:")
    print(tabulate(result_model, headers='keys', tablefmt='pretty', showindex=False))


"""
Show all the used cars in a certain location in a given price range, with a given set of features
"""
def usedcars():

    location = input("Enter location: ")
    min_price = float(input("Enter minimum price: "))
    max_price = float(input("Enter maximum price: "))
    print(Fore.RED + "Those are the Features you choose from" + Style.RESET_ALL)

    table = [
        ["1", "ABS"],
        ["2", "Air Conditioning"],
        ["3", "Airbags"],
        ["4", "Alarm/Anti-Theft System"],
        ["5", "AM/FM Radio"],
        ["6", "Aux Audio In"],
        ["7", "Bluetooth System"],
        ["8", "Cruise Control"],
        ["9", "EBD"],
        ["10", "Fog Lights"],
        ["11", "Keyless Start"],
        ["12", "Leather Seats"],
        ["13", "Navigation System"],
        ["14", "Off-Road Tyres"],
        ["15", "Parking Sensors"],
        ["16", "Power Locks"],
        ["17", "Power Mirrors"],
        ["18", "Power Seats"],
        ["19", "Power Steering"],
        ["20", "Power Windows"],
        ["21", "Premium Wheels/Rims"],
        ["22", "Rear View Camera"],
        ["23", "Roof Rack"],
        ["24", "Sunroof"],
        ["25", "Touch Screen"],
        ["26", "USB Charger"]
    ]

    print(tabulate(table, headers=["No.", "Feature"], tablefmt="pretty"))

    print(Fore.RED +"Those are the Features you choose from\n"+Style.RESET_ALL)
    features = tuple(input("Enter features separated by comma: ").split(','))

    # Construct the SQL query with placeholders for the variables
    query = """
    SELECT c.* FROM Car c
    INNER JOIN AD a
    ON c.AdId = a.AdId
    INNER JOIN Extra_Features ef
    ON c.AdId = ef.CARID
    WHERE a.SUBCITY = %s
    AND c.price BETWEEN %s AND %s
    AND ef.Feature IN ({})
    """.format(','.join(['%s']*len(features)))
    # Execute the query with the variables as parameters
    cursor = mydb.cursor()
    Values = (location, min_price, max_price, *features)
    cursor.execute(query, Values)

    # Fetch the results and print them
    results = cursor.fetchall()
    result = pd.DataFrame(results, columns = ['AdID', 'Brand', 'Model', 'adtype', 'Fuel_Type', 'Price', 'Payment', 'Year', 'Odometer_range', 'Transmission', 'Condition', 'Color', 'BodyType', 'EngineCapacity', 'Video', 'Virtualtour'])
    # Strip the "Ad Id" prefix from the AdID column
    result['AdID'] = result['AdID'].str.replace('Ad id ', '')
    print(tabulate(result, headers='keys', tablefmt='pretty', showindex=False)+"\n")

# Close the database connection

"""Show the top 5 areas in cairo by amount of inventory and average price a given make / model
"""
#Get input from user
def top5areas():
    Brand = input("Enter Brand: ")
    Model = input("Enter Model: ")
    # Construct the SQL query with placeholders for the variables
    query = """
    SELECT ad.SUBCITY, COUNT(*) as inventory_count, AVG(car.Price) as avg_price
    FROM AD ad
    INNER JOIN Car car ON ad.AdID = car.AdID
    WHERE car.Brand = %s AND car.Model = %s AND ad.CITY = ' Cairo'
    GROUP BY ad.SUBCITY
    ORDER BY inventory_count DESC, avg_price DESC
    LIMIT 5
    """
    # Execute the query with the variables as parameters
    cursor = mydb.cursor()
    Values = (Brand, Model)
    cursor.execute(query, Values)
    # Fetch the results and print them
    results = cursor.fetchall()
    result = pd.DataFrame(results, columns=['Area', 'Inventory Count', 'Average Price'])
    print(tabulate(result, headers='keys', tablefmt='pretty', showindex=False)+"\n")
    cursor.close()

#Show all the cars listed by a specific owner (given their first and last name and / or phone no)
def carlistedbyowner():
    seller_name = input("Enter seller name: ")

    # Construct the SQL query with placeholders for the variables
    query = """
     SELECT c.* FROM Car c
     INNER JOIN AD a
     ON a.AdID = c.AdID
     INNER JOIN Seller s
     ON s.SellerLink = a.SellerLink
     WHERE s.Namee = %s
    """
    # Execute the query with the variables as parameters
    cursor = mydb.cursor()
    values = (seller_name,)
    cursor.execute(query, values)

    # Fetch the results and print them
    results = cursor.fetchall()
    result = pd.DataFrame(results, columns=['AdID', 'Brand', 'Model', 'adtype', 'Fuel_Type', 'Price', 'Payment', 'Year',
                                            'Odometer_range', 'Transmission', 'Condition', 'Color', 'BodyType',
                                            'EngineCapacity', 'Video', 'Virtualtour'])
    # Strip the "Ad Id" prefix from the AdID column
    result['AdID'] = result['AdID'].str.replace('Ad id ', '')
    print(tabulate(result, headers='keys', tablefmt='pretty', showindex=False))


# create cursor
"""Show the top 5 sellers by the amount of listings they have, along with their avg price per year
"""

# execute query
def top5seller():
    mycursor = mydb.cursor()
    mycursor.execute(
        """SELECT s.*, COUNT(*) as Listings,
        ROUND(AVG(c.Price)) as Avg_Price_Per_Year
        FROM Seller s INNER JOIN AD a
        ON s.SellerLink = a.SellerLink INNER JOIN Car c ON
        a.AdID = c.AdID
        GROUP BY s.SellerLink
        ORDER BY Listings DESC LIMIT 5""")

    # fetch results
    results = mycursor.fetchall()
    # print results
    result = pd.DataFrame(results, columns=['SellerLink', 'Seller Name', 'Joining Date', 'Number Of Ads Listed', 'Average Price'])
    result['Average Price'] = result['Average Price'].apply(lambda x: f"{int(x):,d} EGP")
    # Strip the "Ad Id" prefix from the AdID column
    print(tabulate(result, headers='keys', tablefmt='pretty', showindex=False))
    mycursor.close()
    # close cursor and connection


def topmodel():
    priceRange1 = float(input("Enter minimum price: "))
    PriceRange2 = float(input("Enter maximum price: "))
    mycursor = mydb.cursor()
    mycursor.execute(
        f"""SELECT Brand, Model, COUNT(*) as Inventory, ROUND(AVG(Price)) as Avg_Price
            FROM Car
            WHERE Price BETWEEN {priceRange1} AND {PriceRange2}
            GROUP BY Brand, Model
            ORDER BY Inventory DESC
            LIMIT 5"""
    )
    results = mycursor.fetchall()
    # Convert the results to a pandas dataframe and format the 'Average Price' column
    result_df = pd.DataFrame(results, columns=['Brand', 'Model', 'Count', 'Average Price'])
    result_df['Average Price'] = result_df['Average Price'].apply(lambda x: f"{int(x):,d} EGP")

    # Strip the "Ad Id" prefix from the AdID column
    print(tabulate(result_df, headers='keys', tablefmt='pretty', showindex=False))
    print("\n")



while True:
    text = "Welcome To OLX "
    font = "big"
    Welcomemsg = pyfiglet.figlet_format(text, font=font)
    print(Welcomemsg)
    print(Fore.YELLOW + "{:^100}".format("Please select an option:") + Style.RESET_ALL)
    print("".center(150, "-"))
    print("1. " + Fore.GREEN + "Register" + Style.RESET_ALL)
    print("2. " + Fore.GREEN + "Add a sale" + Style.RESET_ALL)
    print("3. " + Fore.GREEN + "View existing reviews of a given ad" + Style.RESET_ALL)
    print("4. " + Fore.GREEN + "View aggregated rating of a seller / owner" + Style.RESET_ALL)
    print("5. " + Fore.GREEN + "Show all the ads for a given car make, body type and year in a specific location" + Style.RESET_ALL)
    print("6. " + Fore.GREEN + "Show all the used cars in a certain location in a given price range, with a given set of features" + Style.RESET_ALL)
    print("7. " + Fore.GREEN + "Show the top 5 areas in cairo by amount of inventory and average price a given Brand and Model" + Style.RESET_ALL)
    print("8. " + Fore.GREEN + "Show the top 5 sellers by the amount of listings they have, along with their avg price per year" + Style.RESET_ALL)
    print("9. " + Fore.GREEN + "Show all the Cars listed by a specific owner" + Style.RESET_ALL)
    print("10. " + Fore.GREEN + "Show the top 5 Brand and Models for a given year range" + Style.RESET_ALL)
    print("".center(150, "-"))
    print("E. " + Fore.RED + "Exit" + Style.RESET_ALL)

    choice = input("Enter your choice (1-10) or E/e to exit: ")

    if choice == "1":
        Registration()
        choice2 = input(Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "2":
        inserting()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "3":
        Reviews()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "4":
        Agreggated_Rating()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "5":
        ADSSHOW()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "6":
        usedcars()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "7":
        top5areas()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "8":
        top5seller()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "9":
        carlistedbyowner()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break
    elif choice == "10":
        topmodel()
        choice2 = input(
            Fore.GREEN + "Do you want to get back to the Main Menu? Answer by a Y or N:  " + Style.RESET_ALL)
        if choice2 == "y" or choice2 == "Y":
            continue
        elif choice2 == "N" or choice2 == "n":
            print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
            mydb.close()
            break

    elif choice == "E" or "e":
        print(Fore.RED + "Exiting the program..." + Style.RESET_ALL)
        mydb.close()
        break
    else:
        print(Fore.RED + "Invalid choice, please try again." + Style.RESET_ALL)
        continue

