from pypdf import PdfReader, PdfWriter, Transformation

# # # # BONUS TOOL!
# Annoyed with your competitor cards from Groupifier being cut off at the top when you print them?
# This shifts everything down on the page by an inputted number of pixels so that doesn't happen

filename = input("Give filepath please (no quotes around): ")
reader = PdfReader(filename)
writer = PdfWriter()

dx = int(input("how many pixels down (10 recommended): "))
for page in reader.pages:
    page.add_transformation(Transformation().translate(tx=0, ty=-dx))
    writer.add_page(page)

with open(f'{filename[:-4]}_shifted.pdf', "wb") as f:
    writer.write(f)
