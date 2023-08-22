from manim import *
import cv2

# manim -pqh first.py ImageTrace

class ImageTrace(Scene):
    def construct(self):

        self.camera.background_color = WHITE

        img = cv2.imread("/Users/fred/Development/PloTTY/cache/CAT.jpg", cv2.IMREAD_GRAYSCALE)
        # img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        _, img = cv2.threshold(img, 55, 255, cv2.THRESH_BINARY)

        # img = 255-cv2.ximgproc.thinning(255-img)

        print( "CREATING" )
        pixels = []
        # (X,Y) = (520, 470)
        # (W,H) = (55, 55)
        (X,Y) = (385, 410)
        (W,H) = (85, 70)
        for x in range( X-W, X+W ):
            for y in range( Y-H, Y+H ):
                if img[y,x]!=255 :
                    # print( x,y, img[x,y] )
                    pixels.append( Square(
                        fill_color=BLACK,
                        fill_opacity=1.0,
                        stroke_color=BLACK,
                        stroke_opacity=1.0,
                        stroke_width=0/100.0,
                        side_length=5/100.0
                        ).move_to([(x-X)/17,-(y-Y)/17,0]) )
        print( "DONE" )

        # left_square = Square(color=BLUE, fill_opacity=0.7).shift(2 * LEFT)
        # right_square = Square(color=GREEN, fill_opacity=0.7).shift(2 * RIGHT)
        # self.play(
        #     left_square.animate.rotate(PI), Rotate(right_square, angle=PI), run_time=2
        # )

        self.add( *pixels )
        self.wait()
