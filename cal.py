from tkinter import *
from tkinter import messagebox as msg
from typing import Dict, Optional

# --- Grade Boundaries ---
GRADE_BOUNDARIES = {
    'A': 90,
    'B': 80,
    'C': 70,
    'D': 60,
    'F': 0,
}

# --- Data Storage ---
# Stores all student records: {name: {'marks': {module: mark, ...}, 'average': float, 'grade': str}}
student_records = {}
current_student_marks = {}
current_student_name = ""


# --- Core Logic Functions (Adapted from console code) ---

def get_grade(average_score: Optional[float]) -> str:
    """Returns a letter grade based on the average score."""
    if average_score is None:
        return "N/A"
    avg = float(average_score)

    if avg > 100: return "A+"
    if avg < 0: return "F"

    # Iterate boundaries from highest to lowest
    for grade, lower in sorted(GRADE_BOUNDARIES.items(), key=lambda x: x[1], reverse=True):
        if avg >= lower:
            return grade
    return "N/A"

def calculate_average(marks: Dict[str, float]) -> float:
    """Calculates average score from a mapping of module->mark."""
    if not marks:
        return 0.0
    total = sum(float(v) for v in marks.values())
    return total / len(marks)


# --- GUI Logic Functions ---

def update_summary_list():
    """Updates the Listbox with the comprehensive summary report."""
    summaryList.delete(1.0, END) # Clear content, keeping header

    if not student_records:
        summaryList.insert(END, "\nNo student data entered yet.")
        return
        
    # Header
    header = f"{'Student':<15}{'Modules':<10}{'Average':<10}{'Grade':<8}\n"
    summaryList.insert(END, header, 'header')
    summaryList.insert(END, "-" * 45 + "\n", 'separator')


    for name, data in student_records.items():
        avg = data['average']
        grade = data['grade']
        modules = len(data['marks'])
        
        # Determine tag for coloring the grade
        if grade in ['A', 'A+']: tag = 'high_grade'
        elif grade in ['B', 'C']: tag = 'mid_grade'
        else: tag = 'low_grade'
        
        line = f"{name:<15}{modules:<10}{avg:<10.2f}{grade:<8}\n"
        summaryList.insert(END, line)
        summaryList.tag_add(tag, summaryList.index(f"end-1c linestart + {len(line.split()[3])} chars"), summaryList.index(f"end-1c lineend"))
    
    # Add grading scale below the main data
    summaryList.insert(END, "\n" + "=" * 45 + "\n", 'separator')
    summaryList.insert(END, "Grading Scale:\n", 'separator')
    sorted_boundaries = sorted(GRADE_BOUNDARIES.items(), key=lambda x: x[1], reverse=True)
    for i, (g, lb) in enumerate(sorted_boundaries):
        if i == 0: upper = 100
        else: upper = sorted_boundaries[i-1][1] - 1
        summaryList.insert(END, f"   {g}: {lb} - {upper}\n")

def clear_module_fields():
    """Clears the module name and mark fields."""
    txtModule.delete(0, END)
    txtMark.delete(0, END)

def clear_all_fields():
    """Clears all input fields and resets the session."""
    global current_student_marks, current_student_name
    txtName.delete(0, END)
    clear_module_fields()
    
    current_student_marks = {}
    current_student_name = ""
    lblCurrentStudent.config(text="Student: N/A | Modules: 0")
    lblModuleList.config(text="Current Modules: {}")

def start_new_student_session():
    """Starts a new student session or confirms the name."""
    global current_student_name, current_student_marks
    
    name = txtName.get().strip()
    if not name:
        msg.showerror("Input Error", "Please enter the student's name first.")
        return

    # If the name has changed, reset the marks list
    if name != current_student_name:
        current_student_marks = {}
        clear_module_fields()
        
        # Updated to display new list of keys
        module_keys_display = ", ".join(current_student_marks.keys())
        lblModuleList.config(text=f"Current Modules: {module_keys_display}")
        
        msg.showinfo("Session Started", f"Starting module entry for {name}.")
    
    current_student_name = name
    lblCurrentStudent.config(text=f"Student: {name} | Modules: {len(current_student_marks)}")

