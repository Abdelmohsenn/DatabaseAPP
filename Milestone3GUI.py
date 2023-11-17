import mysql.connector
import flask
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import pandas as pd
from tabulate import tabulate

#Start the event loop


mydb = mysql.connector.connect(
    host="db4free.net",
    user="abdelmohsen",
    password="Pigasis12",
    database="olxserverremote"
)

def Registration(root):
    cursor = mydb.cursor()

    def submit():
        # Get values from entries
        username = username_entry.get()
        email = email_entry.get()
        gender = gender_entry.get()
        age = age_entry.get()
        birthdate = birthdate_entry.get()

        # Check if the username already exists in the database
        sql = "SELECT * FROM Users WHERE Username = %s"
        value = (username,)
        cursor.execute(sql, value)
        result = cursor.fetchone()
        if result:
            message_label.config(text="Username already exists. Please try another username.")
            message_label.config(fg="red")
            username_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            gender_entry.delete(0, tk.END)
            age_entry.delete(0, tk.END)
            birthdate_entry.delete(0, tk.END)
        else:
            sql = "INSERT INTO Users (Username, EMAIL, Age, Birthdate, Gender) VALUES (%s, %s, %s, %s, %s)"
            values = (username, email, age, birthdate, gender)
            cursor.execute(sql, values)
            mydb.commit()
            cursor.close()

            message_label.config(text="You are successfully registered")
            username_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            gender_entry.delete(0, tk.END)
            age_entry.delete(0, tk.END)
            birthdate_entry.delete(0, tk.END)
        window.after(5000, continue_prompt, window, root)

    window = tk.Tk()
    window.title("Registration")
    username_label = tk.Label(window, text="Username:")
    email_label = tk.Label(window, text="Email:")
    gender_label = tk.Label(window, text="Gender:")
    age_label = tk.Label(window, text="Age:")
    birthdate_label = tk.Label(window, text="Birthdate (yyyy-mm-dd):")
    message_label = tk.Label(window, text="")
    username_entry = tk.Entry(window)
    email_entry = tk.Entry(window)
    gender_entry = tk.Entry(window)
    age_entry = tk.Entry(window)
    birthdate_entry = tk.Entry(window)
    submit_button = tk.Button(window, text="Submit", command=submit)

    # Add the labels and entries to the window
    username_label.pack()
    username_entry.pack()
    email_label.pack()
    email_entry.pack()
    gender_label.pack()
    gender_entry.pack()
    age_label.pack()
    age_entry.pack()
    birthdate_label.pack()
    birthdate_entry.pack()
    submit_button.pack()
    message_label.pack()

    window.mainloop()


def inserting(root):
    def execute():
        cursor = mydb.cursor()
        Username = username_entry.get()
        # Check if the username exists in the database
        sql = "SELECT * FROM Users WHERE Username = %s"
        value = (Username,)
        cursor.execute(sql, value)
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Username does not exist, please register first")
            window.destroy()
            Registration()
            return
        AdID = adid_entry.get()
        # Check if the AdID exists in the database
        while True:
            sql = "SELECT * FROM AD WHERE AdID = %s"
            value = (AdID,)
            cursor.execute(sql, value)
            result = cursor.fetchone()
            if result:
                break
        # Check if the car has already been sold
        sql = "SELECT * FROM Purchase WHERE AdID = %s"
        value = (AdID,)
        cursor.execute(sql, value)
        result = cursor.fetchone()
        if result:
            messagebox.showerror("Error", "This car was already sold, please make sure of the ID and try again")
            return

        Rate = rate_entry.get()
        Review = review_entry.get()

        # Insert the data into the Purchase table
        sql = "INSERT INTO Purchase (Rate, Review, USERNAME, AdID) VALUES (%s, %s, %s, %s)"
        values = (Rate, Review, Username, AdID)
        cursor.execute(sql, values)
        mydb.commit()
        cursor.close()
        messagebox.showinfo("Success", "Purchase information is successfully added to the database")
        window.after(5000, continue_prompt, window, root)


