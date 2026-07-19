from typing import List, Optional
from pydantic import BaseModel, Field


class InvoiceLineItem(BaseModel):
    description: str = Field(description="รายละเอียดรายการสินค้า/บริการ")
    amount: float = Field(description="จำนวนเงินก่อนภาษี")
    vat_rate: float = Field(default=0, description="อัตราภาษีมูลค่าเพิ่ม (%)")
    wht_rate: float = Field(default=0, description="อัตราภาษีหัก ณ ที่จ่าย (%)")


class InvoiceExtractionResult(BaseModel):
    supplier_name: str = Field(description="ชื่อผู้ขาย/ผู้ให้บริการ")
    tax_id: str = Field(description="เลขประจำตัวผู้เสียภาษีของผู้ขาย")
    invoice_no: str = Field(description="เลขที่ใบแจ้งหนี้/ใบเสนอราคา")
    invoice_date: Optional[str] = Field(default=None, description="วันที่ออกเอกสาร (YYYY-MM-DD)")
    due_date: Optional[str] = Field(default=None, description="วันครบกำหนดชำระ (YYYY-MM-DD)")
    line_items: List[InvoiceLineItem] = Field(default_factory=list, description="รายการสินค้า/บริการ")
    subtotal: float = Field(description="ยอดรวมก่อนภาษี")
    vat_amount: float = Field(description="ยอดภาษีมูลค่าเพิ่มรวม")
    wht_amount: float = Field(default=0, description="ยอดภาษีหัก ณ ที่จ่ายรวม")
    net_total: float = Field(description="ยอดสุทธิที่ต้องชำระ")
    confidence: float = Field(description="ความมั่นใจของผลลัพธ์การสกัดข้อมูล (0-1)")
    notes: Optional[str] = Field(default=None, description="หมายเหตุ/ข้อสังเกตของ AI (ถ้ามี)")
