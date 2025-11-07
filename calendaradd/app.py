from flask import Flask, request, render_template, jsonify
from datetime import datetime
import json, os

app = Flask(__name__)

EVENTS_FILE = "events.json"
ICS_FILE = "netleader.ics"

def load_events():
    if not os.path.exists(EVENTS_FILE):
        return []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_events(events):
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    generate_ics(events)

def generate_ics(events):
    ics = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SetVlast//Calendar//RU",
        "CALSCALE:GREGORIAN"
    ]
    for e in events:
        ics += [
            "BEGIN:VEVENT",
            f"UID:{e['uid']}@setvlast",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{datetime.strptime(e['start'], '%Y-%m-%dT%H:%M').strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{datetime.strptime(e['end'], '%Y-%m-%dT%H:%M').strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{e['summary']}",
        ]
        if e.get("description"):
            ics.append(f"DESCRIPTION:{e['description']}")
        if e.get("location"):
            ics.append(f"LOCATION:{e['location']}")
        ics.append("END:VEVENT")
    ics.append("END:VCALENDAR")

    with open(ICS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(ics))

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/add", methods=["POST"])
def add_event():
    data = request.json
    events = load_events()
    new_event = {
        "uid": f"event-{len(events)+1}",
        "summary": data["summary"],
        "description": data.get("description", ""),
        "location": data.get("location", ""),
        "start": data["start"],
        "end": data["end"]
    }
    events.append(new_event)
    save_events(events)
    return jsonify({"status": "ok"})

@app.route("/calendar.ics")
def serve_ics():
    return app.send_static_file("../netleader.ics")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
