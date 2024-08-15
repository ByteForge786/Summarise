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
