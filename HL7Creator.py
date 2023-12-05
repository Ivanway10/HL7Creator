import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import Text, END, Checkbutton, IntVar
import sys
from io import StringIO

class HL7MessageGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("HL7 Message Generator")

        # Dropdown for segments
        segments_label = ttk.Label(root, text="Select Segment:")
        segments_label.grid(row=0, column=0, padx=10, pady=10)
        self.segments_var = tk.StringVar()
        self.segments_dropdown = ttk.Combobox(root, textvariable=self.segments_var, values=["MSH", "EVN", "PID", "IN1", "PV1","FT1","OCR","OBR"])
        self.segments_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.segments_dropdown.bind("<<ComboboxSelected>>", self.update_fields)

        # Scrollable frame for dynamic input fields
        self.fields_canvas = tk.Canvas(root)
        self.fields_frame = ttk.Frame(self.fields_canvas)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.fields_canvas.yview)
        self.fields_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.fields_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        self.scrollbar.grid(row=1, column=2, sticky="ns")
        self.fields_canvas.create_window((0, 0), window=self.fields_frame, anchor="nw", tags="self.fields_frame")

        self.message_text = Text(root, wrap="word", height=10, width=60)
        self.message_text.grid(row=2, column=0, padx=10, pady=5, columnspan=2)

        self.messages = []  # Lista para almacenar mensajes generados

       # Checklist for segments
        self.segments_checklist = {}
        self.create_checklist()

        # Generate Test Segment button
        self.generate_test_button = tk.Button(root, text="Generate Test Segment", command=self.generate_test_segment)
        self.generate_test_button.grid(row=6, column=0, pady=5, columnspan=2)

        self.generate_button = tk.Button(root, text="Generate Message", command=self.generate_hl7)
        self.generate_button.grid(row=4, column=0, pady=5, columnspan=2)

        self.save_button = tk.Button(root, text="Save to File", command=self.save_to_file)
        self.save_button.grid(row=5, column=0, pady=5, columnspan=2)

        self.console_redirector = ConsoleRedirector(self.message_text)

        # Redirigir la salida estándar de la consola hacia el widget Text
        sys.stdout = ConsoleRedirector(self.message_text)

        # Configure the scrollable region
        self.fields_frame.bind("<Configure>", self.on_frame_configure)
        self.fields_canvas.bind("<Configure>", self.on_canvas_configure)

        # Make the grid cells expandable
        for i in range(6):
            root.grid_rowconfigure(i, weight=1)
            root.grid_columnconfigure(i, weight=1)

    def update_fields(self, event):
        # Clear existing fields
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        segment = self.segments_var.get()
        # Fetch field names for the selected segment
        field_names = self.get_field_names_for_segment(segment)

        # Create input fields for each field in the segment
        for i, field_name in enumerate(field_names):
            label = ttk.Label(self.fields_frame, text=f"{field_name}:")
            label.grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.fields_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)

    def get_field_names_for_segment(self, segment):
        if segment == "MSH":
            return ["Segment Identifier", "Encoding characters", "Sending application", "Sending facility",
                    "Receiving application", "Receiving facility", "Date/Time of message", "Security", "Message type",
                    "Message control ID", "Processing ID", "Version ID", "Sequence number", "Continuation pointer",
                    "Accept acknowledgment type", "Application acknowledgment type", "Country code", "Character set",
                    "Principal language of message"]
        elif segment == "EVN":
            return ["Segment Identifier", "Event type code", "Recorded date/time", "Date/time planned event",
                    "Event reason code", "Operator ID", "Event occurred"]
        elif segment == "PID":
            return ["Segment Identifier", "Set ID", "Patient ID", "Patient identifier list", "Alternate patient ID",
                    "Patient name", "Mother's maiden name", "Date/Time of birthday", "Gender", "Patient Alias",
                    "Race", "Patient Address", "Country", "Phone number - Home", "Phone number - Business",
                    "Primary Language", "Marital status", "Religion", "Patient account number", "SSN number - Patient",
                    "Driver's license number - Patient", "Mother's identifier", "Ethnic group", "Birth place",
                    "Multiple birth indicator", "Birth order", "Citizenship", "Veterans military status", "Nationality",
                    "Patient death date and time", "Patient death indicator"]
        elif segment == "IN1":
            return ["Set ID IN1", "Insurance Plan ID", "Insurance Company ID", "Insurance Company Name",
                    "Policy Deductible", "Insured's ID Number"]
        elif segment == "PV1":
            return ["Segment Identifier", "Set Id", "Patient Class", "Assigned Patient Location", "Admission Type",
                    "Pre-Admit Number", "Prior Patient Location", "Attending Doctor", "Referring Doctor"]
        elif segment == "FT1":
            return ["Segment identifier","Set ID","Transaction ID","Transaction batch ID","Transaction date","Transaction posting date",
                    "Transaction type","Transaction code","Transaction description","Transaction description - alt","Transaction quantity",
                    "Transaction amount - extended","Transaction amount - unit","Department code","Insurance plan ID","Insurance amount",
                    "Assigned patient location","Fee schedule","Patient type","Diagnosis","Performed by code",
                    "Ordered by code","Unit cost","Filler order number","Entered by code","Procedure code","Procedure code modifier"]
        elif segment == "OCR":
            return ["Segment identifier","Order control","Placer order number","Filler order number""Placer group number.","Order status.",
                    "Response flag","Quantity/Timing","Parent","Date/Time of transaction","Entered by","Verified by","Ordering provider",
                    "Enterer's location","Call back phone number","Order effective date/time","Order control code reason","Entering organization",
                    "Entering device","Action by","Advanced beneficiary notice code",]
        elif segment == "OBR": 
            return [
            "Segment identifier","Set ID","Placer order number","Filler Order number","Universal service ID","Priority",
            "Requested date/time","Observation date/time","Observation end date/time","Collection volume","Collector identified",
            "Specimen action code","Danger code","Relevant clinical info","Specimen received date/time","Specimen source","Ordering provider",
            "Order callback phone number","Placer field 1","Placer field 2","Filler field 1","Filler field 2","Results rpt/status change - Date/time",
            "Charge to practice","Diagnostic service section ID","Result status","Parent result","Quantity/timing","Result copies to","Parent",
            "Transportation mode","Reason for study","Principal result interpreter","Assistant result interpreter","Technician","Transcriptionist",
            "Scheduled date/time","Number of sample/time","Transport logistics of collected sample","Collector's comment","Transport arrangement responsibility",
            "Transport arranged","Escort required","Planned patient transport comment","Ordering facility name","Ordering facility address",
            "Ordering facility phone number","Ordering provider address",]
                    

    def generate_hl7(self):
        segment = self.segments_var.get()
        field_values = [child.get() for child in self.fields_frame.winfo_children() if isinstance(child, ttk.Entry)]
        hl7_message = f"{segment}|{'|'.join(field_values)}|"
        self.messages.append(hl7_message)  # Agregar el mensaje a la lista
        print(hl7_message)

    def save_to_file(self):
        # Obtener la ubicación y el nombre del archivo del usuario
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])

        if file_path:
            # Abrir el archivo y escribir todos los mensajes almacenados
            with open(file_path, "w") as file:
                for message in self.messages:
                    file.write(message + '\n')

            print(f"Messages saved to {file_path}")
    def create_checklist(self):
        segments_label = ttk.Label(self.root, text="Select Segments:")
        segments_label.grid(row=3, column=0, padx=10, pady=10)

        segments = ["MSH", "EVN", "PID", "IN1", "PV1", "FT1", "OCR", "OBR"]
        for i, segment in enumerate(segments):
            var = IntVar()
            checkbox = Checkbutton(self.root, text=segment, variable=var)
            checkbox.grid(row=i + 4, column=0, padx=5, sticky="w")
            self.segments_checklist[segment] = var

    def generate_test_segment(self):
        selected_segments = [segment for segment, var in self.segments_checklist.items() if var.get() == 1]
        
        for segment in selected_segments:
            test_segment = self.generate_hardcoded_test_segment(segment)
            print(test_segment)

    def generate_hardcoded_test_segment(self, segment):
        if segment == "MSH":
            return "MSH|^~\\&|LLS|DN|INF|DN000011|201605300100||ADT^A04|58954.001|P|2.5.1|||NE|NE"
        elif segment == "EVN":
            return "EVN|A04|201605300100"
        elif segment == "PID":
            return "PID|000001|90017|90017||TEST^NAME^Q||19820214|M|||123 SESAME STREET^SOMEWHER^NY^42151||(555)1425890^^PH^johnnyq@praxisemr.com^^555^1425890~(777)4588854^^CP||||||123456789|"
        elif segment == "IN1":
            return "IN1|1||B|BLUE CROSS OF VA|PO BOX 27401^^RICHMOND^VA^23279||(800)242 7277||||||||G|SMITH^JOHN^L|S||123 ANY ST^^LYNCHBURG^VA^24551|||||||||||||||||54321|"
        elif segment == "PV1":
            return "PV1|||||||P2^JONES^BILL^^^^MD|R1^BARNES^EDWARD^^^DR^MD|"
        
    def on_frame_configure(self, event):
        self.fields_canvas.configure(scrollregion=self.fields_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.fields_canvas.itemconfig("self.fields_frame", width=canvas_width)

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        self.text_widget.insert(END, text)
        self.text_widget.see(END)  # Hacer scroll automáticamente

if __name__ == "__main__":
    root = tk.Tk()
    app = HL7MessageGenerator(root)
    root.mainloop()