import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import os

st.title('FDN Route Optimizer')

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
ors_api_key = os.getenv("ORS_API_KEY")