#// Import the functions you need from the SDKs you need
#// import { initializeApp } from "firebase/app";
#// TODO: Add SDKs for Firebase products that you want to use
#// https://firebase.google.com/docs/web/setup#available-libraries
import pyrebase
import streamlit as st
import pandas as pd
import math
import plotly.express as px
#import time
#// Your web app's Firebase configuration

st.set_page_config(page_title='Camporee Scoring',page_icon="🏆")

firebaseConfig = {
 "apiKey": st.secrets['apiKey'],
 "authDomain": st.secrets['authDomain'],
 "projectId": st.secrets['projectId'],
 "storageBucket": st.secrets['storageBucket'],
 "messagingSenderId": st.secrets['messagingSenderId'],
  "appId": st.secrets['appId'],
  "databaseURL": st.secrets['databaseURL']
}
stations = ['Check-In','Archery','Fishing','Shelter Building','Signaling','Fire Building','Two Person Saw','Orienteering','Cooking','Animal Prints','Leader Bonus']

pat = 'Patrol'
stat = 'Station'

first, second, third = st.columns(3)
tab1, tab2, tab3, tab4 = st.tabs(['Input Scores','Unit Leaders','Patrol Leaders','Technicals'])
def sqrt_time_bonus(score,time):
    ## Best method found. Allows a 1 point loss to be overcome by a 35-55 second increase in speed.
    bonus = 0
    temp=0
    try:
        if score > 0:
            bonus = round((score**.5+(math.log2(time)**2/10)*-1),3)
            temp = 10 + bonus
        if bonus+score+temp < score:
            bonus = 0
            temp=0
        return(bonus+score+temp)
    except:
        return(score)

def db_construct(item_list,fbConfig,flag=True):
    firebase = pyrebase.initialize_app(fbConfig)
    db  = firebase.database()
    if flag:
        for item in item_list:
                try:
                    db.child(item).child('name').set(item.split("***")[0])
                    db.child(item).child('unit').set(item.split("***")[1])
                    #db.child(item).child('exp').set(item.split('***')[2])
                    for station in stations:
                        db.child(item).child(station).child('score').set(0)
                        db.child(item).child(station).child('time').set(0)
                        db.child(item).child(station).child('adj_score').set(0)
                except:
                    pass
    else:
        pass
    return(db)

filt = st.sidebar.multiselect(default= 'ALL',label='Filter Options',options=['ALL','Check-In','Archery','Fishing','Shelter Building','Signaling','Fire Building','Two Person Saw','Orienteering','Cooking','Animal Prints','Leader Bonus'])
if 'graph_df' not in st.session_state:
    graph_df = pd.DataFrame()
    for s in range(0,26):
        for t in range(90,610,5):
            graph_df.loc[s,t] = sqrt_time_bonus(s,t)

    st.session_state['graph_df'] = graph_df

if 'time' not in st.session_state:
    st.session_state['time'] = 0

if 'df' not in st.session_state:
    df = pd.read_excel('Camporee_Score_Tool.xlsx',sheet_name='Summary')
    df['patrol_id'] = df['Patrol Name'] +"***"+ df['Unit']#+'***'+'Handicap'
    st.session_state.patrolID = df['patrol_id'].unique().tolist()
    st.session_state.patrols = df['Patrol Name'].tolist()
    st.session_state.unit = df['Unit'].unique().tolist()
    st.session_state['df'] = df
#// Initialize Firebase
if 'db' not in st.session_state:
    st.session_state['db'] = db_construct(st.session_state.patrolID,firebaseConfig,flag=False)

