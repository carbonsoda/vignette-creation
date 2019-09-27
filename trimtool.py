import os, sys, gc, csv
import ui, logic
from functools import partial
from collections import namedtuple
from PySide2 import QtWidgets, QtGui

# MAIN WINDOW
class TrimmingTool(QtWidgets.QMainWindow, ui.UiTrimmingTool, logic.VideoLogic):
    def __init__(self, parent=None):
        super(TrimmingTool, self).__init__(parent)
        self.msg = ui.UIMessageBoxes()
        self.setupUi(self)

        self.vignette = VignetteTool()
        self.batch = BatchTool()

        # initals
        self.savepath = ''
        self.filename = ''  # for purpose of vignette paths
        self.filepath = ''
        self.timeformat = '00:00:000'

        self.hasvignettepath = False
        self.cantrim = False

        # misc UI
        # for some reason, ALL edits won't stick unless at least 1 of these
        self.startedit.dateTimeFromText(self.startedit.text())
        self.trimbatchmode = True

        self.connections()

    def connections(self):
        # upload btns
        self.loadbtn.clicked.connect(partial(self.loadsave, True))
        self.savebtn.clicked.connect(partial(self.loadsave, False))
        # trim btn
        self.trimbtn.clicked.connect(partial(self.startrim))
        # pop up modes
        self.vignmodeAction.triggered.connect(partial(self.startvignmode))
        self.batchmodeAction.triggered.connect(partial(self.startbatchmode))

    # opens QDialog for Vignette-Creating
    def startvignmode(self):
        self.vig_dialogbox(self.window)
        # connections:
        self.videobtn.clicked.connect(partial(self.vignette.loadvideo, self.videolbl))
        self.beepbtn.clicked.connect(partial(self.vignette.loadbeep, self.beeplbl))
        self.csvbtn.clicked.connect(partial(self.vignette.loadtimes, self.csvlbl))

        self.generatebtn.clicked.connect(partial(self.vignette.configvingette))

        self.vigwindow.exec_()

    def startbatchmode(self):
        self.batch_dialogbox(self.window)

        # connections
        self.trimmoderdbtn.toggled.connect(partial(self.batch.setmode, self.trimmoderdbtn))
        self.vignmoderdbtn.toggled.connect(partial(self.batch.setmode, self.vignmoderdbtn))

        self.format_trimbtn.clicked.connect(partial(self.batch_format_msgbox, False))
        self.format_vigbtn.clicked.connect(partial(self.batch_format_msgbox, True))

        self.batchuploadbtn.clicked.connect(partial(self.batch.loading, self.batchpathlbl))
        self.beginbatchbtn.clicked.connect(partial(self.batch.batchstart))

        # Execute only after connected
        self.batchwindow.exec_()

    # upload = False == save btn
    def loadsave(self, upload):
        if upload:
            self.hasvignettepath = False
            file = QtWidgets.QFileDialog.getOpenFileName(filter="Videos (*.mp4)")[0]
            file = os.path.join(file).replace('\\', '/')
            if len(file) < 1:
                pass
            else:
                self.filepath = file
                self.filename = os.path.splitext(file)[0]
                self.savepath = self.checkexisting(os.path.splitext(file)[0])

                self.filelbl.setText('.../' + str(os.path.split(file)[1]))
                self.savelbl.setText('.../' + str(os.path.split(self.savepath)[1]))
        else:
            file = QtWidgets.QFileDialog.getSaveFileName(filter="Videos (*.mp4)")[0].replace('\\', '/')
            file = os.path.join(file).replace('\\', '/')
            if len(file) < 1:
                pass
            else:
                # choosing own save name
                self.savepath = self.checkexisting(file, addon='')
                self.filename = os.path.splitext(os.path.split(file)[1])[0]
                try:  # save only to Q drive
                    self.savelbl.setText('...' + str(os.path.split(self.savepath)[1]))
                except IndexError:
                    self.msg.savepathbox()

    def startrim(self):
        start = None
        end = None

        # checks if ALL the timestamps are just 0's
        if self.allzeros_check():
            self.questionbox()
            return None
        else:
            start, end = self.timegenerate(
                self.startedit.text(),
                self.endedit.text(),
                self.durationedit.text()
            )
            if start and end:
                self.cantrim = True

            # makes the folder and places it into folder for later beep'ing
            if self.vignchkbx.isChecked():
                self.hasvignettepath, self.savepath = self.foldergenerate(self.savepath, self.hasvignettepath)

        # open ffmpeg
        if self.cantrim:
            # for some reason formatting issues on PC, these 2 lines fix it
            videopath = self.filepath.replace('\\', '/')
            savepath = os.path.join(self.savepath).replace('\\', '/')

            if self.trimmer(videopath, savepath, start, end):
                self.msg.confirmbox(True)
            else:
                self.msg.confirmbox(False)
            self.cantrim = False  # reset
            gc.collect()
        else:  # missing parameters
            self.msg.questionbox()

    # Checks if all timestamps are just 0's
    # Seperate function to make starttrim little cleaner
    def allzeros_check(self):
        times = [self.startedit.text(), self.endedit.text(), self.durationedit.text()]
        return 2 > len(set(j for i in [[int(n) for n in t.split(":")] for t in times] for j in i))


