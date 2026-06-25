import pytesseract
import fitz  # PyMuPDF
import re
import os
from PIL import Image
import io

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ==========================================
# STEP 1 — PDF TO TEXT
# ==========================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF first, fall back to OCR if needed"""
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        # Try direct text extraction first (works for digital PDFs)
        page_text = page.get_text()

        if len(page_text.strip()) > 50:
            text += page_text
        else:
            # Fall back to OCR for scanned/image PDFs
            pix = page.get_pixmap(dpi=200)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            page_text = pytesseract.image_to_string(img, lang='eng')
            text += page_text

    doc.close()
    return text.strip()

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image file"""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='eng')
    return text.strip()

def extract_text(file_path: str) -> str:
    """Route to correct extractor based on file type"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)
    else:
        return ""

# ==========================================
# STEP 2 — ENTITY EXTRACTION
# ==========================================

def extract_pan(text: str) -> str:
    # Handle spaced PAN like "A B C D E 1 2 3 4 F"
    # First try normal format
    match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    if match:
        return match.group(0)
    # Try spaced format
    match = re.search(r'\b([A-Z]\s){5}([0-9]\s){4}[A-Z]\b', text)
    if match:
        return match.group(0).replace(" ", "")
    return None

def extract_name(text: str) -> str:
    patterns = [
        r'(?:Employee Name|Account Name)\s*[:\-]\s*(?:Mr\.?|Mrs\.?|Ms\.?)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:नाम\s*/\s*Name)\s*\n\s*([A-Z][A-Z]+(?:\s+[A-Z]+)*)',
        r'^Name\s*\n\s*([A-Z][A-Z]+(?:\s+[A-Z]+)*)$'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            # Only take first line of match, strip noise
            name = match.group(1).strip().split('\n')[0].strip()
            # Remove if too long (picked up extra lines)
            if len(name) < 40:
                return name
    return None

def extract_address(text: str) -> str:
    excluded_pincodes = ['411045', '110064', '110054', '122003', '123456']
    
    matches = re.finditer(r'([A-Za-z0-9\s,\-\.]+?\b(\d{6})\b)', text)
    for match in matches:
        addr = match.group(1).strip()
        pincode = match.group(2)
        # Valid Indian pincodes start with 1-8 and are not in excluded list
        if pincode not in excluded_pincodes and pincode[0] in '12345678':
            # Must have some alphabetic content (real address, not just numbers)
            if re.search(r'[A-Za-z]{3,}', addr):
                return addr
    return None

def extract_income(text: str) -> float:
    clean_text = text.replace('₹', '').replace('\u20b9', '').replace('\xa0', ' ')
    clean_text = re.sub(r'(\d)\.,', r'\1,', clean_text)
    
    patterns = [
        # Handle "Total Net Payable      \n64,900.00" with spaces and newline
        r'Total Net Payable[\s\n]+[₹\u20b9]?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)',
        r'(?:Total Income)\s*\n?\s*([0-9]{1,2},[0-9]{2},[0-9]{3})',
        r'(?:Total Income)\s*\n?\s*([0-9]{4,8}(?:,[0-9]{3})*)',
        r'BULK POSTING-SALARY[^\n]+?([0-9]{4,7}(?:,[0-9]{3})*\.[0-9]{2})',
        r'(?:Gross Earnings)\s*\n?\s*([0-9]{4,7}(?:,[0-9]{3})*(?:\.[0-9]{2})?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '')
            try:
                val = float(value)
                if val > 1000:
                    return val
            except:
                continue
    return None

def extract_employer(text: str) -> str:
    # Normalize to company name only
    known_employers = ["Infosys", "TCS", "Wipro", "HCL", "Accenture", "Cognizant"]
    for employer in known_employers:
        if employer.lower() in text.lower():
            return employer
    patterns = [
        r'(?:Employer|Company Name|Organisation)\s*[:\-]\s*([A-Za-z\s]+(?:Ltd|Limited|Pvt|Inc)?)',
        r'SALARY-([A-Z][A-Z\s]+?)(?:\n|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().split('\n')[0]
    return None

# ==========================================
# STEP 3 — METADATA ANALYSIS
# ==========================================

def check_pdf_metadata(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    doc.close()

    suspicious = False
    reasons = []

    creator = metadata.get("creator", "").lower()
    producer = metadata.get("producer", "").lower()

    # Only flag genuinely suspicious editing tools
    # Normal tools: Microsoft Print to PDF, Skia, LibreOffice, Word, Chrome
    safe_producers = ["microsoft", "skia", "libreoffice", "openoffice", "cairo", "fpdf", "reportlab"]
    suspicious_tools = ["photoshop", "illustrator", "gimp", "inkscape"]

    for tool in suspicious_tools:
        if tool in creator or tool in producer:
            suspicious = True
            reasons.append(f"Document created/edited with {tool.title()}")

    return {
        "creator": metadata.get("creator", "Unknown"),
        "producer": metadata.get("producer", "Unknown"),
        "creation_date": metadata.get("creationDate", "Unknown"),
        "is_suspicious": suspicious,
        "reasons": reasons
    }

# ==========================================
# STEP 4 — CROSS DOCUMENT CORRELATION
# ==========================================

def correlate_documents(docs: dict) -> dict:
    """
    docs = {
        "salary_slip": "/path/to/salary_slip.pdf",
        "itr": "/path/to/itr.pdf",
        "bank_statement": "/path/to/bank_statement.pdf",
        "aadhaar": "/path/to/aadhaar.pdf",
        "pan": "/path/to/pan.pdf"
    }
    """
    extracted = {}
    metadata_results = {}

    print("\nExtracting text from documents...")
    for doc_type, path in docs.items():
        if path and os.path.exists(path):
            print(f"  Processing {doc_type}...")
            extracted[doc_type] = extract_text(path)
            if path.endswith(".pdf"):
                metadata_results[doc_type] = check_pdf_metadata(path)
        else:
            print(f"  Skipping {doc_type} — file not found")
            extracted[doc_type] = ""

    # Extract entities from each document
    entities = {}
    for doc_type, text in extracted.items():
        entities[doc_type] = {
            "pan": extract_pan(text),
            "name": extract_name(text),
            "address": extract_address(text),
            "income": extract_income(text),
            "employer": extract_employer(text),
            "raw_text_length": len(text)
        }

    print("\nExtracted entities:")
    for doc_type, ent in entities.items():
        print(f"  {doc_type}: PAN={ent['pan']}, Name={ent['name']}, Income={ent['income']}")

    # ---- CONSISTENCY CHECKS ----
    flags = []
    checks = {}

    # PAN consistency
    pans = [e["pan"] for e in entities.values() if e["pan"]]
    unique_pans = set(pans)
    checks["pan_match"] = 1 if len(unique_pans) <= 1 else 0
    if checks["pan_match"] == 0:
        flags.append(f"PAN mismatch detected: {unique_pans}")

    # Name consistency
    names = [e["name"].upper() for e in entities.values() if e["name"]]
    unique_names = set(names)
    checks["aadhaar_name_match"] = 1 if len(unique_names) <= 1 else 0
    if checks["aadhaar_name_match"] == 0:
        flags.append(f"Name mismatch across documents: {unique_names}")

    # Address consistency
    addresses = [e["address"] for e in entities.values() if e["address"]]
    checks["address_match"] = 1
    if len(addresses) >= 2:
        # Simple check — do they share a pincode
        pincodes = [re.search(r'\d{6}', a).group() for a in addresses if re.search(r'\d{6}', a)]
        if len(set(pincodes)) > 1:
            checks["address_match"] = 0
            flags.append(f"Address pincode mismatch: {set(pincodes)}")

    # Salary vs ITR income check
    salary_income = entities.get("salary_slip", {}).get("income")
    itr_income = entities.get("itr", {}).get("income")
    bank_income = entities.get("bank_statement", {}).get("income")

    income_difference_pct = None
    checks["salary_itr_match"] = 1
    if salary_income and itr_income:
        # Salary slip shows monthly, ITR shows annual
        annual_from_salary = salary_income * 12
        diff_pct = abs(annual_from_salary - itr_income) / itr_income * 100
        income_difference_pct = round(diff_pct, 2)
        checks["salary_itr_match"] = 1 if diff_pct <= 20 else 0
        if checks["salary_itr_match"] == 0:
            flags.append(
                f"Income mismatch: Salary implies ₹{annual_from_salary:,.0f}/year "
                f"but ITR declares ₹{itr_income:,.0f} — {diff_pct:.1f}% difference"
            )

    # Bank vs salary check
    checks["bank_salary_match"] = 1
    if bank_income and salary_income:
        diff = abs(bank_income - salary_income) / salary_income * 100
        checks["bank_salary_match"] = 1 if diff <= 15 else 0
        if checks["bank_salary_match"] == 0:
            flags.append(
                f"Bank credit ₹{bank_income:,.0f} inconsistent "
                f"with salary ₹{salary_income:,.0f}"
            )

    # Employer consistency
    employers = [e["employer"] for e in entities.values() if e["employer"]]
    checks["employer_match"] = 1 if len(set(employers)) <= 1 else 0
    if checks["employer_match"] == 0:
        flags.append(f"Employer name mismatch: {set(employers)}")

    # Metadata check
    metadata_suspicious = 0
    edited_in_photoshop = 0
    for doc_type, meta in metadata_results.items():
        if meta["is_suspicious"]:
            metadata_suspicious = 1
            for reason in meta["reasons"]:
                if "photoshop" in reason.lower():
                    edited_in_photoshop = 1
                flags.append(f"[{doc_type}] {reason}")

    # OCR confidence — average text length as proxy
    text_lengths = [e["raw_text_length"] for e in entities.values() if e["raw_text_length"] > 0]
    avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
    ocr_confidence = min(100, round(avg_length / 20, 1))

    checks["metadata_suspicious"] = metadata_suspicious
    checks["edited_in_photoshop"] = edited_in_photoshop

    return {
        "extracted_entities": entities,
        "consistency_checks": checks,
        "flags": flags,
        "income_difference_pct": income_difference_pct,
        "ocr_confidence": ocr_confidence,
        "metadata": metadata_results
    }


# ==========================================
# QUICK TEST
# ==========================================

if __name__ == "__main__":
    sample_docs = {
        "salary_slip": "sample_docs/salary_slip.pdf",
        "itr": "sample_docs/itr.pdf",
        "bank_statement": "sample_docs/bank_statement.pdf",
        "aadhaar": "sample_docs/aadhaar.pdf",
        "pan": "sample_docs/pan.pdf"
    }

    result = correlate_documents(sample_docs)

    print("\n========== CORRELATION RESULT ==========")
    print("\nConsistency Checks:")
    for check, value in result["consistency_checks"].items():
        if check in ["metadata_suspicious", "edited_in_photoshop"]:
            status = "✓ PASS" if value == 0 else "✗ FAIL"
        else:
            status = "✓ PASS" if value == 1 else "✗ FAIL"
        print(f"  {check}: {status}")

    print(f"\nIncome Difference: {result['income_difference_pct']}%")
    print(f"OCR Confidence: {result['ocr_confidence']}")

    print("\nFlags Raised:")
    if result["flags"]:
        for flag in result["flags"]:
            print(f"  - {flag}")
    else:
        print("  No flags raised")

    
