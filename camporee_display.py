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

if 'db' not in st.session_state:
 firebase = pyrebase.initialize_app(firebaseConfig)
 db  = firebase.database()
 st.session_state['db'] = db
 
show_df = pd.DataFrame(st.session_state.db.get().val()).T
show_df.set_index('name')

if 'score_df' not in st.session_state:
 st.session_state['score_df'] = pd.DataFrame()

try:
    for clm in stations:
        if len(st.session_state.score_df) == 0:
            st.session_state.score_df = show_df[clm].apply(pd.Series)
            st.session_state.score_df.columns = [clm+'_score',clm+'_time',clm+'_adj_score']
        else:
            st.session_state.score_df[clm+"_score"] = st.session_state.score_df.index.map(show_df[clm].apply(pd.Series)['score'])
            st.session_state.score_df[clm+"_time"] = st.session_state.score_df.index.map(show_df[clm].apply(pd.Series)['time'])
            st.session_state.score_df[clm+"_adj_score"] = st.session_state.score_df.index.map(show_df[clm].apply(pd.Series)['adj_score'])
except:
    pass
st.session_state.score_df
