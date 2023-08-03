import matplotlib.animation as animation
import matplotlib.pyplot as plt
import tkinter as tk
import numpy as np
import serial
import os
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
from animation_function import animate
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
from threading import Thread, Event


def receive_cyclic_data(event: Event(), close_event: Event(), delete_data_event: Event(), cnt, ser: serial.Serial()):
    """
    Function receiving cyclic data from external sensor and saving it to temporary file. Data are stored in FIFO queue.

    Parameters:
        event - manages an internal flag that can be set to true or false. If set to True data are saving in "temp_data.txt" file.
        close_event - -||-. If set to True, application end life and data are not saving.
        delete_data_event - -||-. If set to True, clear "temp_data.txt" file.
        cnt - counter, used to save index of data in "temp_data.txt"
        ser - serial port

    """

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
                    file_data.close()
            else:
                bytesWaiting = ser.inWaiting()
                if (bytesWaiting != 0):
                    takeData(ser)


def save_file():
    """
    Function saving data to .txt file
    """
    f = asksaveasfile(initialfile="Untitled.txt", defaultextension=".txt", filetypes=[
                      ("All Files", "*.*"), ("Text documents", "*.txt*")])
    if f is None:
        return
    text2save = open("temp_data.txt", "r")
    for i in text2save:
        f.write(i)
    f.close()


def delete_data(file_name, delete_data_event: Event()):
    """
    Function deleting data from temporary file

    Parameters:
        file_name - name of temporary file.
        delete_data_event - Event, used with other Threads to prevent racing.
    """
    delete_data_event.set()
    data = open(file_name, "a")
    data.truncate(0)
    data.close()


def add(ser):
    """
    Function writing to serial port '0' - adding '3' to micro controller variable
    """
    ser.write(b'0')


def subtract(ser):
    """
    Function writing to serial port '1' - subtracting '2' from micro controller variable
    """
    ser.write(b'1')


def reset(ser):
    """
    Function writing to serial port '2' - changing micro controller variable to '0'
    """
    ser.write(b'2')


def takeData(ser):
    """
    Function taking data from serial port (FIFO queue)

    Return:
        decoded value of sensor
    """
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
