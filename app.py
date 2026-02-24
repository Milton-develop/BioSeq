from flask import Flask, render_template, request, redirect, url_for, session
from analysis import clean_sequence, sequence_length, gc_content, translate_dna, is_valid_dna, reverse_complement, get_chem_profile
import threading, time, os
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_only")

# --- In-memory user storage ---
users = {}  # format: {username: password}

# --- DNA processing globals ---
latest_results = None
latest_error = None
sequence_history = []

# --- Watch folder ---
WATCH_FOLDER = "./lab_exports"
os.makedirs(WATCH_FOLDER, exist_ok=True)

# --- File Watcher ---
class DNAFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        global latest_results, latest_error, sequence_history
        if event.is_directory or not event.src_path.endswith((".txt", ".csv")):
            return
        try:
            with open(event.src_path, "r") as f:
                raw_seq = f.read().strip()

            seq = clean_sequence(raw_seq)
            filename_or_manual = os.path.basename(event.src_path)

            if not seq:
                latest_error = f"No DNA sequence found in {filename_or_manual}"
                latest_results = None
                return
            if not is_valid_dna(seq):
                latest_error = f"Invalid DNA sequence in {filename_or_manual}"
                latest_results = None
                return

            protein_data = translate_dna(seq)
            rev_comp_seq = reverse_complement(seq)
            complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
            comp_pairs = [{"original": base, "complement": complement_map.get(base, base)} for base in seq]
            rev_comp_pairs = comp_pairs[::-1]
            protein_string = "".join([item['name'][0] if item['name'] != 'STOP' else '*' for item in protein_data])

            latest_results = {
                "length": sequence_length(seq),
                "gc": gc_content(seq),
                "protein_length": len(protein_data),
                "protein": protein_data,
                "protein_str": protein_string,
                "rev_comp": rev_comp_seq,
                "rev_comp_pairs": rev_comp_pairs,
                "source": filename_or_manual
            }

            sequence_history.append({
                "file": filename_or_manual,
                "results": latest_results
            })

            latest_error = None
            print(f"Processed sequence from {filename_or_manual}")

        except Exception as e:
            latest_error = f"Error processing file {os.path.basename(event.src_path)}: {str(e)}"
            latest_results = None

# def start_watcher():
#     observer = Observer()
#     observer.schedule(DNAFileHandler(), WATCH_FOLDER, recursive=False)
#     observer.start()
#     print(f"Watching folder '{WATCH_FOLDER}' for new DNA files...")
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()

# threading.Thread(target=start_watcher, daemon=True).start()

# --- Login route ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error = "Please enter both username and password."
            return render_template("login.html", error=error)

        # Validate credentials
        if username not in users or users[username] != password:
            error = "Invalid username or password."
            return render_template("login.html", error=error)

        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for("home"))

    return render_template("login.html")

# --- Signup route ---
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

# If email was part then "or not email" will be needed in code line 119
    if not username or not password or not confirm_password:  
        error = "Please fill in all fields."
        return render_template("login.html", error=error) 

    if password != confirm_password:
        error = "Passwords do not match."
        return render_template("login.html", error=error)

    if username in users:
        error = "Username already exists."
        return render_template("login.html", error=error)

    # Save user
    users[username] = password

    # Log in automatically
    session["logged_in"] = True
    session["username"] = username
    return redirect(url_for("home"))

# --- Logout ---
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
    return redirect(url_for("login"))

# --- Dashboard ---
@app.route("/", methods=["GET", "POST"])
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    global latest_results, latest_error, sequence_history

    if request.method == "POST":
        raw_seq = request.form.get("sequence", "")
        seq = clean_sequence(raw_seq)
        filename_or_manual = "Manual Input"

        if not seq:
            latest_error = "Please enter a DNA sequence."
            latest_results = None
        elif not is_valid_dna(seq):
            latest_error = "Invalid DNA sequence. Use only A, T, G, and C."
            latest_results = None
        else:
            protein_data = translate_dna(seq)
            rev_comp_seq = reverse_complement(seq)
            complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
            comp_pairs = [{"original": base, "complement": complement_map.get(base, base)} for base in seq]
            rev_comp_pairs = comp_pairs[::-1]
            protein_string = "".join([item['letter'] for item in protein_data])
            chem_profile = get_chem_profile(protein_data)

            latest_results = {
                "length": sequence_length(seq),
                "gc": gc_content(seq),
                "protein_length": len(protein_data),
                "protein": protein_data,
                "chem_profile": chem_profile,
                "protein_str": protein_string,
                "rev_comp": rev_comp_seq,
                "rev_comp_pairs": rev_comp_pairs,
                "source": filename_or_manual
            }

            sequence_history.append({
                "file": filename_or_manual,
                "results": latest_results
            })

            latest_error = None

    return render_template(
        "index.html",
        results=latest_results,
        error=latest_error,
        username=session.get("username")
    )

# --- History ---
@app.route("/history")
def history():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    last_sequences = sequence_history[-10:][::-1]
    return render_template("history.html", history=last_sequences, username=session.get("username"))

# --- About ---
@app.route("/about")
def about():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("about.html", username=session.get("username"))

# --- Account ---
@app.route("/account")
def account():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    total_analyses = len(sequence_history)
    recent_analyses = sequence_history[-5:][::-1]
    return render_template("account.html", username=session.get("username"), institution=session.get("institution"), role=session.get("role"), total_analyses=total_analyses,
        recent_analyses=recent_analyses)
    
@app.route("/clear-history", methods=["POST"])
def clear_history():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    global sequence_history, latest_results, latest_error

    sequence_history.clear()
    latest_results = None
    latest_error = None

    return redirect(url_for("account", msg= "Analysis history successfully cleared."))
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
