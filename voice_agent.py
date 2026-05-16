from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Global storage for the n8n trigger
latest_alert = {"script": "", "processed": True}

# ==========================================
# 🧠 LOCAL AI AGENT LOGIC
# ==========================================
def classify_leave_reason(student_text):
    text = student_text.lower()
    medical = ['fever', 'sick', 'doctor', 'ill', 'headache', 'hospital', 'injury', 'pain', 'medical', 'health', 'unwell']
    duty = ['fest', 'event', 'sports', 'competition', 'hackathon', 'represent', 'official', 'duty', 'tournament', 'ncc', 'nss']

    if any(word in text for word in medical):
        return "Please apply for Medical Leave on CUIMS."
    elif any(word in text for word in duty):
        return "Please apply for Duty Leave on CUIMS."
    else:
        return "I can't help with that. Please contact your coordinator or administrator."

# ==========================================
# 🖥️ FRONTEND (ALFRED-STYLE ARCHITECTURE)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CUIMS Assistant</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #121212; color: white; text-align: center; padding-top: 50px; }
        .container { border: 2px solid #00d4ff; padding: 30px; border-radius: 20px; display: inline-block; background: #1e1e1e; min-width: 400px; }
        #status-light { width: 15px; height: 15px; border-radius: 50%; background: #444; display: inline-block; margin-right: 10px; }
        .active { background: #00ff00 !important; box-shadow: 0 0 10px #00ff00; }
        .listening { background: #ff00ff !important; box-shadow: 0 0 15px #ff00ff; }
        .incoming { background: #f1c40f !important; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.3; } }
        #agent-text { color: #00d4ff; font-size: 1.4em; margin: 20px 0; min-height: 50px; }
        #student-text { color: #888; font-style: italic; }
        button { padding: 15px 30px; border: none; border-radius: 10px; font-size: 1.2em; font-weight: bold; cursor: pointer; }
        .btn-call { background: #2ecc71; color: white; display: none; margin: 0 auto; }
    </style>
</head>
<body>

<div class="container">
    <h1>CUIMS Agent</h1>
    <button id="init-btn" onclick="initSystem()">Initialize Agent</button>
    
    <div id="ui" style="display:none;">
        <p><span id="status-light"></span> Status: <span id="status-label">Standby</span></p>
        <button id="receive-btn" class="btn-call" onclick="handleCall()">📞 Receive Call</button>
        <div id="agent-text">Waiting for n8n trigger...</div>
        <div id="student-text">...</div>
    </div>
</div>

<script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN';
    let pendingScript = "";

    function initSystem() {
        document.getElementById('init-btn').style.display = 'none';
        document.getElementById('ui').style.display = 'block';
        document.getElementById('status-light').className = 'active';
        document.getElementById('status-label').innerText = "Online";
        setInterval(checkAlerts, 2000);
    }

    async function checkAlerts() {
        const res = await fetch('/get_alert');
        const data = await res.json();
        
        if (!data.processed && pendingScript === "") {
            pendingScript = data.script;
            document.getElementById('receive-btn').style.display = 'block';
            document.getElementById('status-light').className = 'incoming';
            document.getElementById('agent-text').innerText = "Incoming Alert Detected...";
        }
    }

    function speak(text, callback) {
        window.speechSynthesis.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.onend = () => { if(callback) callback(); };
        window.speechSynthesis.speak(msg);
        document.getElementById('agent-text').innerText = text;
    }

    async function handleCall() {
        document.getElementById('receive-btn').style.display = 'none';
        document.getElementById('status-light').className = 'active';
        
        // Speak n8n script then listen
        speak(pendingScript, () => {
            startListening();
        });

        await fetch('/mark_processed', {method: 'POST'});
        pendingScript = "";
    }

    function startListening() {
        document.getElementById('status-label').innerText = "Listening...";
        document.getElementById('status-light').className = 'listening';
        
        try {
            recognition.start();
            // 10 Second Safety Timeout
            setTimeout(() => { recognition.stop(); }, 10000);
        } catch(e) { console.error(e); }
    }

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('student-text').innerText = '"' + transcript + '"';
        
        const res = await fetch('/respond', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ response: transcript })
        });
        const data = await res.json();
        
        speak(data.reply); 
    };

    recognition.onend = () => {
        if (document.getElementById('status-label').innerText === "Listening...") {
            document.getElementById('status-light').className = 'active';
            document.getElementById('status-label').innerText = "Online";
        }
    };

    recognition.onerror = (event) => {
        if (event.error === 'no-speech') startListening(); // Retry if silence
    };
</script>
</body>
</html>
"""

# ==========================================
# 🌐 FLASK ENDPOINTS
# ==========================================
@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@app.route('/trigger', methods=['POST'])
def trigger():
    global latest_alert
    latest_alert = {"script": request.json.get('script', 'Hello student.'), "processed": False}
    return jsonify({"status": "OK"})

@app.route('/respond', methods=['POST'])
def respond():
    user_text = request.json.get('response', '')
    reply = classify_leave_reason(user_text)
    return jsonify({"reply": reply})

@app.route('/get_alert')
def get_alert(): return jsonify(latest_alert)

@app.route('/mark_processed', methods=['POST'])
def mark_processed():
    global latest_alert
    latest_alert["processed"] = True
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    app.run(port=5001)