import streamlit as st
import ctranslate2
import transformers
from huggingface_hub import snapshot_download
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_resource
def load_model():
    model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
    model_path = snapshot_download(model_id)
    model = ctranslate2.Generator(model_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer

def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are a data analysis expert. Analyze the given text and provide insights."},
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

def identify_relevant_column(df, question):
    # Create a prompt to identify the relevant column
    column_identification_prompt = f"""
    Based on the following question and available columns, identify which column should be analyzed:
    
    Question: {question}
    
    Available columns: {', '.join(df.columns.tolist())}
    
    Sample data from each text column:
    {df.select_dtypes(include=['object']).head(2).to_string()}
    
    Return only the exact column name that should be analyzed based on the question.
    """
    
    column_name = generate_response(column_identification_prompt).strip()
    
    # Verify the column exists
    if column_name not in df.columns:
        return None
    return column_name

def analyze_text_content(df, question):
    # First, identify the relevant column
    relevant_column = identify_relevant_column(df, question)
    
    if relevant_column is None:
        return "Could not identify a relevant column for analysis based on the question.", None, None
    
    if not pd.api.types.is_string_dtype(df[relevant_column]):
        return f"The identified column '{relevant_column}' is not a text column.", None, None
    
    # Get unique descriptions
    unique_contents = df[relevant_column].unique()
    
    # Create context for analysis
    context = f"""
    Original Question: {question}
    
    Analyzing content from column: {relevant_column}
    
    Sample content:
    {' '.join(str(content) for content in unique_contents[:5])}
    
    Total unique entries: {len(unique_contents)}
    """
    
    # Generate analysis prompt
    analysis_prompt = f"""
    Based on the content from the {relevant_column} column and the original question:
    {question}
    
    Analyze the following aspects:
    1. How does the content specifically relate to the question asked?
    2. What are the key themes or patterns relevant to the question?
    3. What specific insights can be drawn that address the question?
    
    Context:
    {context}
    
    Please provide a focused analysis that directly addresses the original question.
    """
    
    # Get initial analysis
    analysis = generate_response(analysis_prompt)
    
    # Generate summary prompt
    summary_prompt = f"""
    Based on the analysis of the {relevant_column} column content and the original question:
    {question}
    
    Analysis results:
    {analysis}
    
    Please provide a concise summary that directly answers the original question while highlighting the most relevant insights from the text analysis.
    """
    
    summary = generate_response(summary_prompt)
    
    return summary, analysis, relevant_column

# Streamlit app
st.title("Intelligent Text Content Analysis")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
question = st.text_input("Enter your question about the data:")

if uploaded_file is not None and question:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:")
    st.dataframe(df.head())
    
    if st.button("Analyze Content"):
        summary, analysis, identified_column = analyze_text_content(df, question)
        
        if identified_column:
            st.write(f"Analyzing column: {identified_column}")
            st.write("Summary:")
            st.write(summary)
            st.write("Detailed Analysis:")
            st.write(analysis)
        else:
            st.error(summary)  # Display error message if column identification failed
