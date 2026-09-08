from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import List
import datetime
from langchain_core.output_parsers import PydanticOutputParser
import pandas as pd
import json
import os
import re


# ---------------------------------------------------------------------------
# JSON Database helpers
# ---------------------------------------------------------------------------

DB_FILE = "Invoice.json"


def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(store_db, file, indent=4, ensure_ascii=False, default=str)


def load_data():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


store_db = load_data()


# ---------------------------------------------------------------------------
# Pydantic schema (moved to module level so it is defined once)
# ---------------------------------------------------------------------------

class InvoiceItem(BaseModel):
    item_name: str = Field(
        description="Name or description of the item, include unit if given in the name (e.g. Blackforest Cake 1kg)"
    )
    item_hsn_code: int = Field(description="HSN / SAC code of the item")
    item_rate: float = Field(description="Unit price per item before tax")
    item_Qty: float = Field(description="Quantity of item")
    item_unit: str = Field(description="Unit of item (e.g. kg, pcs, box, etc.)")
    cgst_rate: float = Field(default=0.0, description="CGST percentage (e.g. 9 for 9%)")
    cgst_amount: float = Field(default=0.0, description="CGST tax amount")
    sgst_rate: float = Field(default=0.0, description="SGST percentage (e.g. 9 for 9%)")
    sgst_amount: float = Field(default=0.0, description="SGST tax amount")
    igst_rate: float = Field(default=0.0, description="IGST percentage (e.g. 18 for 18%)")
    igst_amount: float = Field(default=0.0, description="IGST tax amount")


class InvoiceStr(BaseModel):
    Supplier_name: str = Field(description="Supplier Name")
    Invoice: str = Field(description="Invoice Number")
    Buyer_name: str = Field(description="Buyer Name")
    Date_of_supply: datetime.date = Field(description="Date of supply")
    Supplier_gst_number: str = Field(description="GST number of supplier")
    Buyer_gst_number: str = Field(description="GST number of buyer")
    Purchase_item: List[InvoiceItem] = Field(description="List of items in purchase")
    taxable_amount: float = Field(description="Taxable amount before tax")
    discount: float = Field(default=0.0, description="Discount amount applied on total amount")
    Total_tax: float = Field(description="Total tax on taxable amount")
    Total_amount: float = Field(description="Total amount including all tax")


parser = PydanticOutputParser(pydantic_object=InvoiceStr)


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert OCR and Invoice Data Extraction AI.
        Extract all requested fields accurately according to the provided schema.

        Rules:
        - Output strict numeric values without currency symbols or '%' signs.
        - Set non-applicable tax rates/amounts to 0.0.
        - Maintain exact line-item tax details.
        - If a field is missing, use 0.0 for numbers and "" for text.

        {Format_instructions}
    """),
    ("human", "{text_content}")
])


# ---------------------------------------------------------------------------
# Text extraction — PDF and Image (OCR)
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using PyPDFLoader."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return "\n\n".join(doc.page_content for doc in docs)


def extract_text_from_image(file_path):
    """
    Extract text from an image using Tesseract OCR (pytesseract).

    Requires:
        pip install pytesseract Pillow
        # System: tesseract-ocr  (apt install tesseract-ocr on Debian/Ubuntu)
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError(
            "Image OCR requires pytesseract and Pillow.\n"
            "  pip install pytesseract Pillow\n"
            "Also install Tesseract OCR engine:\n"
            "  Debian/Ubuntu : sudo apt install tesseract-ocr\n"
            "  Windows       : https://github.com/UB-Mannheim/tesseract/wiki"
        )
    text = pytesseract.image_to_string(Image.open(file_path))
    return text


