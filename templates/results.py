#################################
# Imports
################################

import streamlit as st  # Web App
import pandas as pd  # Dataframes
import numpy as np  # Maths functions
import datetime as dt  # Time Functions
from datetime import datetime

# SQL and Credentials
import os
import io
import dotenv # Protect db creds
dotenv.load_dotenv()
import sqlalchemy

# Charting
from matplotlib import pyplot as plt
import seaborn as sns

# SKLearn
from sklearn.metrics import mean_squared_error, mean_absolute_error  # Mean Squared Error Function (Needs np.sqrt for units)

# load data

# SQL Connection
DATABASE_URL = os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL')
# Cache func for loading Database.
@st.cache(allow_output_mutation=True)
def get_database_connection():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    query = "SELECT user, recorded_result, pallet_used, near_miss, correct FROM colour_data AS cd WHERE cd.user LIKE 'aFalJQ'"



    # Store db in memory for speed up?
    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
       query=query, head="HEADER"
    )
    conn = engine.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    db = pd.read_csv(store)
    
#     db = pd.read_sql_query('SELECT date, forecast, temp_max, issue, extended_text FROM "bom-weather";',engine)
#     db = pd.read_sql('bom-weather', engine) # Don't need whole db
    return db

db = get_database_connection()

st.dataframe(db)

###############################################################
# Part 1
###############################################################

# # Assign (Root) Mean Squared Error
# rmse_today1 = [np.sqrt(mean_squared_error(fac['today+0'][:len(fac['today+1'].dropna())], fac['today+1'].dropna()))]


# # Assign error vals to a df
# accuracy = pd.DataFrame()
# accuracy['1 Day Forecast'] = rmse_today1


# accuracy.index = ["Average Daily Forecast Error (RMSE)"]

# ###############################################################
# # MAE (Mean Absolute Error: Influences lower values more)
# ###############################################################

# # Assign Mean Squared Error
# mae_today1 = [mean_absolute_error(fac['today+0'][:len(fac['today+1'].dropna())], fac['today+1'].dropna())]


# # Assign error vals to a df
# mae_accuracy = pd.DataFrame()
# mae_accuracy['1 Day Forecast'] = mae_today1


# mae_accuracy.index = ["Average Daily Forecast Error (MAE)"]

# #################################
# # VS RMSE
# ################################

# # Assign RMSE value for pmodel
# persistence_rmse = np.sqrt(mean_squared_error(persistence['Persistence Accuracy'], fac['today+0'][:len(fac)-1]))

# persistence_vs = pd.DataFrame()
# persistence_vs['1 Day Error'] = accuracy['1 Day Forecast'] - persistence_rmse


# persistence_vs.index = ["BOM Error vs Persistence Error (RMSE)"]


# #################################
# # VS MAE
# ################################

# # Assign RMSE value for pmodel
# persistence_mae = mean_absolute_error(persistence['Persistence Accuracy'], fac['today+0'][:len(fac)-1])

# mae_persistence_vs = pd.DataFrame()
# mae_persistence_vs['1 Day Error'] = accuracy['1 Day Forecast'] - persistence_mae

# mae_persistence_vs.index = ["BOM Error vs Persistence Error (MAE)"]

# #################################
# #################################
# # Display
# ################################
# #################################

# # App Begins
# st.write("""
# # H1

# ### H2
# Text.
# """)

# st.write("""
# #### Summary of Data
# """)
# # Summary
# st.text(f"Today\'s date is: {today}")
# st.text(f"New forecasts:	{len(tf)}, Starting on: {tf.index[0]}, Ending on: {tf.index[-1]}")
# todays_forecast = f"#### Today's forecast: \n >*{last_row['extended_text'][0]}*"
# st.markdown(todays_forecast)


# # Previous Data Heatmap
# st.image('./static/charts/heatmap_forecast.png', use_column_width=True)

# st.dataframe(accuracy)

# st.line_chart(accuracy.T)
# # Display barchart
# st.bar_chart(persistence_vs.T)

# # The End
# st.write(""" 
# #### Please watch this space for future development.
# # """)