# VIGNETTE LOGISTICS
class VignetteTool(logic.VideoLogic):
    def __init__(self, parent=None):
        super(VignetteTool, self).__init__()
        self.msg = ui.UIMessageBoxes()

        # specific to our lab
        self.beepfile = "vignette_beep.wav"

        self.timesegments = []
        self.rawvideopath = ""
        self.csvpath = ""

        self.usedefault = True
        self.defaultlength = 0.5

        self.vig_savepath = ""
        self.beep_savepath = ""

    def loadtimes(self, lbl):
        self.csvpath = self.loadfile("CSVs (*.csv)")
        if self.csvpath:
            lbl.setText('...' + str(os.path.split(self.csvpath)[1]))

    def loadvideo(self, lbl):
        self.rawvideopath = self.loadfile("Videos (*.mp4)", ".mp4")
        if self.rawvideopath:
            lbl.setText('...' + str(os.path.split(self.rawvideopath)[1]))

    def loadbeep(self, lbl):
        self.beepfile = self.loadfile("Audio (*.wav)")
        if self.beepfile:
            lbl.setText('...' + str(os.path.split(self.beepfile)[1]))

    # loads in desired file type
    def loadfile(self, filetype, extension=None):
        file = QtWidgets.QFileDialog.getOpenFileName(filter=filetype)[0]
        file = os.path.join(file).replace('\\', '/')

        if len(file) < 1:
            pass
        else:
            if extension:  # video file
                root = os.path.splitext(file)[0]
                addon = "_beep"

                self.vig_savepath = self.checkexisting(root, addon)
                self.beep_savepath = self.checkexisting(root, addon, '.wav')

            return file

    # Makes 2 copies of the video (muted + beeped) and a beep.wav
    def configvingette(self):

        self.beep_savepath = self.checkpaths(self.beep_savepath)

        videofile = os.path.join(self.rawvideopath).replace('\\', '/')
        audiofile = self.readinput(videofile, self.beepfile, self.csvpath)

        # successfully made audio
        # desire copy of video muted + copy of video w/ beeps
        if audiofile:
            # save paths
            mutedvideosavepath = self.checkexisting(os.path.splitext(self.rawvideopath)[0], '_muted')
            vig_savepath = self.checkpaths(self.vig_savepath)
            beeppath = os.path.join(self.beep_savepath).replace('\\', '/')

            processing = self.generatevignette(videofile, mutedvideosavepath, vig_savepath, beeppath)

            if isinstance(processing, str):
                self.msg.confirmbox(False, processing)
            else:
                self.msg.confirmbox(True)

# CONNECTIONS FOR BATCH
class BatchTool(logic.VideoLogic):
    def __init__(self, parent=None):
        super(BatchTool, self).__init__()
        self.msg = ui.UIMessageBoxes()

        self.batchcsv = ''  # batch csv file
        self.trimmode = True  # False = vignettes

        self.batches = []

    # toggles between trimmer + vignettes mode
    def setmode(self, button, _):
        btn = button.text().lower()  # type: str
        if btn.startswith('t'):
            self.trimmode = True
        elif btn.startswith('v'):
            self.trimmode = False
        else:
            print(btn)
            print(button.text())

    def batchstart(self):
        # placeholders
        failures = []

        # prevent misclicks
        if self.batchcsv:
            self.batches = self.batch_parsecsv(self.batchcsv)  # returns list of lists

            if not self.batches:
                self.msg.permissionerrorbox()

            if self.trimmode:
                failures = self.batchtrim(self.batchcsv)
            else:
                failures = self.batchvignette(self.batchcsv)

            # operation success
            if not failures:
                self.msg.confirmbox(True)
            else:
                self.logger(self.batchcsv, failures)
                self.msg.confirmbox(False, failures)

    def logger(self, csvfile, loglist):
        pass


    def loading(self, lbl):
        file = QtWidgets.QFileDialog.getOpenFileName(filter="CSVs (*.csv)")[0]
        file = os.path.join(file).replace('\\', '/')

        if len(file) < 1:
            return None
        else:
            if os.access(file, os.R_OK):  # might cut this out
                pass
            else:
                self.msg.permissionerrorbox(checking=True)

            self.batchcsv = file
            lbl.setText('...' + str(os.path.split(self.batchcsv)[1]))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('main.ico'))
    # ensures same look for all
    s = QtWidgets.QStyleFactory.create('Fusion')
    app.setStyle(s)

    # Create and show main window
    window = TrimmingTool()
    window.setWindowTitle('Video Trim Tool')
    window.setWindowIcon(QtGui.QIcon('main.ico'))
    window.show()

    sys.exit(app.exec_())

# "/c/Users/nam14014/Desktop/buildfolder/ffmpeg/ffmpeg/resources/vignette_beep.wav:."
# pyinstaller --icon "/c/Users/nam14014/Desktop/buildfolder/ffmpeg/icon.ico" --add-data "/c/Users/nam14014/Desktop/buildfolder/ffmpeg/ffmpeg/resources/main.ico:." --add-data "/c/Users/nam14014/Desktop/buildfolder/ffmpeg/ffmpeg/resources/vignette_beep.wav:." --add-data "/c/Users/nam14014/Desktop/buildfolder/ffmpeg/ffmpeg/resources/vignette.ico:." --noconsole "ffmpeg/trimtool.py"


# ffmpeg -i muted_input.mp4 -i input.wav -c:v copy -map 0:0 -map 1:0 -shortest output.mp4