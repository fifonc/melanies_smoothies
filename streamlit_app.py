# Import python packages.
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app.
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

import streamlit as st
st.write("Secrets loaded:", st.secrets)

my_dataframe = session.table("fruit_options").select(col('FRUIT_NAME'))

fruit_rows = my_dataframe.collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list
)

if ingredients_list:
    ingredients_string = ''.join(ingredients_list)

    if st.button("Submit Order"):
        session.sql(
            "INSERT INTO orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success('Your Smoothie is ordered!', icon="✅")
