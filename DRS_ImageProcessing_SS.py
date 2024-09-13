from PIL import Image
#import pyserial
import time




def greyCheck(img):
    (width,height) = img.size
    print(width,height)
    for j in range(0, height,2):
        for i in range (width):
            (r,b,g) = img.getpixel((i,j))
            (r2,g2,b2) = img.getpixel((i+1,j))
            (r3,g3,b3) = img.getpixel((i,j+1))
            (r4,g4,b4) = img.getpixel((i+1,j+1))
            (r5,g5,b5) = img.getpixel((i+2,j))
            (r6,g6,b6) = img.getpixel((i+2,j+1))
            (r7,g7,b7) = img.getpixel((i+3,j))
            (r8,g8,b8) = img.getpixel((i+3,j+1))


            r_avg_1 = (r+r2+r3+r4)/4
            g_avg_1 = (g+g2+g3+g4)/4
            b_avg_1 = (b+b2+b3+b4)/4
            r_avg_2 = (r5+r6+r7+r8)/4
            g_avg_2 = (g5+g6+g7+g8)/4
            b_avg_2 = (b5+b6+b7+b8)/4
            if(50<r_avg_1<175 and 50<b_avg_1<175 and 50<b_avg_1<175):
                print(r_avg_1,g_avg_1,b_avg_1,"grey")

            if(50<r_avg_2<175 and 50<g_avg_2<175 and 50<b_avg_2<175):
                print(r_avg_2,g_avg_2,b_avg_2,"grey")

            if(50<r_avg_1<175 and 50<b_avg_1<175 and 50<b_avg_1<175 and 50<r_avg_2<175 and 50<g_avg_2<175 and 50<b_avg_2<175):
                print("still grey")

            else:
                print(r_avg_2,g_avg_2,b_avg_2,"not grey")

            time.sleep(0.5)
           
       
image = Image.open("red_and_grey_2.jpg")
image.show()
greyCheck(image)
