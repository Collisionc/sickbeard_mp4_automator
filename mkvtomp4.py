from __future__ import unicode_literals
import os
import time
import json
import sys
import shutil
import logging
from converter import Converter, FFMpegConvertError
from extensions import valid_input_extensions, valid_output_extensions, bad_subtitle_codecs, valid_subtitle_extensions, subtitle_codec_extensions, valid_tagging_extensions
from babelfish import Language
import datetime


class MkvtoMp4:
    def __init__(self, settings=None,
                 FFMPEG_PATH="FFMPEG.exe",
                 FFPROBE_PATH="FFPROBE.exe",
                 delete=True,
                 output_extension='mp4',
                 output_dir=None,
                 relocate_moov=True,
                 output_format='mp4',
                 video_codec=['h264', 'x264'],
                 video_bitrate_restriction=None,
                 video_bitrate=None,
                 vcrf=None,
                 video_width=None,
                 nvenc_profile=None,
                 nvenc_preset=None,
                 nvenc_rate_control=None,
                 qmin=None,
                 qmax=None,
                 global_quality=None,
                 maxrate=None,
                 minrate=None,
                 bufsize=None,
                 nvenc_gpu=None,
                 nvenc_temporal_aq=False,
                 nvenc_weighted_prediction=False,
                 nvenc_rc_lookahead=None,
                 handle_m2ts_files=False,
                 video_profile=None,
                 h264_level=None,
                 qsv_decoder=True,
                 hevc_qsv_decoder=False,
                 dxva2_decoder=False,
                 hdr_sdr_convert=False,
                 enable_opencl_hdr_sdr_tonemapping=False,
                 init_hw_device='opencl=gpu:0',
                 nvenc_cuvid=False,
                 nvenc_cuvid_hevc=False,
                 nvenc_decoder_gpu=None,
                 nvenc_decoder_hevc_gpu=None,
                 nvenc_hwaccel_enabled=False,
                 burn_in_forced_subs=False,
                 burn_in_full_subs=False,
                 audio_codec=['ac3'],
                 ignore_truehd=True,
                 audio_bitrate=256,
                 audio_filter=None,
                 audio_copyoriginal=False,
                 audio_first_language_track=False,
                 iOS=False,
                 iOSFirst=False,
                 iOSLast=False,
                 iOS_filter=None,
                 maxchannels=None,
                 aac_adtstoasc=False,
                 sample_rate=None,
                 awl=None,
                 swl=None,
                 adl=None,
                 sdl=None,
                 scodec=['mov_text'],
                 subencoding='utf-8',
                 opensubtitles = None,
                 podnapisi = None,
                 downloadsubs=True,
                 processMP4=False,
                 forceConvert=False,
                 copyto=None,
                 moveto=None,
                 embedsubs=True,
                 embedonlyinternalsubs=True,
                 providers=['addic7ed', 'podnapisi', 'thesubdb', 'opensubtitles'],
                 permissions=int("777", 8),
                 pix_fmt=None,
                 logger=None,
                 threads='auto',
                 vsync='-1',
                 preopts=None,
                 postopts=None):
        # Setup Logging
        if logger:
            self.log = logger
        else:
            self.log = logging.getLogger(__name__)

        # Settings
        self.FFMPEG_PATH = FFMPEG_PATH
        self.FFPROBE_PATH = FFPROBE_PATH
        self.threads = threads
        self.vsync = vsync
        self.delete = delete
        self.output_extension = output_extension
        self.output_format = output_format
        self.output_dir = output_dir
        self.relocate_moov = relocate_moov
        self.processMP4 = processMP4
        self.forceConvert = forceConvert
        self.copyto = copyto
        self.moveto = moveto
        self.permissions = permissions
        self.preopts = preopts
        self.postopts = postopts
        # Video settings
        self.video_codec = video_codec
        self.video_bitrate_restriction = video_bitrate_restriction
        self.video_bitrate = video_bitrate
        self.vcrf = vcrf
        self.video_width = video_width
        self.nvenc_profile = nvenc_profile
        self.nvenc_preset = nvenc_preset
        self.qmin = qmin
        self.qmax = qmax
        self.global_quality = global_quality
        self.maxrate = maxrate
        self.minrate = minrate
        self.bufsize = bufsize
        self.nvenc_gpu = nvenc_gpu
        self.nvenc_temporal_aq = nvenc_temporal_aq
        self.nvenc_weighted_prediction = nvenc_weighted_prediction
        self.nvenc_rate_control = nvenc_rate_control
        self.nvenc_rc_lookahead = nvenc_rc_lookahead
        self.video_profile = video_profile
        self.h264_level = h264_level
        self.handle_m2ts_files = handle_m2ts_files
        self.qsv_decoder = qsv_decoder
        self.hevc_qsv_decoder = hevc_qsv_decoder
        self.dxva2_decoder = dxva2_decoder
        self.hdr_sdr_convert = hdr_sdr_convert
        self.enable_opencl_hdr_sdr_tonemapping = enable_opencl_hdr_sdr_tonemapping
        self.init_hw_device = init_hw_device
        self.nvenc_cuvid = nvenc_cuvid
        self.nvenc_cuvid_hevc = nvenc_cuvid_hevc
        self.nvenc_decoder_gpu = nvenc_decoder_gpu
        self.nvenc_decoder_hevc_gpu = nvenc_decoder_hevc_gpu
        self.nvenc_hwaccel_enabled = nvenc_hwaccel_enabled
        self.burn_in_forced_subs = burn_in_forced_subs
        self.burn_in_full_subs = burn_in_full_subs
        self.pix_fmt = pix_fmt
        # Audio settings
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        self.audio_filter = audio_filter
        self.iOS = iOS
        self.iOSFirst = iOSFirst
        self.iOSLast = iOSLast
        self.iOS_filter = iOS_filter
        self.maxchannels = maxchannels
        self.awl = awl
        self.adl = adl
        self.ignore_truehd = ignore_truehd
        self.aac_adtstoasc = aac_adtstoasc
        self.audio_copyoriginal = audio_copyoriginal
        self.audio_first_language_track = audio_first_language_track
        self.sample_rate = sample_rate
        # Subtitle settings
        self.scodec = scodec
        self.swl = swl
        self.sdl = sdl
        self.downloadsubs = downloadsubs
        self.subproviders = providers
        self.embedsubs = embedsubs
        self.embedonlyinternalsubs = embedonlyinternalsubs
        self.subencoding = subencoding
        self.opensubtitles = opensubtitles
        self.podnapisi = podnapisi

        # Import settings
        if settings is not None:
            self.importSettings(settings)
        self.options = None
        self.deletesubs = set()

    def importSettings(self, settings):
        self.FFMPEG_PATH = settings.ffmpeg
        self.FFPROBE_PATH = settings.ffprobe
        self.threads = settings.threads
        self.vsync = settings.vsync
        self.delete = settings.delete
        self.output_extension = settings.output_extension
        self.output_format = settings.output_format
        self.output_dir = settings.output_dir
        self.relocate_moov = settings.relocate_moov
        self.processMP4 = settings.processMP4
        self.forceConvert = settings.forceConvert
        self.copyto = settings.copyto
        self.moveto = settings.moveto
        self.permissions = settings.permissions
        self.preopts = settings.preopts
        self.postopts = settings.postopts
        # Video settings
        self.video_codec = settings.vcodec
        self.video_bitrate_restriction = settings.video_bitrate_restriction
        self.video_bitrate = settings.vbitrate
        self.vcrf = settings.vcrf
        self.video_width = settings.vwidth
        self.nvenc_profile = settings.nvenc_profile
        self.nvenc_preset = settings.nvenc_preset
        self.qmin = settings.qmin
        self.qmax = settings.qmax
        self.global_quality = settings.global_quality
        self.maxrate = settings.maxrate
        self.minrate = settings.minrate
        self.bufsize = settings.bufsize
        self.nvenc_gpu = settings.nvenc_gpu
        self.nvenc_temporal_aq = settings.nvenc_temporal_aq
        self.nvenc_weighted_prediction = settings.nvenc_weighted_prediction
        self.nvenc_rate_control = settings.nvenc_rate_control
        self.nvenc_rc_lookahead = settings.nvenc_rc_lookahead
        self.handle_m2ts_files = settings.handle_m2ts_files
        self.video_profile = settings.vprofile
        self.h264_level = settings.h264_level
        self.qsv_decoder = settings.qsv_decoder
        self.hevc_qsv_decoder = settings.hevc_qsv_decoder
        self.dxva2_decoder = settings.dxva2_decoder
        self.hdr_sdr_convert = settings.hdr_sdr_convert
        self.enable_opencl_hdr_sdr_tonemapping = settings.enable_opencl_hdr_sdr_tonemapping
        self.init_hw_device = settings.init_hw_device
        self.nvenc_cuvid = settings.nvenc_cuvid
        self.nvenc_cuvid_hevc = settings.nvenc_cuvid_hevc
        self.nvenc_decoder_gpu = settings.nvenc_decoder_gpu
        self.nvenc_decoder_hevc_gpu = settings.nvenc_decoder_hevc_gpu
        self.nvenc_hwaccel_enabled = settings.nvenc_hwaccel_enabled
        self.burn_in_forced_subs = settings.burn_in_forced_subs
        self.burn_in_full_subs = settings.burn_in_full_subs
        self.pix_fmt = settings.pix_fmt
        # Audio settings
        self.audio_codec = settings.acodec
        self.audio_bitrate = settings.abitrate
        self.audio_filter = settings.afilter
        self.iOS = settings.iOS
        self.iOSFirst = settings.iOSFirst
        self.iOSLast = settings.iOSLast
        self.iOS_filter = settings.iOSfilter
        self.maxchannels = settings.maxchannels
        self.awl = settings.awl
        self.adl = settings.adl
        self.ignore_truehd = settings.ignore_truehd
        self.aac_adtstoasc = settings.aac_adtstoasc
        self.audio_copyoriginal = settings.audio_copyoriginal
        self.audio_first_language_track = settings.audio_first_language_track
        self.sample_rate = settings.sample_rate
        # Subtitle settings
        self.scodec = settings.scodec
        self.swl = settings.swl
        self.sdl = settings.sdl
        self.downloadsubs = settings.downloadsubs
        self.subproviders = settings.subproviders
        self.embedsubs = settings.embedsubs
        self.embedonlyinternalsubs = settings.embedonlyinternalsubs
        self.subencoding = settings.subencoding
        self.opensubtitles = settings.opensubtitles
        self.podnapisi = settings.podnapisi

        self.log.debug("Settings imported.")

    # Process a file from start to finish, with checking to make sure formats are compatible with selected settings
    def process(self, inputfile, reportProgress=False, original=None):

        self.log.debug("Process started.")

        delete = self.delete
        deleted = False
        options = None
        if not self.validSource(inputfile):
            return False

        if self.needProcessing(inputfile):
            options = self.generateOptions(inputfile, original=original)
            if options == None:
                self.log.debug("Error generating options, possibly due to corrupt input file.")
                return False

            try:
                if reportProgress:
                    self.log.info(json.dumps(options, sort_keys=False, indent=4))
                else:
                    self.log.debug(json.dumps(options, sort_keys=False, indent=4))
            except:
                self.log.exception("Unable to log options.")

            outputfile, inputfile = self.convert(inputfile, options, reportProgress)

            if not outputfile:
                self.log.debug("Error converting, no outputfile present.")
                return False

            self.log.debug("%s created from %s successfully." % (outputfile, inputfile))

        else:
            outputfile = inputfile
            if self.output_dir is not None:
                try:
                    outputfile = os.path.join(self.output_dir, os.path.split(inputfile)[1])
                    self.log.debug("Outputfile set to %s." % outputfile)
                    shutil.copy(inputfile, outputfile)
                except Exception as e:
                    self.log.exception("Error moving file to output directory.")
                    delete = False
            else:
                delete = False

        if delete:
            self.log.debug("Attempting to remove %s." % inputfile)
            if self.removeFile(inputfile):
                self.log.debug("%s deleted." % inputfile)
                deleted = True
            else:
                self.log.error("Couldn't delete %s." % inputfile)
        if self.downloadsubs:
            for subfile in self.deletesubs:
                self.log.debug("Attempting to remove subtitle %s." % subfile)
                if self.removeFile(subfile):
                    self.log.debug("Subtitle %s deleted." % subfile)
                else:
                    self.log.debug("Unable to delete subtitle %s." % subfile)

        dim = self.getDimensions(outputfile)
        input_extension = self.parseFile(inputfile)[2].lower()
        output_extension = self.parseFile(outputfile)[2].lower()

        return {'input': inputfile,
                'input_extension': input_extension,
                'input_deleted': deleted,
                'output': outputfile,
                'output_extension': output_extension,
                'options': options,
                'x': dim['x'],
                'y': dim['y']}

    # Determine if a source video file is in a valid format
    def validSource(self, inputfile):
        input_extension = self.parseFile(inputfile)[2]
        if input_extension.lower() == "m2ts" and not self.handle_m2ts_files:
            self.log.debug( "%s is a m2ts file and handle_m2ts_files is not enabled" % inputfile )
            return False
        # Make sure the input_extension is some sort of recognized extension, and that the file actually exists
        if (input_extension.lower() in valid_input_extensions or input_extension.lower() in valid_output_extensions):
            if (os.path.isfile(inputfile)):
                self.log.debug("%s is valid." % inputfile)
                return True
            else:
                self.log.debug("%s not found." % inputfile)
                return False
        else:
            self.log.debug("%s is invalid with extension %s." % (inputfile, input_extension))
            return False

    # Determine if a file meets the criteria for processing
    def needProcessing(self, inputfile):
        input_extension = self.parseFile(inputfile)[2]
        # Make sure input and output extensions are compatible. If processMP4 is true, then make sure the input extension is a valid output extension and allow to proceed as well
        if (input_extension.lower() in valid_input_extensions or (self.processMP4 is True and input_extension.lower() in valid_output_extensions)) and self.output_extension.lower() in valid_output_extensions:
            self.log.debug("%s needs processing." % inputfile)
            return True
        else:
            self.log.debug("%s does not need processing." % inputfile)
            return False

    # Get values for width and height to be passed to the tagging classes for proper HD tags
    def getDimensions(self, inputfile):
        if self.validSource(inputfile):
            info = Converter(self.FFMPEG_PATH, self.FFPROBE_PATH).probe(inputfile)

        self.log.debug("Height: %s" % info.video.video_height)
        self.log.debug("Width: %s" % info.video.video_width)

        return {'y': info.video.video_height,
                'x': info.video.video_width}

        return {'y': 0,
                'x': 0}

    # Estimate the video bitrate
    def estimateVideoBitrate(self, info):
        total_bitrate = info.format.bitrate
        audio_bitrate = 0
        for a in info.audio:
            audio_bitrate += a.bitrate

        self.log.debug("Total bitrate is %s." % info.format.bitrate)
        self.log.debug("Total audio bitrate is %s." % audio_bitrate)
        self.log.debug("Estimated video bitrate is %s." % (total_bitrate - audio_bitrate))
        return ((total_bitrate - audio_bitrate) / 1000) * .95

    # Generate a list of options to be passed to FFMPEG based on selected settings and the source file parameters and streams
    def generateOptions(self, inputfile, original=None):
        # Get path information from the input file
        input_dir, filename, input_extension = self.parseFile(inputfile)
        drive_letter, directory = os.path.splitdrive( input_dir )
        drive_letter_no_colon = drive_letter.replace( ":", "" )
        output_dir = input_dir if self.output_dir is None else self.output_dir
        directory = directory.replace("\\", "\\\\"); #This part is necessary because the subtitle filter requires double escapes....

        info = Converter(self.FFMPEG_PATH, self.FFPROBE_PATH).probe(inputfile)

        # Video stream
        self.log.info("Reading video stream.")

        if info == None: # Exit before the exception. 
            return None
        self.log.info("Video codec detected: %s." % info.video.codec)

        try:
            vbr = self.estimateVideoBitrate(info)
        except:
            vbr = info.format.bitrate / 1000

        count = 1 # TODO: duplicate less code when not lazy
        while ( count < len( self.video_bitrate_restriction ) ):
            if int(self.video_bitrate_restriction[count - 1]) >= info.video.video_width:
                self.video_bitrate = self.video_bitrate_restriction[count]
                break
            count+=2

        count = 1
        while ( count < len( self.minrate ) ):
            if int(self.minrate[count - 1]) >= info.video.video_width:
                self.minrate = self.minrate[count]
                break
            count+=2

        count = 1
        while ( count < len( self.maxrate ) ):
            if int(self.maxrate[count - 1]) >= info.video.video_width:
                self.maxrate = self.maxrate[count]
                break
            count+=2

        count = 1
        while ( count < len( self.bufsize ) ):
            if int(self.bufsize[count - 1]) >= info.video.video_width:
                self.bufsize = self.bufsize[count]
                break
            count+=2

        if info.video.codec.lower() in self.video_codec and self.forceConvert is False:
            vcodec = 'copy'
        else:
            vcodec = self.video_codec[0]
        vbitrate = self.video_bitrate if self.video_bitrate else vbr

        self.log.info("Pix Fmt: %s." % info.video.pix_fmt)
        if self.pix_fmt and info.video.pix_fmt.lower() not in self.pix_fmt:
            self.log.debug("Overriding video pix_fmt. Codec cannot be copied because pix_fmt is not approved.")
            vcodec = self.video_codec[0]
            pix_fmt = self.pix_fmt[0]
            if self.video_profile:
                vprofile = self.video_profile[0]
        else:
            pix_fmt = info.video.pix_fmt.lower()

        if self.video_bitrate is not None and vbr > float(self.video_bitrate):
            self.log.debug("Overriding video bitrate. Codec cannot be copied because video bitrate is too high.")
            vcodec = self.video_codec[0]
            vbitrate = self.video_bitrate

        if self.video_width is not None and self.video_width < info.video.video_width:
            self.log.debug("Video width is over the max width, it will be downsampled. Video stream can no longer be copied.")
            vcodec = self.video_codec[0]
            vwidth = self.video_width
        else:
            vwidth = None

        if '264' in info.video.codec.lower() and self.h264_level and info.video.video_level and (info.video.video_level / 10 > self.h264_level):
            self.log.info("Video level %0.1f." % (info.video.video_level / 10))
            vcodec = self.video_codec[0]

        self.log.debug("Video codec: %s." % vcodec)
        self.log.debug("Video bitrate: %s." % vbitrate)

        self.log.info("Profile: %s." % info.video.profile)
        if self.video_profile and info.video.profile.lower().replace(" ", "") not in self.video_profile:
            self.log.debug("Video profile is not supported. Video stream can no longer be copied.")
            vcodec = self.video_codec[0]
            vprofile = self.video_profile[0]
            if self.pix_fmt:
                pix_fmt = self.pix_fmt[0]
        else:
            vprofile = None

        if vcodec == 'nvenc_h264' and pix_fmt == 'yuv420': #yuv420 + nvenc has aliasing that is annoying once it is pointed out, nv12 does not and supports the same colors.
            pix_fmt = 'nv12'

        # Audio streams
        self.log.info("Reading audio streams.")

        overrideLang = True
        num_desired_language_audio_streams = 0
        for a in info.audio:
            try:
                if a.metadata['language'].strip() == "" or a.metadata['language'] is None:
                    a.metadata['language'] = 'und'
            except KeyError:
                a.metadata['language'] = 'und'
            if (a.metadata['language'] == 'und' and self.adl) or (self.awl and a.metadata['language'].lower() in self.awl):
                overrideLang = False
                num_desired_language_audio_streams +=1

        if overrideLang:
            self.awl = None
            self.log.info("No audio streams detected in any appropriate language, relaxing restrictions so there will be some audio stream present.")

        audio_settings = {}
        blocked_audio_languages = []
        disable_faststart = False
        if self.output_extension == 'mkv': # MKV has no moov atom 
            disable_faststart = True
        l = 0
        for a in info.audio:
            try:
                if a.metadata['language'].strip() == "" or a.metadata['language'] is None:
                    a.metadata['language'] = 'und'
            except KeyError:
                a.metadata['language'] = 'und'

            self.log.info("Audio detected for stream #%s: %s [%s]." % (a.index, a.codec, a.metadata['language']))

            if self.output_extension in valid_tagging_extensions and ( a.codec.lower() == 'truehd' or a.codec.startswith( 'pcm' ) ):
                if self.ignore_truehd:
                    self.log.info("MP4 containers do not support truehd audio, and converting it is inconsistent due to video/audio sync issues. Skipping stream %s as typically the 2nd audio track is the AC3 core of the truehd stream." % a.index )
                    continue
                else:
                    self.audio_copyoriginal = False

            if 'ac3' in a.codec.lower() and self.audio_copyoriginal: # EAC3 requires the moov atom to be at the end of the file, while ac3 requires delay_moov.
                                         # https://patchwork.ffmpeg.org/patch/11972/  -- recently added in error checking for this
                                         # I've had trouble making delay_moov work, so we're going to disable faststart on ac3/eac3 files.
                                         # This seems to only be needed when copying audio streams. 
                disable_faststart = True

            # Set undefined language to default language if specified
            if self.adl is not None and a.metadata['language'] == 'und':
                self.log.debug("Undefined language detected, defaulting to [%s]." % self.adl)
                a.metadata['language'] = self.adl

            if self.sample_rate is None:
                try:
                    self.sample_rate = a.audio_samplerate
                except:
                    self.sample_rate = 48000

            # Proceed if no whitelist is set, or if the language is in the whitelist
            iosdata = None
            if self.awl is None or (a.metadata['language'].lower() in self.awl and a.metadata['language'].lower() not in blocked_audio_languages):
                # Create iOS friendly audio stream if the default audio stream has too many channels (iOS only likes AAC stereo)
                if self.iOS and a.audio_channels > 2:
                    iOSbitrate = 256 if (self.audio_bitrate * 2) > 384 else (self.audio_bitrate * 2)
                    self.log.info("Creating audio stream %s from source audio stream %s [iOS-audio]." % (str(l), a.index))
                    self.log.debug("Audio codec: %s." % self.iOS[0])
                    self.log.debug("Channels: 2.")
                    self.log.debug("Filter: %s." % self.iOS_filter)
                    self.log.debug("Bitrate: %s." % iOSbitrate)
                    self.log.debug("Language: %s." % a.metadata['language'])
                    iosdata = {
                        'map': a.index,
                        'codec': self.iOS[0],
                        'channels': 2,
                        'bitrate': iOSbitrate,
                        'samplerate': self.sample_rate,
                        'filter': self.iOS_filter,
                        'language': a.metadata['language'],
                        'disposition': 'none',
                        }
                    if not self.iOSLast:
                        audio_settings.update({l: iosdata})
                        l += 1
                # If the iOS audio option is enabled and the source audio channel is only stereo, the additional iOS channel will be skipped and a single AAC 2.0 channel will be made regardless of codec preference to avoid multiple stereo channels
                self.log.info("Creating audio stream %s from source stream %s." % (str(l), a.index))
                if self.iOS and a.audio_channels <= 2:
                    self.log.debug("Overriding default channel settings because iOS audio is enabled but the source is stereo [iOS-audio].")
                    acodec = 'copy' if a.codec in self.iOS else self.iOS[0]
                    audio_channels = a.audio_channels
                    afilter = self.iOS_filter
                    abitrate = a.audio_channels * 128 if (a.audio_channels * self.audio_bitrate) > (a.audio_channels * 128) else (a.audio_channels * self.audio_bitrate)
                else:
                    # If desired codec is the same as the source codec, copy to avoid quality loss
                    acodec = 'copy' if a.codec.lower() in self.audio_codec else self.audio_codec[0]
                    # Audio channel adjustments
                    if ( self.maxchannels and a.audio_channels > self.maxchannels ):
                        audio_channels = self.maxchannels
                        if acodec == 'copy':
                            acodec = self.audio_codec[0]
                            if acodec == 'copy': # Some people put 'copy' as the first audio codec.
                                acodec = 'aac'
                        abitrate = self.maxchannels * self.audio_bitrate
                    else:
                        audio_channels = a.audio_channels
                        abitrate = a.audio_channels * self.audio_bitrate
                    # Bitrate calculations/overrides
                    if self.audio_bitrate is 0:
                        self.log.debug("Attempting to set bitrate based on source stream bitrate.")
                        try:
                            abitrate = a.bitrate / 1000
                        except:
                            self.log.warning("Unable to determine audio bitrate from source stream %s, defaulting to 256 per channel." % a.index)
                            abitrate = a.audio_channels * 256
                    afilter = self.audio_filter

                self.log.debug("Audio codec: %s." % acodec)
                self.log.debug("Channels: %s." % audio_channels)
                self.log.debug("Bitrate: %s." % abitrate)
                self.log.debug("Language: %s" % a.metadata['language'])
                self.log.debug("Filter: %s" % afilter)

                # If the iOSFirst option is enabled, disable the iOS option after the first audio stream is processed
                if self.iOS and self.iOSFirst:
                    self.log.debug("Not creating any additional iOS audio streams.")
                    self.iOS = False

                audio_settings.update({l: {
                    'map': a.index,
                    'codec': acodec,
                    'channels': audio_channels,
                    'bitrate': abitrate,
                    'filter': afilter,
                    'samplerate': self.sample_rate,
                    'language': a.metadata['language'],
                    'disposition': 'none',
                }})

                if acodec == 'copy' and a.codec == 'aac' and self.aac_adtstoasc:
                    audio_settings[l]['bsf'] = 'aac_adtstoasc'
                if self.output_extension == 'mp4':
                    if a.codec.lower() == 'flac' and acodec == 'copy': #flac in mp4 is experimental, ffmpeg requires adding strict -2 to do it.
                        audio_settings[l]['strict'] = '-2'
                l += 1

                #Add the iOS track last instead
                if self.iOSLast and iosdata:
                    audio_settings.update({l: iosdata})
                    l += 1

                if self.audio_copyoriginal and acodec != 'copy' and self.forceConvert == False:
                    self.log.info("Adding copy of original audio track in format %s" % a.codec)
                    audio_settings.update({l: {
                        'map': a.index,
                        'codec': 'copy',
                        'language': a.metadata['language'],
                        'disposition': 'none',
                    }})
                    if a.codec == 'flac' and self.output_extension == 'mp4': #flac in mp4 is experimental, ffmpeg requires adding strict -2 to do it.
                        audio_settings[l]['strict'] = '-2'

                # Remove the language if we only want the first track from a given language
                if self.audio_first_language_track and self.awl:
                    try:
                        blocked_audio_languages.append(a.metadata['language'].lower())
                        self.log.debug("Removing language from whitelist to prevent multiple tracks of the same: %s." % a.metadata['language'])
                    except:
                        self.log.error("Unable to remove language %s from whitelist." % a.metadata['language'])

        # Audio Default
        if len(audio_settings) > 0 and self.adl:
            try:
                default_track = [x for x in audio_settings.values() if x['language'] == self.adl][0]
                default_track['disposition'] = 'default'
            except:
                audio_settings[0]['disposition'] = 'default'
        else:
            self.log.error("Audio language array is empty.")

        # Subtitle streams
        subtitle_settings = {}
        l = 0
        self.log.info("Reading subtitle streams.")
        forced_sub = 0 # This is the index of the subtitle stream in the entire file, overlay uses this index
        guessed_forced_sub = 0
        guessed_subtitle_number  = -1
        overlay_stream = None
        use_overlay_stream = False
        resize_overlay_stream = False
        subtitle_will_be_burned_in = False
        subtitle_burn = ""
        subtitle_number = -1 # Subtitle_used is the index of the subtitle stream compared to only other subtitles. -vf to overlay uses this.
        subtitle_used = subtitle_number
        shortest_duration_subtitle_stream = 86400 # There probably aren't too many movies that are 24 hours long.
        longest_duration_subtitle_stream = 1
        desired_language_streams = 0
        if self.burn_in_full_subs == True:
            self.burn_in_forced_subs = True
        for s in info.subtitle:
            subtitle_number += 1
            try:
                if s.metadata['language'].strip() == "" or s.metadata['language'] is None:
                    s.metadata['language'] = 'und'
            except KeyError:
                s.metadata['language'] = 'und'
            self.log.info("Subtitle detected for stream #%s: %s [%s]." % (s.index, s.codec, s.metadata['language']))
            # Set undefined language to default language if specified
            if self.sdl is not None and s.metadata['language'] == 'und':
                self.log.debug("Undefined language detected, defaulting to [%s]." % self.sdl)
                s.metadata['language'] = self.sdl
            if self.swl is None or s.metadata['language'].lower() not in self.swl:
                continue
            desired_language_streams += 1

            if self.burn_in_forced_subs == True and self.burn_in_full_subs == False:
                if s.sub_forced == 2 and s.sub_default == 1: ## Prefer subs that are flagged forced AND default by their disposition
                    forced_sub = s.index
                    subtitle_used = subtitle_number
                    break
                elif s.sub_forced == 2: ## Prefer flagged subs next
                    forced_sub = s.index
                    subtitle_used = subtitle_number
                    break
                elif s.sub_forced == 1: ## Go searching for forced subs that hang out in the title metadata
                    forced_sub = s.index
                    subtitle_used = subtitle_number
                    break
                elif s.sub_force_guess:# Finally, throw a guess at it if there are 2 desired language subtitle streams.
                    total_seconds = 0
                    s.sub_force_guess = s.sub_force_guess[:-3]
                    try:
                        duration = datetime.datetime.strptime(s.sub_force_guess,'%H:%M:%S.%f')
                        total_seconds = duration.second + ( duration.minute * 60 ) + ( duration.hour * 3600 )
                    except:
                        self.log.info( "Couldn't use experimental subtitle duration. Probably due to odd time formatting - Attempted to parse time format from %s" % s.sub_force_guess )
                        try:
                            total_seconds = float( s.sub_force_guess )
                        except:
                            self.log.info("Attempt #2 failed for subtitle duration.")
                    if total_seconds > 0:
                        if total_seconds < shortest_duration_subtitle_stream:
                            shortest_duration_subtitle_stream = total_seconds
                            guessed_forced_sub = s.index
                            guessed_subtitle_number = subtitle_number
                        if total_seconds > longest_duration_subtitle_stream:
                            longest_duration_subtitle_stream = total_seconds
            elif self.burn_in_full_subs == True:
                if s.sub_force_guess:
                    total_seconds = 0
                    s.sub_force_guess = s.sub_force_guess[:-3]
                    try:
                        duration = datetime.datetime.strptime(s.sub_force_guess,'%H:%M:%S.%f')
                        total_seconds = duration.second + ( duration.minute * 60 ) + ( duration.hour * 3600 )
                    except:
                        self.log.info( "Couldn't use experimental subtitle duration. Probably due to odd time formatting - Attempted to parse time format from %s" % s.sub_force_guess )
                        try:
                            total_seconds = float( s.sub_force_guess )
                        except:
                            self.log.info("Attempt #2 failed for subtitle duration.")
                    if total_seconds > 0:
                        if total_seconds < shortest_duration_subtitle_stream:
                            shortest_duration_subtitle_stream = total_seconds
                        if total_seconds > longest_duration_subtitle_stream:
                            longest_duration_subtitle_stream = total_seconds #Here we actually want the longest subtitle stream. This is probably going to accidentally tag some SDH/hearing impaired streams, but they will work.
                            guessed_forced_sub = s.index
                            guessed_subtitle_number = subtitle_number
                else:
                    forced_sub = s.index   # burn in the first subtitle stream that matches the users language.  
                    subtitle_used = subtitle_number
                    s.sub_forced = 1
                    break

        if self.burn_in_full_subs == True:
            forced_sub = guessed_forced_sub
            subtitle_used = guessed_subtitle_number
        elif forced_sub == 0 and desired_language_streams > 1 and longest_duration_subtitle_stream > 1 and \
            ( float( shortest_duration_subtitle_stream ) / float( longest_duration_subtitle_stream ) ) < 0.75: # This is a sanity check just in case there is a video with multiple
            forced_sub = guessed_forced_sub # native-speaking language subtitle streams and the 2nd one just happens to be a director's commentary instead of foreign language subtitles.
            subtitle_used = guessed_subtitle_number # If the film has >75% forced subtitles then it's probably going to be flagged with overrideLang = true
            self.log.info( "Used experimental forced subtitle guess" ) #Just to check when it is used.

        for s in info.subtitle:
            if forced_sub > 0 and s.index != forced_sub and self.burn_in_forced_subs == True:
                continue
            if forced_sub > 0 and self.burn_in_forced_subs == True:
                subtitle_will_be_burned_in = True
                if vcodec == 'copy':
                    vcodec = self.video_codec[0]
            # Make sure its not an image based codec
            if self.embedsubs and s.codec.lower() not in bad_subtitle_codecs:
                # Proceed if no whitelist is set, or if the language is in the whitelist
                if self.swl is None or s.metadata['language'].lower() in self.swl:
                    subtitle_settings.update({l: {
                        'map': s.index,
                        'codec': self.scodec[0],
                        'language': s.metadata['language'],
                        'encoding': self.subencoding,
                        'disposition': 'none',
                        'forced': s.sub_forced,
                        'default': s.sub_default,
                        'burn_in_forced_subs': self.burn_in_forced_subs,
                        'subtitle_burn': drive_letter_no_colon + r"\:" + directory + "\\\\" + filename + "." + input_extension + \
                            ( ".original:si=" if ( input_extension == self.output_extension and input_dir == output_dir ) else ":si=" ) + str( subtitle_used )  #FFmpeg requires a very specific string of letters for -vf subtitles=
                    }} )
                    if ( os.name != 'nt' ):  #TODO: Make this a bit less hacky... if possible?
                        temp_directory = directory
                        temp_directory = temp_directory.replace("\\", "//" )
                        subtitle_settings[l]['subtitle_burn'] = temp_directory + "//" + filename + "." + input_extension + \
                           ( ".original:si=" if ( input_extension == self.output_extension and input_dir == output_dir ) else ":si=" ) + str( subtitle_used ) + str( subtitle_used )
                    self.log.info("Creating subtitle stream %s from source stream %s." % (l, s.index))
                    subtitle_temporary = subtitle_settings[l]['subtitle_burn']
                    subtitle_temporary = subtitle_temporary.replace( "\\", "\\\\" )
                    subtitle_temporary = subtitle_temporary.replace("'", "\\\\\\\'\\\\\\" ) # "Special character escapes are like violence: If they're not solving your problem, you're not using enough.
                    subtitle_burn = "subtitles=" + subtitle_temporary
                    l = l + 1
            
            use_overlay_stream = ( s.codec.lower() in bad_subtitle_codecs and self.embedsubs == True and forced_sub > 0 and self.burn_in_forced_subs == True ) # This overlays forced picture subtitles on top of the video stream. Slows down conversion significantly.
            if use_overlay_stream == True:
                overlay_stream = s.index
                if s.video_width != None and ( s.video_width != info.video.video_width ) and vwidth == None:
                    resize_overlay_stream = True

            elif s.codec.lower() in bad_subtitle_codecs and self.embedsubs == True and self.output_extension == "mkv":
                # Proceed if no whitelist is set, or if the language is in the whitelist
                if self.swl is None or s.metadata['language'].lower() in self.swl:
                    subtitle_settings.update({l: {
                        'map': s.index,
                        'codec': 'copy',
                        'language': s.metadata['language'],
                        'forced': s.sub_forced,
                        'default': s.sub_default
                    }} )
                    l = l + 1
            elif s.codec.lower() not in bad_subtitle_codecs and not self.embedsubs:
                if self.swl is None or s.metadata['language'].lower() in self.swl:
                    for codec in self.scodec:
                        ripsub = {0: {
                            'map': s.index,
                            'codec': codec,
                            'language': s.metadata['language']
                        }}
                        options = {
                            'format': codec,
                            'subtitle': ripsub,
                        }

                        try:
                            extension = subtitle_codec_extensions[codec]
                        except:
                            self.log.info("Wasn't able to determine subtitle file extension, defaulting to '.srt'.")
                            extension = 'srt'

                        forced = ".forced" if s.sub_forced else ""

                        input_dir, filename, input_extension = self.parseFile(inputfile)
                        output_dir = input_dir if self.output_dir is None else self.output_dir
                        outputfile = os.path.join(output_dir, filename + "." + s.metadata['language'] + forced + "." + extension)

                        i = 2
                        while os.path.isfile(outputfile):
                            self.log.debug("%s exists, appending %s to filename." % (outputfile, i))
                            outputfile = os.path.join(output_dir, filename + "." + s.metadata['language'] + forced + "." + str(i) + "." + extension)
                            i += 1
                        try:
                            self.log.info("Ripping %s subtitle from source stream %s into external file." % (s.metadata['language'], s.index))
                            conv = Converter(self.FFMPEG_PATH, self.FFPROBE_PATH).convert(inputfile, outputfile, options, timeout=None)
                            for timecode in conv:
                                    pass

                            self.log.info("%s created." % outputfile)
                        except:
                            self.log.exception("Unabled to create external subtitle file for stream %s." % (s.index))
                        
                        try:
                            os.chmod(outputfile, self.permissions)  # Set permissions of newly created file
                        except:
                            self.log.exception("Unable to set new file permissions.")

        # Attempt to download subtitles if they are missing using subliminal
        languages = set()
        try:
            if self.swl:
                for alpha3 in self.swl:
                    languages.add(Language(alpha3))
            elif self.sdl:
                languages.add(Language(self.sdl))
            else:
                self.downloadsubs = False
                self.log.error("No valid subtitle language specified, cannot download subtitles.")
        except:
            self.log.exception("Unable to verify subtitle languages for download.")
            self.downloadsubs = False

        if self.downloadsubs:
            import subliminal
            self.log.info("Attempting to download subtitles.")

            # Attempt to set the dogpile cache
            try:
                subliminal.region.configure('dogpile.cache.memory')
            except:
                pass

            try:
                provider_settings = {'opensubtitles': self.opensubtitles,
                                     'podnapisi': self.podnapisi }

                video = subliminal.scan_video(os.path.abspath(inputfile), subtitles=True, embedded_subtitles=True)
                subtitles = subliminal.download_best_subtitles([video], languages, hearing_impaired=False, min_score = 337, providers=self.subproviders, provider_configs = provider_settings )
                try:
                    subliminal.save_subtitles(video, subtitles[video])
                except:
                    # Support for older versions of subliminal
                    subliminal.save_subtitles(subtitles)
                    self.log.info("Please update to the latest version of subliminal.")
            except Exception as e:
                self.log.info("Unable to download subtitles.", exc_info=True)
                self.log.debug("Unable to download subtitles.", exc_info=True)
        # External subtitle import
        if self.embedsubs and not self.embedonlyinternalsubs:  # Don't bother if we're not embeddeding subtitles and external subtitles
            src = 1  # FFMPEG input source number
            for dirName, subdirList, fileList in os.walk(input_dir):
                for fname in fileList:
                    subname, subextension = os.path.splitext(fname)
                    # Watch for appropriate file extension
                    if subextension[1:] in valid_subtitle_extensions:
                        x, lang = os.path.splitext(subname)
                        lang = lang[1:]
                        # Using bablefish to convert a 2 language code to a 3 language code
                        if len(lang) is 2:
                            try:
                                babel = Language.fromalpha2(lang)
                                lang = babel.alpha3
                            except:
                                pass
                        # If subtitle file name and input video name are the same, proceed
                        if x == filename:
                            self.log.info("External %s subtitle file detected." % lang)
                            if self.swl is None or lang in self.swl:

                                self.log.info("Creating subtitle stream %s by importing %s." % (l, fname))

                                if forced_sub == 0 and self.burn_in_forced_subs == True:
                                    subtitle_settings.update({l: {
                                        'path': os.path.join(dirName, fname),
                                        'source': src,
                                        'map': 0,
                                        'codec': 'mov_text',
                                        'language': lang,
                                        'disposition':'none',
                                        'burn_in_forced_subs': self.burn_in_forced_subs,
                                        'subtitle_burn': os.path.join(dirName, fname)
                                        }})
                                else:
                                    subtitle_settings.update({l: {
                                        'path': os.path.join(dirName, fname),
                                        'source': src,
                                        'map': 0,
                                        'codec': 'mov_text',
                                        'language': lang}})

                                self.log.debug("Path: %s." % os.path.join(dirName, fname))
                                self.log.debug("Source: %s." % src)
                                self.log.debug("Codec: mov_text.")
                                self.log.debug("Langauge: %s." % lang)

                                l = l + 1
                                src = src + 1

                                self.deletesubs.add(os.path.join(dirName, fname))

                            else:
                                self.log.info("Ignoring %s external subtitle stream due to language %s." % (fname, lang))

        # Subtitle Default
        if len(subtitle_settings) > 0 and self.sdl:
            try:
                default_track = [x for x in subtitle_settings.values() if x['language'] == self.sdl][0]
                default_track['disposition'] = 'default'
            except:
                subtitle_settings[0]['disposition'] = 'default'
        else:
            self.log.warning("Subtitle language array is empty.")

        # Collect all options
        options = {
            'format': self.output_format,
            'video': {
                'codec': vcodec,
                'map': info.video.index,
                'bitrate': vbitrate,
                'level': self.h264_level,
                'qmin': self.qmin,
                'qmax': self.qmax,
                'global_quality': self.global_quality,
                'maxrate': self.maxrate,
                'minrate': self.minrate,
                'bufsize': self.bufsize,
                'vsync': self.vsync,
                'level': self.h264_level,
                'profile': vprofile,
                'pix_fmt': pix_fmt,
                'color_space_convert': None,
                'filter_complex': None
            },
            'audio': audio_settings,
            'subtitle': subtitle_settings,
            'preopts': ['-fix_sub_duration'],
            'postopts': ['-threads', self.threads]
        }

        # If a CRF option is set, override the determine bitrate
        if self.vcrf:
            del options['video']['bitrate']
            options['video']['crf'] = self.vcrf

        if use_overlay_stream:
            options['preopts'].remove( '-fix_sub_duration' ) #fix_sub_duration really screws up the duration of overlaid "picture" subtitles,
                           #as they stay on the screen for less than a second. This doesn't have any negative consequences that I've noticed.
            del options['video']['map'] #The video stream formally known as [v:(number)] is remapped to [video] in order to support scaling picture subtitles to another resolution.

        if self.preopts:
            options['preopts'].extend(self.preopts)
        if disable_faststart == False and self.relocate_moov is True:
            options['postopts'].extend(['-movflags', 'faststart'])
        if self.postopts:
            options['postopts'].extend(self.postopts)

        options['preopts'].extend(['-vsync', self.vsync ])

        if info.video.color_space == 'bt2020nc':  # Thanks to https://stevens.li/guides/video/converting-hdr-to-sdr-with-ffmpeg/ 
            if self.enable_opencl_hdr_sdr_tonemapping:
                options['preopts'].extend( ['-init_hw_device', self.init_hw_device ] )
                options['preopts'].extend( ['-filter_hw_device', 'gpu' ] )
                if use_overlay_stream:
                    if resize_overlay_stream == True:
                        options['video']['filter_complex'] = "hwupload,tonemap_opencl=t=bt709:tonemap=hable:format=nv12,hwdownload,format=nv12[video];[0:%s][video]scale2ref[sub][video];[video][sub]overlay[video]" % ( overlay_stream )
                    elif vwidth == None:
                        options['video']['filter_complex'] = "hwupload,tonemap_opencl=t=bt709:tonemap=hable:format=nv12,hwdownload,format=nv12[base];[base][0:%s]overlay[video]" % (overlay_stream)
                    else:
                        options['video']['filter_complex'] = "hwupload,tonemap_opencl=t=bt709:tonemap=hable:format=nv12,hwdownload,format=nv12[video];[0:%s][video]scale2ref[sub][video];[video][sub]overlay[video]" % ( overlay_stream )
                else:
                    options['video']['color_space_convert'] = "hwupload,tonemap_opencl=t=bt709:tonemap=hable:format=nv12,hwdownload,format=nv12"
                    if subtitle_will_be_burned_in:
                        options['video']['color_space_convert'] = "hwupload,tonemap_opencl=t=bt709:tonemap=hable:format=nv12,hwdownload,format=nv12," + subtitle_burn 
                        del subtitle_settings[0]
            elif self.hdr_sdr_convert:
                if use_overlay_stream:
                    if resize_overlay_stream == True:
                        options['video']['filter_complex'] = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=nv12[video];[0:%s][video]scale2ref[sub][video];[video][sub]overlay[video]" % ( overlay_stream )
                    elif vwidth == None:
                        options['video']['filter_complex'] = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=nv12[base];[base][0:%s]overlay[video]" % (overlay_stream)
                    else:
                        options['video']['filter_complex'] = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=nv12[video];[0:%s][video]scale2ref[sub][video];[video][sub]overlay[video]" % ( overlay_stream )
                else:
                    options['video']['color_space_convert'] = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=nv12"
                    if subtitle_will_be_burned_in:
                        options['video']['color_space_convert'] = "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=nv12," + subtitle_burn
                        del subtitle_settings[0]
        elif use_overlay_stream:
            if vwidth == None:
                options['video']['filter_complex'] = "[0:v][0:%s]overlay[video]" % ( overlay_stream )
            else:
                options['video']['filter_complex'] = "[video][0:%s]overlay[video]" % ( overlay_stream )

        nvenc_cuvid_codecs = { "h264", "mjpeg", "mpeg1video", "mpeg2video", "mpeg4", "vc1", "vp8", "hevc", "vp9" }

        if self.dxva2_decoder: # DXVA2 will fallback to CPU decoding when it hits a file that it cannot handle, so we don't need to check if the file is supported.
            options['preopts'].extend(['-hwaccel', 'dxva2' ])
        elif info.video.codec.lower() == "hevc" and self.hevc_qsv_decoder:
            options['preopts'].extend(['-vcodec', 'hevc_qsv'])
        elif vcodec == "h264qsv" and info.video.codec.lower() == "h264" and self.qsv_decoder and (info.video.video_level / 10) < 5:
            options['preopts'].extend(['-vcodec', 'h264_qsv'])
        elif info.video.codec.lower() in nvenc_cuvid_codecs and \
        self.nvenc_cuvid and vcodec != "copy" and not '422' in info.video.pix_fmt and not '444' in info.video.pix_fmt: #Cuvid only supports 420 chroma at the moment. 
            if not '10le' in info.video.pix_fmt and not '16le' in info.video.pix_fmt and subtitle_will_be_burned_in == False and pix_fmt == 'yuv420': #Cannot do full hardware decoding with 10/12 bit video, it must be copied to system memory after decoding.
                options['preopts'].extend(['-hwaccel', 'cuvid' ])                                                             #Also cannot do full hardware decoding when subtitles are being burned in
                if info.video.codec.lower() == "hevc" or info.video.codec.lower() == "vp9":
                    if self.nvenc_decoder_hevc_gpu:
                        options['preopts'].extend(['-hwaccel_device', str( self.nvenc_decoder_hevc_gpu )])
                        self.nvenc_decoder_hevc_gpu = None
                elif self.nvenc_decoder_gpu:
                    options['preopts'].extend(['-hwaccel_device', str( self.nvenc_decoder_gpu )])
                    self.nvenc_decoder_gpu = None
                options['video']['nvenc_hwaccel_enabled'] = True
            else:
                options['video']['nvenc_hwaccel_enabled'] = False
            if info.video.codec.lower() == "h264":
                options['preopts'].extend(['-c:v', 'h264_cuvid'])
            elif info.video.codec.lower() == "mjpeg":
                options['preopts'].extend(['-c:v', 'mjpeg_cuvid'])
            elif info.video.codec.lower() == "mpeg1video":
                options['preopts'].extend(['-c:v', 'mpeg1_cuvid'])
            elif info.video.codec.lower() == "mpeg2video":
                options['preopts'].extend(['-c:v', 'mpeg2_cuvid'])
            elif info.video.codec.lower() == "mpeg4":
                options['preopts'].extend(['-c:v', 'mpeg4_cuvid'])
            elif info.video.codec.lower() == "vc1":
                options['preopts'].extend(['-c:v', 'vc1_cuvid'])
            elif info.video.codec.lower() == "vp8":
                options['preopts'].extend(['-c:v', 'vp8_cuvid'])
            elif info.video.codec.lower() == "hevc" and self.nvenc_cuvid_hevc:
                options['preopts'].extend(['-c:v', 'hevc_cuvid'])
            elif info.video.codec.lower() == "vp9" and self.nvenc_cuvid_hevc:
                options['preopts'].extend(['-c:v', 'vp9_cuvid'])
            if info.video.codec.lower() == "hevc" or info.video.codec.lower() == "vp9":
                if self.nvenc_decoder_hevc_gpu:
                    options['preopts'].extend(['-gpu', str( self.nvenc_decoder_hevc_gpu )])
            elif self.nvenc_decoder_gpu:
                options['preopts'].extend(['-gpu', str( self.nvenc_decoder_gpu )])
        else:
            options['video']['nvenc_hwaccel_enabled'] = False

        # Add width option
        if vwidth:
            options['video']['width'] = vwidth
        # Add Nvidia specific options
        if self.nvenc_profile:
            options['video']['nvenc_profile'] = self.nvenc_profile
        if self.nvenc_preset:
            options['video']['nvenc_preset'] = self.nvenc_preset
        if self.nvenc_rate_control:
            options['video']['nvenc_rate_control'] = self.nvenc_rate_control
            if self.nvenc_rate_control == "vbr_minqp" and self.qmin is None:
                self.log.error("nvenc vbr_minqp requires qmin option set.")
            elif self.nvenc_rate_control == "constqp" and self.global_quality is None:
                self.log.error("nvenc constqp requires global_quality to be set." )
        if self.nvenc_gpu:
            options['video']['nvenc_gpu'] = self.nvenc_gpu
        if self.nvenc_temporal_aq:
            options['video']['nvenc_temporal_aq'] = self.nvenc_temporal_aq
        if self.nvenc_weighted_prediction:
            options['video']['nvenc_weighted_prediction'] = self.nvenc_weighted_prediction
        if self.nvenc_rc_lookahead:
            options['video']['nvenc_rc_lookahead'] = self.nvenc_rc_lookahead
        # HEVC Tagging for copied streams
        if info.video.codec.lower() in ['x265', 'h265', 'hevc'] and vcodec == 'copy':
            options['postopts'].extend(['-tag:v', 'hvc1'])
            self.log.info("Tagging copied video stream as hvc1")

        self.options = options
        return options

    # Encode a new file based on selected options, built in naming conflict resolution
    def convert(self, inputfile, options, reportProgress=False):
        self.log.info("Starting conversion.")

        input_dir, filename, input_extension = self.parseFile(inputfile)
        output_dir = input_dir if self.output_dir is None else self.output_dir
        try:
            outputfile = os.path.join(output_dir.decode(sys.getfilesystemencoding()), filename.decode(sys.getfilesystemencoding()) + "." + self.output_extension).encode(sys.getfilesystemencoding())
        except:
            outputfile = os.path.join(output_dir, filename + "." + self.output_extension)
        self.log.debug("Input directory: %s." % input_dir)
        self.log.debug("File name: %s." % filename)
        self.log.debug("Input extension: %s." % input_extension)
        self.log.debug("Output directory: %s." % output_dir)
        self.log.debug("Output file: %s." % outputfile)

        if self.output_extension == input_extension and len([x for x in [options['video']] + [x for x in options['audio'].values()] + [x for x in options['subtitle'].values()] if x['codec'] != 'copy']) == 0:
            self.log.info("Input and output extensions match and every codec is copy, this file probably doesn't need conversion, returning.")
            self.log.info(inputfile)
            return inputfile, ""

        if os.path.abspath(inputfile) == os.path.abspath(outputfile):
            self.log.debug("Inputfile and outputfile are the same.")
            try:
                os.rename(inputfile, inputfile + ".original")
                inputfile = inputfile + ".original"
                self.log.debug("Renaming original file to %s." % inputfile)
            except:
                i = 2
                while os.path.isfile(outputfile):
                    outputfile = os.path.join(output_dir, filename + "(" + str(i) + ")." + self.output_extension)
                    i += i
                self.log.debug("Unable to rename inputfile. Setting output file name to %s." % outputfile)

        conv = Converter(self.FFMPEG_PATH, self.FFPROBE_PATH).convert(inputfile, outputfile, options, timeout=None, preopts=options['preopts'], postopts=options['postopts'])

        try:
            for timecode in conv:
                if reportProgress:
                    try:
                        sys.stdout.write('\r')
                        sys.stdout.write('[{0}] {1}%'.format('#' * (timecode / 10) + ' ' * (10 - (timecode / 10)), timecode))
                    except:
                        sys.stdout.write(str(timecode))
                    sys.stdout.flush()

            self.log.info("%s created." % outputfile)

            try:
                os.chmod(outputfile, self.permissions)  # Set permissions of newly created file
            except:
                self.log.exception("Unable to set new file permissions.")

        except FFMpegConvertError as e:
            self.log.exception("Error converting file, FFMPEG error.")
            self.log.error(e.cmd)
            self.log.error(e.output)
            if os.path.isfile(outputfile):
                self.removeFile(outputfile)
                self.log.error("%s deleted." % outputfile)
            outputfile = None

        return outputfile, inputfile

    # Break apart a file path into the directory, filename, and extension
    def parseFile(self, path):
        path = os.path.abspath(path)
        input_dir, filename = os.path.split(path)
        filename, input_extension = os.path.splitext(filename)
        input_extension = input_extension[1:]
        return input_dir, filename, input_extension

    # Makes additional copies of the input file in each directory specified in the copy_to option
    def replicate(self, inputfile, relativePath=None):
        files = [inputfile]

        if self.copyto:
            self.log.debug("Copyto option is enabled.")
            for d in self.copyto:
                if (relativePath):
                    d = os.path.join(d, relativePath)
                    if not os.path.exists(d):
                        os.makedirs(d)
                try:
                    shutil.copy(inputfile, d)
                    self.log.info("%s copied to %s." % (inputfile, d))
                    files.append(os.path.join(d, os.path.split(inputfile)[1]))
                except Exception as e:
                    self.log.exception("First attempt to copy the file has failed.")
                    try:
                        if os.path.exists(inputfile):
                            self.removeFile(inputfile, 0, 0)
                        try:
                            shutil.copy(inputfile.decode(sys.getfilesystemencoding()), d)
                        except:
                            shutil.copy(inputfile, d)
                        self.log.info("%s copied to %s." % (inputfile, d))
                        files.append(os.path.join(d, os.path.split(inputfile)[1]))
                    except Exception as e:
                        self.log.exception("Unable to create additional copy of file in %s." % (d))

        if self.moveto:
            self.log.debug("Moveto option is enabled.")
            moveto = os.path.join(self.moveto, relativePath) if relativePath else self.moveto
            if not os.path.exists(moveto):
                os.makedirs(moveto)
            try:
                shutil.move(inputfile, moveto)
                self.log.info("%s moved to %s." % (inputfile, moveto))
                files[0] = os.path.join(moveto, os.path.basename(inputfile))
            except Exception as e:
                self.log.exception("First attempt to move the file has failed.")
                try:
                    if os.path.exists(inputfile):
                        self.removeFile(inputfile, 0, 0)
                    shutil.move(inputfile.decode(sys.getfilesystemencoding()), moveto)
                    self.log.info("%s moved to %s." % (inputfile, moveto))
                    files[0] = os.path.join(moveto, os.path.basename(inputfile))
                except Exception as e:
                    self.log.exception("Unable to move %s to %s" % (inputfile, moveto))
        for filename in files:
            self.log.debug("Final output file: %s." % filename)
        return files

    # Robust file removal function, with options to retry in the event the file is in use, and replace a deleted file
    def removeFile(self, filename, retries=2, delay=10, replacement=None):
        for i in range(retries + 1):
            try:
                # Make sure file isn't read-only
                os.chmod(filename, int("0777", 8))
            except:
                self.log.debug("Unable to set file permissions before deletion. This is not always required.")
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                # Replaces the newly deleted file with another by renaming (replacing an original with a newly created file)
                if replacement is not None:
                    os.rename(replacement, filename)
                    filename = replacement
                break
            except:
                self.log.exception("Unable to remove or replace file %s." % filename)
                if delay > 0:
                    self.log.debug("Delaying for %s seconds before retrying." % delay)
                    time.sleep(delay)
        return False if os.path.isfile(filename) else True
