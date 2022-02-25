
  
# -*- coding: utf-8 -*-
# Copyright Chi Shen, 2020-06-04 XJTU.

#--- load packages ---#

import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff


# -- Set page config
apptitle = 'EQ-5D Utility Calculator'

st.set_page_config(page_title=apptitle, page_icon=":eyeglasses:")



# Title the app


html_title = """
    <div style="background-color:orange;"><p style="color:white; font-size:40px; padding:10px; text-align:center; font-family:times">
    A tool to calculate <br> EQ-5D-3L/5L Scale's Utility
    </p></div>
    """
    
st.markdown(html_title, unsafe_allow_html=True)




# Select scale
st.sidebar.markdown("## Select Scale")

scale_level = st.sidebar.selectbox("EQ-5D-3L or EQ-5D-5L",
                                    ["EQ-5D-3L", "EQ-5D-5L"])


# Select value set
st.sidebar.markdown("## Select Value Set")

if scale_level == "EQ-5D-3L":

    value_set = st.sidebar.selectbox("Value Set for EQ-5D-3L",
                                    ["Liu_2014", "Zhuo_2018"])

if scale_level == "EQ-5D-5L":

    value_set = st.sidebar.selectbox("Value Set for EQ-5D-5L",
                                    ["Luo_2017"])





# Set bins for histogram plot
st.sidebar.markdown("## Set bins for histogram plot")
bins = st.sidebar.slider("Bins of Histogram", 0.01, 0.2, 0.05)  # min, max, default






# File upload

st.subheader("1: Please upload your data")
st.text("Attention: the file must be a CSV format and contains \n at least five variable named 'mo, sc, ua, pd, ad'")


data_file = st.file_uploader("Upload CSV", type=["csv"])


if data_file is not None:
    
    file_details = {"filename": data_file.name, 
                    "filetype": data_file.type,
                    "filesize":data_file.size}		
    st.write(file_details)
    data = pd.read_csv(data_file)
    st.dataframe(data)


df = data
raw_names = df.columns.tolist()

#---Loading data---#

value_set_Liu_2014 = pd.read_csv("./dataset/value_set_Liu_2014.csv")
value_set_Zhuo_2018 = pd.read_csv("./dataset/value_set_Zhuo_2018.csv")
value_set_Luo_2017 = pd.read_csv("./dataset/value_set_Luo_2017.csv")

#----functions for EQ-5D-3L---#

def utility(x, level, var, set):

    if level == "EQ-5D-3L":

        if set == "Liu_2014":
            z = [y[1] for y in value_set_Liu_2014.values if y[0] == var + str(x)]

        if set == "Zhuo_2018":
            z = [y[1] for y in value_set_Zhuo_2018.values if y[0] == var + str(x)]


    if level == "EQ-5D-5L" and set == "Luo_2017":
        z = [y[1] for y in value_set_Luo_2017.values if y[0] == var + str(x)]

    return z[0]


df["mo_u"] = df["mo"].apply(utility, args = (scale_level, "MO", value_set, ))
df["sc_u"] = df["sc"].apply(utility, args = (scale_level, "SC", value_set, ))
df["ua_u"] = df["ua"].apply(utility, args = (scale_level, "UA", value_set, ))
df["pd_u"] = df["pd"].apply(utility, args = (scale_level, "PD", value_set, ))
df["ad_u"] = df["ad"].apply(utility, args = (scale_level, "AD", value_set, ))


df["max"] = df[["mo", "sc", "ua", "pd", "ad"]].max(axis=1)
df["n3"] = np.where(df["max"] == 3, 0.022, 0)


def calculate(level, set):

    if level == "EQ-5D-3L" and set == "Liu_2014":
        df["utility"] = np.where(df[["mo", "sc", "ua", "pd", "ad"]].max(axis=1) == 1, 1,
                                 1 - 0.039 - df[["mo_u", "sc_u", "ua_u", "pd_u", "ad_u", "n3"]].sum(axis=1))

    if level == "EQ-5D-3L" and set == "Zhuo_2018":
        df["utility"] = 1 + df[["mo_u", "sc_u", "ua_u", "pd_u", "ad_u"]].sum(axis=1)

    if level == "EQ-5D-5L" and set == "Luo_2017":
        df["utility"] = 1 - df[["mo_u", "sc_u", "ua_u", "pd_u", "ad_u"]].sum(axis=1)


calculate(scale_level, value_set)




# Show data

#- Data
st.subheader("2: Results are presented as below")


raw_names.append("utility")
st.dataframe(df[raw_names])





st.subheader("3: Dowload the result")
st.text("You can click the botton below to download the result")
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button(
    "Press to Download",
    convert_df(df),
    "result.csv",
    "text/csv",
    key="utility"
)





#- Figure

st.subheader("4: Histogram of utility calculated by this App")

#---Create distplot with custom bin_size---#
fig = ff.create_distplot([df["utility"].to_list()], [""], bin_size=bins)

#---Plot!
st.plotly_chart(fig, use_container_width=True)



#- Figure---#

st.subheader("6: Summary table")

import researchpy as rp

tab = rp.summary_cat(df[["mo", "sc", "ua", "pd", "ad"]])

st.table(tab)



st.subheader("Footnote")
st.markdown("""

- *Liu_2014* means: Liu, G. G. ,  Wu, H. ,  Li, M. ,  Gao, C. , &  Luo, N. . (2014). Chinese time trade-off values for eq-5d health states. Value in Health, 17(5), 597-604.

- *Zhuo_2018* means: Zhuo, L. ,  Xu, L. ,  Ye, J. ,  Sun, S. ,  Zhang, Y. , &  Kristina, B. , et al. (2018). Time trade-off value set for eq-5d-3l based on a nationally representative chinese population survey. Value in Health, S1098301518316735-.

- *Luo_2017* means: Luo, N. ,  Liu, G. ,  Li, M. ,  Guan, H. ,  Jin, X. , &  Rand-Hendriksen, K. . (2017). Estimating an eq-5d-5l value set for china. Value in Health, 20(4), 662-669.


\n
\n

**Author Info:** \n
*Shen, Chi*; \n
*chi.shen@xjtu.edu.cn;* \n
*School of Public Policy and Administration;* \n
*Xi'an Jiaotong University*
""")



