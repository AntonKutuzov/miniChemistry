import sys
from pathlib import Path

def make_pdf(text, out_file):
    lines = text.splitlines()
    y = 800
    content_lines = []
    for line in lines:
        escaped = line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
        content_lines.append(f"BT /F1 12 Tf 72 {y} Td ({escaped}) Tj ET")
        y -= 14
    content = "\n".join(content_lines).encode('latin-1', 'ignore')

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n")
    objects.append(f"4 0 obj << /Length {len(content)} >> stream\n".encode('ascii') + content + b"\nendstream\nendobj\n")
    objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    pdf = b"%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj
    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode('ascii')
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode('ascii')
    pdf += f"trailer << /Root 1 0 R /Size {len(objects)+1} >>\nstartxref\n{xref_offset}\n%%EOF".encode('ascii')

    Path(out_file).write_bytes(pdf)

if __name__ == '__main__':
    inp = Path(sys.argv[1]).read_text(encoding='utf-8')
    make_pdf(inp, sys.argv[2])
