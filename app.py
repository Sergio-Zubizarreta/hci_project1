import streamlit as st
import pandas as pd
import time
import os
import altair as alt

# --------------------------------
# File setup
# --------------------------------
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        df_new.to_csv(csv_file, mode="w", header=True, index=False)
    else:
        df_new.to_csv(csv_file, mode="a", header=False, index=False)


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

    # --------------------------------
    # Home tab
    # --------------------------------
    with home:
        st.header("Introduction")
        st.write(
            """
Welcome to the Usability Testing Tool.

This tool is used to collect usability data for the Blender Add-on Explorer app.

In this app, you will:
1. Provide consent for data collection.
2. Fill out a short demographic questionnaire.
3. Test app usability and accessibility through specific tasks.
4. Answer an exit questionnaire about the app experience.
5. View a summary report of the collected data.
"""
        )

    # --------------------------------
    # Consent tab
    # --------------------------------
    with consent:
        st.header("Consent Form")

        st.write(
            """
- Participation is voluntary.
- Participants may stop at any time.
- Responses are used only for research and educational purposes.
- No personally identifiable information will be reported or sold to third parties.

By checking the box below, participants indicate that they have read and agree to participate in this usability test.
"""
        )

        consent_given = st.checkbox(
            "I have read the information above and I agree to participate in this usability test."
        )

        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given,
                }
                save_to_csv(data_dict, CONSENT_CSV)
                st.success("Consent recorded. Thank you.")

    # --------------------------------
    # Demographics tab
    # --------------------------------
    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            name = st.text_input("Name/Alias")
            age = st.number_input("Age", min_value=18, max_value=100, step=1)
            occupation = st.text_input("Occupation / Major")
            familiarity = st.selectbox(
                "How familiar are you with similar tools?",
                [
                    "Not familiar at all",
                    "Slightly familiar",
                    "Moderately familiar",
                    "Very familiar",
                    "Extremely familiar",
                ],
            )

            submitted = st.form_submit_button("Submit Demographics")

        if submitted:
            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "name": name,
                "age": age,
                "occupation": occupation,
                "familiarity": familiarity,
            }
            save_to_csv(data_dict, DEMOGRAPHIC_CSV)
            st.success("Demographic information saved. Thank you.")

    # --------------------------------
    # Task tab
    # --------------------------------
    with tasks:
        st.header("Task Page")
        st.write(
            "Select a task and record your experience while you use "
            "the Blender Add-on Explorer app."
        )

        task_labels = [
            "Task 1 – Find a popular add-on (>= 3000 stars)",
            "Task 2 – Filter to recently updated Python add-ons",
            "Task 3 – Sort by most recently updated add-ons",
        ]
        selected_task = st.selectbox("Select Task", task_labels)

        # Task descriptions
        if selected_task.startswith("Task 1"):
            st.write(
                "Scenario:\n"
                "You want to explore popular Blender add-ons in general.\n\n"
                "Instructions:\n"
                "1. Use the Blender Add-on Explorer app.\n"
                "2. Run a search that shows Blender add-ons from GitHub.\n"
                "3. Find at least one add-on that has more than 3000 stars.\n"
                "4. When you have found such an add-on and feel satisfied with your choice, "
                "tell the facilitator you are done."
            )
            task_id = 1

        elif selected_task.startswith("Task 2"):
            st.write(
                "Scenario:\n"
                "You only want add-ons that are written in Python and have been updated in the last year.\n\n"
                "Instructions:\n"
                "1. Use the filters in the left sidebar of the Blender Add-on Explorer.\n"
                "2. Set the filters so that the app shows only add-ons that:\n"
                "   - Are written in Python.\n"
                "   - Have been updated in the last 12 months.\n"
                "3. From the filtered results, choose one add-on that you might install.\n"
                "4. When you are satisfied with your choice, tell the facilitator you are done."
            )
            task_id = 2

        else:
            st.write(
                "Scenario:\n"
                "Imagine you care more about how recently an add-on was updated than how many stars it has.\n\n"
                "Instructions:\n"
                "1. Use the Blender Add-on Explorer app.\n"
                "2. Change the 'Sort by' option so that add-ons are ordered by how recently they were updated.\n"
                "3. Identify one add-on that fits this priority (recently updated, regardless of stars).\n"
                "4. When you are satisfied with your choice, you may submit the request."
            )
            task_id = 3

        # Timing keys per task
        start_key = f"start_time_{task_id}"
        duration_key = f"task_duration_{task_id}"

        # Timing controls
        if st.button("Start Task Timer"):
            st.session_state[start_key] = time.time()
            st.info("Timer started.")

        if st.button("Stop Task Timer"):
            if start_key in st.session_state:
                duration = time.time() - st.session_state[start_key]
                st.session_state[duration_key] = duration
                st.success(f"Task duration: {duration:.1f} seconds")
            else:
                st.warning("Timer was not started for this task.")

        # Metrics
        success = st.radio(
            "Task success",
            ["Completed", "Partially completed", "Not completed"],
            key=f"success_{task_id}",
        )

        filters_used = st.multiselect(
            "Filters used (check all that apply)",
            [
                "Changed minimum stars slider",
                "Changed 'Sort by' option",
                "Toggled 'Only show add-ons updated in the last 12 months'",
                "Used 'Programming language' multiselect",
                "Other (describe in notes)",
            ],
            key=f"filters_{task_id}",
        )

        difficulty_label = st.radio(
            "How easy or difficult was this task?",
            [
                "1 - Very easy",
                "2 - Easy",
                "3 - Neutral",
                "4 - Difficult",
                "5 - Very difficult",
            ],
            key=f"difficulty_{task_id}",
        )
        difficulty = int(difficulty_label[0])

        notes = st.text_area(
            "Task comments",
            key=f"notes_{task_id}",
        )

        if st.button("Save Task Results"):
            duration_val = st.session_state.get(duration_key, "")

            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_id": task_id,
                "task_name": selected_task,
                "success": success,
                "duration_seconds": duration_val,
                "filters_used": "; ".join(filters_used),
                "difficulty": difficulty,
                "notes": notes,
            }
            save_to_csv(data_dict, TASK_CSV)
            st.success("Task results saved.")

            # Clean up timer for this task
            if start_key in st.session_state:
                del st.session_state[start_key]
            if duration_key in st.session_state:
                del st.session_state[duration_key]

    # --------------------------------
    # Exit Questionnaire tab
    # --------------------------------
    with exit:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            st.write(
                "Please answer a few questions about your experience using the "
                "Blender Add-on Explorer app."
            )

            overall_ease_label = st.radio(
                "Overall, how easy or difficult was it to use the Blender Add-on Explorer app?",
                [
                    "1 - Very easy",
                    "2 - Easy",
                    "3 - Neutral",
                    "4 - Difficult",
                    "5 - Very difficult",
                ],
            )
            overall_ease = int(overall_ease_label[0])

            filters_clarity_label = st.radio(
                "How clear or confusing were the filters in the left sidebar?",
                [
                    "1 - Very clear",
                    "2 - Clear",
                    "3 - Neutral",
                    "4 - Confusing",
                    "5 - Very confusing",
                ],
            )
            filters_clarity = int(filters_clarity_label[0])

            confidence_label = st.radio(
                "How confident would you feel using this app on your own to find Blender add-ons?",
                [
                    "1 - Not at all confident",
                    "2 - Slightly confident",
                    "3 - Moderately confident",
                    "4 - Very confident",
                    "5 - Extremely confident",
                ],
            )
            confidence = int(confidence_label[0])

            like_most = st.text_area("What did you like most about the app?")
            confusing = st.text_area(
                "What was the most confusing or frustrating part of the app?"
            )
            one_change = st.text_area(
                "If you could change one thing in the app to make it easier for new Blender users, what would you change?"
            )

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")

        if submitted_exit:
            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "overall_ease": overall_ease,
                "filters_clarity": filters_clarity,
                "confidence": confidence,
                "like_most": like_most,
                "confusing": confusing,
                "one_change": one_change,
            }
            save_to_csv(data_dict, EXIT_CSV)
            st.success("Exit questionnaire data saved. Thank you.")

    # --------------------------------
    # Report tab
    # --------------------------------
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

            required_cols = {"overall_ease", "filters_clarity", "confidence"}
            if required_cols.issubset(exit_df.columns):
                avg_overall_ease = exit_df["overall_ease"].mean()
                avg_filters_clarity = exit_df["filters_clarity"].mean()
                avg_confidence = exit_df["confidence"].mean()

                st.write(
                    f"**Average overall ease** (1=very easy, 5=very difficult): {avg_overall_ease:.2f}"
                )
                st.write(
                    f"**Average filters clarity** (1=very clear, 5=very confusing): {avg_filters_clarity:.2f}"
                )
                st.write(
                    f"**Average confidence** (1=not at all, 5=extremely confident): {avg_confidence:.2f}"
                )

                avg_df = pd.DataFrame(
                    {
                        "metric": [
                            "Overall ease",
                            "Filters clarity",
                            "Confidence",
                        ],
                        "average": [
                            avg_overall_ease,
                            avg_filters_clarity,
                            avg_confidence,
                        ],
                    }
                )

                color_scale = alt.Scale(
                    domain=["Overall ease", "Filters clarity", "Confidence"],
                    range=["#1f77b4", "#ff7f0e", "#2ca02c"],
                )

                chart = alt.Chart(avg_df).mark_bar().encode(
                    y=alt.Y("metric:N", title="", axis=alt.Axis(labelAngle=0)),
                    x=alt.X(
                        "average:Q",
                        title="Average score (1–5)",
                        scale=alt.Scale(domain=[1, 5]),
                    ),
                    color=alt.Color(
                        "metric:N",
                        scale=color_scale,
                        legend=alt.Legend(title="Metric"),
                    ),
                ).properties(width=400, height=200)

                st.altair_chart(chart, use_container_width=True)
            else:
                st.info(
                    "Existing exit_data.csv uses an older format (without overall_ease/filters_clarity/confidence). "
                    "Fill out the new Exit Questionnaire at least once to see summary statistics."
                )


if __name__ == "__main__":
    main()