# Create the tkinter window
    window = tk.Tk()
    window.title("Car Purchase Review Form")

    # Create the username entry box
    username_label = tk.Label(window, text="Username:")
    username_label.grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    # Create the AdID entry box
    adid_label = tk.Label(window, text="AdID:")
    adid_label.grid(row=1, column=0, padx=10, pady=10)
    adid_entry = tk.Entry(window)
    adid_entry.grid(row=1, column=1, padx=10, pady=10)

    # Create the Rate entry box
    rate_label = tk.Label(window, text="Rate (1-5):")
    rate_label.grid(row=2, column=0, padx=10, pady=10)
    rate_entry = tk.Entry(window)
    rate_entry.grid(row=2, column=1, padx=10, pady=10)

    # Create the Review entry box
    review_label = tk.Label(window, text="Review:")
    review_label.grid(row=3, column=0, padx=10, pady=10)
    review_entry = tk.Entry(window)
    review_entry.grid(row=3, column=1, padx=10, pady=10)

    # Create the Submit button
    submit_button = tk.Button(window, text="Submit", command=execute)
    submit_button.grid(row=4, column=1, padx=10, pady=10)

    # Run the tkinter window
    window.mainloop()


    
def ads(root):
    def searchads():
        subcity = subcity_entry.get()
        location2 = location2_entry.get()
        city = location2.rjust(6, ' ')
        brand = brand_entry.get()
        body_type = body_type_entry.get()
        year_start = int(year_start_entry.get())
        year_end = int(year_end_entry.get())

        result_table.delete(*result_table.get_children())

        # Execute the query for the main table
        cursor = mydb.cursor()
        sql = """
                SELECT a.AdID, a.SUBCITY, a.CITY, a.CreationDate, c.Model, c.Price, a.SellerLink, AVG(c.Price) AS AveragePrice, COUNT(*) AS NumOfListings
                FROM AD a
                INNER JOIN Car c ON a.AdID = c.AdID
                WHERE a.SUBCITY = %s AND a.CITY = %s AND c.Brand = %s AND c.BodyType = %s AND c.Yearr BETWEEN %s AND %s
                GROUP BY a.AdID, a.SUBCITY, a.CITY, a.CreationDate, c.Model, a.SellerLink
            """
        values = (subcity, city, brand, body_type, year_start, year_end)
        cursor.execute(sql, values)
        result_main = cursor.fetchall()
        result_table.heading('#0', text='AdID')
        for i, column in enumerate(('Area', 'City', 'CreationDate', 'Model', 'Price', 'SellerLink', 'AveragePrice', 'NumOfListings')):
            result_table.heading(str(i), text=column)
        for row in result_main:
            ad_id = row[0].replace('Ad id ', '') # strip "Ad id " prefix from AdID column
            result_table.insert('', tk.END, text=ad_id, values=row[1:])


        # Execute the query for the model table
        cursor = mydb.cursor()
        sql = """
                SELECT c.Model, COUNT(*) AS NumOfListings, AVG(c.Price) AS AveragePrice
                FROM AD a
                INNER JOIN Car c ON a.AdID = c.AdID
                WHERE a.SUBCITY = %s AND a.CITY = %s AND c.Brand = %s AND c.BodyType = %s AND c.Yearr BETWEEN %s AND %s
                GROUP BY c.Model
            """
        values = (subcity, city, brand, body_type, year_start, year_end)
        cursor.execute(sql, values)
        result_model = cursor.fetchall()
        result_table2.heading('#0', text='Model')
        for i, column in enumerate(('NumOfListings', 'AveragePrice')):
            result_table2.heading(str(i), text=column)
        for row in result_model:
            ad_id = row[0].replace('Ad id ', '') # strip "Ad id " prefix from AdID column
            result_table2.insert('', tk.END, text=ad_id, values=row[1:])



    window = tk.Tk()
    window.title("ADS Show")
    window.geometry("800x600")

    # Create the input labels and text boxes
    subcity_label = tk.Label(window, text="Enter the subcity location of the cars you want:")
    subcity_label.pack()
    subcity_entry = tk.Entry(window)
    subcity_entry.pack()

    location2_label = tk.Label(window, text="Enter the city location of the cars you want:")
    location2_label.pack()
    location2_entry = tk.Entry(window)
    location2_entry.pack()

    brand_label = tk.Label(window, text="Enter the Car Brand you are looking for:")
    brand_label.pack()
    brand_entry = tk.Entry(window)
    brand_entry.pack()

    body_type_label = tk.Label(window, text="Enter the body type of the car:")
    body_type_label.pack()
    body_type_entry = tk.Entry(window)
    body_type_entry.pack()

    year_start_label = tk.Label(window, text="Enter the start year of the car range:")
    year_start_label.pack()
    year_start_entry = tk.Entry(window)
    year_start_entry.pack()

    year_end_label = tk.Label(window, text="Enter the end year of the car range:")
    year_end_label.pack()
    year_end_entry = tk.Entry(window)
    year_end_entry.pack()
    
    search_button = tk.Button(window, text="Search", command=searchads)
    search_button.pack()

    table_frame1 = tk.Frame(window)
    table_frame1.pack()

    table1 = tk.Label(table_frame1, text='Ads Table')
    table1.pack()
    result_table = ttk.Treeview(window, columns=('AdID', 'Area', 'City', 'CreationDate', 'Model', 'Price', 'SellerLink', 'AveragePrice', 'NumOfListings'), height=20)
    result_table.pack()

    table_frame2 = tk.Frame(window)
    table_frame2.pack()
    table2 = tk.Label(table_frame2, text='Models Table')
    table2.pack()
    result_table2 = ttk.Treeview(window, columns=('Model', 'NumOfListings', 'AveragePrice'), height=30)
    result_table2.pack(expand=True, fill=tk.BOTH)

    window.mainloop


