# AI Invoice Reader & Purchase Management System

An AI-powered Invoice Reader built using **LangChain**, **Groq LLM**, **Pydantic**, and **Python**. It extracts structured information from PDF and image invoices, validates buyer GST details, stores invoices in a local JSON database, and provides supplier and stock reports — plus Excel export.

---

## Features

- Extract invoice data from **PDF and image files** (OCR via Tesseract)
- AI-powered structured data extraction using Groq LLM
- Pydantic schema validation for accurate field mapping
- Automatic JSON database storage
- Duplicate invoice detection
- Buyer GST verification
- Edit extracted data before saving
- Supplier-wise purchase reports
- Stock summary report
- **Export all invoices to Excel**
- Command-line menu interface

---

## How It Works

1. You provide an invoice file (PDF or image)
2. Text is extracted (PyPDF for PDFs, Tesseract OCR for images)
3. LangChain sends the text to Groq LLM with a Pydantic schema
4. LLM returns structured invoice data as JSON
5. Buyer name and GST number are verified
6. Duplicate invoice check runs against the database
7. You review, edit (if needed), and save
8. Invoice is stored in `Invoice.json`
9. Export to Excel anytime

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12+ |
| LLM Framework | LangChain |
| LLM Provider | Groq (openai/gpt-oss-120b) |
| Data Validation | Pydantic |
| PDF Extraction | PyPDF |
| Image OCR | Tesseract + pytesseract |
| Data Processing | Pandas |
| Excel Export | OpenPyXL |
| Storage | JSON file database |

---

## Installation

### Clone the repository

```bash
git clone https://github.com/kunjkanojia37-ops/Invoice_reader.git
cd Invoice_reader
```

### Create a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install Tesseract OCR (for image invoices)

- **Windows:** Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Ubuntu/Debian:** `sudo apt install tesseract-ocr`
- **Mac:** `brew install tesseract`

---

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your API key from [console.groq.com](https://console.groq.com/keys)

> **Important:** Never commit your `.env` file. It is already in `.gitignore`.

---

## Usage

```bash
python invoice_read.py
```

### Menu Options

```
1. Add Purchase  (PDF or Image)  — Extract invoice data from a file
2. Supplier Information           — View all saved invoices
3. Stock Information              — View stock summary by supplier
4. Export to Excel                — Export all data to .xlsx
5. Exit
```

---

## Extracted Fields

### Supplier Details
- Supplier Name
- Supplier GST Number

### Buyer Details
- Buyer Name
- Buyer GST Number

### Invoice Details
- Invoice Number
- Date of Supply

### Line Items (per item)
- Item Name
- HSN/SAC Code
- Quantity
- Unit (kg, pcs, box, etc.)
- Rate (unit price before tax)
- CGST Rate + Amount
- SGST Rate + Amount
- IGST Rate + Amount

### Invoice Totals
- Taxable Amount
- Discount
- Total Tax
- Total Amount

---

## Project Structure

```
Invoice_reader/
├── invoice_read.py       # Main application
├── Invoice.json          # JSON database (auto-generated)
├── .env                  # API key (not tracked in git)
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Reports

### Supplier Report
Shows date, supplier, invoice number, all purchased items with quantities and rates, and invoice totals.

### Stock Report
Aggregates all purchases by supplier and item, showing total quantity per item per supplier.

### Excel Export
Exports all invoice data into a flat spreadsheet — one row per line item — with all fields as columns.

---

## Future Improvements

- [ ] Streamlit web interface
- [ ] SQLite / PostgreSQL database
- [ ] Multi-company support
- [ ] Dashboard and analytics
- [ ] Automatic purchase order matching
- [ ] Invoice search and filtering
- [ ] PDF report generation

---

## Author

**Kunj Kanojia**

- GitHub: [@kunjkanojia37-ops](https://github.com/kunjkanojia37-ops)
- LinkedIn: [Kunj Kanojia](https://www.linkedin.com/in/kunj-kanojia-3533a2402)

---

Built as a practical AI-powered Purchase Invoice Management System using LangChain and Groq.
