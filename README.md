# ATTENDANCE MANAGEMENT USING N8N

This project was built using self hosted N8N running on Docker container. Using Ngrok for the public domain


## Tech Stack

-Ngrok
-Docker
-N8N
-VSCode
-Mysql

## API
-Google sheet API
-Google Drive API
-Google Gemini Api

## Project Structure


-Face_recognition_uploader.py: Identifies the image of the person and sends his name to N8N webhook node
-Voice_Agent.py: This is where you receive AI calls and talk to AI for further guidance on your query
-Employees File Folder: contains image of the employees with their names

### Workflows

Workflow 1 : Attendance updater
Workflow 2 : Voice Agent

## Database(MYSQL)

-Database Name: SmartAttendance
-Tables : Attendance_Logs and Students Table
