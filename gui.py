import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
import serial
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import os
from threading import Thread, Event
import numpy as np
from tkinter import messagebox
from animation_function import animate

# if "ser.write(b'0')" add 3 to 'cnt'
# if "ser.write(b'1')" from 'cnt' subtract 2
# if "ser.write(b'2')" reset 'cnt' to 0


# def animate(i, file_name, f, a):
#     pullData = open(file_name, "r").read()
#     dataList = pullData.split('\n')
#     xList = []
#     yList = []
#     for eachLine in dataList:
#         if len(eachLine) > 1:
#             x, y = eachLine.split(',')
#             xList.append(int(x))
#             yList.append(int(y.strip()))
#     a[0].clear()
#     if len(xList) == 0:
#         a[0].set_ylim([-1, 1])
#     else:
#         a[0].set_ylim([-1, max(yList[-400:])+1])
#     if len(xList) >= 400:
#         a[0].plot(xList[-400:], yList[-400:])
#     else:
#         a[0].plot(xList, yList)


def receive_cyclic_data(event, close_event, delete_data_event, cnt, ser):
    while True:
        if close_event.is_set():
            break
        if delete_data_event.is_set():
            cnt = 0
            # takeData()
            delete_data_event.clear()
        else:
            if event.is_set():
                bytesWaiting = ser.inWaiting()
                if (bytesWaiting != 0):
                    file_data = open("temp_data.txt", "a")
                    data = takeData(ser)
                    if data:
                        cnt += 1
                        file_data.write(f"{cnt}, {data}\n")
            else:
                bytesWaiting = ser.inWaiting()
                if (bytesWaiting != 0):
                    takeData(ser)


def save_file():
    f = asksaveasfile(initialfile="Untitled.txt", defaultextension=".txt", filetypes=[
                      ("All Files", "*.*"), ("Text documents", "*.txt*")])
    if f is None:
        return
    text2save = open("temp_data.txt", "r")  # starts from `1.0`, not `0.0`
    for i in text2save:
        f.write(i)
    f.close()


def delete_data(file_name, delete_data_event):
    delete_data_event.set()
    data = open(file_name, "a")
    data.truncate(0)
    data.close()


def add(ser):
    ser.write(b'0')


def subtract(ser):
    ser.write(b'1')


def reset(ser):
    ser.write(b'2')


def takeData(ser):
    line = ser.readline()
    return line.decode('utf-8').strip()


