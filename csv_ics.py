import streamlit as st

st.title("ICS to CSV")

ics_file=st.file_uploader("Upload ICS file", type="ics")

import csv
import os
import sys
from icalendar import Calendar

# Create a new CSV file
csv_file_path = 'calendar.csv'
csv_file = open(csv_file_path, 'w', newline='', encoding='utf-8')

# Write the CSV header
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Subject', 'Start Time', 'End Time', 'Description'])

# Read the iCalendar file
cal = Calendar.from_ical(ics_file.read())
for event in cal.walk('VEVENT'):
    print(event)
    subject = event['SUMMARY']
    start_time = event['DTSTART'].dt
    end_time = ""
    if 'DTEND' in event:
        end_time = event['DTEND'].dt
    description = ''
    if 'DESCRIPTION' in event:
        description = event['DESCRIPTION']
    csv_writer.writerow([subject, start_time, end_time, description])

# Close the CSV file
csv_file.close()

# Display a link to download the CSV file
st.markdown('### **Download CSV File**')

filename = "calendar.csv"
with open(filename, 'rb') as f:
    bytes = f.read()
    st.download_button(label='Download file', data=bytes, file_name=filename, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')