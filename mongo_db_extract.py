import pandas as pd
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["excel_db"]  # Use the same database name as in Step 1

# Define the Excel file and sheet name you want to retrieve
excel_file = "Admission_data"  # Name of your Excel file (without the .xlsx extension)
sheet_name = "Admission_data"      # Name of the sheet you want to retrieve

# Create the MongoDB collection name
collection_name = f"{excel_file}_{sheet_name}".replace(" ", "_")

# Fetch the data from the specified collection
data = list(db[collection_name].find())  # Fetch all documents in the collection

# Convert the MongoDB data to a DataFrame
df = pd.DataFrame(data).drop(columns=["_id"])  # Drop the '_id' column (auto-created by MongoDB)

# Display the first few rows of the DataFrame
print(f"\n📄 Data from collection: {collection_name}")
print(df.head())
