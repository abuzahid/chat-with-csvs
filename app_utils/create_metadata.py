import pandas as pd
import os
import re
import json

# Generate metadata from csv file
def generate_metadata(file_path):
    df = pd.read_csv(file_path)
    metadata = {
        'head': str(df.head().to_dict()),
        'desc': str(df.describe(include='all').to_dict()),
        'cols': str(df.columns.to_list()),
        'dtype': str(df.dtypes.to_dict())
    }
    return metadata

# Creating metadata dict
def process_files(dir_name):
    all_metadata = {}
    for file_path in os.listdir(dir_name):
        file_name = os.path.basename(file_path)
        metadata = generate_metadata(os.path.join('data', file_path))
        all_metadata[file_name] = metadata
    return all_metadata


# Extracting python code from llm response
def extract_python_code(text):
    pattern = r'```python\s(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        return None
    else:
        return matches[0]
    
# Finds the suitable csv file
def select_df(user_query, metadata, client):
    system_instruction_phase2=f"""You are an expert python developer who works with pandas. You make sure to read the user question and find the most suitable csv file name to answer the question \
                          Here is the user query ###{user_query}
                          Here is the metadata where the csv files are the file name and the value regarding that csv file represents the metadata.
                          {metadata}
                          Your response should in JSON format like the following:
                            {{
                                "registry_info": [
                                    {{
                                    "file_name": <the most suitable csv file name>
                                    }}
                                ]
                            }}
                            """
    chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_instruction_phase2,
                    }
                ],
                response_format={"type": "json_object"},
                model="llama3-8b-8192",
            )
    
    response = chat_completion.choices[0].message.content
    file_name = json.loads(response)['registry_info'][0]["file_name"]

    return file_name


# Makes visualization
def visualization(final_query, client):
    viz_response = f"Generate the code <code> for plotting the data in plotly, in the format requested. The solution should be given using plotly\
                    and only plotly. Do not use matplotlib based on the following instruction:\
                    {final_query}\
                    Return the code <code> in the following format ```python <code>```"
    chat_completion_viz = client.chat.completions.create(
                            messages=[
                                    {
                                        "role": "system",
                                        "content": viz_response,
                                    }
                                ],
                                model="llama3-8b-8192",
                            )
    
    
    response_final = chat_completion_viz.choices[0].message.content
    code = extract_python_code(response_final)
    code = code.replace("fig.show()", "")
    code += """st.chat_message("assistant").plotly_chart(fig, theme='streamlit', use_container_width=True)"""

    return code

# Create texual response.
def natural_response(final_query, data, client):
    natural_response = f"The user query is {final_query}. The output of the command is {str(data)}. If the data is 'None', you can say 'Please ask a query to get started'. DO NOT mention the command used. Generate a response in natural language for the output."

    chat_completion_final = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": natural_response,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion_final.choices[0].message.content
