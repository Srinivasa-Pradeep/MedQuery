import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from config import CHAT_PROMPT_TEMPLATE
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import seaborn as sns
import numpy as np
import datetime
import plotly.graph_objects as go
from pymongo import MongoClient
if 'flag' not in st.session_state:
    st.session_state.flag = 0
st.title("MedQuery")
st.markdown("### Chat with Excel sheet using Llama")
st.markdown("---")
df = pd.DataFrame()
tab1, tab2 = st.tabs(["Excel Sheets", "Mongo DB"])

with tab1:
    st.session_state.flag = 0
    st.header("From Excel Sheet")
    # File Upload Section
    PDF_STORAGE_PATH = 'files/'
    uploaded_file = st.file_uploader(
        "Upload a Excel Sheet",
        type="xlsx",
        help="Select a Excel Sheet for Querying",
        accept_multiple_files=False
    )
    options = ["Patients data", "Admission data", "Doctors data", "Insurance data", "Medicine data","Mortality data"]
    selected_option = st.selectbox('Select an option', options, index=None,key="input1")


    def save_uploaded_file(uploaded_file):
        file_path = PDF_STORAGE_PATH + uploaded_file.name
        with open(file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())
        return file_path

    if uploaded_file and selected_option:
        st.session_state.flag  = 1
        file_path = save_uploaded_file(uploaded_file)
        df = pd.read_excel(file_path, header=0)
        #print(df.dtypes)
        #st.dataframe(df)
        if(selected_option == "Mortality data"):
            date_format = '%m/%d/%Y'  
            df=df.dropna(axis=0)
            df['DATE OF BROUGHT DEAD'] = pd.to_datetime(df['DATE OF BROUGHT DEAD'], format=date_format)

        elif(selected_option == "Admission data"):
            date_format = '%m/%d/%Y'  
            df['D.O.A'] = pd.to_datetime(df['D.O.A'], format=date_format, errors='coerce')
            df['D.O.D'] = pd.to_datetime(df['D.O.D'], format=date_format, errors='coerce')
            df['month year'] = pd.to_datetime(df['month year'], format='%b-%Y', errors='coerce')
            df=df.dropna(axis=0)
            df['ALCOHOL'] = pd.to_numeric(df['ALCOHOL'])
            #df['SMOKING'] = pd.to_numeric(df['SMOKING'])
            
        elif(selected_option == "Medicine data"):
            df['Strength'] = df['Strength'].str.extract('(\d+)')  
            df['Strength'] = pd.to_numeric(df['Strength'], errors='coerce')
        st.markdown("### Uploaded Data")
        st.dataframe(df)
   
with tab2:
    st.session_state.flag = 0
    st.header("From Mongo DB")
    options = ["Patients data", "Admission data", "Doctors data", "Insurance data", "Medicine data","Mortality data"]
    selected_option = st.selectbox('Select an option', options, index=None,key="input2")

    if selected_option:
        st.session_state.flag = 1
        client = MongoClient("mongodb://localhost:27017/")
        db = client["excel_db"]  # Use the same database name as in Step 1

        # Define the Excel file and sheet name you want to retrieve
        if(selected_option == "Admission data"):
            excel_file = "Admission_data"  # Name of your Excel file (without the .xlsx extension)
            sheet_name = "Admission_data"      # Name of the sheet you want to retrieve
        elif(selected_option == "Patients data"):
            excel_file = "Patients_data"  # Name of your Excel file (without the .xlsx extension)
            sheet_name = "Sheet1" 
        elif(selected_option == "Doctors data"):
            excel_file = "Doctors data"  # Name of your Excel file (without the .xlsx extension)
            sheet_name = "Doctors data" 
        elif(selected_option == "Insurance data"):
            excel_file = "Insurance data"  # Name of your Excel file (without the .xlsx extension)
            sheet_name = "Insurance data"
        elif(selected_option == "Medicine data"):
            excel_file = "Medicine data"  # Name of your Excel file (without the .xlsx extension)
            sheet_name = "Medicine data"
        elif(selected_option == "Mortality data"):
            excel_file = "Mortality data"  # Name of your Excel file (without the .xlsx extension)
            sheet_name = "Mortality data"
        # Create the MongoDB collection name
        collection_name = f"{excel_file}_{sheet_name}".replace(" ", "_")

        # Fetch the data from the specified collection
        data = list(db[collection_name].find())  # Fetch all documents in the collection

        # Convert the MongoDB data to a DataFrame
        df = pd.DataFrame(data).drop(columns=["_id"])  # Drop the '_id' column (auto-created by MongoDB)

        #print(df.dtypes)
        if(selected_option == "Mortality data"):
            date_format = '%m/%d/%Y'  
            df=df.dropna(axis=0)
            df['DATE OF BROUGHT DEAD'] = pd.to_datetime(df['DATE OF BROUGHT DEAD'], format=date_format)

        elif(selected_option == "Admission data"):
            date_format = '%m/%d/%Y'  
            df['D.O.A'] = pd.to_datetime(df['D.O.A'], format=date_format, errors='coerce')
            df['D.O.D'] = pd.to_datetime(df['D.O.D'], format=date_format, errors='coerce')
            df['month year'] = pd.to_datetime(df['month year'], format='%b-%Y', errors='coerce')
            df=df.dropna(axis=0)
            df['ALCOHOL'] = pd.to_numeric(df['ALCOHOL'])
            #df['SMOKING'] = pd.to_numeric(df['SMOKING'])
            
        elif(selected_option == "Medicine data"):
            df['Strength'] = df['Strength'].str.extract('(\d+)')  
            df['Strength'] = pd.to_numeric(df['Strength'], errors='coerce')

        st.markdown("### Uploaded Data")
        st.dataframe(df)