def add_module_mark():
    """Adds a validated module mark to the current student's record."""
    global current_student_marks
    
    if not current_student_name:
        msg.showerror("Error", "Please click '1. Start New Student / Confirm Name' first.")
        return

    module = txtModule.get().strip()
    mark_input = txtMark.get().strip()

    if not module or not mark_input:
        msg.showerror("Input Error", "Module name and Mark cannot be empty.")
        return
    
    # Validation Logic
    try:
        mark = float(mark_input)
    except ValueError:
        msg.showerror("Input Error", "Mark must be a numeric value.")
        return

    if not (0 <= mark <= 100):
        msg.showerror("Input Error", "Mark must be between 0 and 100.")
        return

    # Add/Overwrite Mark
    if module in current_student_marks:
        msg.showwarning("Warning", f"Module '{module}' updated. Mark overwritten from {current_student_marks[module]} to {mark}.")

    current_student_marks[module] = mark
    clear_module_fields()
    
    # --- CORRECTION: Change display format to comma-separated string ---
    module_keys_display = ", ".join(current_student_marks.keys())
    
    # Update status labels
    lblCurrentStudent.config(text=f"Student: {current_student_name} | Modules: {len(current_student_marks)}")
    lblModuleList.config(text=f"Current Modules: {module_keys_display}")


def finalize_student():
    """Calculates the average and grade, saves the record, and resets input."""
    global student_records, current_student_name, current_student_marks

    if not current_student_name:
        msg.showerror("Error", "No student session started.")
        return
        
    if not current_student_marks:
        msg.showerror("Error", "Please add at least one module mark.")
        return
        
    # Calculate Results
    avg = calculate_average(current_student_marks)
    grade = get_grade(avg)
    
    # Save to records
    student_records[current_student_name] = {
        'marks': dict(current_student_marks), # Save a copy of the marks
        'average': avg,
        'grade': grade
    }
    
    msg.showinfo("Success", f"Record saved for {current_student_name}:\nAverage: {avg:.2f}, Grade: {grade}")

    # Reset input fields and start new session implicitly
    clear_all_fields()
    update_summary_list()

def view_live_report():
    """Displays the current student's calculated average and grade without saving."""
    if not current_student_name or not current_student_marks:
        msg.showwarning("Incomplete Data", "Start a student session and add at least one mark to view the live calculation.")
        return
        
    avg = calculate_average(current_student_marks)
    grade = get_grade(avg)
    
    # Display the result in a message box
    msg.showinfo(
        f"Live Grade for {current_student_name}",
        f"Average Score: {avg:.2f}\n"
        f"Assigned Grade: {grade}\n\n"
        "Note: This record has NOT been saved to the Final Summary Report yet."
    )
    # Also ensure the overall summary list is updated with saved records (if any)
    update_summary_list()


# --- Tkinter Setup ---
window = Tk()
window.title("Student Grade Calculator")
window.geometry("1200x650")
window.configure(bg="#0d0d0d") # Dark theme
window.resizable(False, False)

# Header Label
lab = Label(window, text="Student Grade Calculator: Data Processor",
            bg="#1a1a1a", fg="lightgreen", font=("Arial", 18, "bold"), height=1, width=80, relief="ridge") # Reduced height
lab.pack(pady=10)

# Main Content Frames
frmLeft = Frame(window, bd=5, bg="#121212", padx=20, pady=10) # Reduced pady
frmLeft.pack(side=LEFT, padx=30, pady=0, fill="y")

frmRight = Frame(window, bd=5, bg="#1e1e1e", padx=10, pady=10)
frmRight.pack(side=LEFT, padx=20, pady=0, fill="both", expand=True)


# --- Left Frame: Input and Control ---

# Current Student Status
lblCurrentStudent = Label(frmLeft, text="Student: N/A | Modules: 0", 
                        font=("Arial", 13, "bold"), bg="#2a2a2a", fg="#f0f0f0", width=30, height=1, relief="groove") # Reduced height/font
