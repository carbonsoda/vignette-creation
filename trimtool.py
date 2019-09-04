import os, sys
import ui, logic
from functools import partial
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
        # specific to our lab
        self.delimter = 'Suanda'

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
        # self.vingrb.toggled.connect(lambda: self.trimbatchmode = False)
        self.trimfilebtn.clicked.connect(partial(self.batch.loading,
                                                 self.trimfilelbl
                                                 ))

        self.beginbatchbtn.clicked.connect(partial(self.batch.batchstart,
                                                   self.beepchk.isChecked()))

        self.batchwindow.exec_()

    # upload = False == save btn
    def loadsave(self, upload):
        if upload:
            file = QtWidgets.QFileDialog.getOpenFileName(filter="Videos (*.mp4)")[0]
            file = os.path.join(file).replace('\\', '/')
            if len(file) < 1:
                pass
            else:
                self.filepath = file
                self.filename = os.path.splitext(file)[0]
                self.savepath = self.checkexisting(os.path.splitext(file)[0])

                self.filelbl.setText('...' + str(file.split(self.delimter)[1]))
                self.savelbl.setText('...' + str(self.savepath.split(self.delimter)[1]))
        else:
            file = QtWidgets.QFileDialog.getSaveFileName(filter="Videos (*.mp4)")[0].replace('\\', '/')
            file = os.path.join(file).replace('\\', '/')
            if len(file) < 1:
                pass
            else:
                # choosing own save name
                try: # save only to Q drive
                    self.savepath = self.checkexisting(file, addon='')
                    self.filename = os.path.splitext(os.path.split(file)[1])[0]
                    self.savelbl.setText('...' + str(self.savepath.split(self.delimter)[1]))
                except IndexError:
                    self.msg.savepathbox()

    def startrim(self):
        start = None
        end = None

        # checks if ALL the timestamps are just 0's
        # i don't want to make a temp variable or func for this thing... but...
        if 2 > len(set(
                j for i in [
                    [int(n) for n in t.split(":")] for t in
                    [self.startedit.text(), self.endedit.text(), self.durationedit.text()]] for j in i)):
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
                oldsavepath = os.path.split(self.savepath)  # (desired save location, filename_trimmed)

                if not self.hasvignettepath:
                    folder, name = self.makevignettepath(self.savepath)
                    if folder and name:
                        self.hasvignettepath = True
                        self.savepath = self.checkexisting(folder + os.sep + name, '_original')
                else:
                    filename = str(oldsavepath[1].rsplit('_trimmed')[0])
                    self.savepath = self.checkexisting(oldsavepath[0] + os.sep + filename, '_original')
        # open ffmpeg
        if self.cantrim:
            videopath = self.filepath.replace('\\', '/')
            savepath = os.path.join(self.savepath).replace('\\', '/')

            if self.trimmer(videopath, savepath, start, end):
                self.msg.confirmbox(True)
            else:
                self.msg.confirmbox(False)
            self.cantrim = False  # reset
        else:  # missing parameters
            self.msg.questionbox()

# VIGNETTE LOGISTICS
class VignetteTool(logic.VideoLogic):
    def __init__(self, parent=None):
        super(VignetteTool, self).__init__()
        self.msg = ui.UIMessageBoxes()

        # specific to our lab
        self.delimter = "Suanda"
        self.beepfile = "vignette_beep.wav"

        self.timesegments = []
        self.rawvideopath = ""
        self.csvpath = ""

        self.usedefault = True
        self.defaultlength = 1.0 # one second

        self.vig_savepath = ""
        self.beep_savepath = ""

    def loadtimes(self, lbl):
        self.csvpath = self.loadfile("CSVs (*.csv)")
        if self.csvpath:
            lbl.setText('...' + str(self.csvpath.split(self.delimter)[1]))

    def loadvideo(self, lbl):
        self.rawvideopath = self.loadfile("Videos (*.mp4)", ".mp4")
        if self.rawvideopath:
            lbl.setText('...' + str(self.rawvideopath.split(self.delimter)[1]))

    def loadbeep(self, lbl):
        self.beepfile = self.loadfile("Audio (*.wav)")
        if self.beepfile:
            lbl.setText('...' + str(self.beepfile.split(self.delimter)[1]))

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

        self.trimcsv = ''  # trim csv
        self.savefolder = ''  # main save folder
        self.delimter = 'Suanda'

    def batchstart(self, hasvignettes = False):
        failedtrims = self.batchtrim(self.trimcsv, self.savefolder)

        if isinstance(failedtrims, list):
            if len(failedtrims) > 0:
                print(failedtrims)
            else:  # empty list
                self.msg.confirmbox(True)
        elif not failedtrims:
            self.msg.permissionerrorbox()

        if hasvignettes:
            failedbeeps = self.batchvignette(self.savefolder)
            if isinstance(failedbeeps, list):
                if len(failedbeeps) > 0:
                    print(failedbeeps)
                else:
                    self.msg.confirmbox(True)
            return None

    def loading(self, lbl):

        file = QtWidgets.QFileDialog.getOpenFileName(filter="CSVs (*.csv)")[0]
        file = os.path.join(file).replace('\\', '/')

        if len(file) < 1:
            return None
        else:
            self.trimcsv = file
            try:
                lbl.setText('...' + str(self.trimcsv.split(self.delimter)[1]))
            except:
                lbl.setText(self.trimcsv)

        self.savefolder = os.path.join(os.path.split(file)[0], 'Vignettes').replace('\\','/')

        if not os.path.exists(self.savefolder):
            os.makedirs(self.savefolder)


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