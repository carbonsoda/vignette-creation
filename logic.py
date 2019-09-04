import os, csv, subprocess, re
from collections import namedtuple
from pydub import AudioSegment


class VideoLogic:

    def __init__(self):
        self.defaultlength = 0.5  # 0.5 seconds
        self.beepfile = "vignette_beep.wav"

        self.beep_savepath = ''

    # goes through csv file of times + generates time segments
    def readinput(self, videopath, savebeeppath, csvfile):
        audiofile = AudioSegment.empty()
        try:
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
                        if silentstart == 0:
                            if not time[0]:  # beep starts @ t=0.0
                                silentstart = time[1]
                        else:
                            silentend = time[1]
                            audiofile += self.audiogenerator((silentstart, silentend))
                            # for next row
                            silentstart = time[0]

                        audiofile += self.audiogenerator(time, True)

            if audiofile.duration_seconds > 1:
                correctlength = self.get_video_length(audiofile.duration_seconds, videopath)
                if correctlength:
                    silence = correctlength * 1000
                    audiofile += AudioSegment.silent(duration=silence)

                with open(self.beep_savepath, 'w+') as f:
                    audiofile.export(self.beep_savepath, format="wav")
                return os.path.exists(self.beep_savepath)
        except (PermissionError, OSError) as e:
            # self.permissionerrorbox()
            return None

    def audiogenerator(self, time, isbeep=False):
        # in milliseconds
        # seperate *1000 to avoid Decimal import https://floating-point-gui.de/languages/python/
        if type(time) != tuple:
            return None
        timespan = (time[1] * 1000) - (time[0] * 1000)

        if isbeep:
            song = AudioSegment.from_file(self.beepfile)
            beep = song[:timespan]  # after testing, can return just this line
            return beep
        else:
            return AudioSegment.silent(duration=timespan)

    # to determine length of the wav file
    def get_video_length(self, audiolength, path):
        process = subprocess.Popen([r'ffmpeg', '-i', path], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = process.communicate()

        regex = r'Duration: (?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+)'
        matches = re.search(regex, stdout.decode('UTF-8'), re.DOTALL).groupdict()

        hr = float(matches['hours'])
        minut = float(matches['minutes'])
        sec = float(matches['seconds'])

        vidtime = (60 * 60 * hr) + (60 * minut) + sec

        if audiolength < vidtime:
            return vidtime - audiolength

        return 0

    # runs ffmpeg commands for making muted copy + beeped video
    def generatevignette(self, rawvideopath, mutedpath, vignettevideopath, audiopath):

        mutedprocess = subprocess.Popen(
            [r'ffmpeg', '-i', rawvideopath, '-c', 'copy', '-an', mutedpath],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
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
                    stderr=subprocess.STDOUT,
                    shell=True
                )
            stdout, stderr = process.communicate()  # acts as a timer function
            if os.path.exists(vignettevideopath):
                return True
            else:
                return "Issue with mixing beep with video"

    # Trims videos and saves accordingly
    def trimmer(self, sourcepath, savepath, start, end):
        process = subprocess.Popen(
                [
                    r'ffmpeg', '-i', sourcepath,
                    '-ss', start,
                    '-to', end,
                    savepath
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True)

        stdout, stderr = process.communicate()  # basically a timer
        if os.path.exists(savepath):
            return True
        else:
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


    # times are given in mm:ss:zzz, return as hh:mm:ss.zzz
    # validates timestamps, otherwise calculate missing endstamp
    # start CANNOT be considered "blank", ie if person wants from start of video!
    def timegenerate(self, start, end, duration):
        t1 = start
        t2 = ''

        # missing end timestamps ( end == 00:00:000)
        if set(int(n) for n in end.split(':')) == {0}:
            durate = duration.split(":")
            # if has duration
            if set(int(n) for n in durate) != {0}:
                for i, j in zip(start.split(":"), durate):
                    k = int(i) + int(j)

                    if len(str(k)) < 2:
                        t2 += "0" + str(k) + ":"
                    else:
                        t2 += str(k) + ":"
                if t2.endswith(":"):
                    t2 = t2[:-1]
            else:
                return None  # no duration time given
        else:
            t2 = end

        while len(t1.split(":")) < 4:
            t1 = "00:" + t1
        while len(t2.split(":")) < 4:
            t2 = "00:" + t2

        try:
            # ffmpeg requires 00:00:00.000
            t1hhmmss, _, t1milli = t1.rpartition(":")
            t2hhmmss, _, t2milli = t2.rpartition(":")
            starttime = t1hhmmss + "." + t1milli
            endtime = t2hhmmss + "." + t2milli
            # can merge after testing
            return starttime, endtime
        except:
            print(t1)
            return None

    def batchtrim(self, csvfile, savefolder):
        # totrim {} == video_id : [sourcepath, start, end, savepath]
        totrim = self._batchtrim(csvfile, savefolder)
        failedtrim = []

        if totrim:
            for video_id in totrim:
                start, end = self.timegenerate(totrim[video_id][1], totrim[video_id][2], "0")

                if start and end:
                    source = totrim[video_id][0]
                    savepath = totrim[video_id][3]

                    if not self.trimmer(sourcepath=source, savepath=savepath, start=start, end=end):
                        failedtrim.append(source)
        else:
            return None

        print(failedtrim)
        return failedtrim

    # self.trims = {}  # ID : name, beeppath, mutepath, vigpath
    # helper method for batchtrim
    # opens csvfile and loads contents + creates savepath for each
    def _batchtrim(self, csvfile, savefolder):
        totrim = {}

        try:
            with open(csvfile, 'r+') as f:
                csv_input = csv.reader(f, delimiter=',')

                for row in csv_input:  # ID, Onset, Offset, File
                    if len(row) < 4:
                        pass
                    else:
                        try:
                            video_id = row[0]
                            onset = row[1]
                            offset = row[2]
                            source = row[3]

                            totrim[video_id] = [source, onset, offset]
                        except (IndexError, KeyError) as e:
                            print(e)
                            print(row)
            # return totrim
        except PermissionError:
            return None

        if totrim:
            for video_id in totrim:
                try:
                    id_folder = os.path.join(savefolder, video_id).replace("\\", "/")
                    if not os.path.isdir(id_folder):
                        os.makedirs(id_folder)

                    savepath = self.checkexisting(id_folder + os.sep + video_id)
                    if savepath:
                        totrim[video_id].append(savepath)
                except:
                    print(video_id)
            return totrim

    def batchvignette(self, mainfolder):
        tobeep = []  # [(csvfile, beepfile, sourcevideo, mutedfile, vignettepath)]
        failedbeeps = []

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

        return failedbeeps

    def _batchvignette(self, csvfile, beepfile, sourcevideo, mutedpath, vignettepath):

        audiofile = self.readinput(sourcevideo, beepfile, csvfile)

        if audiofile:
            processing = self.generatevignette(sourcevideo, mutedpath, vignettepath, beepfile)
            if isinstance(processing, str):
                return False, processing
            else:
                return True