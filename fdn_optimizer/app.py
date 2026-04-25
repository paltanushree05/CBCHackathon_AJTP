# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
from data.load_data import load_pantries, load_partners, load_donations, load_drivers
from engine.claude import parse_input, generate_briefing
from engine.build_time_matrix import build_time_matrix
from engine.greedy_insert import greedy_insert

load_dotenv()

st.set_page_config(page_title="FDN Optimizer", layout="wide")
st.title("🥖 Friendship Donations Network — Route Optimizer")

# --- Sidebar ---
with st.sidebar:
    st.header("Today's Settings")

    day = st.selectbox("Day of Week", [
        "Monday","Tuesday","Wednesday",
        "Thursday","Friday","Saturday","Sunday"
    ], index=5)  # default Saturday

    st.subheader("Active Pantries Today")
    all_pantries = load_pantries(day)
    active_pantries = []
    for pantry in all_pantries:
        if st.checkbox(f"{pantry['name']} ({pantry['open']}–{pantry['close']})", value=True):
            active_pantries.append(pantry)

    st.caption(f"{len(active_pantries)} pantries active today")

# --- Main Input ---
st.subheader("Coordinator Input")
raw_input = st.text_area(
    "Describe today's donations and any volunteer notes:",
    height=150,
    placeholder="e.g. We have 20 loaves of bread near Collegetown expiring at 3PM, "
                "and 2 volunteers available until 5PM..."
)

run = st.button("Run Optimizer", type="primary", disabled=not raw_input)

if run:
    donations = load_donations()
    drivers   = load_drivers()
    partners  = load_partners()

    with st.spinner("Parsing input with Claude..."):
        parsed = parse_input(raw_input)

    with st.spinner("Building real-world distance matrix from OpenRouteService..."):
        time_matrix = build_time_matrix(donations, active_pantries)

    with st.spinner("Running greedy EDF insertion heuristic..."):
        assignments, unroutable = greedy_insert(
            donations, active_pantries, drivers, time_matrix
        )

    with st.spinner("Generating coordinator briefing with Claude..."):
        briefing = generate_briefing(assignments, unroutable, partners, day)

    # --- Layout ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Today's Briefing")
        st.write(briefing)

        st.divider()

        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Delivered", f"{len(assignments)}/{len(donations)}")
        m2.metric("Unroutable", len(unroutable))
        m3.metric("Pantries Active", len(active_pantries))

        if unroutable:
            st.warning("⚠️ Unroutable Donations")
            for d in unroutable:
                st.write(f"- {d['item']} ({d['quantity']} units) — expires {d['expiry']}")

        # Assignment table
        if assignments:
            st.divider()
            st.subheader("Route Assignments")
            for a in assignments:
                st.write(
                    f"**{a['driver']['name']}** → "
                    f"{a['donation']['item']} ({a['donation']['quantity']} units) "
                    f"to **{a['pantry']['name']}** — {a['travel_time_min']} min drive"
                )

    with col2:
        st.subheader("🗺️ Route Map")

        m = folium.Map(location=[42.4440, -76.5019], zoom_start=12)
        colors = ["blue", "red", "green", "purple", "orange"]

        # Plot assignments
        for i, a in enumerate(assignments):
            color = colors[i % len(colors)]
            donor_loc  = a["donation"]["location"]
            pantry_loc = [a["pantry"]["lat"], a["pantry"]["lng"]]  # real CSV coords

            folium.Marker(
                donor_loc,
                popup=f"📦 {a['donation']['item']} ({a['donation']['quantity']} units)",
                icon=folium.Icon(color=color, icon="arrow-up")
            ).add_to(m)

            folium.Marker(
                pantry_loc,
                popup=f"🏪 {a['pantry']['name']}\n{a['pantry']['open']}–{a['pantry']['close']}",
                icon=folium.Icon(color=color, icon="home")
            ).add_to(m)

            folium.PolyLine(
                [donor_loc, pantry_loc],
                color=color,
                weight=3,
                tooltip=f"Driver: {a['driver']['name']} — {a['travel_time_min']} min"
            ).add_to(m)

        # Plot FDN partner organizations as a separate layer
        partner_group = folium.FeatureGroup(name="FDN Partners")
        for partner in partners:
            folium.CircleMarker(
                location=[partner["lat"], partner["lng"]],
                radius=6,
                color="gray",
                fill=True,
                fill_opacity=0.5,
                popup=f"🤝 {partner['name']} ({partner['type']})"
            ).add_to(partner_group)
        partner_group.add_to(m)

        folium.LayerControl().add_to(m)  # toggle partner layer on/off
        st_folium(m, width=700, height=500)