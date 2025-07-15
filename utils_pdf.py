from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Laporan Produksi Harian", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Halaman {self.page_no()}", align="C")

def generate_report(data, kategori_order):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    tanggal = data[0]["Tanggal"] if data else datetime.today().date().isoformat()
    pdf.cell(0, 10, f"Tanggal Produksi: {tanggal}", ln=True)
    pdf.ln(5)

    for kategori in kategori_order:
        items = [item for item in data if item["Kategori"] == kategori]
        if items:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, kategori, ln=True)
            pdf.set_font("Arial", size=11)

            for item in items:
                nama   = item["Nama Barang"]
                masuk  = item["Masuk"]
                keluar = item["Keluar"]
                pdf.cell(0, 10, f"- {nama}  |  Masuk: {masuk}  |  Keluar: {keluar}", ln=True)
            pdf.ln(3)

    return bytes(pdf.output(dest="S"))
