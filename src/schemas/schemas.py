# --- Pydantic Imports (for data structure) ---
from pydantic import BaseModel, Field
from typing import List, Optional


# -- bill to name and address class
class BillToInfo(BaseModel):
    name: Optional[str] = Field(description="Name of the person or company being billed")
    address: Optional[str] = Field(description="Billing address")
    city: Optional[str] = Field(description="City of the billing address")
    state: Optional[str] = Field(description="State of the billing address")
    zip_code: Optional[str] = Field(description="ZIP code of the billing address")
    country: Optional[str] = Field(description="Country of the billing address")

# --- Pay To Information Class ---
class PayToInfo(BaseModel):
    name: Optional[str] = Field(description="Name of the person or company bill to be paid")
    address: Optional[str] = Field(description="Payable Billing address")
    city: Optional[str] = Field(description="City of the pay to address")
    state: Optional[str] = Field(description="State of the pay to address")
    zip_code: Optional[str] = Field(description="ZIP code of the pay to address")
    country: Optional[str] = Field(description="Country of the pay to address")

# --- Line Item Class ---
class LineItem(BaseModel):
    description: Optional[str] = Field(description="Description of the item or service")
    quantity: Optional[float] = Field(description="Quantity of the item")
    unit_price: Optional[float] = Field(description="Unit price of the item")
    total: Optional[float] = Field(description="Total price for the line item")

class InvoiceHeader(BaseModel):
    invoice_id: Optional[str] = Field(description="The invoice number or ID")
    invoice_date: Optional[str] = Field(description="The date the invoice was issued")
    due_date: Optional[str] = Field(description="The date the payment is due")
    vendor_info: Optional[PayToInfo] = Field(description="Information about the vendor")
    bill_to_info: Optional[BillToInfo] = Field(description="Information about the entity being billed")
    total_amount: Optional[float] = Field(description="The total amount due on the invoice")
    tax_amount: Optional[float] = Field(description="The total tax amount on the invoice")
    line_items: Optional[List[LineItem]] = Field(description="A list of all line items on the invoice")

