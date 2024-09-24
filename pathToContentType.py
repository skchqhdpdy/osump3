import os

def pathToContentType(path, isInclude=False):
    if path == 0: return None
    fn, fe = os.path.splitext(os.path.basename(path));
    ffln = path.replace(f"/{path.split('/')[-1]}", "")
    fln = os.path.splitext(os.path.basename(ffln.split('/')[-1]))[0]
    if os.name == "nt":
        while fln.endswith("."): fln = fln[:-1]

    if isInclude and ".aac" in path or not isInclude and path.endswith(".aac"): ct, tp = ("audio/aac", "audio")
    elif isInclude and ".apng" in path or not isInclude and path.endswith(".apng"): ct, tp = ("image/apng", "image")
    elif isInclude and ".avif" in path or not isInclude and path.endswith(".avif"): ct, tp = ("image/avif", "image")
    elif isInclude and ".avi" in path or not isInclude and path.endswith(".avi"): ct, tp = ("video/x-msvideo", "video")
    elif isInclude and ".bin" in path or not isInclude and path.endswith(".bin"): ct, tp = ("application/octet-stream", "file")
    elif isInclude and ".css" in path or not isInclude and path.endswith(".css"): ct, tp = ("text/css", "file")
    elif isInclude and ".gif" in path or not isInclude and path.endswith(".gif"): ct, tp = ("image/gif", "image")
    elif isInclude and ".html" in path or not isInclude and path.endswith(".html"): ct, tp = ("text/html", "file")
    elif isInclude and ".ico" in path or not isInclude and path.endswith(".ico"): ct, tp = ("image/x-icon", "image")
    elif isInclude and ".jfif" in path or not isInclude and path.endswith(".jfif"): ct, tp = ("image/jpeg", "image")
    elif isInclude and ".jpeg" in path or not isInclude and path.endswith(".jpeg"): ct, tp = ("image/jpeg", "image")
    elif isInclude and ".jpg" in path or not isInclude and path.endswith(".jpg"): ct, tp = ("image/jpeg", "image")
    elif isInclude and ".js" in path or not isInclude and path.endswith(".js"): ct, tp = ("text/javascript", "file")
    elif isInclude and ".json" in path or not isInclude and path.endswith(".json"): ct, tp = ("application/json", "file")
    elif isInclude and ".mp3" in path or not isInclude and path.endswith(".mp3"): ct, tp = ("audio/mpeg", "audio")
    elif isInclude and ".mp4" in path or not isInclude and path.endswith(".mp4"): ct, tp = ("video/mp4", "video")
    elif isInclude and ".mpeg" in path or not isInclude and path.endswith(".mpeg"): ct, tp = ("audio/mpeg", "audio")
    elif isInclude and ".oga" in path or not isInclude and path.endswith(".oga"): ct, tp = ("audio/ogg", "audio")
    elif isInclude and ".ogg" in path or not isInclude and path.endswith(".ogg"): ct, tp = ("application/ogg", "audio")
    elif isInclude and ".ogv" in path or not isInclude and path.endswith(".ogv"): ct, tp = ("video/ogg", "video")
    elif isInclude and ".ogx" in path or not isInclude and path.endswith(".ogx"): ct, tp = ("application/ogg", "audio")
    elif isInclude and ".opus" in path or not isInclude and path.endswith(".opus"): ct, tp = ("audio/opus", "audio")
    elif isInclude and ".png" in path or not isInclude and path.endswith(".png"): ct, tp = ("image/png", "image")
    elif isInclude and ".svg" in path or not isInclude and path.endswith(".svg"): ct, tp = ("image/svg+xml", "image")
    elif isInclude and ".tif" in path or not isInclude and path.endswith(".tif"): ct, tp = ("image/tiff", "image")
    elif isInclude and ".tiff" in path or not isInclude and path.endswith(".tiff"): ct, tp = ("image/tiff", "image")
    elif isInclude and ".ts" in path or not isInclude and path.endswith(".ts"): ct, tp = ("video/mp2t", "video")
    elif isInclude and ".txt" in path or not isInclude and path.endswith(".txt"): ct, tp = ("text/plain", "file")
    elif isInclude and ".wav" in path or not isInclude and path.endswith(".wav"): ct, tp = ("audio/wav", "audio")
    elif isInclude and ".weba" in path or not isInclude and path.endswith(".weba"): ct, tp = ("audio/webm", "audio")
    elif isInclude and ".webm" in path or not isInclude and path.endswith(".webm"): ct, tp = ("video/webm", "video")
    elif isInclude and ".webp" in path or not isInclude and path.endswith(".webp"): ct, tp = ("image/webp", "image")
    elif isInclude and ".zip" in path or not isInclude and path.endswith(".zip"): ct, tp = ("application/zip", "file")
    elif isInclude and ".flv" in path or not isInclude and path.endswith(".flv"): ct, tp = ("video/x-flv", "video")
    elif isInclude and ".wmv" in path or not isInclude and path.endswith(".wmv"): ct, tp = ("video/x-ms-wmv", "video")
    elif isInclude and ".mkv" in path or not isInclude and path.endswith(".mkv"): ct, tp = ("video/x-matroska", "video")

    elif isInclude and ".osz" in path or not isInclude and path.endswith(".osz"): ct, tp = ("application/x-osu-beatmap-archive", "file")
    elif isInclude and ".osr" in path or not isInclude and path.endswith(".osr"): ct, tp = ("application/x-osu-replay", "file")
    elif isInclude and ".osu" in path or not isInclude and path.endswith(".osu"): ct, tp = ("application/x-osu-beatmap", "file")
    elif isInclude and ".osb" in path or not isInclude and path.endswith(".osb"): ct, tp = ("application/x-osu-storyboard", "file")
    elif isInclude and ".osk" in path or not isInclude and path.endswith(".osk"): ct, tp = ("application/x-osu-skin", "file")

    else: ct, tp = ("application/octet-stream", "?")
    return {"Content-Type": ct, "foldername": fln, "fullFoldername": ffln, "filename": fn, "extension": fe, "fullFilename": fn + fe, "type": tp, "path": path}