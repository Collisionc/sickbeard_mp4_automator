ffmpeg -h full > ffmpegHelpOutput.txt
ffmpeg -encoders >> ffmpegHelpOutput.txt
ffmpeg -decoders >> ffmpegHelpOutput.txt
ffmpeg -codecs >> ffmpegHelpOutput.txt
ffmpeg -pix_fmts >> ffmpegHelpOutput.txt
ffmpeg -formats >> ffmpegHelpOutput.txt
ffmpeg -muxers >> ffmpegHelpOutput.txt
ffmpeg -demuxers >> ffmpegHelpOutput.txt
ffmpeg -hwaccels >> ffmpegHelpOutput.txt
ffmpeg -filters >> ffmpegHelpOutput.txt
ffmpeg -layouts >> ffmpegHelpOutput.txt
ffmpeg -sample_fmts >> ffmpegHelpOutput.txt
ffmpeg -colors >> ffmpegHelpOutput.txt
ffmpeg -bsfs >> ffmpegHelpOutput.txt
ffmpeg -h encoder=nvenc_h264 >> ffmpegHelpOutput.txt
ffmpeg -h encoder=nvenc_hevc >> ffmpegHelpOutput.txt
ffmpeg -h decoder=h264_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=hevc_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=mjpeg_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=mpeg1_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=mpeg2_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=mpeg4_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=vc1_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=vp8_cuvid >> ffmpegHelpOutput.txt
ffmpeg -h decoder=vp9_cuvid >> ffmpegHelpOutput.txt
