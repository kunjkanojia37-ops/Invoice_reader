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



def save_data():
    with open("Invoice.json","w",encoding="utf-8") as file:
        json.dump(store_db,file, indent=4,ensure_ascii=False,default=str)


def load_data():
    try:
        with open("Invoice.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

store_db = load_data()
       

load_data()

def pdf_text_reader(Input_path,llm):
 
  pdf_page = PyPDFLoader(Input_path)

  docs = pdf_page.load()

  print(docs)

  class InvoiceItem(BaseModel):
     item_name   :   str          = Field(
        description="Name or description of the item also take unit is given in item name(e.g Blackforest Cake1kg)"
        )
     item_hsn_code : int = Field(
        description="Hsn code of the item"
     )
     item_rate   :   float        = Field(
        description="unit price per item before tax"
        )
     item_Qty  :   float        = Field(
            description="quantity of item"
            )
        
     item_unit :   str        = Field(
            description="unit of item (e.g kg, pcs, etc.)"
            )
     cgst_rate   :   float  |None = Field(
        description="Cgst percentage(e.g 9 for 9%)"
        )
     cgst_amount :   float  |None = Field(
        description="cgst tax amount"
        )
     sgst_rate   :   float  |None = Field(
        description="sgst percentage(e.g 9 for 9%)"
        )
     sgst_amount :   float  |None = Field(
        description="sgst tax amount"
       )
     igst_rate   :   float  |None = Field(
        description="igst percentage(e.g 18% ,5%, 12%)"
        )
     igst_amount :   float  |None = Field(
        description="igst tax amount"
        )

  class invoice_str(BaseModel):
     Supplier_name         :  str = Field(
        description="Supplier Name"
        ) 
     Invoice               :  str = Field(
        description="Invoice Number"
        )
     Buyer_name            :  str = Field(
        description="Buyer Name"
        )
     Date_of_supply        : datetime.date = Field(
        description=" Date of supply"
        )
     Supplier_gst_number   : str = Field(
     description= " GST number of supplyer"
      )
     Buyer_gst_number      : str = Field(
        description= " GST number of buyer"
        )
     Purchase_item         : List [InvoiceItem] = Field(
        description=" list of items in purchase"
        )
     taxable_amount        : float = Field(
        description="taxable amount before tax"
        )
     discount              : float = Field(
        description="discount amount apply on total amount"
        )
     Total_tax          : float = Field(
            description="total tax on taxable amount"
            )
     Total_amount           : float = Field(
        description="total amonut include all tax"
        )

  parser = PydanticOutputParser(pydantic_object= invoice_str)

  prompt = ChatPromptTemplate.from_messages([
   ("system","""
 
        You are an expert OCR and Invoice Data Extraction AI.
        Extract all requested fields accurately according to the provided schema.
        
        Rules:
        - Output strict numeric values without currency symbols (₹, $) or '%' signs.
        - Set non-applicable tax rates/amounts to 0.0.
        - Maintain exact line-item tax details.
    
                 {Format_instructions}
      """),
       ("human","{Pdf_details}")
     ])

  pdf_text = "\n\n".join(doc.page_content for doc in docs)


  final_prompt = prompt.invoke(
     {
     "Pdf_details": pdf_text,
     "Format_instructions": parser.get_format_instructions()
     }
     )
  print(" wait for few seconds we do our work")

  ai_message = llm.invoke(final_prompt)

  raw_text_response = ai_message.content

  
  print(raw_text_response)
  
  raw_json_dict = json.loads(raw_text_response) # convert ai response to "dic" datatype
  


  def show_invoice(data):

    print("=" * 50)
    print("      EXTRACTED INVOICE DATA")
    print("=" * 50)

    print(f"Supplier      : {data['Supplier_name']}")
    print(f"Invoice No    : {data['Invoice']}")
    print(f"Date          : {data['Date_of_supply']}")
    print(f"Buyer         : {data['Buyer_name']}")

    print("-" * 50)
    print("Items")
    print("-" * 50)

    for i, item in enumerate(data["Purchase_item"], start=1):

        print(f"\n{i}.")
        print(f"Name     : {item['item_name']}")
        print(f"Qty      : {item['item_Qty']}")
        print(f"Unit     : {item['item_unit']}")
        print(f"Rate     : {item['item_rate']}")
        print(f"Rate     : {item['item_hsn_code']}")
        print(f"Name     : {item['cgst_rate']}")
        print(f"Name     : {item['item_name']}")
        print(f"Name     : {item['cgst_rate']}") 
        print(f"Name     : {item['item_name']}")
        print(f"Name     : {item['cgst_rate']}")
        print(f"Name     : {item['item_name']}")
        

    print("-" * 50)
    print(f"Taxable Amount : {data['taxable_amount']}")
    print(f"Discount       : {data['discount']}")
    print(f"Total Tax      : {data['Total_tax']}")
    print(f"Total Amount   : {data['Total_amount']}")
    print("=" * 50)

  def add_purchase_ai():
    
    global store_db

    new_invoice = {
    "Date": raw_json_dict["Date_of_supply"],
    "Supplier_name": raw_json_dict["Supplier_name"],
    "Supplier_gst_number": raw_json_dict["Supplier_gst_number"],
    "Buyer_name": raw_json_dict["Buyer_name"],
    "Buyer_gst_number": raw_json_dict["Buyer_gst_number"],
    "Invoice": raw_json_dict["Invoice"],
    "Items": raw_json_dict["Purchase_item"],
    "hsn" : raw_json_dict["item_hsn_code"],
    "Taxable_amount": raw_json_dict["taxable_amount"],
    "Discount": raw_json_dict["discount"],
    "Total_tax": raw_json_dict["Total_tax"],
    "Total_amount": raw_json_dict["Total_amount"]
    }
    store_db.append(new_invoice)
    save_data()

    print(store_db)
    print("\n please wait for few seconds \n")
    print("\n we add invoice you  can see it in supplier information")

     
  buyer_name = raw_json_dict["Buyer_name"].strip().lower()
  buyer_gst = raw_json_dict["Buyer_gst_number"].strip()

  
  if buyer_name in ["shree brijwasi sweets & restaurant" ,"shri brijwasi sweets & restaurant"] and buyer_gst == "09AKWPP6151B1ZT":
     
     print("I  match your firm name and Gst number it match well.")
     print("\n--- Processed DataFrame ---")



     choose =input (" I hope you check buyer details also \n(Yes/No) :")
     if  choose.lower() == "yes":
        print("\nI am going to do my task......!\n")
        
        invoice_no = raw_json_dict["Invoice"]
        supplier_name = raw_json_dict["Supplier_name"]

        already_exists = False

        global store_db
        store_db = load_data()

        for invoice in store_db:
           if (invoice ["Invoice"] == invoice_no
          and invoice["Supplier_name"] == supplier_name
          ):
            already_exists = True
            break

        if already_exists:
           
           print("✅ This invoice already exists.")

        else:
           
           print("New invoice found.")
           

           print(f"Now I get invoce details")
           show_invoice(raw_json_dict)

           print("=" * 60)
           print("""
             1. Save Invoice

             2. Edit Extracted Data

             3. Cancel

              """)
           print("=" * 60)
           
           user_purchase_opretion = int(input("Enter Choice :"))

           if user_purchase_opretion == 1:
              
              print(" Invoice save sucessfully")
              add_purchase_ai()
              

           elif user_purchase_opretion == 2:
              print("="* 35)
              print("Which field is incorrect?")
              print("1. Supplier Name")
              print("2. Supplier Gst Number")
              print("3. Invoice Number")
              print("4. Date")
              print("5. Buyer Name")
              print("2. Buyer Gst Number")
              print("7. Purchase Items")
              print("8. Taxable Amount")
              print("9. Total Discount")
              print("10. Tax Amount")
              print("11. Total Amount")
              print("12. Go back to Menu")
              print("="* 35)

              while True:
                opretion_choose = int(input("Enter choose :"))

                if opretion_choose == 1:
                   
                   correct_supp_name = input("Enter Correct  Supplier Name : ")
                   raw_json_dict["Supplier_name"] = correct_supp_name

                elif opretion_choose == 2 :
                     
                   correct_supp_gst = input("Enter Correct  Supplier Gst Number : ")
                   raw_json_dict["Supplier_gst_number"] = correct_supp_gst

                elif opretion_choose ==3:
                   
                   correct_Invoice = input("Enter Correct Invoice Number : ")
                   raw_json_dict["Invoice"]= correct_Invoice

                elif opretion_choose == 4:
                    
                    correct_Date = input("Enter Correct Date of Supply : ")
                    raw_json_dict["Date_of_supply"] = correct_Date

                elif opretion_choose == 5:
                   
                   correct_buyer_name = input("Enter Correct Buyer Name : ")
                   raw_json_dict["Buyer_name"] = correct_buyer_name

                elif opretion_choose == 6:
                    
                    correct_buyer_gst = input("Enter Correct Buyer Gst Number :")
                    raw_json_dict["Buyer_gst_number"] = correct_buyer_gst

                elif opretion_choose == 7 :
                   
                   while True:
                  
                      print("=" * 35)

                      # Show all items
                      for i, item in enumerate(raw_json_dict["Purchase_item"], start=1):
                           print(f"{i}. {item['item_name']}")

                           print("\nSelect an item to edit.")
                           print("0. Exit")

                           item_no = int(input("Enter item number: "))

                           if item_no == 0:
                              break

                           item_no -= 1

                           # Check valid index
                           if item_no < 0 or item_no >= len(raw_json_dict["Purchase_item"]):
                               print("Invalid item number.")
                               continue

                           print("\n1. Item Name")
                           print("2. Item Rate")
                           print("3. Item Quantity")
                           print("4. Item Unit")
                           print("5. CGST Rate")
                           print("6. CGST Amount")
                           print("7. SGST Rate")
                           print("8. SGST Amount")
                           print("9. IGST Rate")
                           print("10. IGST Amount")
                           print("11. HSN Code")
                           print("11. Back")

                           choice = input("Enter your choice: ")

                           if choice == "1":
                              raw_json_dict["Purchase_item"][item_no]["item_name"] = input("New Item Name: ")

                           elif choice == "2":
                              raw_json_dict["Purchase_item"][item_no]["item_rate"] = float(input("New Rate: "))

                           elif choice == "3":
                              raw_json_dict["Purchase_item"][item_no]["item_Qty"] = float(input("New Quantity: "))
 
                           elif choice == "4":
                              raw_json_dict["Purchase_item"][item_no]["item_unit"] = input("New Unit: ")

                           elif choice == "5":
                              raw_json_dict["Purchase_item"][item_no]["cgst_rate"] = input("New Unit: ")

                           elif choice == "6":
                              raw_json_dict["Purchase_item"][item_no]["cgst_amount"] = input("New Unit: ")

                           elif choice == "7":
                              raw_json_dict["Purchase_item"][item_no]["sgst_rate"] = input("New Unit: ")

                           elif choice == "8":
                             raw_json_dict["Purchase_item"][item_no]["sgst_amount"] = input("New Unit: ")

                           elif choice == "9":
                             raw_json_dict["Purchase_item"][item_no]["igst_rate"] = input("New Unit: ")

                           elif choice == "10":
                              raw_json_dict["Purchase_item"][item_no]["igst_amount"] = input("New Unit: ")

                           elif choice == "11":
                             raw_json_dict["Purchase_item"][item_no]["item_hsn_code"] = input("New Unit: ")

                           elif choice == "12":
                              print("okay sir .....")

                           else:
                            print("Invalid Choice")
                            continue

                elif opretion_choose == 8:
                   
                   correct_Taxable_amount = float(input("Enter Correct Taxable Amount : "))
                   store_db["taxable_amount"] = correct_Taxable_amount

                elif opretion_choose == 9:
                   
                   correct_discount = float(input("Enter Correct Discount : "))
                   store_db["discount"] = correct_discount

                elif opretion_choose == 10:

                   correct_tax_amount = float(input("Enter Correct Tax Value : "))
                   store_db["Total_tax"] = correct_tax_amount

                elif opretion_choose == 11:

                   correct_total_amount = float(input("Enter correct Total value : "))
                   store_db["Total_amount"] = correct_total_amount

                elif opretion_choose == 12:
                   
                   print("okay I think I cann't make any mistake let go forward ......")
                   break
                else:
                   print("\n Wrong Input given by user .\nI think you don't want to do it okay\n")
                   continue


     else:
        print(f" \nif you don't want it it's okay...\n")
      
  else:
     print(f"\nsomething worng find in buyer information {raw_json_dict.get('Buyer_name')} / {buyer_gst}\n please check it out\n")


def supplier_info():
    df = pd.DataFrame(load_data())

    if df.empty:
        print("No supplier data found.")
        return

    grouped = df.groupby(["Date", "Supplier_name", "Invoice"])

    for (date, supplier, invoice), group in grouped:

        print("=" * 70)
        print(f"Date     : {date}")
        print(f"Supplier : {supplier}")
        print(f"Invoice  : {invoice}")
        print("=" * 70)

        print(f"{'Item':25} {'Qty':>8} {'Unit':>8}")
        print("-" * 45)

        for _, row in group.iterrows():

            for item in row["Items"]:
                print(
                    f"{item['item_name']:25}"
                    f"{item['item_Qty']:>8}"
                    f"{item['item_unit']:>8}"
                )

        print("-" * 45)
        print(f"Taxable Amount : {group['Taxable_amount'].sum()}")
        print(f"Discount       : {group['Discount'].sum()}")
        print(f"Total Tax      : {group['Total_tax'].sum()}")
        print(f"Total Amount   : {group['Total_amount'].sum()}")
        print()

def stock_level():

    data = load_data()

    stock = []

    for invoice in data:

        for item in invoice["Items"]:

            stock.append({
                "Supplier": invoice["Supplier_name"],
                "Item": item["item_name"],
                "Qty": item["item_Qty"],
                "Unit": item["item_unit"]
            })

        df_stock = pd.DataFrame(stock)
        report = ( df_stock.groupby(["Supplier","Item", "Unit"])["Qty"]
          .sum()
          .reset_index()
          )
        print(report)



  

import os

def call_function():

    llm = ChatGroq(    model="openai/gpt-oss-120b",
    temperature=0)

    invoice_folder = "purchase_invoices"

    pdf_files = [f for f in os.listdir(invoice_folder) if f.endswith(".pdf")]

    if not pdf_files:
        print("No PDF invoices found.")
        return

    print("\nAvailable Invoices\n")

    for i, pdf in enumerate(pdf_files, start=1):
        print(f"{i}. {pdf}")

    choice = int(input("\nSelect Invoice Number: ")) - 1

    if choice < 0 or choice >= len(pdf_files):
        print("Invalid choice.")
        return

    pdf_path = os.path.join(invoice_folder, pdf_files[choice])

    print(f"\nOpening: {pdf_files[choice]}")

    pdf_text_reader(pdf_path, llm)



while True:
 
 print("\n====================================")
 print("Please select following opration :")
 print("a). Purchase  ") 
 print("b). Menu  ")
 print("c).Exit")
 print("===================================\n")

 choose = input("Enter You choice : ")

 if choose.lower() == "a":
    
    while True:
        print("\n===================================")
        print("\nokay we receive Your order,please Wait for a movement.\n")
        print("a). Add purchase")
        print("b). supplier Information")
        print("c). Stock Information")
        print("d). Go back to main menu")
        print("===================================\n")

        pur_choose = input("\n Enter Your choice : ")

        if pur_choose.lower() == "a":
       
           print(" let's go to level up purchase...")
           call_function()

        elif pur_choose.lower() == "b":
          
          print("\nokay we receive Your order,please Wait for a movement.")
          supplier_info()

        elif pur_choose.lower() == "c":
           
           print("\nokay we receive Your order,please Wait for a movement.")
           stock_level()

        elif pur_choose.lower() == "d":
          
          print("\nokay we receive Your order,please Wait for a movement.")
          break

        else:
           print(" System cann't perform with this request.")
           continue
           
  

 elif choose.lower() == "b": 
    
  
      while True:
          print("\n===================================")
          print("\nokay we receive Your order,please Wait for a movement.\n")
          print("a). Menu item ")
          print("b). Go back to main menu")
          print("===================================\n")
  
          pur_choose = input("\n Enter Your choice : ")
  
          if pur_choose.lower() == "a":
         
            
             print("\nokay we receive Your order,please Wait for a movement.")
             print(" Sorry but this servies is still not available. \n")
          
  
  
          elif pur_choose.lower() == "b":
            
            print("\nokay we receive Your order,please Wait for a movement.")
            break
  
          else:
             
             print(" System cann't perform with this request.")
             continue
             

 elif choose.lower() == "c":
    
    print("\nokay sir...\n")
    break
 
 else: 
    
    print("\nSorry but we cann't  get accurate instructions.\n")
    continue

