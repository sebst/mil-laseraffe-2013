
from tkinter import *
from PIL import Image, ImageTk

# root = Tk()

# image = Image.open('affe.png')
# display = ImageTk.PhotoImage(image)

# label = Label(root, image=display)
# label.pack()

# root.mainloop()




# root = Tk()
# var = StringVar()
# label = Label( root, textvariable=var, relief=RAISED )
# var.set("Hey!? How are you doing?")
# label.pack()
# root.mainloop()



# root = Tk()
# label = Label( root, text="Hello")
# label.pack()
# root.mainloop()

print(Image)

# class MainWin:
#     def __init__(self):
#         self.tk = Tk()
#         self.l()
#     def l(self):
#         image = Image.open('affe.png')
#         display = ImageTk.PhotoImage(image)
#         label = Label( self.tk, image=display)
#         # label = Label( self.tk, text="Hello")
#         label.pack()
# w = MainWin()
# w.tk.mainloop()


tk = Tk()


def keyup(e):
    print('up', e.char)
def keydown(e):
    print('down', e.char)


image = Image.open('affe.png')
display = ImageTk.PhotoImage(image)
label = Label( tk, image=display)
label.pack()

# frame = Frame(root, width=100, height=100)
# frame.bind("<KeyPress>", keydown)
# frame.bind("<KeyRelease>", keyup)
# frame.pack()
# frame.focus_set()

tk.mainloop()