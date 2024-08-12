import streamlit as st
import ctranslate2
import transformers
from huggingface_hub import snapshot_download
import pandas as pd
import matplotlib.pyplot as plt
import io
import sys
import numpy as np

# Load the model
@st.cache_resource
def load_model():
    model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
    model_path = snapshot_download(model_id)
    model = ctranslate2.Generator(model_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer

model, tokenizer = load_model()

def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are a data analysis expert. Analyze the given data and provide insights."},
        {"role": "user", "content": prompt},
    ]
    input_ids = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    input_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(input_ids))
    results = model.generate_batch([input_tokens], include_prompt_in_result=False, max_length=512, sampling_temperature=0.6, sampling_topp=0.9, end_token=terminators)
    return tokenizer.decode(results[0].sequences_ids[0])

def analyze_dataframe(df, question):
    df_description = f"""
    Original Question: {question}
    
    DataFrame Information:
    Columns: {df.columns.tolist()}
    Data types: {df.dtypes.tolist()}
    Shape: {df.shape}
    
    Sample data:
    {df.head().to_string()}
    
    Summary statistics:
    {df.describe().to_string()}
    """
    
    prompt = f"""
    Based on the following DataFrame description and the original question, generate Python code to answer these questions:
    1. What are the highest and lowest values, and on which dates do they occur?
    2. Is there an increasing or decreasing trend in the data?
    3. What is the average value, and how many days are above/below this average?
    4. Are there any notable patterns or anomalies in the data?
    5. Can you identify any seasonality or cyclical patterns?
    {df_description}
    Provide the Python code to answer these questions. Each code snippet should be followed by a brief explanation of what it does.
    """
    
    analysis_code = generate_response(prompt)
    
    summary_prompt = f"""
    Based on the DataFrame description, the original question, and the analysis performed, provide a comprehensive summary of the findings in plain English. 
    The summary should include insights about trends, patterns, anomalies, and any other relevant observations.
    
    {df_description}
    
    Analysis results:
    {analysis_code}
    
    Please provide a detailed yet concise summary of the key insights derived from this data, focusing on answering the original question.
    """
    
    summary = generate_response(summary_prompt)
    
    return summary, analysis_code

def generate_graphs(df, question):
    prompt = f"""
    Based on the following DataFrame description and the original question, generate Python code to create 3 meaningful and insightful graphs:
    
    Original Question: {question}
    
    DataFrame Information:
    Columns: {df.columns.tolist()}
    Data types: {df.dtypes.tolist()}
    Shape: {df.shape}
    
    Sample data:
    {df.head().to_string()}
    
    Summary statistics:
    {df.describe().to_string()}
    
    Provide Python code to create 3 different types of graphs (e.g., line plot, scatter plot, bar chart, histogram) that best represent the data and reveal interesting patterns or insights related to the original question. Use matplotlib for plotting. Each graph should have appropriate labels, titles, and legends.
    """
    
    graph_code = generate_response(prompt)
    return graph_code

# Streamlit app
st.title("Data Analysis App")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
question = st.text_input("Enter your question about the data:")

if uploaded_file is not None and question:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:")
    st.dataframe(df.head())

    if st.button("Analyze Data"):
        summary, analysis_code = analyze_dataframe(df, question)
        st.write("Analysis Summary:")
        st.write(summary)
        
        st.write("Analysis Code:")
        st.code(analysis_code)

    if st.button("Generate Graphs"):
        graph_code = generate_graphs(df, question)
        st.write("Graph Code:")
        st.code(graph_code)
        
        # Execute the graph code
        fig, ax = plt.subplots(3, 1, figsize=(10, 15))
        exec(graph_code, {'df': df, 'np': np, 'plt': plt, 'ax': ax})
        st.pyplot(fig)