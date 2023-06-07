import streamlit as st
import base64
import pandas as pd
import pickle

# Load the saved model and scaler
best_model = pickle.load(open('pickle/nn_model.pkl', 'rb'))
scaler = pickle.load(open('pickle/scaler.pkl', 'rb'))

# Load the dictionaries for driver confidence and constructor reliability
driver_confidence_dict = pickle.load(open('pickle/driver_confidence_dict.pkl', 'rb'))
constructor_reliability_dict = pickle.load(open('pickle/constructor_reliability_dict.pkl', 'rb'))

# Load the LabelEncoder object
le_gp = pickle.load(open('pickle/gp_label_encoder.pkl', 'rb'))
le_d = pickle.load(open('pickle/d_label_encoder.pkl', 'rb'))
le_c = pickle.load(open('pickle/c_label_encoder.pkl', 'rb'))

# Define driver, constructor, and circuit dropdowns
driver_names = le_d.inverse_transform(list(driver_confidence_dict.keys()))
constructor_names = le_c.inverse_transform(list(constructor_reliability_dict.keys()))
gp_names = le_gp.inverse_transform(range(len(le_gp.classes_)))
qualifying_positions = list(range(1, 21))

st.set_page_config(
    page_icon="🏎️",
    layout="wide"
)

st.markdown(
    f'<h1 style="text-align: center;">Formula One Race Winner Prediction App</h1>',
    unsafe_allow_html=True
)

file_ = open("f1.gif", "rb")

contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()
st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="f1 gif" style="display:block; margin:auto;" height="300" width="1000">',
    unsafe_allow_html=True,
)

# Take user input
season = st.text_input("Enter season: ")
driver_name = st.selectbox("Select driver's name: ", driver_names)
constructor_name = st.selectbox("Select constructor's name: ", constructor_names)
gp_name = st.selectbox("Select circuit's name: ", gp_names)
qualifying_position = st.selectbox("Enter driver's qualifying position: ", qualifying_positions)


# Encode the categorical variables
if driver_name != '':
    driver_name_encoded = le_d.transform([driver_name])[0]
else:
    st.error("Please enter a valid driver name")
if constructor_name != '':
    constructor_name_encoded = le_c.transform([constructor_name])[0]
else:
    st.error("Please enter a valid constructor name")
if gp_name != '':
    gp_name_encoded = le_gp.transform([gp_name])[0]
else:
    st.error("Please enter a valid circuit name")

if st.button("Predict"):
    if driver_name != '' and constructor_name != '' and gp_name != '' and season != '':
        # Create a new dataframe for prediction
        data = pd.DataFrame({
            'GP_name': [gp_name_encoded],
            'quali_pos': [qualifying_position],
            'constructor': [constructor_name_encoded],
            'driver': [driver_name_encoded],
            'driver_confidence': driver_confidence_dict[driver_name_encoded],
            'constructor_relaiblity': constructor_reliability_dict[constructor_name_encoded],
            'season': [season]
        })

        # Scale the features
        data_scaled = scaler.transform(data)

        # Make the prediction using the loaded model
        position_pred = best_model.predict(data_scaled)

        # Print the predicted position
        st.divider()
        st.success("SUCCESS!")
        st.subheader(f'Predicted final grid position of the driver: {int(position_pred[0])}')
        st.divider()

        all_input_data = pd.DataFrame({
                'GP_name': [gp_name_encoded] * 22,
                'quali_pos': range(1, 23),
                'constructor': [constructor_name_encoded] * 22,
                'driver': [driver_name_encoded] * 22,
                'driver_confidence': [driver_confidence_dict[driver_name_encoded]] * 22,
                'constructor_relaiblity': [constructor_reliability_dict[constructor_name_encoded]] * 22,
                'season': [season] * 22
            })

        all_input_data.to_csv('all_input_data.csv', index=False)

        # Scale the features
        all_data_scaled = scaler.transform(all_input_data)

        # Make the prediction using the loaded model
        all_position_pred = best_model.predict(all_data_scaled)

        # Create a new dataframe to store the predicted position for all qualifying positions
        all_predicted_df = pd.DataFrame({
            'Possible Qualifying position': range(1, 23),
            'Predicted Final Grid Position': all_position_pred.astype(int)
        })

        # Draw a line chart to show the predicted positions for all qualifying positions
        st.subheader(f"Predicted Final Grid Position for {driver_name} at {gp_name} for different qualifying position")
        col1, col2 = st.columns([3, 1], gap="medium")
        col1.line_chart(data=all_predicted_df, x='Possible Qualifying position', y='Predicted Final Grid Position', width=0, height=0, use_container_width=True)

        col2.table(all_predicted_df)

    else:
        st.error("Please fill out all the required fields.")







