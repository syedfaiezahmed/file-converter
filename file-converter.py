import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="File Converter, Cleaner, and Editor", layout="wide")
st.title("File Converter, Cleaner, Editor, and Visualizer")
st.write("Upload CSV or Excel files, clean data, edit dynamically, visualize, and convert formats.")

files = st.file_uploader("Upload CSV or Excel files.", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1]
        df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)

        st.subheader(f"{file.name} - Preview and Edit")
        df = st.data_editor(df, use_container_width=True, key=file.name)

        # Remove Duplicates
        if st.checkbox(f"Remove Duplicates - {file.name}"):
            df = df.drop_duplicates()
            st.success("Duplicates Removed")
            st.dataframe(df.head())

        # Fill Missing Values
        if st.checkbox(f"Fill Missing Values - {file.name}"):
            numeric_cols = df.select_dtypes(include=["number"])
            df[numeric_cols.columns] = df[numeric_cols.columns].fillna(numeric_cols.mean())
            st.success("Missing values filled with column means")
            st.dataframe(df.head())

        # Select Specific Columns
        selected_columns = st.multiselect(f"Select Columns - {file.name}", df.columns, default=list(df.columns))
        if selected_columns:
            df = df[selected_columns]
            st.dataframe(df.head())

        # Show Chart
        if st.checkbox(f"Show Chart - {file.name}") and not df.select_dtypes(include="number").empty:
            st.write("### Chart Options")
            chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])
            x_axis = st.selectbox("Select X-axis", df.columns)
            y_axis = st.selectbox("Select Y-axis", df.select_dtypes(include="number").columns)

            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x_axis, y=y_axis, title="Bar Chart", text_auto=True)
            elif chart_type == "Line Chart":
                fig = px.line(df, x=x_axis, y=y_axis, title="Line Chart", markers=True)
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, title="Scatter Plot", size_max=10)

            st.plotly_chart(fig, use_container_width=True)

        # File Format Conversion
        format_choice = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name + "_format")

        if st.button(f"Download {file.name} as {format_choice}", key=file.name + "_download"):
            output = BytesIO()
            if format_choice == "CSV":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file.name.replace(ext, "csv")
            else:
                df.to_excel(output, index=False, engine="openpyxl")
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.replace(ext, "xlsx")

            output.seek(0)
            st.download_button("Download File", data=output, file_name=new_name, mime=mime)

            st.success("Processing complete!")
