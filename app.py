from flask import Flask, request
import sqlite3
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
print("Gemini API key loaded:", bool(api_key))

app = Flask(__name__)
def create_database():
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL,
            description TEXT
        )
    """)
    cursor.execute("PRAGMA table_info(claims)")
    columns = [column[1] for column in cursor.fetchall()]

    if "description" not in columns:
        cursor.execute("ALTER TABLE claims ADD COLUMN description TEXT")

    conn.commit()
    conn.close()

create_database()

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Insurance Claims</title>
        <style>
            body {
                font-family: Arial;
                background: linear-gradient(135deg, #667eea, #764ba2);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
            }

            .card {
                background: white;
                padding: 40px;
                border-radius: 20px;
                width: 350px;
                box-shadow: 0 10px 30px #33333355;
            }

            h1 {
                color: #6045a5;
                text-align: center;
            }

            p {
                color: #666;
                text-align: center;
            }

            label {
                font-weight: bold;
                color: #444;
            }

            input {
                width: 100%;
                padding: 12px 0;
                margin: 10px 0 20px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 16px;
            }
            textarea {
                 width: 100%;
                 box-sizing: border-box;
                 min-height: 100px;
                 padding: 12px;
                 margin: 10px 0 20px;
                 border: 1px solid #ccc;
                 border-radius: 8px;
                 font-size: 16px;
                 font-family: Arial;
}

            button {
                width: 100%;
                padding: 14px;
                background: #6c5ce7;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover {
                background: #4834d4;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Smart Insurance Claims</h1>
            <p>Submit your insurance claim below.</p>

            <form action="/claim" method="post">
                <label>Your Name</label>
                <input type="text" name="name" required>

                <label>Claim Amount (₹)</label>
                <input type="number" name="amount" min="1" required>

                <label>Claim Description</label>
                <textarea name="description" placeholder="Describe what happened..." required></textarea>

                <button type="submit">Submit Claim</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/claim", methods=["POST"])
def claim():
    name = request.form["name"]
    amount = request.form["amount"]
    description = request.form["description"]
    
    response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=f"""
    You are an insurance claim review assistant.

    Analyze this claim description:
    {description}

    Give the result in this format:

    1. Claim Summary:
    Summarize the incident in 1-2 sentences.

    2. Important Information:
    List the key details provided.

    3. Missing Information:
    Mention details needed for further review.

    4. Potential Concerns:
    Identify inconsistencies or information that may need verification.
    Do not assume fraud without evidence.

    5. Suggested Next Steps:
    List documents or information that may be required.

    Important:
    Do not approve or reject the claim.
    Do not invent facts.
    If information is missing, clearly say so.
    """
)
    ai_analysis = response.text
    ai_analysis = ai_analysis.replace("\n", "<br>")
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO claims (name, amount, description) VALUES (?, ?, ?)",
    (name, amount, description)
)


    conn.commit()
    conn.close()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            font-family: Arial;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }}
        .card {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px #33333344;
        }}
        a {{
            display: inline-block;
            margin-top: 15px;
            color: white;
            background: #764ba2;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
        }}
        
        .ai-report {{
             background: #ffffff;
             padding: 25px;
             border-radius: 15px;
             border: 1px solid #eeeeff
             text-align: left;
             line-height: 2;
             color: #333333;
             box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
             margin-top: 20px;
             background:#ffffff;
             white-space: normal;
             overflow-wrap: anywhere;
         }}

       .ai-report h3 {{
           color: #6655cc;
           border-bottom: 2px solid #eeeeff;
           padding-bottom: 8px;
         }}

       .ai-report p {{
         margin-bottom: 12px;
       }}

    </style>
    </head>
    <body>
        <div class="card">
            <h1>Claim Received! 🎉</h1>
            <p>Name: {name}</p>
            <p>Amount: ₹{amount}</p>
            <h2>Gemini AI Claim Report</h2>
            <div class="ai-report">{ai_analysis.replace(chr(10), '<br>')}</div>
        </div>
    </body>
    </html>
    """
