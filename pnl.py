import pandas as pd
import numpy as np 
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import time

st.set_page_config(
    page_title="P&L Explained",
    page_icon="✅",
    layout="wide",
)

st.title("P&L Explained")

#Read csv file for analysis
#sets default path of file
default_path = r"C:\Users\jf03180\OneDrive - KBC Group\Excel Files\Test PL.csv"
#Creates text input box to change the file location
st.text_input("Copy path where the file is located", default_path)
#reads dataframe from the path
df = pd.read_csv(default_path, encoding='utf-8-sig', sep = ';', engine = 'python', header =[0])

#create drag and drop menu for csv file
csv_file = st.file_uploader("Upload a CSV file", type=([".csv"]))

#columns needed for PNL tables
pnl_columns = ['Currency', 'Curve_name', 'Date','Change_market_rate','P&L_market_rate','Change_yield_zero_rate','P&L_yield_zero_rate']

#Checks if csv file is present and returns details + dataframe 
if csv_file is not None:
    file_details = {"filename": csv_file.name, "filetype":csv_file.type, "filesize":csv_file.size}
    st.write(file_details)
    #Clean dataframe
    dataframe = pd.read_csv(csv_file, encoding='utf-8-sig', sep = ';', engine = 'python', header =[0])
    dataframe.columns = dataframe.columns.str.replace(' ','_')
    
    
    #Add additional columbs for change and p&l
    dataframe['Change_market_rate'] = dataframe['Market_rate_1'] - dataframe['Market_rate']

    dataframe['Change_yield_zero_rate'] = dataframe['Yield_zero_rate_1'] - dataframe['Yield_zero_rate']
    
    dataframe = dataframe.fillna(0)
    
    dataframe['Change_market_rate'] = dataframe['Change_market_rate'].apply(lambda x: float(x))
    #dataframe['DV01_(zero)'] = dataframe['DV01_(zero)'].str.replace(',', '')
    dataframe['DV01_(zero)'] = dataframe['DV01_(zero)'].apply(lambda x: float(x))
    
    #dataframe['DV01_(zero)'] = dataframe['DV01_(zero)'].fillna(0)
    dataframe['P&L_market_rate'] = dataframe['Change_market_rate'] * dataframe['DV01_(zero)']
    dataframe['P&L_yield_zero_rate'] = dataframe['Change_yield_zero_rate'] * dataframe['DV01_(zero)']

    #Creates markdown + prints dataframe in webapp
    st.markdown("### Original Dataframe")
    dataframe = dataframe.round(decimals = 4)
    st.dataframe(dataframe)


#returns all unique curves in 'curve name' column as a list
curves = dataframe['Curve_name'].unique()
number_of_curves = len(curves)
#returns all unique currencies as a list
currencies = dataframe['Currency'].unique()
number_of_currencies = len(currencies)

#Create sidebar selectbox for currency and curve
currency_choice = st.sidebar.selectbox('Select your currency:', currencies)
#curve_choice = st.sidebar.selectbox("Select Curve", curves)

#Create empty curve list
curve_list = []

st.markdown('### Slice of Dataframe')

#loop through curves to check if the curve starts with the currency choice 
#Adds currency choice to list
for curve in curves:
    #Had eerst code met tuple(currency_choice) --> beter of werkt dit evenzeer? 
    #Tuple splitst Currency Code op in afzodnerlijke letters en zoekt of curve begint met één van deze letters
    if curve.startswith(currency_choice):
        curve_list.append(curve)

#create selectbox contigent on the choice(s) in the first selectbox      
curve_choice = st.sidebar.multiselect("Select Curve", curve_list)

#creates slice of dataframe on the basis of the chosen currency
if len(curve_list) < 2:    
    if currency_choice is not None:    
        x = dataframe.loc[dataframe['Currency'] == currency_choice]
        x= x.reset_index(drop = True)
        st.dataframe(x) 
else: 
    if currency_choice is not None:
        for i in range(len(curve_choice)):
            x = dataframe.loc[dataframe['Currency'] == currency_choice]
            x = x.loc[x['Curve_name'] == curve_choice[i]]
            x = x.reset_index(drop = True)
            st.write(curve_choice[i])
            st.dataframe(x)
        

st.markdown("## P&L Dataframe")

placeholder = st.empty()

st.markdown("### P&L for " + currency_choice)
#defines the columns necessary for the P&L dataframe
pnl_columns = ['Currency', 'Curve_name', 'Date','Change_market_rate','P&L_market_rate','Change_yield_zero_rate','P&L_yield_zero_rate']


if len(curve_list) < 2:    
    if currency_choice is not None:    
        temp = dataframe.loc[dataframe['Currency'] == currency_choice]
        temp= temp.reset_index(drop = True)
        temp = temp[pnl_columns].copy()
        st.dataframe(temp) 
else: 
    if currency_choice is not None:
        for i in range(len(curve_list)):
            x = dataframe.loc[dataframe['Currency'] == currency_choice]
            x = x.loc[x['Curve_name'] == curve_list[i]]
            x = x.reset_index(drop = True)
            x = x[pnl_columns]
            st.markdown("##### "+ curve_list[i])
            st.dataframe(x)
            
            
#Ag Grid - creates interactive dataframe in streamlit
# Ag Grid params
ob = GridOptionsBuilder.from_dataframe(dataframe)
#creates column 'Name'
ob.configure_column("Change_market_rate", type=["numericColumn”,“numberColumnFilter”,“customNumericFormat"], precision=4)
#Creates column 'Miles'
#ob.configure_column("Change", aggFunc="sum")

st.markdown("### Interactive Dataframe") 
            
#AgGrid(dataframe,  enable_entreprise_modules = True)
#
##Clean Dataframe
#df.columns = df.columns.str.replace(' ','_')
#df.columns = df.columns.str.strip()
#
##creates dictionary of dataframes for every unique currency
#dict_of_currencies = dict(tuple(df.groupby("Currency")))
