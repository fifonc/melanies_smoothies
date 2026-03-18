import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

name_on_order = st.text_input("Name on Smoothie")

# ✅ Use Snowflake-provided session
session = get_active_session()

# ✅ Use simple table name (context already set)
df = session.table("fruit_options").select(col("FRUIT_NAME"))

# Convert to list
fruit_list = [row["FRUIT_NAME"] for row in df.collect()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

if ingredients_list:
    ingredients_string = ",".join(ingredients_list)

    if st.button("Submit Order"):
        session.sql(
            "INSERT INTO orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
