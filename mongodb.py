import pandas as pd
from pymongo import MongoClient
import os

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["excel_db"]

# Folder where all Excel files are stored
folder_path = "Excel_sheets"  # change this to your folder path

# Loop through all Excel files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        file_path = os.path.join(folder_path, file_name)
        excel_name = os.path.splitext(file_name)[0]

        # Read all sheets in the Excel file
        xls = pd.read_excel(file_path, sheet_name=None)
        for sheet_name, df in xls.items():
            collection_name = f"{excel_name}_{sheet_name}".replace(" ", "_")
            print(f"Inserting {collection_name} into MongoDB")
            collection = db[collection_name]
            collection.delete_many({})  # clear old data
            collection.insert_many(df.to_dict("records"))

print("✅ All Excel sheets inserted.")