def Reviews(root):
    def execute():
        ad_id = entryADID.get()

        # Execute the SQL query
        mycursor = mydb.cursor()
        mycursor.execute("SELECT Review, USERNAME FROM Purchase WHERE AdID = %s", (ad_id,))

        # Print the results
        results = mycursor.fetchall()
        if not results:
            messagebox.showinfo("No reviews found.")
        else:
            review_text.delete("1.0", tk.END)
            for (review, username) in results:
                review_text.insert(tk.END, f"Review Given: {review}\nReviewed By: {username}\n\n")

        mycursor.fetchall() # clear any remaining results
        mycursor.close()
        window.after(5000, continue_prompt, window, root)


    window = tk.Tk()
    window.title("Reviews")
    window.geometry("800x500")

    labelADID = tk.Label(window, text="Ad ID:")
    entryADID = tk.Entry(window)
    button_show_reviews = tk.Button(window, text="Show Reviews", command=execute)
    review_text = tk.Text(window, height=100, width=100)

    labelADID.pack(pady=10, anchor="center")
    entryADID.pack(pady=10, anchor="center")
    button_show_reviews.pack(pady=10, anchor="center")
    review_text.pack(pady=10, anchor="center")
    window.mainloop()

    


def topmodel(root):
    def searchmodel():

        result_table.delete(*result_table.get_children())
        priceRange1 = float(min_price_entry.get())
        priceRange2 = float(max_price_entry.get())

        mycursor = mydb.cursor()
        mycursor.execute(
            f"""SELECT Brand, Model, COUNT(*) as Inventory, ROUND(AVG(Price)) as Avg_Price
                FROM Car
                WHERE Price BETWEEN {priceRange1} AND {priceRange2}
                GROUP BY Brand, Model
                ORDER BY Inventory DESC
                LIMIT 5"""
        )
        results = mycursor.fetchall()
        
        # Clear previous search results
        for child in result_table.get_children():
            result_table.delete(child)
        
        # Insert the results into the table
        for row in results:
            result_table.insert('', tk.END, text=row[0], values=row[1:])
        for col in result_table["columns"]:
            result_table.column(col, anchor="center")

        mycursor.close()
        window.after(5000, continue_prompt, window, root)


