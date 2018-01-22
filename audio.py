from tkinter import *
from tkinter.ttk import Frame, Button, Style, Label
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy
import numpy as np
import wave
import contextlib
from scipy.io import wavfile
# import sounddevice as sd

class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.canvas1 = None
        self.initUI()

    def initUI(self):
        self.parent.title("Audio Signal")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=True)
        frame1 = Frame(self, relief = RAISED, borderwidth=1)
        frame1.pack(fill=X)

        browseButton=Button(frame1, text="Chọn file", command=self.browseFile)
        browseButton.pack(side=LEFT, padx=5, pady=5)

        self.label1 = Label(frame1)
        self.label1.pack(side=LEFT)

        frame2 = Frame(self, relief=RAISED, borderwidth=1)
        frame2.pack(fill=X)
        label1 = Label(frame2, text='Chiều dài frame (số mẫu)')
        label1.pack(side=LEFT, padx = 20)
        self.entry1 = Entry(frame2)
        self.entry1.pack(side=LEFT)

        frame3 = Frame(self, relief=RAISED, borderwidth=1)
        frame3.pack(fill=X)
        label2 = Label(frame3, text='Mức năng lượng')
        label2.pack(side=LEFT, padx = 43)
        self.entry2 = Entry(frame3)
        self.entry2.pack(side=LEFT)

        frame6 = Frame(self, relief=RAISED, borderwidth=1)
        frame6.pack(fill=X)
        label3 = Label(frame6, text='Ngưỡng thời gian(ms)')
        label3.pack(side=LEFT, padx = 28)
        self.entry3 = Entry(frame6)
        self.entry3.pack(side=LEFT)

        frame5 = Frame(self, relief=RAISED, borderwidth=1)
        frame5.pack(fill=X)
        label14 = Label(frame5, text='Số thứ tự âm được tách')
        label14.pack(side=LEFT, padx=25)
        self.entry4 = Entry(frame5)
        self.entry4.pack(side=LEFT)

        frame4 = Frame(self, relief=RAISED, borderwidth=1)
        frame4.pack(fill=X)
        self.pack(fill=BOTH, expand=True)
        drawButton = Button(frame4, text="Vẽ đồ thị", command=self.draw_handle_file)
        drawButton.pack(side=LEFT, padx=5, pady=5)
        # drawButton2 = Button(frame4, text="F0", command=self.draw_f0)
        # drawButton2.pack(side=LEFT, padx=5, pady=5)
        drawButton3 = Button(frame4, text="Nghe âm cơ bản", command=self.listen)
        drawButton3.pack(side=LEFT, padx=5, pady=5)
        drawButton4 = Button(frame4,text="Nghe hamming", command=self.listen_hamming)
        drawButton4.pack(side=LEFT, padx=5, pady=5)

        self.frame5 = Frame(self, relief=RAISED, borderwidth=1)
        self.frame5.pack(fill=BOTH)
        self.pack(fill=BOTH, expand=True)
    def browseFile(self):
        from tkinter.filedialog import askopenfilename
        self.filename = askopenfilename()
        self.label1['text'] = self.filename

    def draw_handle_file(self):
        # global sound
        if(self.canvas1 != None):
            self.canvas1.get_tk_widget().destroy()
        self.a = Figure()
        self.canvas1 = FigureCanvasTkAgg(self.a, self.frame5)
        self.b = self.a.add_subplot(131)
        self.c = self.a.add_subplot(132)
        self.d = self.a.add_subplot(133)
        self.fs, data = wavfile.read(self.filename)
        self.data = data
        self.n = len(data)
        self.frame_len= int(self.entry1.get())
        self.i = int(self.entry4.get())
        number_frame = np.floor(self.n / self.frame_len) + 1
        data_add = [0 for i in range(int(number_frame * self.frame_len) - self.n)]
        data = numpy.append(data, data_add)
        # self.data = data
        energy = int(self.entry2.get())
        i = 0
        no_signal = 1 # khong co tin hieu
        y = [max(data), min(data)]
        time_limit = int(self.entry3.get())
        self.b.plot(data)
        time = (self.b.get_xticks() * 1000 / self.fs)
        time = (self.b.get_xticks()*1000/self.fs).astype(int)
        self.b.set_xticklabels(time)
        self.b.set_xlabel('T(ms)')
        j = 0
        k = 0
        k1= 0
        self.sound = []

        #================đánh dấu khoảng lặng âm thanh=================
        while i <= self.n - self.frame_len:
            frame = data[int(i):int(i + self.frame_len - 1)]
            nang_luong = np.mean(np.square(frame))
            if (nang_luong > energy):
                if (no_signal == 1):# nang luong > energy va truoc do k co tin hieu
                    # x = [i, i]
                    j = i
                    # self.b.plot(x, y, 'r') # ve mau do
                no_signal = 0 #set trang thai co tin hieu
            else:
                if (no_signal == 0): # nang luong < energy va truoc do co tin hieu
                    # x = [i, i]
                    k = i
                    # self.b.plot(x, y, 'g') # ve mau xanh
                no_signal = 1 # set ve trang thai k co tin hieu
            if ((k-j > time_limit) and (k!=k1)):
                x1 = [j, j]
                x2 = [k, k]
                # self.sound = [j, k]
                self.sound = self.sound + [j, k]# sound lưu các điểm đánh dấu của âm thanh
                self.b.plot(x1, y, 'r')
                self.b.plot(x2, y, 'g')
                k1 = k
            i = i + self.frame_len / 2
        #===xong===

        #===========tìm tần số cơ bản f0 của âm thanh=============
        # print(self.sound)
        self.sound1 = data[int(self.sound[2*self.i-2]):int(self.sound[2*self.i-1])]
        # sound1 là mảng lưu trữ giá trị các mẫu của âm thanh đâu tiên
        self.f0=[] # mảng f lưu giá trị tần số f0 của các frame của âm thanh đầu tiên
        n = 0# giống tài liệu
        k = 0
        # N = frame_len = 350
        # K = 150
        i = 0*self.frame_len # frame thu 20
        rk = 0
        j = 0
        sum = 0 # tổng giá trị các rk, sum = R(k)
        while i < len(self.sound1)-self.frame_len:
            self.Rk = []  # mảng lưu giá trị mẫu của frame đầu tiên của âm thanh đâu tiên
            for k in range(0,151,1):# k chay tu 0 den K = 150
                for n in range(0, self.frame_len - 1 - k,1):
                    # print(self.sound[n+k])
                    rk= (self.sound1[n+i]*self.sound1[n+k+i]).astype(float)
                    sum = sum + rk
                # hết vòng lặp for n thì có 1 giá trị Rk, sum = rk
                self.Rk.append(sum)# them phan tu sum vao mang Rk
                sum = 0
            # hết vòng lặp for k có mảng self.Rk gồm các Rk của frame đầu tiên
            Rk_max = 0
            j_max = 0
            for j in range(1,150):
                if (self.Rk[j] > self.Rk[j - 1] and self.Rk[j] > self.Rk[j + 1]):
                    if(Rk_max<self.Rk[j]):
                        Rk_max = self.Rk[j]
                        j_max = j
            tanso = self.fs/j_max
            if(tanso > 80 and tanso<400):
                self.f0.append(tanso)
            i = i + self.frame_len
        self.c.set_title("F0 của âm thanh cơ bản")
        self.c.set_ylim(0,800)
        self.c.plot(self.f0)
        # ==============nhân tín hiệu với hàm hamming================
        self.hammingArr = []
        i=600
        multi=np.hamming(self.frame_len)
        while i < len(self.sound1)-self.frame_len:
            hamArr = []
            hamArr = list(self.sound1[i:i+self.frame_len]*multi)#nhân tín hiệu với hamming
            print(i)
            self.hammingArr = self.hammingArr + hamArr
            i = i + self.frame_len
        # c.set_ylim(0, 800)

        #==========tìm f0 của hamming============
        self.f0_hamming = []  # mảng f lưu giá trị tần số f0 của các frame của âm thanh đầu tiên
        n = 0  # giống tài liệu
        k = 0
        # N = frame_len = 350
        # K = 150
        i = 0 * self.frame_len  # frame thu 20
        rk = 0
        j = 0
        sum = 0  # tổng giá trị các rk, sum = R(k)
        while i < len(self.hammingArr) - self.frame_len:
            self.Rk_hamming = []  # mảng lưu giá trị mẫu của frame đầu tiên của âm thanh đâu tiên
            for k in range(0, 151, 1):  # k chay tu 0 den K = 150
                for n in range(0, self.frame_len - 1 - k, 1):
                    # print(self.sound[n+k])
                    rk = (self.hammingArr[n + i] * self.hammingArr[n + k + i]).astype(float)
                    sum = sum + rk
                # hết vòng lặp for n thì có 1 giá trị Rk, sum = rk
                self.Rk_hamming.append(sum)  # them phan tu sum vao mang Rk
                sum = 0
            # hết vòng lặp for k có mảng self.Rk gồm các Rk của frame đầu tiên
            Rk_max = 0
            j_max = 0
            for j in range(1, 150):
                if (self.Rk_hamming[j] > self.Rk_hamming[j - 1] and self.Rk_hamming[j] > self.Rk_hamming[j + 1]):
                    if (Rk_max < self.Rk_hamming[j]):
                        Rk_max = self.Rk_hamming[j]
                        j_max = j
            tanso = self.fs / j_max
            if (tanso > 80 and tanso < 400):
                self.f0_hamming.append(tanso)
            i = i + self.frame_len
        # self.d.plot(self.hammingArr)
        self.d.set_title('Tần số F0 của hàm hamming')
        self.d.set_ylim(0, 800)
        self.d.plot(self.f0_hamming)
        self.canvas1.get_tk_widget().pack(fill=BOTH, expand=True)
        self.canvas1.draw()
    def listen(self):
        import sounddevice as sd
        sd.play(self.data[int(self.sound[self.i*2-2]):int(self.sound[self.i*2-1])], self.fs)
        # sd.play(self.hammingArr,self.fs)
    def listen_hamming(self):
        import sounddevice as sd
        # sd.play(self.data[int(self.sound[self.i*2-2]):int(self.sound[self.i*2-1])], self.fs)
        sd.play(self.hammingArr,self.fs)

root = Tk()
# root.geometry("800x600+300+300")
root.state("zoomed")
app = Example(root)
root.mainloop()