lblCurrentStudent.pack(pady=(0, 10))


# Helper function for input fields
def create_label_entry(text, frame, label_bg, label_fg):
    Label(frame, text=text, font=("Arial", 12, "bold"), # Reduced font size
          bg=label_bg, fg=label_fg, width=15, height=1).pack(pady=(2, 0)) # Reduced padding
    entry = Entry(frame, font=("Arial", 14), width=25, bd=3, relief="ridge", 
                  bg="#262626", fg="lightblue", insertbackground="white")
    entry.pack(pady=3) # Reduced padding
    return entry

# Student Name Input
txtName = create_label_entry("Student Name", frmLeft, "#2a2a2a", "lightgreen")

# Start/Confirm Student Button
btStart = Button(frmLeft, text="1. Start New Student / Confirm Name", height=1, width=30, # Reduced height
                 font=("Arial", 11, "bold"), bg="#008000", fg="white", 
                 relief="raised", command=start_new_student_session)
btStart.pack(pady=(5, 10)) # Reduced padding


# Module Input
txtModule = create_label_entry("Module Name", frmLeft, "#2a2a2a", "#fff")
txtMark = create_label_entry("Mark (0-100)", frmLeft, "#2a2a2a", "#fff")


# Add Module Button
btAddModule = Button(frmLeft, text="2. Add Module Mark", height=1, width=30, # Reduced height
                     font=("Arial", 11, "bold"), bg="#006400", fg="white", 
                     relief="raised", command=add_module_mark)
btAddModule.pack(pady=(5, 5)) # Reduced padding


# Current Modules List Label
lblModuleList = Label(frmLeft, text="Current Modules: {}", 
                    font=("Arial", 9), bg="#121212", fg="#ffcc66", width=35, height=2, wraplength=300) # Reduced height/font
lblModuleList.pack(pady=3) # Reduced padding


# Clear button moved up
btClearAll = Button(frmLeft, text="Clear All Fields", height=1, width=30, 
                    font=("Arial", 10, "bold"), bg="#444444", fg="white", 
                    relief="raised", command=clear_all_fields)
btClearAll.pack(pady=(10, 3)) 

# Finalize button (Button 3) is now definitely visible
btFinalize = Button(frmLeft, text="3. FINALISE STUDENT & SAVE RECORD", height=1, width=30, 
                    font=("Arial", 11, "bold"), bg="#b30000", fg="white", 
                    relief="raised", command=finalize_student)
btFinalize.pack(pady=(3, 3))


# New Button: View Live Report (Button 4)
btLiveView = Button(frmLeft, text="4. VIEW LIVE REPORT (Unsaved)", height=1, width=30, 
                    font=("Arial", 10, "bold"), bg="#4a4a00", fg="white", 
                    relief="raised", command=view_live_report)
btLiveView.pack(pady=(3, 3))


# --- Right Frame: Summary Report ---
lblReportTitle = Label(frmRight, text="FINAL GRADE SUMMARY REPORT", 
                       font=("Arial", 16, "bold"), bg="#1e1e1e", fg="lightblue")
lblReportTitle.pack(pady=10)

# Summary Display (Using Text widget for multi-line formatting and tags)
summaryList = Text(frmRight, height=30, width=90, font=("Consolas", 12), 
                   bg="#262626", fg="#f0f0f0", relief="groove", bd=5)
summaryList.pack(pady=5, padx=5, fill="both", expand=True)

# Define Text tags for coloring grades
summaryList.tag_configure('header', font=('Consolas', 12, 'bold'), foreground='yellow')
summaryList.tag_configure('separator', foreground='gray')
summaryList.tag_configure('high_grade', foreground='#00ff00') # Bright green for A/A+
summaryList.tag_configure('mid_grade', foreground='#ffcc66')  # Orange for B/C
summaryList.tag_configure('low_grade', foreground='#ff0000')  # Red for D/F

# Initial call to populate list with header
update_summary_list()

window.mainloop()
  

