import pyrebase
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='2023 Aquehonga Camporee',page_icon="🏆")

firebaseConfig = {
 "apiKey": st.secrets['apiKey'],
 "authDomain": st.secrets['authDomain'],
 "projectId": st.secrets['projectId'],
 "storageBucket": st.secrets['storageBucket'],
 "messagingSenderId": st.secrets['messagingSenderId'],
  "appId": st.secrets['appId'],
  "databaseURL": st.secrets['databaseURL']
}
stations = ['Check-In','Archery','Fishing','Shelter Building','Semaphore','Fire Building','Two Person Saw','Orienteering','Cooking','First Aid','Animal Prints','Leader Bonus']

if 'db' not st.session_state:
 firebase = pyrebase.initialize_app(firebaseConfig)
 db  = firebase.database()
 st.session_state['db'] = db