class Windows(tk.Tk):
    def __init__(self, event: Event(), close_app_event: Event(), delete_data_event: Event(), ser: serial.Serial(), f, file_name, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title('Uart communication')

        self.event = event
        self.close_app_event = close_app_event
        self.delete_data_event = delete_data_event
        self.ser = ser
        self.fig = f
        self.file_name = file_name

        container = tk.Frame(self, height=400, width=600)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainPage, SecondPage, ThirdPage):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()

    def on_closing(self):
        self.event.clear()
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.close_app_event.set()
            self.destroy()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.event = controller.event
        self.close_app_event = controller.close_app_event
        self.delete_data_event = controller.delete_data_event
        self.ser = controller.ser
        self.fig = controller.fig
        self.file_name = controller.file_name

        # Menu frame
        menu_frame = tk.Frame(self)
        menu_frame.grid(row=0, column=0, sticky='W')
        menu_frame.config(bg='white')

        first_page = ttk.Button(
            menu_frame, text='Main Page', command=lambda: self.controller.show_frame(MainPage))
        first_page.grid(row=0, column=0, padx=5, pady=5)

        second_page = ttk.Button(
            menu_frame, text='Second Page', command=lambda: self.controller.show_frame(SecondPage))
        second_page.grid(row=0, column=1, padx=5, pady=5)

        third_page = ttk.Button(menu_frame, text="Third Page",
                                command=lambda: self.controller.show_frame(ThirdPage))
        third_page.grid(row=0, column=2, padx=5, pady=5)

        # Main frame
        main_frame = tk.Frame(self)
        main_frame.grid(row=1, column=0, sticky='W')

        # Buttons Frame
        buttons_frame = ttk.LabelFrame(
            main_frame, text="Communication buttons")
        buttons_frame.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

        # data transmitting
        self.stop_btn = ttk.Button(
            buttons_frame, text="Stop data Transmit", command=lambda: self.if_transmit(False))
        self.stop_btn.grid(row=0, column=0, padx=5, pady=5)

        self.start_btn = ttk.Button(
            buttons_frame, text="Start data transmit", command=lambda: self.if_transmit(True))
        self.start_btn.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

        # change data
        self.add_bnt = ttk.Button(buttons_frame, text="Add",
                                  style='my.TButton', command=lambda: add(self.ser))
        self.add_bnt.grid(row=1, column=0, padx=5, pady=5)

        self.subtract_bnt = ttk.Button(
            buttons_frame, text="Subtract", command=lambda: subtract(self.ser))
        self.subtract_bnt.grid(row=1, column=1, padx=5, pady=5)

        self.reset_btn = ttk.Button(
            buttons_frame, text="Reset", command=lambda: reset(self.ser))
        self.reset_btn.grid(row=1, column=2, padx=5, pady=5)

        # Showed value
        display_frame = ttk.LabelFrame(main_frame, text="Displayed variables")
        display_frame.grid(row=1, column=0, padx=5, pady=5)

        self.variable = tk.IntVar()
        self.variable.set(takeData(self.ser))

        counter_label = ttk.Label(display_frame, text="Counter:")
        counter_label.grid(row=0, column=0, padx=5, pady=5)
        counter_display = ttk.Label(
            display_frame, textvariable=self.variable, justify='right', width=10)
        counter_display.grid(row=0, column=1, padx=5,
                             pady=3, sticky='w')

        # Saving data to file
        save = ttk.Button(
            main_frame, text="Save data to file", command=save_file)
        save.grid(row=1, column=1)

        # Clearing temp_data.txt file
        clear = ttk.Button(main_frame, text="Delete data", command=lambda: delete_data(
            self.file_name, self.delete_data_event))
        clear.grid(row=1, column=2)

        # Chart display
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0)

        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.update()
        canvas._tkcanvas.grid()

    def if_transmit(self, par):
        if par:
            self.controller.event.set()
        else:
            self.controller.event.clear()


class SecondPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Menu frame
        menu_frame = tk.Frame(self)
        menu_frame.grid(row=0, column=0, sticky='W')
        menu_frame.config(bg='white')

        first_page = ttk.Button(
            menu_frame, text='Main Page', command=lambda: controller.show_frame(MainPage))
        first_page.grid(row=0, column=0, padx=5, pady=5)

        second_page = ttk.Button(
            menu_frame, text='Second Page', command=lambda: controller.show_frame(SecondPage))
        second_page.grid(row=0, column=1, padx=5, pady=5)

        third_page = ttk.Button(menu_frame, text="Third Page",
                                command=lambda: controller.show_frame(ThirdPage))
        third_page.grid(row=0, column=2, padx=5, pady=5)


class ThirdPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Menu frame
        menu_frame = tk.Frame(self)
        menu_frame.grid(row=0, column=0, sticky='W')
        menu_frame.config(bg='white')

        first_page = ttk.Button(
            menu_frame, text='Main Page', command=lambda: controller.show_frame(MainPage))
        first_page.grid(row=0, column=0, padx=5, pady=5)

        second_page = ttk.Button(
            menu_frame, text='Second Page', command=lambda: controller.show_frame(SecondPage))
        second_page.grid(row=0, column=1, padx=5, pady=5)

        third_page = ttk.Button(menu_frame, text="Third Page",
                                command=lambda: controller.show_frame(ThirdPage))
        third_page.grid(row=0, column=2, padx=5, pady=5)


def main():
    file_name = 'temp_data.txt'
    f, a = plt.subplots(2, 2)

    ser = serial.Serial('COM3', 38400, timeout=0.05)

    cnt = 0
    event = Event()
    close_app_event = Event()
    delete_data_event = Event()

    delete_data(file_name, delete_data_event)

    app = Windows(event, close_app_event, delete_data_event, ser, f, file_name)
    ani = animation.FuncAnimation(
        f, animate, interval=500, fargs=(file_name, f, a,),)

    Thread(target=receive_cyclic_data, args=(
        event, close_app_event, delete_data_event, cnt, ser, )).start()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)

    app.mainloop()
    ser.close()


if __name__ == "__main__":
    main()
