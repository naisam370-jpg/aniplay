# AniPlay API Documentation

## IPC Events

### Video Events
- `video:load` - Load a video file
- `video:play` - Start playback
- `video:pause` - Pause playback
- `video:seek` - Seek to specific time
- `video:stop` - Stop playback

### File Events
- `file:open` - Open file dialog

## MPV Controller Methods

### loadVideo(filePath)
Loads a video file for playback.

### play()
Starts video playback.

### pause()
Pauses video playback.

### seek(time)
Seeks to specific time in seconds.
