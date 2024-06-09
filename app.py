import pandas as pd
import json
import streamlit as st
from dotenv import load_dotenv
import os
from app_utils.create_metadata import process_files, select_df, visualization, natural_response
from app_utils.constants import system_instruction_to_gen_command


load_dotenv()

from groq import Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Getting the metadata
metadata = process_files('data')


# Streamlit
st.title('Gemini for CSV')
st.write('Talk with your CSV data using Gemini Flash!')

#Add File
if os.listdir('data'):
    # User Query
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
   
    if user_query := st.chat_input():
        # Select suitable data based on the query
        file_name = select_df(user_query, metadata, client)

        # reading and getting metadata of selected csv
        df = pd.read_csv(os.path.join('data', file_name))
        head = str(df.head().to_dict())
        desc = str(df.describe().to_dict())
        cols = str(df.columns.to_list())
        dtype = str(df.dtypes.to_dict())


        st.session_state.messages.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)
    
        final_query = f"The dataframe name is 'df'. df has the columns {cols} and their datatypes are {dtype}. df is in the following format: {desc}. The head of df is: {head}. You cannot use df.info() or any command that cannot be printed. Write a pandas command for this query on the dataframe df: {user_query}"

        # Spin till the response comes.
        with st.spinner('Analyzing the data...'):
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_instruction_to_gen_command,
                    },
                    {
                        "role": "system",
                        "content": final_query,
                    }
                ],
                response_format={"type": "json_object"},
                model="llama3-8b-8192",
            )

            response = chat_completion.choices[0].message.content
            response_command = json.loads(response)['registry_info'][0]
            command = response_command["command"]
            response_type = response_command["format"]
        try:
            if response_type=='viz':
                # If user asks for a visualization
                code = visualization(final_query, client)
                exec(code)
                st.session_state.fig.append({"role": "assistant", "content": "Here is the chart"})

            else:
                # If user asks for a texual answer
                exec(f"data = {command}")
                response_final = natural_response(final_query, data, client)
                st.chat_message("assistant").write(response_final)
                st.session_state.messages.append({"role": "assistant", "content": response_final})

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": "Error"})
else:
    st.write("No csv file found at the 'data' folder")
