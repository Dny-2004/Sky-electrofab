from PIL import Image

img = Image.open('images/logo.jpg')
img = img.convert("RGBA")
datas = img.getdata()

newData = []
# If it's a checkerboard, it's usually exactly #ccc and #fff or similar. 
# Let's just make anything very light or specific greys transparent.
for item in datas:
    # item is (R, G, B, A)
    # Check if pixel is white or light grey (like the checkerboard)
    r, g, b, a = item
    
    # Simple thresholding: if pixel is close to white or is light gray
    if (r > 200 and g > 200 and b > 200) or (abs(r-g)<10 and abs(g-b)<10 and r > 150):
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save("images/logo.png", "PNG")
print("Saved transparent logo as logo.png")
