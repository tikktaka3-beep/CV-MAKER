from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image

def generate_pdf(resume_data: dict, photo_path: str | None, template: str, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, resume_data["full_name"])
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 80, resume_data["position"])

    if photo_path:
        img = Image.open(photo_path)
        img.thumbnail((150, 150))
        img.save("processed_photo.jpg")
        c.drawImage("processed_photo.jpg", width - 200, height - 200, 150, 150)

    c.showPage()
    c.save()