# Create the main window
    window = tk.Tk()
    window.title("Top Models")
    window.geometry("800x600")

    # Min price input
    min_price_label = tk.Label(window, text="Enter minimum price:")
    min_price_label.pack(pady=10, anchor="center")
    min_price_entry = tk.Entry(window)
    min_price_entry.pack(pady=10, anchor="center")

    # Max price input
    max_price_label = tk.Label(window, text="Enter maximum price:")
    max_price_label.pack(pady=10, anchor="center")
    max_price_entry = tk.Entry(window)
    max_price_entry.pack(pady=10, anchor="center")

    # Search button
    search_button = tk.Button(window, text="Search", command=searchmodel)
    search_button.pack(pady=10, anchor="center")

    # Result table
    result_table = ttk.Treeview(window, columns=('Brand', 'Model', 'Count', 'Average Price'), height=30)
    result_table.heading('#0', text='Brand')
    for i, column in enumerate(('Model', 'Count', 'Average Price')):
        result_table.heading(str(i), text=column)
        
    # Pack the Treeview widget
    result_table.pack(expand=True, fill=tk.BOTH)

    window.mainloop()

    # Close the database connection

    # Convert the results to a pandas dataframe and format the 'Average Price' column

def top5seller(root):
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
    # result = pd.DataFrame(results, columns=['SellerLink', 'Seller Name', 'Joining Date', 'Number Of Ads Listed', 'Average Price'])
    # result['Average Price'] = result['Average Price'].apply(lambda x: f"{int(x):,d} EGP")
    
    # Create the GUI window
    window = tk.Tk()
    window.title("Top 5 Sellers")
    window.geometry("800x600")
    
    # Create the Treeview widget
    result_table = ttk.Treeview(window, columns=('SellerLink', 'Seller Name', 'Joining Date', 'Number Of Ads Listed', 'Average Price'),height=30)
    result_table.heading('#0', text='Seller Link')
    for i, column in enumerate(('Seller Name', 'Joining Date', 'Number Of Ads Listed', 'Average Price')):
        result_table.heading(str(i), text=column)
    
    # Insert the results into the table
    for row in results:
        result_table.insert('', tk.END, text=row[0], values=row[1:])
    for col in result_table["columns"]:
        result_table.column(col, anchor="center")
    
    
    # Pack the Treeview widget
    result_table.pack(expand=True, fill=tk.BOTH)

    # Run the GUI Main
    window.mainloop()
    continue_prompt(window,root)
    
    mycursor.close()
    window.after(5000, continue_prompt, window, root)



def usedcars(root):

    def search():
        result_table.delete(*result_table.get_children())
        location = location_entry.get()
        min_price = float(min_price_entry.get())
        max_price = float(max_price_entry.get())
        features = tuple(features_entry.get().split(','))

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
        result_table.delete(*result_table.get_children())
        result_table.heading('#0', text='AdID')
        for i, column in enumerate(('Brand', 'Model', 'adtype', 'Fuel_Type', 'Price', 'Payment', 'Year', 'Odometer_range', 'Transmission', 'Condition', 'Color', 'BodyType', 'EngineCapacity', 'Video', 'Virtualtour')):
            result_table.heading(str(i), text=column)
        for col in result_table["columns"]:
             result_table.column(col, anchor="center")
        for row in results:
            ad_id = row[0].replace('Ad id ', '') # strip "Ad id " prefix from AdID column
            result_table.insert('', tk.END, text=ad_id, values=row[1:])
         # Update the label with the string

    # Connect to the database

    # Create the GUI
    window = tk.Tk()
    window.title("Used Cars Search")
    window.geometry("800x600")

    # Location input
    location_label = tk.Label(window, text="Enter location:")
    location_label.pack()
    location_entry = tk.Entry(window)
    location_entry.pack()

    # Min price input
    min_price_label = tk.Label(window, text="Enter minimum price:")
    min_price_label.pack()
    min_price_entry = tk.Entry(window)
    min_price_entry.pack()

    # Max price input
    max_price_label = tk.Label(window, text="Enter maximum price:")
    max_price_label.pack()
    max_price_entry = tk.Entry(window)
    max_price_entry.pack()

    # Features input
    features_label = tk.Label(window, text="Enter features (separated by comma):")
    features_label.pack()
    features_entry = tk.Entry(window)
    features_entry.pack()

    # Search button
    search_button = tk.Button(window, text="Search", command=search)
    search_button.pack()

    # Result table
    result_table = ttk.Treeview(window, columns=('AdID', 'Brand', 'Model', 'adtype', 'Fuel_Type', 'Price', 'Payment', 'Year', 'Odometer_range', 'Transmission', 'Condition', 'Color', 'BodyType', 'EngineCapacity', 'Video', 'Virtualtour' ), height=50)
    result_table.pack(expand=True, fill=tk.BOTH)


    window.mainloop()




