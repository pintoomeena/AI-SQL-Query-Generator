import streamlit as st
from services.query_service import process_question
from services.llm_service import explain_result


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="AI SQL Query Generator",
    page_icon="🗄️",
    layout="wide"
)


# -----------------------------
# Header
# -----------------------------

st.title("🗄️ AI SQL Query Generator")

st.write(
    "Ask questions about your database using natural language."
)


# -----------------------------
# Query Input
# -----------------------------

question = st.text_input(
    "Ask your database a question:"
)


# -----------------------------
# Run Query
# -----------------------------

if st.button("Run Query"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            # -----------------------------
            # Process Question
            # -----------------------------

            response = process_question(question)

            sql = response["sql"]
            result = response["result"]
            rows = result["rows"]


            # -----------------------------
            # Generated SQL
            # -----------------------------

            st.subheader("Generated SQL")

            st.code(
                sql,
                language="sql"
            )


            # -----------------------------
            # AI Explanation
            # -----------------------------

            st.subheader("🤖 AI Explanation")

            explanation = explain_result(
                question,
                sql,
                result
            )

            st.write(explanation)


            # -----------------------------
            # Results
            # -----------------------------

            st.subheader("📊 Results")

            if rows:

                st.dataframe(
                    rows,
                    use_container_width=True
                )


                # -----------------------------
                # Visualization
                # -----------------------------

                if len(rows) >= 2:

                    columns = list(rows[0].keys())

                    numeric_columns = []
                    categorical_columns = []


                    # Find numeric and categorical columns
                    for column in columns:

                        values = [
                            row[column]
                            for row in rows
                            if row[column] is not None
                        ]

                        if not values:
                            continue

                        try:

                            for value in values:
                                float(value)

                            numeric_columns.append(column)

                        except (ValueError, TypeError):

                            categorical_columns.append(column)


                    # -----------------------------
                    # Create Chart
                    # -----------------------------

                    if numeric_columns:

                        st.subheader("📈 Visualization")


                        selected_numeric = st.selectbox(
                            "Select numeric column:",
                            numeric_columns,
                            key="numeric_column"
                        )


                        if categorical_columns:

                            selected_category = st.selectbox(
                                "Select category column:",
                                categorical_columns,
                                key="category_column"
                            )


                            chart_data = {}

                            for row in rows:

                                category = str(
                                    row[selected_category]
                                )

                                value = row[selected_numeric]

                                if value is not None:

                                    chart_data[category] = float(
                                        value
                                    )


                            st.bar_chart(chart_data)


                        else:

                            values = [
                                float(row[selected_numeric])
                                for row in rows
                                if row[selected_numeric] is not None
                            ]

                            st.bar_chart(values)


            else:

                st.info("No results found.")


            # -----------------------------
            # Attempts
            # -----------------------------

            st.caption(
                f"Attempts: {response['attempts']}"
            )


        except Exception as e:

            st.error(
                f"Query failed: {str(e)}"
            )