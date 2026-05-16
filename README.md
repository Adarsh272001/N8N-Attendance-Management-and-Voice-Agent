+--------------------------+
|  Face Recognition &     |
|  Uploader (Python CLI)   |
+------------+-------------+
|
| HTTP POST (JSON)
v
+--------------------------+
|    n8n Webhook Node      |
+------------+-------------+
|
+-----------------------+
|                       |
v                       v
+------------+------------+  +-------+------------------+
|      Google Sheets       |  |      MySQL Database      |
|    (Live Attendance)    |  |     (smartattendance)  |
+-------------------------+  +-------+------------------+
^
| SQL Query (Daily Cron)
v
+-------+------------------+
|    n8n Daily Trigger     |
+-------+------------------+
|
| Triggers Call (CLI Args)
v
+-------+------------------+
|  AI Voice Agent System   |
|    (voice_agent.py)      |
+--------------------------+
