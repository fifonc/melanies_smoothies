# Import Python packages
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
            response.raise_for_status()  # Raise error if API call fails
            data = response.json()

            # Convert dict to DataFrame for nice display
            nutrition_df = pd.DataFrame([data])
            st.dataframe(nutrition_df, use_container_width=True)

        except requests.exceptions.RequestException:
            st.error(f"Failed to fetch data for {fruit_chosen}")

# --- Submit Order ---
if ingredients_list and st.button("Submit Order"):
    # Remove trailing comma and space
    ingredients_string = ingredients_string.rstrip(", ")

    # Insert order into Snowflake
    session.sql(
        "INSERT INTO orders (ingredients, name_on_order) VALUES (?, ?)",
        params=[ingredients_string, name_on_order]
    ).collect()

    st.success("Your Smoothie is ordered!", icon="✅")
