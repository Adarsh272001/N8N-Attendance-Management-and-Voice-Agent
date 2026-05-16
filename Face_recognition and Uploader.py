import cv2
import os
import requests
import time
from deepface import DeepFace

# --- CONFIGURATION ---
# Replace with your actual n8n webhook URL
N8N_WEBHOOK_URL = "https://unperpendicularly-unpetticoated-adrianne.ngrok-free.dev/webhook-test/60d26f50-dbfa-47d6-95f7-e0e2c8e9fc0d"
EMPLOYEE_DB_PATH = "employees"
MONITORING_DURATION_SECONDS = 30 

def start_attendance_session():
    cap = cv2.VideoCapture(0)
    
    # 1. Create master list using filenames as UIDs (e.g., '25MDA10053')
    # We remove the extension but keep the exact casing for the DB
    all_uids = [os.path.splitext(f)[0] for f in os.listdir(EMPLOYEE_DB_PATH) if f.endswith(('.jpg', '.png'))]
    
    found_uids = set()
    start_time = time.time()
    last_processed_time = 0

    print(f"--- Session Started ---")
    print(f"Monitoring UIDs: {all_uids}")

    while True:
        ret, frame = cap.read()
        if not ret: break

        elapsed = time.time() - start_time
        remaining = max(0, int(MONITORING_DURATION_SECONDS - elapsed))
        
        # Display Info
        cv2.putText(frame, f"Scanning... {remaining}s left", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Attendance Monitor', frame)

        # 2. Recognition Phase
        if elapsed < MONITORING_DURATION_SECONDS:
            if time.time() - last_processed_time > 2: # Scan every 2 seconds
                temp_path = "live_capture.jpg"
                cv2.imwrite(temp_path, frame)
                
                try:
                    # Search for the face in the employees folder
                    matches = DeepFace.find(img_path=temp_path, db_path=EMPLOYEE_DB_PATH, 
                                            enforce_detection=False, detector_backend='opencv', silent=True)
                    
                    if len(matches) > 0 and not matches[0].empty:
                        path = matches[0].iloc[0]['identity']
                        uid = os.path.splitext(os.path.basename(path))[0]
                        
                        if uid not in found_uids:
                            print(f"✅ Found {uid}: Marking Present")
                            send_to_n8n(uid, 1) 
                            found_uids.add(uid)
                except Exception as e:
                    pass 
                last_processed_time = time.time()

        # 3. Bulk Absence Sweep
        else:
            print("\n--- Time Up. Logging Absentees ---")
            absentees = [u for u in all_uids if u not in found_uids]
            
            for u in absentees:
                print(f"❌ {u}: Marking Absent")
                send_to_n8n(u, 0)
            
            print("--- All Data Sent to n8n ---")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

def send_to_n8n(uid, status):
    """
    Sends data to n8n. 
    Keys match the 'AttendanceLogs' table columns: uid, status, log_date
    """
    payload = {
        "uid": uid, 
        "status": status, 
        "log_date": time.strftime('%Y-%m-%d')
    }
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ n8n returned error: {response.status_code}")
    except Exception as e:
        print(f"❌ Network Error for {uid}: {e}")

if __name__ == "__main__":
    start_attendance_session()