def Aggregated_Rating(root):
    def execute():
    # Get the seller name from the entry box
        seller_name = sellerentry.get()

        # Execute the SQL query
        mycursor = mydb.cursor()
        query = """SELECT AVG(p.Rate) FROM Purchase p INNER JOIN AD a 
        ON p.AdID = a.AdID 
        INNER JOIN Seller s 
        ON a.SellerLink = s.SellerLink 
        WHERE s.Namee = %s"""
        mycursor.execute(query, (seller_name,))

        # Fetch the result
        result_tuple = mycursor.fetchone()

    # Update the result label
        if result_tuple[0]:
            result.config(text="The aggregated rating of the seller chosen is: " + str(result_tuple[0]))
        else:
            result.config(text="No ratings found for this seller.")
        window.after(5000, continue_prompt, window, root)

# Create the Tkinter window
    window = tk.Tk()
    window.title("Aggregated Rating Calculator")
    window.geometry("800x600")


    # Create the seller name label and entry box
    sellerlabel = tk.Label(window, text="Enter the name of the seller:",font=("Arial", 20))
    sellerlabel.pack()
    sellerentry = tk.Entry(window,font=("Arial", 20))
    sellerentry.pack(pady=10, anchor="center")

    # Create the button to calculate the aggregated rating
    calculate = tk.Button(window, text="Calculate",font=("Arial", 20), command=execute)
    calculate.pack(pady=10, anchor="center")

    # Create the label to display the result
    result = tk.Label(window, text="", font=("Arial", 20))
    result.pack(fill=tk.BOTH, expand=True)

    # Run the Tkinter event loop
    window.mainloop



def top5areas(root):

    def execute():
        result_table.delete(*result_table.get_children())
        result_table.delete()
        Brand = Brand_entry.get()
        Model = Model_entry.get()
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
        result_table.heading('#0', text='Area')
        for i, column in enumerate(('Inventory Count', 'Average Price')):
            result_table.heading(str(i), text=column)
        for row in results:
            result_table.insert('', tk.END, text=row[0], values=row[1:])
        cursor.close()
        window.after(5000, continue_prompt, window, root)
        
    window=tk.Tk()
    Brandlablel=tk.Label(window, text="Enter Brand: ")
    Brandlablel.pack(pady=10, anchor="center")
    Brand_entry=tk.Entry(window)
    Brand_entry.pack(pady=10, anchor="center")

    Modellablel=tk.Label(window, text="Enter Model: ")
    Modellablel.pack(pady=10, anchor="center")
    Model_entry=tk.Entry(window)
    Model_entry.pack(pady=10, anchor="center")

    search_button = tk.Button(window, text="Search", command=execute)
    search_button.pack(pady=10, anchor="center")

    result_table = ttk.Treeview(window, columns=('Area', 'Inventory Count', 'Average Price'), height=50)
    result_table.pack(expand=True, fill=tk.BOTH)
    window.mainloop()
         