def extract_text(file_path):
    """Route to PDF or image extraction based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"):
        return extract_text_from_image(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {ext}\n"
            "Supported: .pdf .png .jpg .jpeg .bmp .tiff .webp"
        )


# ---------------------------------------------------------------------------
# Clean LLM JSON response (strip markdown fences if present)
# ---------------------------------------------------------------------------

def clean_json_response(text):
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Display extracted invoice
# ---------------------------------------------------------------------------

def show_invoice(data):
    print("=" * 70)
    print("           EXTRACTED INVOICE DATA")
    print("=" * 70)
    print(f"  Supplier      : {data['Supplier_name']}")
    print(f"  Supplier GST  : {data['Supplier_gst_number']}")
    print(f"  Invoice No    : {data['Invoice']}")
    print(f"  Date          : {data['Date_of_supply']}")
    print(f"  Buyer         : {data['Buyer_name']}")
    print(f"  Buyer GST     : {data['Buyer_gst_number']}")
    print("-" * 70)
    print(f"  {'#':>3}  {'Item Name':30} {'HSN':>8} {'Qty':>6} {'Unit':>6} {'Rate':>10}")
    print("-" * 70)

    for i, item in enumerate(data["Purchase_item"], start=1):
        print(f"  {i:>3}. {item['item_name']:30} {str(item.get('item_hsn_code', '')):>8} "
              f"{item['item_Qty']:>6} {item['item_unit']:>6} {item['item_rate']:>10.2f}")
        if item.get("cgst_rate"):
            print(f"       CGST {item['cgst_rate']}%  =  {item['cgst_amount']:.2f}")
        if item.get("sgst_rate"):
            print(f"       SGST {item['sgst_rate']}%  =  {item['sgst_amount']:.2f}")
        if item.get("igst_rate"):
            print(f"       IGST {item['igst_rate']}%  =  {item['igst_amount']:.2f}")

    print("-" * 70)
    print(f"  Taxable Amount : {data['taxable_amount']:.2f}")
    print(f"  Discount       : {data['discount']:.2f}")
    print(f"  Total Tax      : {data['Total_tax']:.2f}")
    print(f"  Total Amount   : {data['Total_amount']:.2f}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Add invoice to JSON database
# ---------------------------------------------------------------------------

def add_purchase_ai(raw_json_dict):
    global store_db

    new_invoice = {
        "Date": raw_json_dict["Date_of_supply"],
        "Supplier_name": raw_json_dict["Supplier_name"],
        "Supplier_gst_number": raw_json_dict["Supplier_gst_number"],
        "Buyer_name": raw_json_dict["Buyer_name"],
        "Buyer_gst_number": raw_json_dict["Buyer_gst_number"],
        "Invoice": raw_json_dict["Invoice"],
        "Items": raw_json_dict["Purchase_item"],
        "Taxable_amount": raw_json_dict["taxable_amount"],
        "Discount": raw_json_dict["discount"],
        "Total_tax": raw_json_dict["Total_tax"],
        "Total_amount": raw_json_dict["Total_amount"],
    }
    store_db.append(new_invoice)
    save_data()

    print("\n Invoice saved successfully.")
    print(" You can view it in Supplier Information.\n")


# ---------------------------------------------------------------------------
# Export all invoices to Excel
# ---------------------------------------------------------------------------

def export_to_excel(filename="Invoice_data.xlsx"):
    data = load_data()
    if not data:
        print("No data to export.")
        return

    rows = []
    for inv in data:
        for item in inv.get("Items", []):
            rows.append({
                "Date":            inv.get("Date"),
                "Supplier Name":   inv.get("Supplier_name"),
                "Supplier GST":    inv.get("Supplier_gst_number"),
                "Buyer Name":      inv.get("Buyer_name"),
                "Buyer GST":       inv.get("Buyer_gst_number"),
                "Invoice No":      inv.get("Invoice"),
                "Item Name":       item.get("item_name"),
                "HSN Code":        item.get("item_hsn_code"),
                "Qty":             item.get("item_Qty"),
                "Unit":            item.get("item_unit"),
                "Rate":            item.get("item_rate"),
                "CGST Rate":       item.get("cgst_rate"),
                "CGST Amount":     item.get("cgst_amount"),
                "SGST Rate":       item.get("sgst_rate"),
                "SGST Amount":     item.get("sgst_amount"),
                "IGST Rate":       item.get("igst_rate"),
                "IGST Amount":     item.get("igst_amount"),
                "Taxable Amount":  inv.get("Taxable_amount"),
                "Discount":        inv.get("Discount"),
                "Total Tax":       inv.get("Total_tax"),
                "Total Amount":    inv.get("Total_amount"),
            })

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"\n Excel exported: {filename}  ({len(rows)} rows)\n")


# ---------------------------------------------------------------------------
# Edit extracted invoice data
# ---------------------------------------------------------------------------

def edit_invoice_data(raw_json_dict):
    print("=" * 45)
    print("  Which field is incorrect?")
    print("   1.  Supplier Name")
    print("   2.  Supplier GST Number")
    print("   3.  Invoice Number")
    print("   4.  Date of Supply")
    print("   5.  Buyer Name")
    print("   6.  Buyer GST Number")
    print("   7.  Purchase Items")
    print("   8.  Taxable Amount")
    print("   9.  Discount")
    print("  10.  Total Tax")
    print("  11.  Total Amount")
    print("  12.  Go back to Menu")
    print("=" * 45)

    choice = int(input("Enter choice: "))

    if choice == 1:
        raw_json_dict["Supplier_name"] = input("Correct Supplier Name: ")
    elif choice == 2:
        raw_json_dict["Supplier_gst_number"] = input("Correct Supplier GST: ")
    elif choice == 3:
        raw_json_dict["Invoice"] = input("Correct Invoice Number: ")
    elif choice == 4:
        raw_json_dict["Date_of_supply"] = input("Correct Date (YYYY-MM-DD): ")
    elif choice == 5:
        raw_json_dict["Buyer_name"] = input("Correct Buyer Name: ")
    elif choice == 6:
        raw_json_dict["Buyer_gst_number"] = input("Correct Buyer GST: ")
    elif choice == 7:
        edit_items(raw_json_dict)
    elif choice == 8:
        raw_json_dict["taxable_amount"] = float(input("Correct Taxable Amount: "))
    elif choice == 9:
        raw_json_dict["discount"] = float(input("Correct Discount: "))
    elif choice == 10:
        raw_json_dict["Total_tax"] = float(input("Correct Total Tax: "))
    elif choice == 11:
        raw_json_dict["Total_amount"] = float(input("Correct Total Amount: "))
    elif choice == 12:
        print("Returning to menu...")
    else:
        print("Invalid choice.")


def edit_items(raw_json_dict):
    items = raw_json_dict["Purchase_item"]

    while True:
        print("=" * 45)
        for i, item in enumerate(items, start=1):
            print(f"  {i}. {item['item_name']}")
        print("  0. Done")
        print("-" * 45)

        item_no = int(input("Select item to edit (0 to exit): "))
        if item_no == 0:
            break

        item_no -= 1
        if item_no < 0 or item_no >= len(items):
            print("Invalid item number.")
            continue

        item = items[item_no]
        print("\n  1.  Item Name")
        print("  2.  Item Rate")
        print("  3.  Item Quantity")
        print("  4.  Item Unit")
        print("  5.  HSN Code")
        print("  6.  CGST Rate")
        print("  7.  CGST Amount")
        print("  8.  SGST Rate")
        print("  9.  SGST Amount")
        print("  10. IGST Rate")
        print("  11. IGST Amount")
        print("  12. Back")

        field = input("Enter choice: ")

        if field == "1":
            item["item_name"] = input("New Item Name: ")
        elif field == "2":
            item["item_rate"] = float(input("New Rate: "))
        elif field == "3":
            item["item_Qty"] = float(input("New Quantity: "))
        elif field == "4":
            item["item_unit"] = input("New Unit: ")
        elif field == "5":
            item["item_hsn_code"] = int(input("New HSN Code: "))
        elif field == "6":
            item["cgst_rate"] = float(input("New CGST Rate: "))
        elif field == "7":
            item["cgst_amount"] = float(input("New CGST Amount: "))
        elif field == "8":
            item["sgst_rate"] = float(input("New SGST Rate: "))
        elif field == "9":
            item["sgst_amount"] = float(input("New SGST Amount: "))
        elif field == "10":
            item["igst_rate"] = float(input("New IGST Rate: "))
        elif field == "11":
            item["igst_amount"] = float(input("New IGST Amount: "))
        elif field == "12":
            pass
        else:
            print("Invalid choice.")


# ---------------------------------------------------------------------------
# Main invoice reader (PDF + Image)
# ---------------------------------------------------------------------------

def invoice_reader(input_path, llm):
    # 1. Extract text from file
    print("Extracting text from file...")
    try:
        text_content = extract_text(input_path)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return

    print(f"Extracted {len(text_content)} characters.\n")

    # 2. Build prompt and invoke LLM
    final_prompt = prompt.invoke({
        "text_content": text_content,
        "Format_instructions": parser.get_format_instructions(),
    })
    print("Wait for few seconds, extracting invoice data...\n")

    ai_message = llm.invoke(final_prompt)
    raw_text_response = ai_message.content

    # 3. Parse JSON (handle markdown code fences)
    cleaned = clean_json_response(raw_text_response)
    try:
        raw_json_dict = json.loads(cleaned)
    except json.JSONDecodeError:
        print("Failed to parse LLM response as JSON.")
        print("Raw response:")
        print(raw_text_response)
        return

    # 4. Show extracted data
    show_invoice(raw_json_dict)

    # 5. Buyer verification
    buyer_name = raw_json_dict["Buyer_name"].strip().lower()
    buyer_gst = raw_json_dict["Buyer_gst_number"].strip()

    valid_buyers = [
        ("shree brijwasi sweets & restaurant", "09AKWPP5424B1ZT"),
        ("shri brijwasi sweets & restaurant",  "09AKWPP5424B1ZT"),
    ]

    matched = any(
        buyer_name == bn and buyer_gst == bg for bn, bg in valid_buyers
    )

    if not matched:
        print(f"\n Buyer verification failed: {raw_json_dict.get('Buyer_name')} / {buyer_gst}")
        print(" Please check the buyer information.\n")
        return

    print(" Buyer verified successfully.\n")

    # 6. Duplicate check
    global store_db
    store_db = load_data()

    invoice_no = raw_json_dict["Invoice"]
    supplier_name = raw_json_dict["Supplier_name"]

    already_exists = any(
        inv["Invoice"] == invoice_no and inv["Supplier_name"] == supplier_name
        for inv in store_db
    )

    if already_exists:
        print("This invoice already exists in the database.\n")
        return

    print("New invoice found.\n")

    # 7. Save / Edit / Cancel loop
    while True:
        print("=" * 40)
        print("  1. Save Invoice")
        print("  2. Edit Extracted Data")
        print("  3. Cancel")
        print("=" * 40)

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_purchase_ai(raw_json_dict)
            break
        elif choice == "2":
            edit_invoice_data(raw_json_dict)
            print("\nUpdated invoice data:")
            show_invoice(raw_json_dict)
        elif choice == "3":
            print("Cancelled.\n")
            break
        else:
            print("Invalid choice.\n")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def supplier_info():
    data = load_data()
    if not data:
        print("No supplier data found.")
        return

    for inv in data:
        print("=" * 70)
        print(f"  Date     : {inv.get('Date')}")
        print(f"  Supplier : {inv.get('Supplier_name')}")
        print(f"  Invoice  : {inv.get('Invoice')}")
        print("=" * 70)
        print(f"  {'Item':30} {'Qty':>8} {'Unit':>8} {'Rate':>10}")
        print("-" * 60)

        for item in inv.get("Items", []):
            print(f"  {item['item_name']:30} {item['item_Qty']:>8} "
                  f"{item['item_unit']:>8} {item['item_rate']:>10.2f}")

        print("-" * 60)
        print(f"  Taxable Amount : {inv.get('Taxable_amount', 0):.2f}")
        print(f"  Discount       : {inv.get('Discount', 0):.2f}")
        print(f"  Total Tax      : {inv.get('Total_tax', 0):.2f}")
        print(f"  Total Amount   : {inv.get('Total_amount', 0):.2f}")
        print()


def stock_level():
    data = load_data()
    if not data:
        print("No stock data found.")
        return

    stock = []
    for invoice in data:
        for item in invoice.get("Items", []):
            stock.append({
                "Supplier": invoice["Supplier_name"],
                "Item": item["item_name"],
                "Qty": item['item_Qty'],
                "Unit": item["item_unit"],
            })

    df_stock = pd.DataFrame(stock)
    report = (
        df_stock.groupby(["Supplier", "Item", "Unit"])["Qty"]
        .sum()
        .reset_index()
    )
    print(report.to_string(index=False))


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def main():
    llm = ChatGroq(model_name="openai/gpt-oss-120b")

    while True:
        print("\n" + "=" * 45)
        print("        INVOICE READER MENU")
        print("=" * 45)
        print("  1. Add Purchase  (PDF or Image)")
        print("  2. Supplier Information")
        print("  3. Stock Information")
        print("  4. Export to Excel")
        print("  5. Exit")
        print("=" * 45)

        choice = input("Enter choice: ").strip()

        if choice == "1":
            path = input("Enter file path (PDF/Image): ").strip().strip('"').strip("'")
            if os.path.exists(path):
                invoice_reader(path, llm)
            else:
                print("File not found. Please check the path.\n")
        elif choice == "2":
            supplier_info()
        elif choice == "3":
            stock_level()
        elif choice == "4":
            export_to_excel()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