@app.route("/claims")
def view_claims():
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()
    search = request.args.get("search", "")

    cursor.execute(
    "SELECT * FROM claims WHERE name LIKE ?",
    ("%" + search + "%",)
    )
    claims = cursor.fetchall()
    total_claims = len(claims)
    total_amount = sum(float(c[2]) for c in claims)
    conn.close()

    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Insurance Claims</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea, #764ba2);
                padding: 30px;
                margin: 0;
            }}
            .card {{
                background: white;
                max-width: 900px;
                margin: 30px auto;
                padding: 30px;
                border-radius: 18px;
                box-shadow: 0 10px 30px #33333344;
            }}
            h1 {{
                color: #6655cc;
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 14px;
                border-bottom: 1px solid #dddddd;
                text-align: left;
            }}
            th {{
                background: #764ba2;
                color: white;
            }}
            tr:nth-child(even) {{
                background: #f4f2ff;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                background: #764ba2;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>All Insurance Claims</h1>
            <div style="display:flex; gap:20px; margin:20px 0;">
        <div style="background:#f3e8ff; padding:20px; border-radius:10px;">
        <h3>Total Claims</h3>
        <h2>{total_claims}</h2>
       </div>
       <div style="background:#e8eaff; padding:20px; border-radius:10px;">
        <h3>Total Claim Amount</h3>
        <h2>₹{total_amount:,.2f}</h2>
    </div>
</div>
            <form action="/claims" method="get">
            <input type="text" name="search" placeholder="Search by name" style="padding:10px; width:250px; border:1px solid #ccc; border-radius:8px;">
            <button type="submit" style="padding:10px 20px; background:#764ba2; color:white; border:none; border-radius:8px; cursor:pointer;">Search</button>
            </form>
            <table style="width:100%; border-collapse:collapse; margin-top:20px;">
                <tr>
                    <th>Claim ID</th>
                    <th>Name</th>
                    <th>Amount</th>
                    <th>Description</th>
                    <th>Action</th>
                    <th>Edit</th>
                </tr>
                
                {"".join(f'<tr><td>{c[0]}</td><td>{c[1]}</td><td>₹{c[2]:,.2f}</td><td>{c[3] or ""}</td><td><form action="/delete/{c[0]}" method="post" onsubmit="return confirm(\'Delete this claim?\')"><button type="submit">Delete</button></form></td><td><a href="/edit/{c[0]}"><button type="button">Edit</button></a></td></tr>' for c in claims)}

            </table>
            <a href="/">Go back</a>
        </div>
    </body>
    </html>
    """
@app.route("/delete/<int:claim_id>", methods=["POST"])
def delete_claim(claim_id):
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
    conn.commit()
    conn.close()
    return '<p>Claim deleted successfully!</p><a href="/claims">Go back</a>'

@app.route("/edit/<int:claim_id>", methods=["GET", "POST"])
def edit_claim(claim_id):
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        amount = request.form["amount"]
        description = request.form["description"]

        cursor.execute(
            "UPDATE claims SET name = ?, amount = ?, description = ? WHERE id = ?",
            (name, amount, description, claim_id)
        )
        conn.commit()
        conn.close()
        return '<p>Claim updated successfully!</p><a href="/claims">Back to Claims</a>'

    cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
    claim = cursor.fetchone()
    conn.close()

    if claim is None:
        return "Claim not found", 404

    return f"""
    <h1>Edit Insurance Claim</h1>
    <form method="post">
        <label>Name</label>
        <input type="text" name="name" value="{claim[1]}" required>
        <br><br>
        <label>Amount</label>
        <input type="number" name="amount" value="{claim[2]}" min="1" required>
        <br><br>
        <label>Description</label>
        <textarea name="description" required>{claim[3] or ""}</textarea>
        <br><br>
        <button type="submit">Save Changes</button>
    </form>
    <a href="/claims">Cancel</a>
    """


if __name__ == "__main__":
    app.run(debug=True)