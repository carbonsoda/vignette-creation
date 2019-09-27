#### _For [Dr. Suanda's](https://psych.uconn.edu/faculty/umay-suanda/) Communication and Development lab_

## Vignette Creation tool
This tool is a...
1. GUI for trimming in ffmpeg
    * given two timestamps, generates a trimmed clip and the trimmed clip's audio (as .mp3)
2. Vignette generator
    * uses [pydub](https://github.com/jiaaro/pydub) to generate the full audio file
    * merged with the trimmed, muted clip through ffmpeg

It also includes a "batch" mode, for either mass trimming or vignette generating. _(work in progress)_
 
 
Vignettes are generated for Human Simulation Paradigm (HSP) studies, as first described by [Gillette et al. (1998)](https://www.sciencedirect.com/science/article/pii/S0010027799000360).\
The purpose is to simulate how a child learns language by using adult participants, and a collection of target noun and verbs.
 
 In this context, a vignette is a ~40 second video that is silent except for "beep moments."\
The beeps correspond to a target noun or verb, at the instant it is uttered. Note that each vignette has one target word.
