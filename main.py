from flask import Flask, request
import json
import os
import random
import string

app = Flask(__name__)

ADMIN_KEY = "WALKSAFE2024SECRET"  # Change this!
DB_FILE = "/tmp/codes.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"codes": {}}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

def generate_code():
    p1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    p2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{p1}-{p2}"

# Public: Check code
@app.route('/check/<code>')
def check(code):
    code = code.upper().strip()
    db = load_db()
    if code not in db["codes"]:
        return "INVALID"
    if db["codes"][code]["status"] == "used":
        return "ALREADY_USED"
    db["codes"][code]["status"] = "used"
    save_db(db)
    return "VALID"

# Secret: Generate new code
@app.route('/admin/generate')
def admin_generate():
    key = request.args.get('key')
    if key != ADMIN_KEY:
        return "UNAUTHORIZED"
    
    db = load_db()
    code = generate_code()
    while code in db["codes"]:
        code = generate_code()
    
    db["codes"][code] = {"status": "unused"}
    save_db(db)
    
    return f"CODE:{code}"

# Secret: List unused codes
@app.route('/admin/list')
def admin_list():
    key = request.args.get('key')
    if key != ADMIN_KEY:
        return "UNAUTHORIZED"
    
    db = load_db()
    unused = [c for c, d in db["codes"].items() if d["status"] == "unused"]
    return f"UNUSED:{len(unused)}:" + ",".join(unused[:20])

@app.route('/')
def home():
    return "WalkSafe API OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
