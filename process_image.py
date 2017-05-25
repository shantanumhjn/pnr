from PIL import Image, ImageOps, ImageFilter
from pytesseract import image_to_string

im = Image.open('capta.png')
print image_to_string(im, config = '-psm 7')

im1 = im.convert('L')
im1.save("capta1.png", "PNG")
print image_to_string(im1, config = '-psm 7')

im2 = im1.filter(ImageFilter.EDGE_ENHANCE).convert('1')
im2.save("capta2.png", "PNG")
print image_to_string(im2, config = '-psm 7')

w, h = im2.size
array = (list(im2.getdata()))
bits = []
for i in range(h):
    a = array[:w]
    del array[:w]
    bits.append(a)

new_bits = []
for a in bits:
    new_bits.append(list(a))

def print_array(data):
    for a in data:
        out = ""
        for i in a:
            if i == 255: i = 1
            out += str(i)
        print out

for i in range(len(bits)):
    for j in range(len(bits[i])):
        val = bits[i][j]
        if val == 255:
            tl = bits[i-1][j-1]
            tt = bits[i-1][j]
            tr = bits[i-1][j+1]
            ll = bits[i][j-1]
            rr = bits[i][j+1]
            bl = bits[i+1][j-1]
            bb = bits[i+1][j]
            br = bits[i+1][j+1]
            adjs = [tl, tt, tr, ll, rr, bl, bb, br]
            found = False
            for adj in adjs:
                if adj == 255:
                    found = True
                    break
            if not found:
                new_bits[i][j] = 0

print 'original:'
print_array(bits)
print
print 'new:'
print_array(new_bits)

# im1 = im1.convert('1')
# im1 = ImageOps.invert(im1)
# im = ImageOps.invert(im)

# im1 = im.convert('1')
#
# w, h = im.size
#
# factor = 10
# print w, h
#
# new_size = w*factor, h*factor
# print new_size
#
# im_resized = im1.resize(new_size, Image.ANTIALIAS)
# im_resized.save("capta2.png", "PNG")
#
#

# print image_to_string(im_resized, config = '-psm 7')
#
# im_resized1 = im_resized.convert('L')
# im_resized1.save("capta3.png", "PNG")
# print image_to_string(im_resized1, config = '-psm 7')
