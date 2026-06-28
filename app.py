import streamlit as st
import pandas as pd
import time
import os
import altair as alt

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    # Convert dict to DataFrame with a single row
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        # If CSV doesn't exist, write with headers
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        # Else, we need to append without writing the header!
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()

def main():

    st.title("Usability Testing Tool")

    home, consent, demographics, tasks, exit, report = st.tabs(
        ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"]
    )

    # Home tab
    with home:
        st.header("Introduction")
        st.write("""
        Welcome to the Usability Testing Tool for the Stella Magna app built for HCI.

        In this app, you will:
        1. Provide consent for data collection.
        2. Fill out a short demographic questionnaire.
        3. Perform a specific task (or tasks).
        4. Answer an exit questionnaire about your experience.
        5. View a summary report (for demonstration purposes).
        """)

    # Consent tab
    with consent:
        st.header("Consent Form")

        st.write("""
        In this consent form:

        - Your participation is voluntary.
        - You may stop at any time.
        - Your responses will be used only for research and educational purposes.
        - No personally identifiable information will be reported or sold to third parties.

        By checking the box below, you indicate that you have read and agree to participate in this usability test.
        """)

        consent_given = st.checkbox(
            "I have read the information above and I agree to participate in this usability test."
        )

        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)
                st.success("Consent recorded. Thank you.")

    # Demographics tab
    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            name = st.text_input("Name/Alias")
            age = st.number_input("Age", min_value=18, max_value=100, step=1)
            occupation = st.text_input("Occupation / Major")
            familiarity = st.selectbox(
                "How familiar are you with similar tools?",
                ["Not familiar at all", "Slightly familiar", "Moderately familiar", "Very familiar", "Extremely familiar"]
            )

            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name,
                    "age": age,
                    "occupation": occupation,
                    "familiarity": familiarity
                }
                save_to_csv(data_dict, DEMOGRAPHIC_CSV)
                st.success("Demographic information saved. Thank you.")

    # Task tab
    with tasks:
        st.header("Task Page")
        st.write("Please select a task and record your experience completing it.")

        selected_task = st.selectbox("Select Task", ["Task 1: Example Task"])
        st.write("Task Description: Perform the example task in our system...")

        start_button = st.button("Start Task Timer")
        if start_button:
            st.session_state["start_time"] = time.time()

        stop_button = st.button("Stop Task Timer")
        if stop_button and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.session_state["task_duration"] = duration

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_val = st.session_state.get("task_duration", None)

            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_name": selected_task,
                "success": success,
                "duration_seconds": duration_val if duration_val else "",
                "notes": notes
            }
            save_to_csv(data_dict, TASK_CSV)

            if "start_time" in st.session_state:
                del st.session_state["start_time"]
            if "task_duration" in st.session_state:
                del st.session_state["task_duration"]

    # Exit Questionnaire tab
    with exit:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            st.write("Please answer a few questions about your experience using this application.")

            satisfaction_options = [
                "0 - Highly inconvenient / very unclear",
                "1 - Inconvenient",
                "2 - Somewhat inconvenient",
                "3 - Neutral",
                "4 - Convenient",
                "5 - Highly convenient / very clear"
            ]
            satisfaction_label = st.radio(
                "Overall, how clear and convenient was it to navigate and use the application?",
                satisfaction_options
            )
            satisfaction = int(satisfaction_label[0])

            difficulty_options = [
                "0 - Extremely difficult",
                "1 - Very difficult",
                "2 - Somewhat difficult",
                "3 - Neutral",
                "4 - Easy",
                "5 - Very easy"
            ]
            difficulty_label = st.radio(
                "Overall, how difficult was it to complete the task(s)?",
                difficulty_options
            )
            difficulty = int(difficulty_label[0])

            missing_info = st.text_area(
                "Is there any missing information or prompt you would consider important for us to be aware of?"
            )
            open_feedback = st.text_area(
                "Any other suggestions for improving your awareness of, access to, and experience with the application?"
            )

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "difficulty": difficulty,
                    "missing_info": missing_info,
                    "open_feedback": open_feedback
                }
                save_to_csv(data_dict, EXIT_CSV)
                st.success("Exit questionnaire data saved. Thank you.")

    # Report tab
    with report:
        st.header("Usability Report - Aggregated Results")

        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            st.dataframe(consent_df)
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not demographic_df.empty:
            st.dataframe(demographic_df)
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
        else:
            st.info("No exit questionnaire data available yet.")

        if not exit_df.empty:
            st.subheader("Exit Questionnaire Averages")
            avg_satisfaction = exit_df["satisfaction"].mean()
            avg_difficulty = exit_df["difficulty"].mean()
            st.write(f"**Average Satisfaction**: {avg_satisfaction:.2f}")
            st.write(f"**Average Difficulty**: {avg_difficulty:.2f}")

            avg_df = pd.DataFrame({
                "metric": ["Satisfaction", "Difficulty"],
                "average": [avg_satisfaction, avg_difficulty]
            })
            # Define a colorblind-friendly palette (e.g., blue and orange) [web:99][web:105]
            color_scale = alt.Scale(
                domain=["Satisfaction", "Difficulty"],
                range=["#1f77b4", "#ff7f0e"]  # blue and orange
            )

            chart = alt.Chart(avg_df).mark_bar().encode(
                y=alt.Y("metric:N", title="", axis=alt.Axis(labelAngle=0)),
                x=alt.X("average:Q", title="Scale from 0–5", scale=alt.Scale(domain=[0, 5])),
                color=alt.Color("metric:N", scale=color_scale, legend=alt.Legend(title="Metric"))
            ).properties(
                width=400,
                height=200
            )

            st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()