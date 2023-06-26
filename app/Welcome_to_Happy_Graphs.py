import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import requests
import openai
from utils import get_data, get_indicator_reason, filter_projects

st.title('Happy Graphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

data = pd.read_excel('world_bank_data.xlsx')