st.markdown("<h2 style='text-align: center; color: #4CAF50; font-family: Arial;'>MedQuery</h2>",
    unsafe_allow_html=True,
)
try:
    template = CHAT_PROMPT_TEMPLATE[selected_option]
except KeyError:
    template = CHAT_PROMPT_TEMPLATE["Admission data"]
prompt = ChatPromptTemplate.from_template(template)
print(selected_option)
# Load the local granite3.1-dense model that we pulled using ollama
model = OllamaLLM(model="llama3.2:1b")
chain = prompt | model

# Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How may I help you?","type":0}
    ]
# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"]==0:
            st.markdown(message["content"])
        elif message["type"]==1:
            st.dataframe(message["content"])
        elif message["type"]==2:
            st.plotly_chart(message["content"]["fig"],key=message["content"]["key"])
        elif message["type"]==3:
            st.image([message["content"]],use_container_width=True)

# Handle user input
if user_input := st.chat_input("What is up?",key="tab1"):
    # Add user message to session state
    flag=0
    st.session_state.messages.append({"role": "user", "content": user_input,"type":0})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        try_count = 3
        error_occured = 1
        while(try_count > 0 and error_occured == 1):
            response = chain.invoke({"question": user_input})
            
            response = response.splitlines()[0]
            response = ' '.join(response.split())
            #if(response[0]=='0' and response[2:4]!="df" and response[1:3]!="df"):
            #    flag=0
            #    st.markdown(response[1:])

            if(response[0]=='2'):
                flag=2
                try:
                    if(response[0]=="2"):
                        response=response[1:]
                    response_data = eval(response)
                    try:
                        result_df = pd.DataFrame(response_data)
                    except (TypeError, ValueError):
                        result_df = pd.Series(response_data)
                        result_df = result_df.to_frame()
                    print(result_df)
                    column_name = result_df.columns[0]
                    fig = go.Figure(data=[go.Pie(
                        labels=result_df[column_name].index,
                        values=result_df[column_name],
                        hovertemplate='%{label}: %{value}'
                    )])

                    fig.update_layout(title_text=f'Counts of {result_df.index.name.capitalize()}',
                                    template='plotly_dark')
                    
                    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  
                    key = f'plot_{current_time}'
                    chart_data={"fig":fig,"key":key}
                    st.plotly_chart(fig,key=key)
                    error_occured = 0
                except Exception as e:
                    print(e)
                    st.markdown(e)
                    flag=0
                    response="0"+"There was a problem, Try Running the same query again !!\n"
                    error_occured = 1

            

            elif(response[0]=='3'):
                flag=3
                try:
                    if(response[0]=="3"):
                        response=response[1:]
                    response_data = eval(response)
                    
                    try:
                        result_df = pd.DataFrame(response_data)
                    except (TypeError, ValueError):
                        result_df = pd.Series(response_data)
                        result_df = result_df.to_frame()
                    print(result_df)
                    result_df=result_df.dropna(axis=0)
                    column_name = result_df.columns[0]
                    x=result_df[column_name].index
                    y=result_df[column_name]
                    palette=sns.cubehelix_palette(len(y))

                    fig, ax = plt.subplots(figsize=(10,6))
                    sns.barplot(x=x, y=y, ax=ax,hue=x, legend=False, palette=palette)
                    ax.set_title(f'Counts of {result_df.index.name.capitalize()}')
                    ax.set_xticks(x)
                    ax.set_xticklabels(ax.get_xticklabels(),rotation=45, ha='right')
                    for p in ax.patches:
                        ax.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width()/2, p.get_height()), ha='center', va='center',size=10, xytext=(0, 8), textcoords='offset points')
                    
                    # Save the plot to a BytesIO object
                    plt.tight_layout()
                    img = BytesIO()
                    plt.savefig(img, format='png')
                    img.seek(0)

                    # Display the image using streamlit
                    st.image([img], use_container_width=True)

                    error_occured = 0
                except Exception as e:
                    print(e)
                    flag=0
                    response="0"+"There was a problem, Try Running the same query again !!\n"
                    error_occured = 1
            else:
                
                flag=1
                try:
                    if(response[0]=="0"):
                        response=response[1:]
                    if(response[0]=="1"):
                        response=response[1:]
                    response_data = eval(response)  # Evaluate the string as Python code
                    try:
                        result_df = pd.DataFrame(response_data)
                    except (TypeError, ValueError):
                        result_df = pd.Series(response_data)
                    #result_df=result_df.dropna(axis=0) 
                    if(result_df.iloc[0, 0] == True) or (result_df.iloc[0, 0] == False):
                        result_df = df.loc[result_df.iloc[:,0]]
                    print(result_df)
                    
                    st.dataframe(result_df)
                    error_occured = 0
                except Exception as e:
                    print(e)
                    flag=0
                    response="0"+"There was a problem, Try Running the same query again !!\n"
                    error_occured = 1
            try_count -=1 
        if(error_occured==1):
            st.markdown(response[1:])
            
    if(flag==0):
        st.session_state.messages.append({"role": "assistant", "content": response[1:],"type":flag})
    elif(flag==1):
        st.session_state.messages.append({"role": "assistant", "content": result_df,"type":flag})
    elif(flag==2):
        st.session_state.messages.append({"role": "assistant", "content": chart_data,"type":flag})
    elif(flag==3):
        st.session_state.messages.append({"role": "assistant", "content": img,"type":flag})

