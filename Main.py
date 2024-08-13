def main():
    st.set_page_config(page_title="Data Query and Visualization App", layout="wide")

    st.title("Data Query and Visualization App")

    # Load cached model
    model, tokenizer = load_model()

    if model is None or tokenizer is None:
        st.stop()

    # Your prompt (to be filled)
    prompt = ["Your prompt here"]

    # User input
    question = st.text_input("Enter your question:")

    if 'result_df' not in st.session_state:
        st.session_state.result_df = None

    if st.button("Submit"):
        if question:
            with st.spinner("Generating SQL query..."):
                response = get_model_response(question, prompt, model, tokenizer)
                sql_query = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
                sql_query = sql_query.group(1) if sql_query else None
                chart_recommendation = re.search(r'Chart recommendation: (.*?)$', response, re.MULTILINE)
                chart_recommendation = chart_recommendation.group(1) if chart_recommendation else None

            if sql_query:
                st.subheader("Generated SQL Query:")
                st.code(sql_query, language="sql")

                with st.spinner("Executing query..."):
                    # This is where you would run your SQL query on Snowflake
                    # For now, we'll use a dummy DataFrame.
                    st.session_state.result_df = pd.DataFrame({
                        'Column1': ['A', 'B', 'C'],
                        'Column2': [10, 20, 30]
                    })

    if st.session_state.result_df is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Query Results:")
            st.dataframe(st.session_state.result_df)

        with col2:
            st.subheader("Visualization:")
            fig = px.bar(st.session_state.result_df, x='Column1', y='Column2')
            st.plotly_chart(fig)

        # Add analysis and graph generation options
        st.subheader("Additional Analysis")
        col3, col4 = st.columns(2)

        with col3:
            if st.button("Analyze Data", key="analyze"):
                with st.spinner("Analyzing data..."):
                    summary, analysis_code = analyze_dataframe(st.session_state.result_df, question)
                    st.write("Analysis Summary:")
                    st.write(summary)
                    st.write("Analysis Code:")
                    st.code(analysis_code)

        with col4:
            if st.button("Generate Graphs", key="generate_graphs"):
                with st.spinner("Generating graphs..."):
                    graph_code = generate_graphs(st.session_state.result_df, question)
                    st.write("Graph Code:")
                    st.code(graph_code)
                    
                    # Execute the graph code
                    fig, ax = plt.subplots()
                    exec(graph_code, {'df': st.session_state.result_df, 'plt': plt, 'ax': ax})
                    st.pyplot(fig)

if __name__ == "__main__":
    main()
