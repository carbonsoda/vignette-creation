from PySide2 import QtCore, QtGui, QtWidgets

class UiTrimmingTool:
    def setupUi(self, MainWindow):
        MainWindow.setFixedSize(QtCore.QSize(550, 330))
        MainWindow.setWindowTitle('Video Trim Tool')
        self.menubar = MainWindow.menuBar()  # type: QtWidgets.QMenu

        self.vignmodeAction = QtWidgets.QAction('Vignette Maker Mode')
        self.batchmodeAction = QtWidgets.QAction('Batch Mode')
        self.menubar.addAction(self.vignmodeAction)
        self.menubar.addAction(self.batchmodeAction)
        self.menubar.setNativeMenuBar(False)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 400, 21))


        self.window = QtWidgets.QWidget(MainWindow)
        self.window.setFixedSize(QtCore.QSize(550, 315))
        self.window.setFont(QtGui.QFont('Arial', 10))

        self.fileframe = self.fileframesetup()
        self.trimframe = self.trimframesetup()

        # menubar.addAction()
        self.windowlyt = QtWidgets.QVBoxLayout(self.window)
        self.windowlyt.addWidget(self.fileframe)
        self.windowlyt.addWidget(self.trimframe)

        MainWindow.setCentralWidget(self.window)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # configuration for each filepath label
    def file_lblsetup(self):
        lbl = QtWidgets.QLabel(" ")

        lbl.setFixedHeight(25)
        lbl.setMinimumWidth(200)
        # lbl.setFont(QtGui.QFont('Courier New', 9))
        lbl.setFont(QtGui.QFont('Lucida Console', 8))
        lbl.setFrameShape(QtWidgets.QFrame.Box)
        lbl.setFrameShadow(QtWidgets.QFrame.Sunken)
        lbl.setStyleSheet("background-color: rgba(255, 255, 255, 0.5)")

        return lbl

    # configuration for each upload-file button
    def file_btnsetup(self, text, shortcut=None):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(QtCore.QSize(100, 25))
        btn.setFont(QtGui.QFont("Arial", 10))

        if shortcut:
            btn.setShortcut(QtGui.QKeySequence(shortcut))
        return btn

    # configuration for each timeedit widget
    def timewidgetsetup(self, parent):
        t = QtWidgets.QTimeEdit(QtCore.QTime(0, 0, 0, 0), parent)

        t.setDisplayFormat('mm:ss:zzz')
        t.setCurrentSection(QtWidgets.QDateTimeEdit.MinuteSection)
        t.setToolTip("Minutes : Seconds : Milliseconds")

        return t

    # File loading area
    def fileframesetup(self):
        fileframe = QtWidgets.QFrame()
        fileframe.setFixedHeight(120)

        fileguidelbl = QtWidgets.QLabel("Trim this file:", fileframe)
        saveguidelbl = QtWidgets.QLabel("Save the trimmed video as...", fileframe)

        # displays chosen file paths
        self.filelbl = self.file_lblsetup()
        self.savelbl = self.file_lblsetup()

        # upload-function buttons
        self.loadbtn = self.file_btnsetup("Upload", 'Ctrl+O')
        self.savebtn = self.file_btnsetup("Save as...", 'Ctrl+S')

        fileframelyt = QtWidgets.QFormLayout(fileframe)
        fileframelyt.setAlignment(QtCore.Qt.AlignCenter)
        fileframelyt.setHorizontalSpacing(15)

        right = QtWidgets.QFormLayout.FieldRole
        left = QtWidgets.QFormLayout.LabelRole
        fileframelyt.setWidget(0, right, fileguidelbl)
        fileframelyt.setWidget(1, right, self.filelbl)
        fileframelyt.setWidget(1, left, self.loadbtn)
        fileframelyt.setWidget(2, right, saveguidelbl)
        fileframelyt.setWidget(3, right, self.savelbl)
        fileframelyt.setWidget(3, left, self.savebtn)

        return fileframe

    # Trimming actions area
    def trimframesetup(self):
        trimframe = QtWidgets.QFrame()
        trimframe.setFixedHeight(170)
        trimframelyt = QtWidgets.QGridLayout(trimframe)
        trimframelyt.setVerticalSpacing(6)
        trimframelyt.setHorizontalSpacing(6)

        self.trimbtn = QtWidgets.QPushButton("Start Trimming", trimframe)
        self.trimbtn.setFont(QtGui.QFont('Arial', 11))

        self.vignchkbx = QtWidgets.QCheckBox('Yes')
        self.vignchkbx.setChecked(True)
        vigntxt = QtWidgets.QLabel("Is this for a vignette?  ")

        trimframelyt.addWidget(vigntxt, 0, 0, 1, 1)
        trimframelyt.addWidget(self.vignchkbx, 0, 1, 1, 1)
        trimframelyt.addWidget(self.timeboxsetup(trimframe), 1, 0, 1, 4)  # timebox made/returned
        trimframelyt.addWidget(self.trimbtn, 2, 0, 1, 4)

        return trimframe

    # Container for timeedit widgets + respective labels
    def timeboxsetup(self, trimframe):
        timebox = QtWidgets.QGroupBox("Fill at least 2 time parameters to start trimming", trimframe)
        timebox.setFixedHeight(90)

        timelyt = QtWidgets.QGridLayout(timebox)
        timelyt.setContentsMargins(30, 15, 30, -1)
        timelyt.setHorizontalSpacing(60)

        timelbls = ["Start Time", "Stop Time", "Duration"]
        i = 0
        for time in timelbls:
            lbl = QtWidgets.QLabel(time, timebox)
            lbl.setFixedHeight(20)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            timelyt.addWidget(lbl, 2, i, 1, 1)
            i += 1

        # time edit widgets
        self.startedit = self.timewidgetsetup(trimframe)
        self.endedit = self.timewidgetsetup(trimframe)
        self.durationedit = self.timewidgetsetup(trimframe)

        # add to time groupbox
        # timelyt.addWidget(instructionlbl, 0, 0, 1, 1)
        timelyt.addWidget(self.startedit, 1, 0, 1, 1)
        timelyt.addWidget(self.endedit, 1, 1, 1, 1)
        timelyt.addWidget(self.durationedit, 1, 2, 1, 1)

        return timebox

    # VIGNNETTE MODE SETUP
    def vig_dialogbox(self, parent):
        self.vigwindow = QtWidgets.QDialog(parent)

        self.vigwindow.setWindowTitle('Vignette Tool')
        self.vigwindow.setWindowIcon(QtGui.QIcon("main.ico"))
        self.vigwindow.setFont(QtGui.QFont("Arial", 11))
        self.vigwindow.setFixedSize(QtCore.QSize(500, 270))

        self.generatebtn = QtWidgets.QPushButton("Generate Vignette")
        self.viewfolderbtn = QtWidgets.QPushButton("View Vignette Folder")
        self.generatebtn.setFixedHeight(30)
        self.viewfolderbtn.setFixedHeight(30)

        lyt = QtWidgets.QGridLayout(self.vigwindow)
        lyt.addWidget(self.vig_uploadbox(), 0, 0, 1, 2)
        lyt.addWidget(self.generatebtn, 1, 0, 1, 1)
        lyt.addWidget(self.viewfolderbtn, 1, 1, 1, 1)

    def vig_uploadbox(self):
        uploadbx = QtWidgets.QGroupBox("Upload...")
        uploadbx.setFixedHeight(190)

        bxlayout = QtWidgets.QFormLayout(uploadbx)
        bxlayout.setContentsMargins(9, 0, 9, 15)
        bxlayout.setVerticalSpacing(9)
        right = QtWidgets.QFormLayout.FieldRole  # for ease/more human sense
        left = QtWidgets.QFormLayout.LabelRole

        # upload-function buttons
        self.videobtn = self.file_btnsetup("Video File")
        self.beepbtn = self.file_btnsetup("Beep File")
        self.csvbtn = self.file_btnsetup("Time CSV")

        # file path lbls
        self.videolbl = self.file_lblsetup()
        self.beeplbl = self.file_lblsetup()
        self.beeplbl.setText(".../Trim+Vignette/vignette_beep.wav")
        self.csvlbl = self.file_lblsetup()

        # instruction lbls
        i = 0
        for name in ["Raw vignette video:", "Beep file to use:", "CSV file for beep times:"]:
            lbl = QtWidgets.QLabel(name, uploadbx)
            lbl.setFont(QtGui.QFont("Arial", 10))
            lbl.setFixedHeight(16)  # <16 cuts off letters: g, p, y, etc

            bxlayout.setWidget(i, right, lbl)
            i += 2

        # add filepath lbls
        bxlayout.setWidget(1, right, self.videolbl)
        bxlayout.setWidget(3, right, self.beeplbl)
        bxlayout.setWidget(5, right, self.csvlbl)
        # add upload btns
        bxlayout.setWidget(1, left, self.videobtn)
        bxlayout.setWidget(3, left, self.beepbtn)
        bxlayout.setWidget(5, left, self.csvbtn)

        return uploadbx

    # BATCH MODE
    def batch_dialogbox(self, parent):
        self.batchwindow = QtWidgets.QDialog(parent)

        self.batchwindow.setWindowTitle('Batch Mode')
        self.batchwindow.setWindowIcon(QtGui.QIcon("batch.ico"))
        self.batchwindow.setFont(QtGui.QFont("Arial", 11))
        self.batchwindow.setFixedSize(QtCore.QSize(500, 200))

        # MODE PICKER
        checktrimlbl = QtWidgets.QLabel("Do you have a trimlist.csv?")
        checkbeeplbl = QtWidgets.QLabel("Are there any beep csvs?")
        self.trimchk = QtWidgets.QCheckBox("Yes")
        self.beepchk = QtWidgets.QCheckBox("Yes")

        # Guide label
        trimlbl = QtWidgets.QLabel("trimlist.csv location:")
        # UPLOAD BUTTON
        self.trimfilebtn = self.file_btnsetup("Upload CSV")
        # SAVE PATH LABEL
        self.trimfilelbl = self.file_lblsetup()

        # BEGIN BUTTON
        self.beginbatchbtn = QtWidgets.QPushButton("Start Batch")
        self.beginbatchbtn.setFixedHeight(30)

        # Add all to the layout
        batchlyt = QtWidgets.QFormLayout(self.batchwindow)
        batchlyt.setContentsMargins(9, 0, 9, 15)
        batchlyt.setVerticalSpacing(9)
        right = QtWidgets.QFormLayout.FieldRole  # for ease/more human sense
        left = QtWidgets.QFormLayout.LabelRole

        batchlyt.setWidget(0, left, self.trimchk)
        batchlyt.setWidget(0, right, checktrimlbl)
        batchlyt.setWidget(1, right, checkbeeplbl)
        batchlyt.setWidget(1, left, self.beepchk)

        batchlyt.setWidget(2, right, trimlbl)
        batchlyt.setWidget(3, right, self.trimfilelbl)
        batchlyt.setWidget(3, left, self.trimfilebtn)

        batchlyt.setWidget(4, right, self.beginbatchbtn)

class UIMessageBoxes:
    # generic error box for both vignette + trimming
    def confirmbox(self, exists, error=''):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Saving')

        if exists:
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Operation successful")
        else:
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Error while processing request")
            msg.setInformativeText(error)

        msg.exec_()

    def questionbox(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Missing')

        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("Missing time information")
        msg.setInformativeText("Are at least 2 times filled in?\nPlease check and try again")

        msg.exec_()

    def permissionerrorbox(self):
        msg = QtWidgets.QMessageBox()
        msg.setMinimumWidth(80)
        msg.setWindowTitle('File in Use')

        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("CSV is currently open")
        msg.setInformativeText("Make sure no one has it open and try again")

        msg.exec_()

    def savepathbox(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Invalid')

        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Must save to Q Drive')
        msg.setInformativeText('Saving to personal or local drives is not permitted.\nPlease try again.')

        msg.exec_()
