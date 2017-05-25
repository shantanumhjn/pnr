from PIL import Image, ImageOps, ImageFilter
from pytesseract import image_to_string


def process1(img):
    im1 = img.convert('L').filter(ImageFilter.EDGE_ENHANCE).convert('1')
    return im1

def process2(img):
    new_img = img.copy()
    w, h = img.size
    for i in range(h):
        for j in range(w):
            if img.getpixel((j, i)) == 255:
                tl = img.getpixel((j-1, i-1))
                tt = img.getpixel((j, i-1))
                tr = img.getpixel((j+1, i-1))
                ll = img.getpixel((j-1, i))
                rr = img.getpixel((j+1, i))
                bl = img.getpixel((j-1, i+1))
                bb = img.getpixel((j, i+1))
                br = img.getpixel((j+1, i+1))
                adjs = [tl, tt, tr, ll, rr, bl, bb, br]
                found = False
                for adj in adjs:
                    if adj == 255:
                        found = True
                        break
                if not found:
                    new_img.putpixel((j, i), 0)
    return new_img

def print_img(img):
    w, h = img.size
    for i in range(h):
        out = ""
        for j in range(w):
            val = img.getpixel((j, i))
            if val == 0:
                val = ' '
            else:
                val = 8
            out += str(val)
        print out

def do_stuff(inp):
    print image_to_string(inp, config = '-psm 7')
    inp.save('capta.png', 'PNG')
    img = process1(inp)
    img.save('capta1.png', 'PNG')
    print 'original:'
    print_img(img)
    print 'OCR output:', image_to_string(img, config = '-psm 7')
    print
    img2 = process2(img)
    img2.save('capta2.png', 'PNG')
    print 'new:'
    print_img(img2)
    print 'OCR output:', image_to_string(img2, config = '-psm 7')
    w, h = img2.size
    size = (w*2, h*2)
    img3 = img2.resize(size, Image.ANTIALIAS)
    img3.save('capta4.png', 'PNG')
    print '\nimage resized * 2'
    print 'OCR output:', image_to_string(img3, config = '-psm 7')
    size = (w*3, h*3)
    img4 = img2.resize(size, Image.ANTIALIAS)
    img4.save('capta5.png', 'PNG')
    print '\nimage resized * 3'
    print 'OCR output:', image_to_string(img4, config = '-psm 7')


if __name__ == "__main__":
    im = Image.open('capta.png')
    print image_to_string(im)
    img = process1(im)
    print 'original:'
    print_img(img)
    print 'OCR output:', image_to_string(img, config = '-psm 7')
    print
    img2 = process2(img)
    print 'new:'
    print_img(img2)
    print 'OCR output:', image_to_string(img2)