show_df = pd.DataFrame()
with tab1:
    st.write('Input Score info')

    update_flag = st.checkbox("Turn On Update Mode")
    if update_flag:
        st.warning('💥 💥💥 💥💥💥You are in override mode. Destructive changes can occur.💥💥💥 💥💥 💥')
    with st.form('score_input',clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox(label='Patrol',options=st.session_state.patrols,key='pats')
            st.selectbox(label='Station',options=stations,key='stats')
            st.number_input(label = 'Minutes',min_value=0,step=1,key='mins')

        with col2:
            st.selectbox(label='Unit',options=st.session_state.unit,key='units')
            st.number_input(label=f"{pat}'s {stat} Score",min_value=0,max_value=25,step=1,key='score')

            st.number_input(label = 'Seconds',min_value=0,step=1,key='secs')
        patrolid = st.session_state.pats + "***" + st.session_state.units
        submitted = st.form_submit_button('Submit')



        st.write(patrolid)

    if submitted:
        if st.session_state.stats in ['Shelter Building','Signaling','Fire Building','Two Person Saw','Orienteering','Cooking']:
            st.session_state.time = st.session_state.mins*60 + st.session_state.secs
        else:
            st.session_state.time=0
        adjustment = sqrt_time_bonus(st.session_state.score,st.session_state.time)
        st.write(f'Time is {st.session_state.time} seconds. Adjusted Score is {round(adjustment,3)}.')
        score = {'score':st.session_state.score}
        time = {'time':st.session_state.time}
        adj_score = {'adj_score':adjustment}
        unit = {'unit':st.session_state.units}

        try:
            if update_flag:
                st.session_state.db.child(patrolid).child(st.session_state.stats).update(score)
                st.session_state.db.child(patrolid).child(st.session_state.stats).update(time)
                st.session_state.db.child(patrolid).child(st.session_state.stats).update(adj_score)
                #st.session_state.db.child(st.session_state.stats).child(st.session_state.pats).update(unit)
                st.success(f'{st.session_state.pats}\'s {st.session_state.stats} score saved!')
            else:
                if st.session_state.db.child(patrolid).child(st.session_state.stats).child('score').get().val() > 0:
                    st.warning('A score already exists! Did you enter the correct data? Double check and resubmit with update mode turned on.')
                else:
                    st.session_state.db.child(patrolid).child(st.session_state.stats).update(score)
                    st.session_state.db.child(patrolid).child(st.session_state.stats).update(time)
                    st.session_state.db.child(patrolid).child(st.session_state.stats).update(adj_score)
                    #st.session_state.db.child(st.session_state.stats).child(st.session_state.pats).update(unit)
                    st.success(f'{st.session_state.pats}\'s {st.session_state.stats} score saved!')
        except:
            st.warning('Not Found! Make sure Unit and Patrol are correct!')

show_df = pd.DataFrame(st.session_state.db.get().val()).T
#.set_index('name').drop(['unit'],axis=1)

if 'score_df' not in st.session_state:
    st.session_state['score_df'] = pd.DataFrame()
    st.session_state['adj_df'] = pd.DataFrame()
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

lead_button = st.sidebar.button('Process Leaders')
if 'ALL' not in filt:
    temp_list = []
    for i in filt:
        hold = [col for col in st.session_state.score_df.columns if i in col]
        for x in hold:
            temp_list.append(x)
else:
    temp_list = st.session_state.score_df.columns

score_list = [col for col in temp_list if '_adj_score' in col]



try: 
 
    st.session_state.adj_df = st.session_state.score_df.reset_index()
    score_list.append('unit')
    st.session_state.adj_df['unit'] = st.session_state.adj_df['index'].apply(lambda x: x.split('***')[1])
    st.session_state.adj_df['patrol'] = st.session_state.adj_df['index'].apply(lambda x: x.split('***')[0])
    scoreseries = st.session_state.adj_df[score_list].groupby(by='unit').sum().sum(axis=1)/st.session_state.adj_df[score_list].groupby(by='unit').count()[temp_list[2]]
    scoreseries = pd.DataFrame(scoreseries)
  if lead_button:
     scoreseries['num_patrols']=scoreseries.index.map(st.session_state.adj_df[score_list].groupby(by='unit').count()[temp_list[2]])
     scoreseries.columns=['Average Score','Number of Patrols']
     scoreseries.sort_values(by='Average Score',ascending=False,inplace=True)
except:
    pass
with tab2:
    try:
        st.write('Leading Units')
        col1, col2, col3 = st.columns(3)
        col1.metric(label=scoreseries.index[0],value=round(scoreseries.iloc[0,0],3))
        col2.metric(label=scoreseries.index[1],value=round(scoreseries.iloc[1,0],3))
        col3.metric(label=scoreseries.index[2],value=round(scoreseries.iloc[2,0],3))
        scoreseries
        st.balloons()
    except:
        pass


with tab3:
   
   st.write('Leading Patrols')
   score_list = [col for col in temp_list if '_adj_score' in col]
   score_list.append('patrol')
   score_list.append('unit')
   #out_df = st.session_state.adj_df
   #out_df_scores = pd.DataFrame(out_df[score_list].sum(axis=1).sort_values(ascending=False))
   see_it = st.session_state.adj_df[score_list].set_index('patrol')
   see_it['total'] = see_it.drop('unit',axis=1).sum(axis=1)
   see_it = see_it.sort_values(by='total',ascending=False)
   col1, col2, col3 = st.columns(3)
   col1.metric(label=f"{see_it['total'].index[0]} {see_it['unit'][0]}",value=round(see_it['total'][0],3))
   col2.metric(label=f"{see_it['total'].index[1]} {see_it['unit'][1]}",value=round(see_it['total'][1],3))
   col3.metric(label=f"{see_it['total'].index[2]} {see_it['unit'][2]}",value=round(see_it['total'][2],3))
   see_it

with tab4:

    st.write('Time Adjustment Function')
    st.latex(r'''f(x) = score^{{0.5}}+(log_{2}(time)^2)*-1) ''')
    st.latex(r'''f(y) = f(x) + 10''')
    st.latex(r'''Adj. Score = f(x) + f(y) + score''')
    st.plotly_chart(px.line(st.session_state.graph_df.T,title='Time Adjustment Graph'))

    st.warning('This is a destrcutive rebuild of the database. Only use in extreme cases or during testing. Changes to individual scores can be made using Update Mode.')
    reset = st.button('⛔Reset Database⛔')
    if reset:
        st.session_state.db = db_construct(st.session_state.patrolID,firebaseConfig)

#with tab2:
#"""    with first:
#        st.metric(label=Total.index[0], value = Total.iloc[0])
##    with second:
#        st.metric(label=Total.index[1], value = Total.iloc[1])
#        st.write('2nd Place')
####leads = st.checkbox('Show Leaders')"""



#"""if leads:
        #out_df = output_df.style.highlight_max(color='lightgreen',axis=0)
        #out_df
#        show_df"""
