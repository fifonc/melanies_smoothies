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

# --- Add SEARCH_ON column and populate from API ---
try:
    # Add column if not exists
    session.sql("""
        ALTER TABLE fruit_options
        ADD COLUMN IF NOT EXISTS SEARCH_ON STRING
    """).collect()

    # Fetch all fruits from API
    api_response = requests.get("https://my.smoothiefroot.com/api/fruit/all")
    api_response.raise_for_status()
    all_fruits = api_response.json()  # Expecting list of dicts

    # Update each fruit's SEARCH_ON
    for fruit in all_fruits:
        fruit_name = fruit["name"]
        search_value = fruit.get("search_on", "")
        session.sql("""
            UPDATE fruit_options
            SET SEARCH_ON = ?
            WHERE FRUIT_NAME = ?
        """, params=[search_value, fruit_name]).collect()

except requests.exceptions.RequestException:
    st.error("Failed to fetch SEARCH_ON data from the API")
except Exception as e:
    st.warning(f"Could not update SEARCH_ON column: {e}")

# --- Fetch fruit options from Snowflake ---
fruit_df = session.table("fruit_options").select(col("FRUIT_NAME"))
fruit_rows = fruit_df.collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# --- Fruit Selection ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", fruit_list, max_selections=5
)

# --- Show nutrition info for selected fruits ---
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ", "

        st.subheader(fruit_chosen + " Nutrition Information")

        # Fetch nutrition info from API
        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
            )
            response.raise_for_status()
            data = response.json()

            # Convert to DataFrame for nice display
            nutrition_df = pd.DataFrame([data])
            st.dataframe(nutrition_df, use_container_width=True)

        except requests.exceptions.RequestException:
            st.error(f"Failed to fetch data for {fruit_chosen}")

# --- Submit Order ---
if ingredients_list and st.button("Submit Order"):
    ingredients_string = ingredients_string.rstrip(", ")
    session.sql(
        "INSERT INTO orders (ingredients, name_on_order) VALUES (?, ?)",
        params=[ingredients_string, name_on_order]
    ).collect()
    st.success("Your Smoothie is ordered!", icon="✅")
