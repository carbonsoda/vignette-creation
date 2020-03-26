import os, csv, subprocess, re
from collections import defaultdict
from pydub import AudioSegment


class VideoLogic:

    def __init__(self):
        self.defaultlength = 0.5  # 0.5 seconds
        self.defaultbeeptime = 30  # 30 seconds in
        self.beepfile = "resources/vignette_beep.wav"

        self.beep_savepath = ''

    # goes through csv file of times + generates time segments
    def readinput(self, videopath, savebeeppath, csvfile):
        audiofile = AudioSegment.empty()
        correctlength = self.get_video_length(videopath)

        try:

            if len(csvfile) < 5:
                return self.defaultdurationbeep(videopath)

            with open(csvfile, 'r+') as f:
                csv_input = csv.reader(f, delimiter=',')

                # needed silence duration is calculated by start2 - end1
                silentstart = 0
                silentend = 0
                for row in csv_input:
                    hastime = False
                    # format: start+end must be side by side, thats all
                    for i in range(0, len(row)):
                        if hastime:  # time is already set
                            break
                        elif row[i].replace('.', '1').isdigit():  # at least 1 time given
                            try:
                                time = (float(row[i]), float(row[i + 1]))
                                hastime = True
                            except (IndexError, ValueError) as e:  # set to default time
                                # need to optimize later
                                time = (float(row[i]), float(row[i]) + self.defaultlength)
                                hastime = True
                    if hastime:
                        # beep starts @ t = 0
                        if silentstart == 0 and time[0] == 0:
                            silentstart = time[1]
                        else:
                            # silence starts @ 0
                            silentend = time[0]
                            audiofile += self.audiogenerator((silentstart, silentend), isbeep=False)
                            # for next row
                            silentstart = time[1]

                        audiofile += self.audiogenerator(time, True)

            if audiofile.duration_seconds > 0:
                if correctlength > audiofile.duration_seconds:
                    silence = (correctlength - audiofile.duration_seconds) * 1000
                    audiofile += AudioSegment.silent(duration=silence)

                with open(self.beep_savepath, 'w+') as f:
                    audiofile.export(self.beep_savepath, format="wav")
                return os.path.exists(self.beep_savepath)
        except (PermissionError, OSError) as e:
            # self.permissionerrorbox()
            return None

    def defaultdurationbeep(self, videopath):
        audiofile = AudioSegment.empty()
        audiofile += self.audiogenerator((0, 30), isbeep=False)
        audiofile += self.audiogenerator((30, 30 + self.defaultlength), True)

        if audiofile.duration_seconds > 0:
            correctlength = self.get_video_length(videopath)
            if correctlength > audiofile.duration_seconds:
                silence = (correctlength - audiofile.duration_seconds) * 1000
                audiofile += AudioSegment.silent(duration=silence)
            try:
                with open(self.beep_savepath, 'w+') as f:
                    audiofile.export(self.beep_savepath, format="wav")
                return os.path.exists(self.beep_savepath)
            except (PermissionError, OSError) as e:
                return None

    # Generates beep audiosegments
    def audiogenerator(self, time, isbeep=False):
        # in milliseconds
        # seperate *1000 to avoid Decimal import https://floating-point-gui.de/languages/python/
        if type(time) != tuple:
            return None
        timespan = (time[1] * 1000) - (time[0] * 1000)

        if isbeep:
            beep = AudioSegment.from_file(self.beepfile)[:timespan]
            return beep
        else:
            return AudioSegment.silent(duration=timespan)

    # For purpose of determining length of the wave file
    # make sure that the lengths match up
    def get_video_length(self, path):
        process = subprocess.Popen([r'ffmpeg', '-i', path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()

        regex = r'Duration: (?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+)'
        matches = re.search(regex, stdout.decode('UTF-8'), re.DOTALL).groupdict()

        hr = float(matches['hours'])
        minut = float(matches['minutes'])
        sec = float(matches['seconds'])

        vidtime = (60 * 60 * hr) + (60 * minut) + sec

        return vidtime

    # runs ffmpeg commands for making muted copy + beeped video
    def generatevignette(self, rawvideopath, mutedpath, vignettevideopath, audiopath):
        mutedprocess = subprocess.Popen(
            [
                r'ffmpeg',
                '-i', rawvideopath,
                '-c', 'copy', '-an', mutedpath
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = mutedprocess.communicate()  # acts as a timer function
        if not os.path.exists(mutedpath):
            return "Issue with creating muted video"
        else:
            process = subprocess.Popen(
                    [
                        r'ffmpeg',
                        '-i', mutedpath,
                        '-i', audiopath,
                        '-c:v', 'copy', '-map', '0:0', '-map', '1:0', '-shortest',
                        vignettevideopath
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
            stdout, stderr = process.communicate()  # acts as a timer function
            if os.path.exists(vignettevideopath):
                return True
            else:
                return "Issue with mixing beep with video"

    # Trims videos and saves accordingly
    def trimmer(self, sourcepath, savepath, start, end):
        starttime = str(start)
        endtime = str(end)
        process = subprocess.Popen(
                [
                    r'ffmpeg', '-i', sourcepath,
                    '-ss', starttime,
                    '-to', endtime,
                    savepath
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
        )

        stdout, stderr = process.communicate()  # basically a timer
        if os.path.exists(savepath):
            try:
                # unsure if i should check for existing...
                audioname = os.path.splitext(savepath)[0] + '.mp3'

                process = subprocess.Popen(
                    [
                        r'ffmpeg', '-i', savepath,
                        '-vn', '-acodec', 'mp3', audioname
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                stdout, stderr = process.communicate()  # basically a timer
            except:
                pass  # idk possible errors
            return True
        return False

    def checkpaths(self, expectedpath):
        if os.path.exists(expectedpath):
            root, extension = os.path.splitext(expectedpath)
            return self.checkexisting(root, '', extension)
        return expectedpath

    # prevents overwriting files
    def checkexisting(self, root, addon='_trimmed', extension='.mp4'):
        file = root + addon + extension
        i = 1
        while True:
            if os.path.exists(file):
                file = root + addon + '_' + str(i) + extension
                i += 1
            else:
                return file

    # when vignette box is checked, at time of trimming
    def makevignettepath(self, filepath, makefolder=True):
        root, filename = os.path.split(filepath)
        name = os.path.splitext(filename)[0].rsplit("_trimmed")[0].rsplit("_vignette")[0].rsplit("_original")[0]

        if makefolder:
            newfolder = os.path.join(root, name + "_vignette").replace('\\','/')
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            try:
                os.chmod(newfolder, 0o777)
            except PermissionError:
                print('Permission\n')

            return newfolder, str(name)
        else:
            return name

    # makes the folder and places it into folder for later beep'ing
    def foldergenerate(self, savepath, hasvignettepath = False):
        oldsavepath = os.path.split(savepath) # (desired save location, filename_trimmed)
        newsavepath = ''

        if not hasvignettepath:
            # avoids folder naming nightmare
            folder, name = self.makevignettepath(savepath)

            if folder and name:
                newsavepath = self.checkexisting(folder + os.sep + name, '_original')
                return True, newsavepath
        else:
            # Issue where after 1st trim, it doesn't generate it's own folder
            # might have to just snip this all out, we'll see?
            filename = str(oldsavepath[1].rsplit('_trimmed')[0])
            newsavepath = self.checkexisting(oldsavepath[0] + os.sep + filename, '_original')
            return hasvignettepath, newsavepath


    # Converts mm:ss:zzz into purely seconds, NO hh:mm:ss:zzz
    def timetoseconds(self, time):
        seconds = 0
        i = 2

        for timepart in time.split(':'):
            t = int(timepart)

            if i == 2:
                t = t * 60
            elif i == 0:
                t = round((t / 6000), 6)
            elif i < 0:
                print(timepart)
                raise ValueError
            seconds += t
            i -= 1

        return seconds

    # validates timestamps, otherwise calculate missing end-stamps
    def timegenerate(self, start, end, timeduration):
        starttime = self.timetoseconds(start)
        endtime = self.timetoseconds(end)

        if not endtime:  # missing END timestamp
            endtime = self.timetoseconds(timeduration)
            if not endtime: # no duration time given
                return None

        return starttime, endtime

    # Parses each row in CSV
    # returns list of lists
    def batch_parsecsv(self, csvfile):
        batch = []
        bad = []

        try:
            with open(csvfile, 'r+') as f:
                csv_reader = csv.reader(f, delimiter=',')
                next(csv_reader)

                for line in csv_reader:
                    # line = tuple(row)
                    if 4 < len(line) < 3:
                        bad.append(line)
                    else:
                        batch.append(line)
        except PermissionError:
            return None
        print(bad)
        return batch

    # batches = [[source, start, end]]
    def batchtrim(self, batches):
        failed = []

        for row in batches:
            try:
                source = row[0]
                start = self.timetoseconds(row[1])
                end = self.timetoseconds(row[2])

                savepath = self.foldergenerate(source)

                success = self.trimmer(source, savepath, start, end)
                if not success:
                    failed.append(row)
            except ValueError:
                failed.append(row)

        return failed

    def batchvignette(self, batches):
        tobeep = []  # [sourcevideo, beeptimes)]
        failed = []

        for row in batches:
            try:
                pass
            except ValueError:
                failed.append(row)

        try:
            pass
        except (PermissionError, IOError) as e:
            return str(e)

        for path, dirs, files in os.walk(mainfolder):
            csvfile = ''
            sourcevideo = ''
            for file in files:
                if csvfile and sourcevideo:
                    root, name = os.path.split(sourcevideo)
                    vignettefile = os.path.join(root, os.path.splitext(name)[0]).replace('\\','/')

                    beepfile = self.checkexisting(vignettefile, '_beep', '.wav')
                    mutedpath = self.checkexisting(vignettefile, '_muted')
                    vignettepath = self.checkexisting(vignettefile, '_beep')

                    tobeep.append((csvfile, beepfile, sourcevideo, mutedpath, vignettepath))
                elif file.endswith(".csv"):
                    csvfile = os.path.join(path, file).replace("\\","/")
                elif file.endswith(".mp4"):
                    sourcevideo = os.path.join(path, file).replace("\\","/")
        for i in range(len(tobeep)):
            try:
                csvfile, beepfile, sourcevideo, mutedpath, vignettepath = tobeep[i]
                beeped, failed = self._batchvignette(csvfile, beepfile, sourcevideo, mutedpath, vignettepath)

                if not beeped:  # False, processing
                    failedbeeps.append((vignettepath, failed))

            except IndexError:
                print(tobeep[i])

        return False, failedbeeps

    def _batchvignette(self, csvfile, beepfile, sourcevideo, mutedpath, vignettepath):

        audiofile = self.readinput(sourcevideo, beepfile, csvfile)

        if audiofile:
            processing = self.generatevignette(sourcevideo, mutedpath, vignettepath, beepfile)
            if isinstance(processing, str):
                return False, processing
            else:
                return True