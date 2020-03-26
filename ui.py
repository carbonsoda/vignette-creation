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
        self.vigwindow.setWindowIcon(QtGui.QIcon("resources/main.ico"))
        self.vigwindow.setFont(QtGui.QFont("Arial", 11))
        self.vigwindow.setFixedSize(QtCore.QSize(500, 300))

        self.generatebtn = QtWidgets.QPushButton("Generate Vignette")
        self.viewfolderbtn = QtWidgets.QPushButton("View Vignette Folder")
        self.generatebtn.setFixedHeight(30)
        self.viewfolderbtn.setFixedHeight(30)

        lyt = QtWidgets.QGridLayout(self.vigwindow)
        lyt.addWidget(self.vig_uploadbox(), 0, 0, 1, 2)
        # lyt.addWidget(questiondefaultbl, 1, 0, 1, 1)
        # lyt.addWidget(defaultslbl, 1, 1, 1, 1)
        lyt.addWidget(self.vig_defaultsbox(), 1, 0, 1, 2)
        lyt.addWidget(self.generatebtn, 2, 0, 1, 1)
        lyt.addWidget(self.viewfolderbtn, 2, 1, 1, 1)

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

    def vig_defaultsbox(self):
        questionlbl = QtWidgets.QLabel("Start at a default time?")
        # questionlbl.setFont(QtGui.QFont("Arial", 10))

        self.vigdefault = QtWidgets.QCheckBox("Yes")
        self.vigdefault.setChecked(True)
        self.vigtime = QtWidgets.QLineEdit("30.00")
        self.vigtime.setFixedWidth(60)

        frame = QtWidgets.QFrame()
        frame.setFont(QtGui.QFont("Arial", 10))
        lyt = QtWidgets.QHBoxLayout(frame)
        lyt.setSpacing(10)
        lyt.addWidget(questionlbl)
        lyt.addWidget(self.vigdefault)
        # lyt.addItem(QtWidgets.QSpacerItem())
        lyt.addWidget(self.vigtime)
        lyt.addItem(QtWidgets.QSpacerItem(200,1))

        return frame


    # BATCH MODE
    def batch_dialogbox(self, parent):
        self.batchwindow = QtWidgets.QDialog(parent)

        self.batchwindow.setWindowTitle('Batch Mode')
        self.batchwindow.setWindowIcon(QtGui.QIcon("resources/batch.ico"))
        self.batchwindow.setFont(QtGui.QFont("Arial", 10))
        self.batchwindow.setFixedSize(QtCore.QSize(400, 300))

        # MODE PICKER
        rdbtnfont = QtGui.QFont("Arial", 9)
        self.trimmoderdbtn = QtWidgets.QRadioButton('Trimming')
        self.vignmoderdbtn = QtWidgets.QRadioButton('Vignettes (beeps)')
        modebox = QtWidgets.QGroupBox('Which batch mode?')
        modebox.setFixedHeight(70)
        modeboxlyt = QtWidgets.QHBoxLayout(modebox)
        modeboxlyt.addWidget(self.trimmoderdbtn)
        modeboxlyt.addWidget(self.vignmoderdbtn)

        # UPLOADING + GUIDE
        uploadbox = self._batch_upload()

        # BEGIN BUTTON
        self.beginbatchbtn = QtWidgets.QPushButton('Start Batch')
        self.beginbatchbtn.setFixedHeight(30)

        # Add all to the layout
        batchlyt = QtWidgets.QVBoxLayout(self.batchwindow)

        batchlyt.addWidget(modebox)
        batchlyt.addWidget(uploadbox)
        batchlyt.addWidget(self.beginbatchbtn)

    # Groupbox containing file selector + guide btns
    def _batch_upload(self):
        uploadbox = QtWidgets.QGroupBox('Batch File Upload')
        uploadbox.setFixedHeight(130)

        self.batchuploadbtn = self.file_btnsetup('Upload CSV')
        self.batchpathlbl = self.file_lblsetup()

        self.format_trimbtn = QtWidgets.QPushButton("Trimming Format")
        self.format_vigbtn = QtWidgets.QPushButton("Vignettes Format")
        self.format_trimbtn.setFixedWidth(110)
        self.format_vigbtn.setFixedWidth(110)

        lyt = QtWidgets.QGridLayout(uploadbox)
        lyt.setVerticalSpacing(12)
        lyt.setHorizontalSpacing(9)
        lyt.setContentsMargins(3, 9, 3, 9)

        lyt.addWidget(self.batchuploadbtn, 0, 0, 1, 1)
        lyt.addWidget(self.batchpathlbl, 0, 1, 1, 2)
        lyt.addWidget(self.format_trimbtn, 1, 1, 1, 1)
        lyt.addWidget(self.format_vigbtn, 1, 2, 1, 1)

        return uploadbox

    def batch_format_msgbox(self, isVignettes=True):
        msg = QtWidgets.QMessageBox()
        msg.setFixedSize(QtCore.QSize(600, 400))
        msg.setWindowTitle('Batch formatting')
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setInformativeText(
            'Please include the headers\n (not case-sensitive)'
        )
        if isVignettes:
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Batch CSV for Vignettes")
            msg.setDetailedText(
                "KEY:\n" +
                "Source = The exact location of the raw video\n" +
                "Beeps = List of all beep moments, in seconds\n" +
                # "Save As = OPTIONAL, the exact location where to save vignette, otherwise defaults\n\n" +
                "-------------------------------------------------------\n" +
                "source              |  " +
                "beeps              " +
                # "|   save as\n" +
                "-------------------------------------------------------\n" +
                "X:/Input/Video.mp4  |  30, 38.02, 40.333  " +
                # "|  X:/Input/Noun.mp4\n\n" +
                "\n\n(produces beeps at 30, 38.02, and 40.333 seconds)"
            )
        else:  # Trim mode
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Batch CSV for Trimming")

            msg.setDetailedText(
                "KEY:\n" +
                "Source = The exact location of video to trim\n" +
                "Start / End = The exact time in MM:SS:ZZZ format\n\n" +
                "----------------------------------------\n" +
                "source             |  " +
                "start    | end\n" +
                "----------------------------------------\n" +
                "X:/Input/Video.mp4 | 00:00:00 | 01:00:00\n\n" +
                "(produces 1 min long video)"
            )

        # enables "show details" w/o user needing to click
        for btn in msg.buttons():  # type: QtWidgets.QAbstractButton
            btn.click()

        detailsbox = msg.findChild(QtWidgets.QTextEdit)  # type:QtWidgets.QTextEdit
        if detailsbox:
            detailsbox.setFont(QtGui.QFont('Courier New', 9))
            detailsbox.setFixedSize(QtCore.QSize(600, 200))

        print(detailsbox.size())

        msg.exec_()

    def batch_think(self, isVignettes = True):
        msg = QtWidgets.QDialog()



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

    def permissionerrorbox(self, checking=False):
        msg = QtWidgets.QMessageBox()
        msg.setMinimumWidth(80)
        msg.setWindowTitle('File in Use')

        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("CSV is currently open")

        if checking:
            msg.setInformativeText('Remember to close it before starting the process')
        else:
            msg.setInformativeText("Make sure no one has it open and try again")

        msg.exec_()

    def savepathbox(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Invalid')

        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Must save to Q Drive')
        msg.setInformativeText('Saving to personal or local drives is not permitted.\nPlease try again.')

        msg.exec_()
