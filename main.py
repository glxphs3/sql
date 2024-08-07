import streamlit as st
from code_editor import code_editor
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="SQL", layout="wide")

# Initialize SQLite database
db_file = 'database.db'
conn = sqlite3.connect(db_file, check_same_thread=False)
cursor = conn.cursor()

# Function to execute SQL commands
def execute_sql(sql_commands):
    results = []
    try:
        # Split the input into individual statements
        statements = sql_commands.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                if statement.upper().startswith("SELECT"):
                    # For SELECT statements, fetch and store the results
                    df = pd.read_sql_query(statement, conn)
                    results.append(("success", df))
                else:
                    # For non-SELECT statements, execute and commit
                    cursor.execute(statement)
                    conn.commit()
                    results.append(("success", f"Executed: {statement}"))
        
        return True, results
    except Exception as e:
        conn.rollback()
        return False, str(e)

# Function to fetch table data
def fetch_table_data(table_name):
    try:
        # Fetch table schema
        schema = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
        columns = [f"{row['name']} ({row['type']})" for _, row in schema.iterrows()]
        
        # Fetch table data
        data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Set column names with types
        data.columns = columns
        
        return data
    except:
        return pd.DataFrame()

# Create two columns
left_column, right_column = st.columns([1, 1])

with left_column:
    # SQL code editor
    sql_query = code_editor(
        code='',
        lang='sql',
        height=[10, 20],
        theme='contrast',
        options={"showLineNumbers": True},
        response_mode="debounce"
    )

    # Run SQL command button
    if st.button("Run Commands"):
        success, results = execute_sql(sql_query["text"])
        if success:
            st.success("Commands executed successfully!")
            for i, (status, result) in enumerate(results, 1):
                if isinstance(result, pd.DataFrame):
                    st.write(f"Result {i}:")
                    st.dataframe(result)
                else:
                    st.write(result)
        else:
            st.error(f"An error occurred: {results}")

with right_column:
    # Display tables and their data
    st.write("Tables")

    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    for table in tables['name']:
        st.write(table)
        data = fetch_table_data(table)
        st.dataframe(data)

# Close the database connection when the app is done
conn.close()