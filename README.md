# AI Invoice Reader & Purchase Management System

An AI-powered Invoice Reader built using **LangChain**, **Groq LLM**, **Pydantic**, and **Python**.

The application extracts structured information from PDF purchase invoices, validates buyer details, stores invoices in a local JSON database, and provides supplier and stock reports.

---

# Features

- Extract invoice information from PDF files
- AI-powered data extraction using Groq LLM
- Structured output with Pydantic
- Automatic JSON database storage
- Duplicate invoice detection
- Buyer GST verification
- Edit extracted invoice data before saving
- Supplier-wise purchase reports
- Stock summary report
- Command-line menu interface

---

# Technologies Used

- Python
- LangChain
- Groq LLM
- Pydantic
- Pandas
- JSON Database
- dotenv

---

# Project Structure

```
Invoice-Reader/
│
├── invoice_read.py
├── Invoice.json
├── .env
├── purchase_invoices/
│   ├── invoice1.pdf
│   ├── invoice2.pdf
│   └── ...
│
├── README.md
└── requirements.txt
```

---

# Installation

Clone the repository

```bash
git clone <repository-url>

cd Invoice-Reader
```

Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

Example

```env
GROQ_API_KEY=your_groq_api_key
```

---

# Running the Project

```bash
python invoice_read.py
```

---

# Menu

```
Purchase

    Add Purchase
    Supplier Information
    Stock Information

Menu

Exit
```

---

# Workflow

1. Select **Add Purchase**
2. Choose a PDF invoice
3. AI extracts invoice details
4. Buyer information is verified
5. Duplicate invoice is checked
6. Review extracted data
7. Save or edit the invoice
8. Invoice is stored in `Invoice.json`

---

# Extracted Fields

## Supplier Details

- Supplier Name
- Supplier GST Number

## Buyer Details

- Buyer Name
- Buyer GST Number

## Invoice Details

- Invoice Number
- Date of Supply

## Purchase Items

Each item includes

- Item Name
- HSN Code
- Quantity
- Unit
- Rate
- CGST Rate
- CGST Amount
- SGST Rate
- SGST Amount
- IGST Rate
- IGST Amount

## Invoice Totals

- Taxable Amount
- Discount
- Total Tax
- Total Amount

---

# Reports

## Supplier Report

Displays

- Date
- Supplier
- Invoice Number
- Purchased Items
- Taxable Amount
- Discount
- Total Tax
- Total Amount

## Stock Report

Displays

- Supplier
- Item Name
- Quantity
- Unit

---

# AI Model

Current LLM

```
openai/gpt-oss-120b
```

via Groq.

---

# Future Improvements

- Streamlit Web Interface
- SQLite / PostgreSQL database
- OCR support for scanned invoices
- Export to Excel
- Dashboard and analytics
- Multi-company support
- Automatic purchase order matching
- Invoice search
- PDF report generation

---

# Requirements

See `requirements.txt`

---

# Author

Developed as an AI-powered Purchase Invoice Management System using LangChain and Groq.