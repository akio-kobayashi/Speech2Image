import tkinter
from PIL import Image, ImageTk

window_geometory="1024x768"
canvas_width=640
canvas_height=480

version = tkinter.Tcl().eval('info patchlevel')
window = tkinter.Tk()
window.geometry(window_geometory)
window.title("画像表示:"+version)

canvas = tkinter.Canvas(window, bg="#fff", height=canvas_height, width=canvas_width)
canvas.place(x=0, y=0)

#img = tkinter.PhotoImage(file='test.png', width=200, height=200)
img = Image.open('test.png')
img = img.resize(( int(img.width * (canvas_width/img.width)), int(img.height * (canvas_height/img.width)) ))
img = ImageTk.PhotoImage(img)

canvas.create_image(0, 0, image=img, anchor=tkinter.NW)

window.mainloop()
