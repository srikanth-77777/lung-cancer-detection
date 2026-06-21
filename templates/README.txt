================================================================
LUNG CANCER AI DIAGNOSTIC SYSTEM
Setup & Run Instructions
================================================================

STEP 1 — Install Flask
-----------------------
Open CMD and run:
    pip install flask

STEP 2 — Copy files to your project
-------------------------------------
Copy the entire webapp\ folder to:
    C:\MedicalProject\webapp\

Final structure should be:
    C:\MedicalProject\
        webapp\
            app.py
            gradcam.py
            notes.py
            templates\
                index.html

STEP 3 — Run the server
-------------------------
Open CMD and run:
    cd C:\MedicalProject\webapp
    python app.py

You will see:
    ✅ EfficientNetB0 loaded
    ✅ DenseNet201 loaded
    ✅ Grad-CAM ready
    🚀 Running on http://localhost:5000

STEP 4 — Open in browser
--------------------------
Open Chrome or Edge and go to:
    http://localhost:5000

STEP 5 — Demo flow
-------------------
1. Click "Browse from Computer"
2. Select any CT scan PNG/JPG
3. Click "Analyze Scan"
4. Sector 1 shows Binary result
5. If Malignant → Grad-CAM heatmap shows
6. Click "Proceed to Sector 2"
7. Sector 2 shows subtype + full clinical notes

================================================================
DEMO IMAGES TO USE
================================================================

For Sector 1 (Binary — LIDC-IDRI):
    C:\MedicalProject\final_dataset\test\LIDC-IDRI-0015\40.png

For Sector 2 (4-Class — Chest CT):
    C:\MedicalProject\chest_ct\Data\test\adenocarcinoma\000001.png
    C:\MedicalProject\chest_ct\Data\test\normal\000001.png

================================================================
TROUBLESHOOTING
================================================================

Error: "Flask not found"
→ Run: pip install flask

Error: "Model weights not found"
→ Check paths in app.py lines 28-29
→ EFF_WEIGHTS and DENSE_WEIGHTS

Error: "Port already in use"
→ Run: python app.py --port 5001
→ Open: http://localhost:5001

================================================================
