import qrcode,json
from PIL import Image
from io import BytesIO

def generate_checksum(text):
    """Generate CRC-16-CCITT checksum for VietQR"""
    crc = 0xFFFF  # initial value
    polynomial = 0x1021  # 0001 0000 0010 0001 (0, 5, 12)
    bytes_data = text.encode('utf-8')
    
    for byte in bytes_data:
        for i in range(8):
            bit = ((byte >> (7 - i)) & 1) == 1
            c15 = ((crc >> 15) & 1) == 1
            crc <<= 1
            if c15 ^ bit:
                crc ^= polynomial
    
    return format(crc & 0xFFFF, '04x')


def generate_vietqr_content(bank_code, bank_account, amount, message):
    """Generate VietQR code content string"""
    # Bank ID mapping
    with open('code_bank.json', 'r', encoding='utf-8') as f:
      bank_id_by_code=json.load(f)
    bank_id = bank_id_by_code[bank_code]['bin']
    if not bank_id:
        raise ValueError(f"Unknown bank code: {bank_code}. Please check the bank code and try again.")
    
    # Build part 12
    part12 = (
        "00" +
        f"{len(bank_id):02d}" +
        bank_id +
        "01" +
        f"{len(bank_account):02d}" +
        bank_account
    )
    
    # Build part 11
    part11 = (
        "0010A000000727" +
        "01" +
        f"{len(part12):02d}" +
        part12 +
        "0208QRIBFTTA"
    )
    
    # Build part 1
    part1 = (
        "38" +
        f"{len(part11):02d}" +
        part11
    )
    
    # Build part 21
    part21 = (
        "08" +
        f"{len(message):02d}" +
        message
    )
    
    # Build part 2
    part2 = (
        "5303704" +
        "54" +
        f"{len(amount):02d}" +
        amount +
        "5802VN" +
        "62" +
        f"{len(part21):02d}" +
        part21
    )
    
    # Build final QR code content without checksum
    builder = (
        "000201" +
        "010212" +
        part1 +
        part2 +
        "6304"
    )
    
    # Generate and append checksum
    checksum = generate_checksum(builder).upper()
    qrcode_content = builder + checksum
    
    return qrcode_content

def generate_vietqr_bytes(bank_code, bank_account, amount, message, box_size=10, border=4):
    qr_content = generate_vietqr_content(bank_code, bank_account, amount, message)
    qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=box_size,border=border,)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    bio.name = 'vietqr.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio