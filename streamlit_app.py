# Import packages
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# --- App Header ---
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# --- User Input ---
name_on_order = st.text_input("Name on Smoothie")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# --- Snowflake Connection ---
cnx = st.connection("snowflake")
session = cnx.session()

# --- Fetch fruit options from Snowflake ---
fruit_df = session.table("fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
fruit_rows = fruit_df.collect()

# Convert Snowpark Rows to dictionary: FRUIT_NAME -> SEARCH_ON
fruit_map = {row.FRUIT_NAME: row.SEARCH_ON for row in fruit_rows}
fruit_list = list(fruit_map.keys())

if not fruit_list:
    st.warning("No fruits found in Snowflake table! Check your database/schema/table.")

# --- Fruit Selection ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_list,
    max_selections=5
)

# --- Show nutrition info for selected fruits ---
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ", "

        st.subheader(fruit_chosen + " Nutrition Information")

        # Use SEARCH_ON field for API lookup
        api_name = fruit_map.get(fruit_chosen, fruit_chosen)  # fallback to user input
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{api_name}")
            response.raise_for_status()
            data = response.json()

            # Convert to DataFrame for display
            nutrition_df = pd.DataFrame([data])
            st.dataframe(nutrition_df, use_container_width=True)

        except requests.exceptions.RequestException:
            st.error(f"Failed to fetch data for {fruit_chosen} (API lookup: {api_name})")

# --- Submit Order ---
if ingredients_list and st.button("Submit Order"):
    ingredients_string = ingredients_string.rstrip(", ")
    session.sql(
        "INSERT INTO orders (ingredients, name_on_order) VALUES (?, ?)",
        params=[ingredients_string, name_on_order]
    ).collect()
    st.success("Your Smoothie is ordered!", icon="✅")
