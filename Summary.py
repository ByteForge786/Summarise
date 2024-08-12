import ctranslate2
import transformers
from huggingface_hub import snapshot_download
import pandas as pd
import matplotlib.pyplot as plt
import io
import sys

# Load the model (as in your code)
model_id = "ByteForge/Defog_llama-3-sqlcoder-8b-ct2-int8_float16"
model_path = snapshot_download(model_id)
model = ctranslate2.Generator(model_path)
tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are a data analysis expert. Given a dataframe description and a question, provide Python code to analyze the data."},
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
    results = model.generate_batch([input_tokens], include_prompt_in_result=False, max_length=256, sampling_temperature=0.6, sampling_topp=0.9, end_token=terminators)
    return tokenizer.decode(results[0].sequences_ids[0])

def generate_questions(df):
    columns = df.columns.tolist()
    data_types = df.dtypes.tolist()
    
    prompt = f"""Given a DataFrame with the following structure:
    Columns: {columns}
    Data types: {data_types}
    
    Generate 5 insightful questions for data analysis."""
    
    response = generate_response(prompt)
    questions = response.split('\n')
    return [q.strip() for q in questions if q.strip()]

def generate_analysis_code(df, question):
    prompt = f"""Given a DataFrame with the following structure:
    Columns: {df.columns.tolist()}
    Data types: {df.dtypes.tolist()}
    
    Generate Python code to answer this question: {question}
    Only provide the code, no explanations."""
    
    return generate_response(prompt)

def execute_analysis(df, code):
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        exec(code)
        result = buffer.getvalue()
    except Exception as e:
        result = f"Error: {str(e)}"
    finally:
        sys.stdout = old_stdout
    
    return result

def summarize_results(question, result):
    prompt = f"""Summarize the following data analysis result in plain English:
    Question: {question}
    Result: {result}
    Provide a concise summary."""
    
    return generate_response(prompt)

def analyze_dataframe(df):
    questions = generate_questions(df)
    summary = "Data Analysis Summary:\n\n"
    
    for question in questions:
        code = generate_analysis_code(df, question)
        result = execute_analysis(df, code)
        summary += f"Question: {question}\n"
        summary += f"Analysis: {result}\n"
        summary += f"Summary: {summarize_results(question, result)}\n\n"
    
    return summary

# Example usage
df = pd.read_csv('your_data.csv')
analysis_summary = analyze_dataframe(df)
print(analysis_summary)
