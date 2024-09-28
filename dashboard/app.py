import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import streamlit as st

# load dataset
df = pd.read_csv("dataset_clean.csv")
df['dteday'] = pd.to_datetime(df['dteday'])

st.set_page_config(page_title="Project Dicoding bangkit",
                   page_icon="bar_chart:",
                   layout="wide")
#css file
with open('style.css')as f:
 st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)


def create_monthly_users_df(df):
    pengguna_bulanan = df.resample(rule='M', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    pengguna_bulanan.index = pengguna_bulanan.index.strftime('%b-%y')
    pengguna_bulanan =pengguna_bulanan.reset_index()
    pengguna_bulanan.rename(columns={
        "dteday": "yearmonth",
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    return pengguna_bulanan

def create_seasonly_users_df(df):
    pengguna_musiman = df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    pengguna_musiman = pengguna_musiman.reset_index()
    pengguna_musiman.rename(columns={
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    pengguna_musiman = pd.melt(pengguna_musiman,
                                      id_vars=['season'],
                                      value_vars=['casual_rides', 'registered_rides'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')
    
    pengguna_musiman['season'] = pd.Categorical(pengguna_musiman['season'],
                                             categories=['Spring', 'Summer', 'Fall', 'Winter'])
    
    pengguna_musiman = pengguna_musiman.sort_values('season')
    
    return pengguna_musiman

def create_weekday_users_df(df):
    weekday_users_df = df.groupby("weekday").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    weekday_users_df = weekday_users_df.reset_index()
    weekday_users_df.rename(columns={
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)

    weekday_users_df = pd.melt(weekday_users_df,
                                      id_vars=['weekday'],
                                      value_vars=['casual_rides', 'registered_rides'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')
    
    weekday_users_df['weekday'] = pd.Categorical(weekday_users_df['weekday'],
                                             categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    weekday_users_df = weekday_users_df.sort_values('weekday')
    
    return weekday_users_df

def create_hourly_users_df(df):
    pengguna_jam = df.groupby("hr").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    pengguna_jam = pengguna_jam.reset_index()
    pengguna_jam.rename(columns={
        "cnt": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    return pengguna_jam


min_date = df["dteday"].min()
max_date = df["dteday"].max()


with st.sidebar:
    st.image("https://i.pinimg.com/originals/ca/65/54/ca655453eb79fe8db19601dfcf53ed95.jpg")

    st.sidebar.header("Filter:")

    start_date = st.sidebar.date_input(
        label="Start Date",
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )

    end_date = st.sidebar.date_input(
        label="End Date",
        min_value=min_date,
        max_value=max_date,
        value=max_date
    )


main_df = df[
    (df["dteday"] >= str(start_date)) &
    (df["dteday"] <= str(end_date))
]


pengguna_bulanan = create_monthly_users_df(main_df)
weekday_users_df = create_weekday_users_df(main_df)
pengguna_musiman = create_seasonly_users_df(main_df)
pengguna_jam = create_hourly_users_df(main_df)

st.title("Bike Sharing Dashboard diaz")
st.markdown("#")

col1, col2, col3 = st.columns(3)

with col1:
    total_all_rides = main_df['cnt'].sum()
    st.metric("Total Rides", value=total_all_rides)
with col2:
    total_casual_rides = main_df['casual'].sum()
    st.metric("Total Casual Rides", value=total_casual_rides)
with col3:
    total_registered_rides = main_df['registered'].sum()
    st.metric("Total Registered Rides", value=total_registered_rides)

st.markdown("---")

plot_options = ['Daily Bikeshare User Count', 'Monthly Bikeshare Usage']
plot_choice = st.radio('Choose Plot Type', plot_options)

if plot_choice == 'Daily Bikeshare User Count':
    st.write('Count by bikeshare users by day')

    line_chart = alt.Chart(df).mark_line(
        color='darkblue',  
        interpolate='basis' 
    ).encode(
        x='dteday:T',
        y='cnt:Q',
        tooltip=['dteday:T', 'cnt:Q']
    )

    area_chart = alt.Chart(df).mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color='lightblue', offset=0),  
                alt.GradientStop(color='darkblue', offset=1)   
            ],
            x1=0,
            x2=1,
            y1=1,
            y2=0
        ),
        line={'color': 'darkblue'}, 
        interpolate='basis' 
    ).encode(
        x='dteday:T',
        y='cnt:Q',
    )

    chart = alt.layer(area_chart, line_chart).resolve_scale(y='independent')

    st.altair_chart(chart, use_container_width=True)

elif plot_choice == 'Monthly Bikeshare Usage':
   
    fig = px.line(monthly_users_df,
                  x='yearmonth',
                  y=['casual_rides', 'registered_rides', 'total_rides'],
                  color_discrete_sequence=["#2CA02C", "#FF7F0E", "#1F77B4"],  # Mengatur warna secara manual
                  markers=True,
                  title="Monthly Count of Bike-share Rides")

    fig.update_layout(
        xaxis_title='', 
        yaxis_title='Total Rides', 
        font=dict(
            family="Arial",
            size=12,
            color="black"
        ),
        title_font_family="Arial", 
        title_font_size=20,  
        title_font_color="white"  
    )

    
    st.plotly_chart(fig, use_container_width=True)

fig1 = px.bar(seasonly_users_df,
              x='season',
              y=['count_rides'],
              color='type_of_rides',
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#aec7e8"],  # Warna berbeda dari sebelumnya
              title='Count of bike-share rides by season')

fig1.update_layout(
    xaxis_title='', 
    yaxis_title='Total Rides',
    font=dict(
        family="Arial",
        size=12,
        color="white"
    ),
    title_font_family="Arial",
    title_font_size=20,  
    title_font_color="white"  
)

fig2 = px.bar(weekday_users_df,
              x='weekday',
              y=['count_rides'],
              color='type_of_rides',
              barmode='group',
              color_discrete_sequence=["#2ca02c", "#98df8a", "#d62728"],  # Warna berbeda dari sebelumnya
              title='Count of bike-share rides by weekday')

fig2.update_layout(
    xaxis_title='',  
    yaxis_title='Total Rides',  
    font=dict(
        family="Arial",
        size=12,
        color="white"
    ),
    title_font_family="Arial",  
    title_font_size=20,  
    title_font_color="white"  
)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig1, use_container_width=True)
right_column.plotly_chart(fig2, use_container_width=True)
fig = px.line(hourly_users_df,
              x='hr',
              y=['casual_rides', 'registered_rides'],
              color_discrete_sequence=["skyblue", "orange"],
              markers=True,
              title='Count of bike-share rides by hour of day').update_layout(xaxis_title='', yaxis_title='Total Rides')

st.plotly_chart(fig, use_container_width=True)


st.write('Clusters of bike-share rides count by season and temperature')

scatter = alt.Chart(df).mark_circle(size=60).encode(
    x='temp',
    y='cnt',
    color='season',
    tooltip=['temp', 'cnt', 'season']
).properties(
    width=600,
    height=400
).interactive()

st.altair_chart(scatter, use_container_width=True)





st.caption('Copyright (c), created by Muhammad Farid')

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)
