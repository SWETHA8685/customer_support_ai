import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# FILE
# ============================================================

INPUT_FILE = "data/golden/golden_set.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

# Make sure these columns exist
if "intent" not in df.columns:
    df["intent"] = ""

if "decision" not in df.columns:
    df["decision"] = ""

# IMPORTANT:
# Convert empty columns to object/string-compatible columns.
# This prevents:
# TypeError: Invalid value 'delivery_issue' for dtype 'float64'
df["intent"] = df["intent"].fillna("").astype(object)
df["decision"] = df["decision"].fillna("").astype(object)


# ============================================================
# INTENT OPTIONS
# ============================================================

INTENTS = [
    "delivery_issue",
    "delivery_not_received",
    "order_issue",
    "refund_return",
    "payment_issue",
    "prime_membership",
    "account_issue",
    "product_issue",
    "service_complaint",
]


# ============================================================
# DECISION OPTIONS
# ============================================================

DECISIONS = [
    "auto_handle",
    "escalate",
]


# ============================================================
# CURRENT EXAMPLE
# ============================================================

current_index = 0


# ============================================================
# LOAD CURRENT EXAMPLE
# ============================================================

def load_example():

    # Clear old text
    message_box.delete("1.0", tk.END)
    response_box.delete("1.0", tk.END)

    # Get current row
    row = df.iloc[current_index]

    # Customer message
    customer_message = row["customer_message"]

    # Historical response
    agent_response = row["agent_response"]

    # Display customer message
    message_box.insert(
        tk.END,
        str(customer_message)
    )

    # Display agent response
    response_box.insert(
        tk.END,
        str(agent_response)
    )

    # Update progress
    progress_label.config(
        text=f"Example {current_index + 1} / {len(df)}"
    )

    # Load previously saved intent
    saved_intent = row["intent"]

    if pd.isna(saved_intent) or str(saved_intent).strip() == "":
        intent_var.set("")
    else:
        intent_var.set(str(saved_intent))

    # Load previously saved decision
    saved_decision = row["decision"]

    if pd.isna(saved_decision) or str(saved_decision).strip() == "":
        decision_var.set("")
    else:
        decision_var.set(str(saved_decision))


# ============================================================
# SAVE CURRENT EXAMPLE
# ============================================================

def save_current():

    intent = intent_var.get().strip()
    decision = decision_var.get().strip()

    # Check intent
    if not intent:

        messagebox.showwarning(
            "Missing Intent",
            "Please select an intent."
        )

        return False

    # Check decision
    if not decision:

        messagebox.showwarning(
            "Missing Decision",
            "Please select Auto Handle or Escalate."
        )

        return False

    # Save values
    df.at[current_index, "intent"] = intent
    df.at[current_index, "decision"] = decision

    # Save CSV
    df.to_csv(
        INPUT_FILE,
        index=False
    )

    return True


# ============================================================
# SAVE BUTTON
# ============================================================

def save_button():

    success = save_current()

    if success:

        messagebox.showinfo(
            "Saved",
            f"Example {current_index + 1} saved successfully."
        )


# ============================================================
# NEXT BUTTON
# ============================================================

def next_example():

    global current_index

    # Save before moving
    success = save_current()

    if not success:
        return

    # Move to next example
    if current_index < len(df) - 1:

        current_index += 1

        load_example()

    else:

        messagebox.showinfo(
            "Completed",
            "You have labeled all 200 examples!"
        )


# ============================================================
# PREVIOUS BUTTON
# ============================================================

def previous_example():

    global current_index

    if current_index > 0:

        current_index -= 1

        load_example()

    else:

        messagebox.showinfo(
            "First Example",
            "You are already on the first example."
        )


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Hiver Golden Set Labeling Tool"
)

root.geometry(
    "1000x750"
)

root.minsize(
    800,
    600
)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="Hiver AmazonHelp Golden Set",
    font=("Arial", 20, "bold")
)

title.pack(
    pady=10
)


# ============================================================
# PROGRESS
# ============================================================

progress_label = tk.Label(
    root,
    text="",
    font=("Arial", 12)
)

progress_label.pack(
    pady=5
)


# ============================================================
# CUSTOMER MESSAGE
# ============================================================

customer_label = tk.Label(
    root,
    text="Customer Message",
    font=("Arial", 12, "bold")
)

customer_label.pack(
    anchor="w",
    padx=20
)


message_box = tk.Text(
    root,
    height=8,
    wrap="word",
    font=("Arial", 11)
)

message_box.pack(
    fill="x",
    padx=20,
    pady=5
)


# ============================================================
# AGENT RESPONSE
# ============================================================

response_label = tk.Label(
    root,
    text="Historical AmazonHelp Response",
    font=("Arial", 12, "bold")
)

response_label.pack(
    anchor="w",
    padx=20
)


response_box = tk.Text(
    root,
    height=8,
    wrap="word",
    font=("Arial", 11)
)

response_box.pack(
    fill="x",
    padx=20,
    pady=5
)


# ============================================================
# SELECTION FRAME
# ============================================================

selection_frame = tk.Frame(
    root
)

selection_frame.pack(
    pady=15
)


# ============================================================
# INTENT
# ============================================================

intent_label = tk.Label(
    selection_frame,
    text="Intent:",
    font=("Arial", 11, "bold")
)

intent_label.grid(
    row=0,
    column=0,
    padx=10,
    pady=10
)


intent_var = tk.StringVar()


intent_dropdown = ttk.Combobox(
    selection_frame,
    textvariable=intent_var,
    values=INTENTS,
    state="readonly",
    width=32
)

intent_dropdown.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)


# ============================================================
# DECISION
# ============================================================

decision_label = tk.Label(
    selection_frame,
    text="Decision:",
    font=("Arial", 11, "bold")
)

decision_label.grid(
    row=1,
    column=0,
    padx=10,
    pady=10
)


decision_var = tk.StringVar()


decision_dropdown = ttk.Combobox(
    selection_frame,
    textvariable=decision_var,
    values=DECISIONS,
    state="readonly",
    width=32
)

decision_dropdown.grid(
    row=1,
    column=1,
    padx=10,
    pady=10
)


# ============================================================
# BUTTON FRAME
# ============================================================

button_frame = tk.Frame(
    root
)

button_frame.pack(
    pady=20
)


# ============================================================
# PREVIOUS
# ============================================================

previous_button = tk.Button(
    button_frame,
    text="Previous",
    width=15,
    height=2,
    command=previous_example
)

previous_button.grid(
    row=0,
    column=0,
    padx=10
)


# ============================================================
# SAVE
# ============================================================

save_button_widget = tk.Button(
    button_frame,
    text="Save",
    width=15,
    height=2,
    command=save_button
)

save_button_widget.grid(
    row=0,
    column=1,
    padx=10
)


# ============================================================
# NEXT
# ============================================================

next_button = tk.Button(
    button_frame,
    text="Next",
    width=15,
    height=2,
    command=next_example
)

next_button.grid(
    row=0,
    column=2,
    padx=10
)


# ============================================================
# LOAD FIRST EXAMPLE
# ============================================================

load_example()


# ============================================================
# START
# ============================================================

root.mainloop()