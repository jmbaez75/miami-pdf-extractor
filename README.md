# 🌴 MIAMI PDF Extractor (M.P.E)

<p align="center">
  <img src="assets/logo.png" alt="MPE Logo" width="150"/>
</p>

### *WHEN YOU HAVE TO READ DATA FROM THOUSANDS OF SIMILAR PDFs...*

<p align="center">
  <img src="static/images/screeshot.png" alt="MIAMI PDF Extractor screenshot" width="80%">
</p>

**M.P.E** is a feasible, user-friendly solution for batch PDF data extraction. Built with a clean UI and robust backend, it eliminates manual data entry, saving you time and reducing human error.

---

### 🚀 Get Started

**Download for Linux:** Get the single-file AppImage from our [Releases page](https://github.com/jmbaez75/miami-pdf-extractor/releases).

---

## 🚀 Key Features

* **Batch Processing:** Process hundreds of PDFs in seconds.
* **Smart Mapping:** Dynamically map PDF layouts without complex coding.
* **Automated Cleaning:** Built-in filter system to sanitize and format data on the fly.
* **Error Resilience:** Real-time feedback and detailed error handling to ensure data integrity.
* **Responsive Web Interface:** A sleek, intuitive dashboard to manage your workflows.

## 🛠 Tech Stack

* **Backend:** Python (Django 6.0)
* **Frontend:** HTML5, CSS3, JavaScript
* **Data Handling:** JSON, CSV, Pandas

## 📋 How it Works

1. **Map Execution:** Scan a sample PDF to generate your coordinate reference map.
2. **Output Columns:** Easily configure which data fields you want to extract.
3. **Filters:** Apply rules to clean your text (e.g., currency formatting, removing symbols).
4. **Execute Batch:** Let the tool do the heavy lifting while you monitor the progress.

## 📦 Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/jmbaez75/miami-pdf-extractor.git](https://github.com/jmbaez75/miami-pdf-extractor.git)
cd miami-pdf-extractor

# Install dependencies
pip install -r requirements.txt

# Run the application
python manage.py runserver