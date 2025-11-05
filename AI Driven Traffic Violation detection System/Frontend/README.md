# AI-driven Traffic Violation Citizen Interface (Flask)

Simple Flask web interface for citizens to register/login, view challans, evidence (images), and download challan details. Payment is a placeholder (Coming soon).

Quick start (Windows PowerShell):

```powershell
python -m pip install -r requirements.txt
python init_db.py
python app.py
```

Open http://127.0.0.1:5000 in a browser.

Notes:
- Uses SQLite at `traffic.db` in the project root.
- Evidence images in sample challengs point to external placeholder images for demo.
- Download challan provides a downloadable text file. You can later change to PDF generator.