def carlistedbyowner(root):
    def execute():
        seller_name = name_entry.get()
        result_table.delete(*result_table.get_children())

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
        results = cursor.fetchall()

        result_table.heading('#0', text='AdID')
        for i, column in enumerate(('Brand', 'Model', 'adtype', 'Fuel_Type', 'Price', 'Payment', 'Year','Odometer_range', 'Transmission', 'Condition', 'Color', 'BodyType','EngineCapacity', 'Video', 'Virtualtour')):
            result_table.heading(str(i), text=column)
        for row in results:
            ad_id = row[0].replace('Ad id ', '') # strip "Ad id " prefix from AdID column
            result_table.insert('', tk.END, text=ad_id, values=row[1:])
        
        # Call continue_prompt function after 5 seconds
        window.after(5000, continue_prompt, window, root)

    window = tk.Tk()
    window.title("Sellers")
    window.geometry("800x600")

    name_label = tk.Label(window, text="Enter the Seller Name:")
    name_label.pack(pady=10, anchor="center")
    name_entry = tk.Entry(window)
    name_entry.pack(pady=10, anchor="center")

    submitButton = tk.Button(window, text="Search", command=execute)
    submitButton.pack(pady=10, anchor="center")

    result_table = ttk.Treeview(window, columns=('AdID', 'Brand', 'Model', 'adtype', 'Fuel_Type', 'Price', 'Payment', 'Year','Odometer_range', 'Transmission', 'Condition', 'Color', 'BodyType','EngineCapacity', 'Video', 'Virtualtour'), height=30)
    result_table.pack(expand=True, fill=tk.BOTH)

    window.mainloop()
    

def main_window():

    root = Tk()

    label = Label(root, text="Welcome To OLX", font=("Arial Bold", 30))
    label.pack()

    registerbutton = Button(root, text="1. Register", command=lambda : Registration(root))
    registerbutton.pack(pady=10, anchor="center")

    addsale_button = Button(root, text="2. Add a sale", command=lambda :inserting(root))
    addsale_button.pack(pady=10, anchor="center")

    view_reviewss= Button(root, text="3. View existing reviews of a given ad", command=lambda :Reviews(root))
    view_reviewss.pack(pady=10, anchor="center")

    view_rating_button = Button(root, text="4. View aggregated rating of a seller / owner", command=lambda :Aggregated_Rating(root))
    view_rating_button.pack(pady=10, anchor="center")

    show_ads_button = Button(root, text="5. Show all the ads for a given car make, body type and year in a specific location", command=lambda :ads(root))
    show_ads_button.pack(pady=10, anchor="center")

    show_used_cars_button = Button(root, text="6. Show all the used cars in a certain location in a given price range, with a given set of features", command=lambda :usedcars(root))
    show_used_cars_button.pack(pady=10, anchor="center")

    top_5_areas_button = Button(root, text="7. Show the top 5 areas in cairo by amount of inventory and average price a given Brand and Model", command=lambda: top5areas(root))
    top_5_areas_button.pack(pady=10, anchor="center")

    top_5_sellers_button = Button(root, text="8. Show the top 5 sellers by the amount of listings they have, along with their avg price per year", command=lambda :top5seller(root))
    top_5_sellers_button.pack(pady=10, anchor="center")

    cars_by_owner_button = Button(root, text="9. Show all the Cars listed by a specific owner", command=lambda :carlistedbyowner(root))
    cars_by_owner_button.pack(pady=10, anchor="center")

    top_brand_models_button = Button(root, text="10. Show the top 5 Brand and Models for a given year range", command=lambda :topmodel(root))
    top_brand_models_button.pack(pady=10, anchor="center")

    exitbutton = Button(root, text="E. Exit", command=root.quit)
    exitbutton.pack(pady=10, anchor="center")

    root.mainloop()

def continue_prompt(window,root):
    def on_yes():
        prompt_window.destroy()
        window.destroy()

    def on_no():
        prompt_window.destroy()
        root.destroy()
        window.destroy()

    prompt_window = Tk()
    prompt_window.title("Confirmation")
    prompt_label = Label(prompt_window, text="Do you want to continue?")
    prompt_label.pack()

    yes_button = Button(prompt_window, text="Yes", command=on_yes)
    yes_button.pack(side=LEFT, padx=5, pady=5)

    no_button = Button(prompt_window, text="No", command=on_no)
    no_button.pack(side=RIGHT, padx=5, pady=5)

    prompt_window.mainloop()


# Call the main_window function to start the program
main_window()

