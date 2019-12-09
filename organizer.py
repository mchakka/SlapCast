import os
import shutil
import threading
import cv2
from subprocess import call, DEVNULL
from datetime import datetime
from tkinter import Tk, ttk, Frame, Label, HORIZONTAL, messagebox, OptionMenu, StringVar
from tkinter.filedialog import askopenfilename, askopenfilenames
from pyzbar.pyzbar import decode, ZBarSymbol
import collections

CURRENT = os.getcwd()

class Window(Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Clapper")
        self.master.geometry('400x450+450+200')
        self.master.config(bg="#1b1b1b")
        # self.master.resizable(0, 0)
        self.AddWidgets()

    def AddWidgets(self):
        global User_input
        fontColor = '#f8bbd0'
        bgColor = '#1b1b1b'
        fontColorDull = '#c29ca5'

        self.TopFrame = Frame(self.master, bg=bgColor, width=400, height=50)
        self.TopFrame.grid(row=1, column=0)

        self.TextLabel = Label(self.master, text="Welcome to Clapper", font="Laksaman", fg=fontColor, bg=bgColor)
        self.TextLabel.grid(row=1, column=0, padx=10, pady=10)

        self.TextLabel = Label(self.master, text="Project Title", font="Laksaman", fg=fontColor, bg=bgColor)
        self.TextLabel.grid(row=2, sticky='W', padx=10, pady=10)

        self.TextLabel = Label(self.master, text="Video File", font="Laksaman", fg=fontColor, bg=bgColor)
        self.TextLabel.grid(row=3, sticky='W', padx=10, pady=10)

        self.TextLabel = Label(self.master, text="Organization:", font="Laksaman", fg=fontColor, bg=bgColor)
        self.TextLabel.grid(row=4, sticky='W', padx=10, pady=10)

        self.User_input = ttk.Entry(self.master, width=15)
        self.User_input.grid(row=2, column=0)
        User_input = self.User_input

        self.button = ttk.Button(self.master, text="Browse", cursor="hand2", width=10, command=self.OpenFile)
        self.button.grid(row=3, column=0, padx=10, pady=10)

        self.processButton = ttk.Button(self.master, text="Start", cursor="hand2", width=10, command=self.Process)
        self.processButton.grid(row=4, column=0, padx=10, pady=10)

        # Hidden Initially

        self.OrgLabel = Label(self.master, text="Organizing...", font=("Laksaman", 12), fg=fontColorDull, bg=bgColor)

        self.CutLabel = Label(self.master, text="Compiling...", font=("Laksaman", 12), fg=fontColorDull, bg=bgColor)

        self.RoughLabel = Label(self.master, text="Rough Cut:", font="Laksaman", fg=fontColorDull, bg=bgColor)

        self.CutButton = ttk.Button(self.master, text="Start", cursor="hand2", width=10, command=self.ScenePicker)

        self.progress = ttk.Progressbar(self.master, orient=HORIZONTAL, length=100,  mode='determinate')

    def ScenePicker(self):
        global wantedTakes
        i = 7
        wantedTakes = {}
        for scene in sorted(timeStampsCleaned):
            takeList = list(timeStampsCleaned[scene].keys())
            wantedTakes[scene] = StringVar(self.master)
            wantedTakes[scene].set(takeList[0])
            self.PickerLabel = Label(self.master, text=("What take would you like for scene %s" % scene))
            self.PickerLabel.grid(row = i, column = 0)
            self.Picker = OptionMenu(self.master, wantedTakes[scene], *takeList)
            self.Picker.grid(row = i+1, column = 0)
            i += 2

        self.finishedButton = ttk.Button(self.master, text="Finish", cursor="hand2", width=10, command=self.CompileCut)
        self.finishedButton.grid(row=i+1, column=0)

    def OpenFile(self):
        #global inputDir
        global inputVideos
        inputVideos = []
        # Get the file
        files = askopenfilenames(initialdir=CURRENT, filetypes=[("Video Files", "*.mov *.mp4 *.avi")])
        print(files)
        # Split the filepath to get the directory
        for file in files:
            inputDir = os.path.split(file)[0]
            inputVideo = os.path.split(file)[1]
            inputVideos.append((inputDir, inputVideo))

    def Process(self):
        ''' Gets the project name from the input box
            Assigns it to a variable
            Calls the organize function
        '''
        global projectName
        projectName = (User_input.get())
        print("Project Name: %s" % projectName)
        self.Organize()

    def Organize(self):
        ''' Takes the input video and started searching for the QR codes
            When it finds them, it calls the Trim function
            Also creates a nested Dict with {Scenes:{Takes:Frame}}
        '''

        # Timer for keeping track of performance
        START_TIME = datetime.now()

        os.chdir(inputVideos[0][0])
        global timeStampsCleaned
        timeStampsCleaned = {}

        def org_thread(inputVideo):
            global success
            self.processButton.grid_forget()
            self.OrgLabel.grid(row=4, column=0, padx=10, pady=10)
            self.progress.grid(row=4, sticky='E', padx=10, pady=10)
            self.progress.start()

            print("CHECK")

            timeStamps = {}
            video = inputVideo
            cap = cv2.VideoCapture(video)

            fps = cap.get(cv2.CAP_PROP_FPS)

            success, frame = cap.read()

            success = True
            count = 0
            frame1 = 0
            switch = 0
            timeStamp1 = ''

            while success:
                if(count%(int(fps/2))) == 0:
                    success, frame = cap.read()
                    count += 1
                    data = decode(frame, symbols=[ZBarSymbol.QRCODE])
                    if data == []:
                        continue
                    else:
                        dataClean = (data[0].data).decode('utf8')
                        timeStamps[dataClean] = count
                        if switch == 0:
                            timeStamp1 = dataClean
                            frame1 = count
                            switch += 1
                        if dataClean != timeStamp1:
                            frame2 = count
                            fileName = timeStamp1.split(':')[0] + '.' + timeStamp1.split(':')[1] + '.mp4'
                            self.Trim(str(frame1/fps), str(frame2/fps - 1), video, fileName)
                            sceneNum = int(timeStamp1.split(':')[0])
                            takeNum = int(timeStamp1.split(':')[1])

                            timeStamp1 = dataClean
                            frame1 = count
                            fileNameFinal = timeStamp1.split(':')[0] + '.' + timeStamp1.split(':')[1] + '.mp4'
                            sceneNumFinal = int(timeStamp1.split(':')[0])
                            takeNumFinal = int(timeStamp1.split(':')[1])

                            if not os.path.exists('%s/Scene %d' % (projectName, sceneNum)):
                                os.makedirs('%s/Scene %d' % (projectName, sceneNum))
                            dirName = ('%s/Scene %d' % (projectName, sceneNum)) + ('/Take %d' % (takeNum)) + '.mp4'
                            shutil.move(fileName, dirName)
                else:
                    success, frame = cap.read()
                    count += 1
            try:
                self.Trim(str(frame1/fps), str(count/fps), video, fileNameFinal)
                if not os.path.exists('%s/Scene %d' % (projectName, sceneNumFinal)):
                    os.makedirs('%s/Scene %d' % (projectName, sceneNumFinal))
                dirNameFinal = ('%s/Scene %d' % (projectName, sceneNumFinal)) + ('/Take %d' % (takeNumFinal)) + '.mp4'
                shutil.move(fileNameFinal, dirNameFinal)
                success = True
            except UnboundLocalError:
                success = False
                messagebox.showinfo("Error", "There was no QR Code found in this video.")

            for key in timeStamps:
                sceneNum = int(key.split(':')[0])
                takeNum = int(key.split(':')[1])
                try:
                    timeStampsCleaned[sceneNum][takeNum] = timeStamps[key]
                except:
                    timeStampsCleaned[sceneNum] = {}
                    timeStampsCleaned[sceneNum][takeNum] = timeStamps[key]

            print(timeStampsCleaned)
            cap.release()
            cv2.destroyAllWindows()

            # Timer for keeping track of performance
            END_TIME = datetime.now()
            print('Duration to Organize: {}'.format(END_TIME - START_TIME) + '\n')

        for loc, inputVideo in inputVideos:
            orgthread = threading.Thread(target=org_thread(inputVideo))
            orgthread.start()

        if success:
            self.progress.stop()
            self.progress.grid_forget()
            self.OrgLabel['text'] = "Organized!"
            self.CutButton.grid(row=5, column=0, padx=10, pady=10)
            self.RoughLabel.grid(row=5, sticky='W', padx=10, pady=10)
            messagebox.showinfo("Finished", "Finished Organizing. Continue to see a rough cut of your project.")

    def CompileCut(self):
        ''' Compiles the different scenes together
            Take the input from the multiple drop down menus
            Adds the names to a txt file and calls ffmpeg using subprocess
        '''
        folders = []
        def cut_thread():
            START_TIME = datetime.now()
            for scene in sorted(timeStampsCleaned):
                wantedFile = (projectName + (r'\Scene %s\Take %s.mp4' % (scene, wantedTakes[scene].get())))
                print(wantedFile)
                folders.append(wantedFile)

            self.CutButton.grid_forget()
            self.CutLabel.grid(row=5, column=0, padx=10, pady=10)
            self.progress.grid(row=5, sticky='E', padx=10, pady=10)
            self.progress.start()
            filenames = open("filenames.txt", "w")

            # Add all the file names to a txt for concatenation
            for folder in folders:
                filenames.write("file '" + folder + "'\n")
            filenames.close()

            ffmpegCall = (r'%s\ffmpeg' % CURRENT)
            command = [ffmpegCall, "-f", "concat", "-safe", "0", "-i", "filenames.txt", "-c", "copy", "%s/roughcut.mp4" % (projectName)]
            call(command, shell=True, stderr=DEVNULL, stdout=DEVNULL)
            print("Finished creating a rough cut.")
            os.remove('filenames.txt')

            self.progress.stop()
            self.progress.grid_forget()
            self.CutLabel['text'] = "Generated!"
            END_TIME = datetime.now()
            print('Duration to Organize: {}'.format(END_TIME - START_TIME) + '\n')
            messagebox.showinfo("Finished", "Finished Editing. A rough cut of your project will be in your project folder.")


        cutthread = threading.Thread(target=cut_thread)
        cutthread.start()

    def Trim(self, start, end, inputVid, outputVid):
        ''' Edits a given video by the starting and ending points of the video
            Uses subprocess to call ffmpeg application to edit the video
            As long as it is in the same folder as this python script it will work
        '''
        ffmpegCall = (r'"%s\ffmpeg"' % CURRENT)
        trim_command = ffmpegCall + ' -i ' + inputVid + " -ss  " + start + " -to " + end + " -c copy " + outputVid
        call(trim_command, stderr=DEVNULL, stdout=DEVNULL)
        print("Finished cutting: %s" % outputVid)

root = Tk()
Window = Window(root)
root.mainloop()