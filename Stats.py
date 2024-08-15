def get_dataframe_statistics(df):
    stats = df.describe(include='all').transpose()
    stats['missing'] = df.isnull().sum()
    stats['dtype'] = df.dtypes
    return stats

def analyze_dataframe_stats(df):
    stats = get_dataframe_statistics(df)
    
    prompt = f"""Given the following DataFrame statistics:
    {stats.to_string()}
    
    Provide a comprehensive analysis of the dataset, including insights on data distribution, missing values, and potential areas for further investigation."""
    
    return generate_response(prompt)
def analyze_dataframe_hybrid(df, sample_size=1000):
    stats = get_dataframe_statistics(df)
    
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
    else:
        df_sample = df
    
    prompt = f"""Given a DataFrame with the following statistics:
    {stats.to_string()}
    
    And a sample of the data:
    {df_sample.head(10).to_string()}
    
    Provide a comprehensive analysis of the dataset, including:
    1. Insights on overall data distribution and statistics
    2. Analysis of potential patterns or trends visible in the sample
    3. Recommendations for further investigation or data preprocessing
    """
    
    return generate_response(prompt)
