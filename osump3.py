import winreg
import os
import random
import threading
from pynput import keyboard
import pygame
import time
import requests
from tqdm import tqdm
import hashlib
import zipfile
from pydub.utils import mediainfo
import ctypes

requestHeaders = {"User-Agent": "osump3"}
version = "1.0.0"
try:
    nv = requests.get("https://raw.githubusercontent.com/skchqhdpdy/osump3/main/version.txt", headers=requestHeaders).text
    if version != nv:
        print(f"업데이트 있음!\n현재버전 : {version}\n최신버전 : {nv}")
        print("https://github.com/skchqhdpdy/osump3")
        if input("Press Enter to exit...") != "ignore":
            exit()
except Exception as e:
    print(f"Version Check Error | {e}")

#ffmpeg 설치확인
if os.system(f"ffmpeg -version > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1") != 0:
    if not ctypes.windll.shell32.IsUserAnAdmin() != 0: input("관리자 권한으로 실행하세요!"); exit()

    print("https://aodd.xyz/file%20hosting/Downloads/ffmpeg.zip --> C:\\Program Files\\ffmpeg osump3")
    ff = requests.get("https://aodd.xyz/file%20hosting/Downloads/ffmpeg.zip", headers=requestHeaders, stream=True)
    # tqdm을 사용하여 진행률 표시
    with open("C:/Program Files/ffmpeg osump3.zip", 'wb') as file:
        with tqdm(total=int(ff.headers.get('Content-Length', 0)), unit='B', unit_scale=True, unit_divisor=1024, ncols=60) as pbar:
            for data in ff.iter_content(1024):
                file.write(data)
                pbar.update(len(data))
    zipfile.ZipFile("C:/Program Files/ffmpeg osump3.zip").extractall("C:/Program Files/ffmpeg osump3")
    os.remove(f"C:/Program Files/ffmpeg osump3.zip")
    #시스템 환경변수 Path의 키
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS)
    current_path, _ = winreg.QueryValueEx(key, 'Path') #현재 Path 값을 읽어옴
    new_path = f"{current_path};C:\\Program Files\\ffmpeg osump3\\bin" #기존 Path에 새 경로 추가
    winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path) #변경된 Path 값을 설정

def getOsupath():
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"osu\Shell\Open\Command")
        return winreg.QueryValue(key, None).strip('"').split("osu!.exe")[0].replace("\\", "/")
    except Exception as e:
        print(f"Error: {e}")
        return None
osu_path = getOsupath()
if not osu_path: osu_path = input("Error! Not Found osu! Path! \nInput osu! Root Folder Path : ").replace("\\", "/") + "/"

np = bid = VolumeUniversal = VolumeMusic = uSel = ""
songPause = False
songStatus = "Stoped"
vol = 10
cfg = [i for i in os.listdir(f"{osu_path}") if i.endswith(".cfg")]
cfg = f"{osu_path}osu!.{os.environ.get('USERNAME')}.cfg" if f"osu!.{os.environ.get('USERNAME')}.cfg" in cfg else None
if cfg:
    with open(cfg, "r", encoding="utf-8") as f:
        cfg = f.read()
        cfg = cfg[cfg.find("VolumeUniversal"):].split("\n")[:3]
        VolumeUniversal = int(cfg[0].replace("VolumeUniversal = ", ""))
        VolumeMusic = int(cfg[2].replace("VolumeMusic = ", ""))
        vol = round((VolumeUniversal / 100) * (VolumeMusic / 100) * 100, 2)
print(f"Default Volume : {vol} | (VolumeUniversal : {VolumeUniversal}, VolumeMusic : {VolumeMusic})")

# pygame 초기화
pygame.init()
pygame.mixer.init()

class calculate_md5:
    @classmethod
    def file(cls, fn) -> str:
        md5 = hashlib.md5()
        with open(fn, "rb") as f:
            md5.update(f.read())
        return md5.hexdigest()

    @classmethod
    def text(cls, t) -> str:
        md5 = hashlib.md5()
        md5.update(t.encode("utf-8"))
        return md5.hexdigest()

#play
def mp3Play(np):
    global vol, songStatus
    pygame.mixer.music.load(np)
    pygame.mixer.music.set_volume(vol / 100)
    pygame.mixer.music.play()
    songStatus = "Playing"
    while pygame.mixer.music.get_busy() or songPause: pygame.time.Clock().tick(10)

def toggle_pause():
    global songPause, songStatus
    if songPause:
        pygame.mixer.music.unpause()
        songPause = False; songStatus = "Playing"
    else:
        pygame.mixer.music.pause()
        songPause = True; songStatus = "Paused"

def skip_song():
    global songPause
    pygame.mixer.music.stop()
    songPause = False

def stop_song():
    global songStatus
    toggle_pause()
    pygame.mixer.music.rewind()
    songStatus = "Stoped"

def song_process():
    now = int(pygame.mixer.music.get_pos() / 1000)
    length = int(float(mediainfo(np)["duration"]))
    percent = f"{round((now / length) * 100, 2)}%"
    return [now, length, percent] if now != -1 else [length, length, "100%"]

def on_press(key):
    global songPause
    try:
        if key == keyboard.Key.f2: toggle_pause() #resume
        elif key == keyboard.Key.f3: toggle_pause() #pause
        elif key == keyboard.Key.f4: stop_song() #stop
        elif key == keyboard.Key.f5: skip_song() #skip
    except AttributeError:
        pass
listener = keyboard.Listener(on_press=on_press)
listener.start()

# 콘솔 입력 처리 함수
def ccmd():
    global vol, songPause, songStatus
    while True:
        i = input("command : ")
        if i.lower() == "help" or i.lower() == "h":
            print("\nhelp (h) || command list"); print("np (n) || Now Playing"); print("vol (v) 1~100 || Volume Check/Setting")
            print("resume (r) || resume song ('F2' Key same this)"); print("pause (p) || pause song ('F3' Key same this)"); print("skip (s) || skip ('F5' Key same this)")
            print("s/{BeatmapSetID} || Play Song With BeatmapSetID"); print("b/{BeatmapSetID} || Play Song With BeatmapID"); print("cho (c) || Open Bancho Link")
            print("redstar (red) || Open Redstar Link"); print("exit (kill, x) || exit this program") ;print()

        elif i.lower() == "np" or i.lower() == "n": SP = song_process(); print(f"{np} | {SP[0]}/{SP[1]} {SP[2]} | {songStatus}")
        elif i.lower() == "vol" or i.lower() == "v": print(f"{vol}%")
        elif i.startswith("vol") or i.startswith("v "):
            try:
                vol = int(i.split(" ")[1])
                if not 0 <= vol <= 100: raise
                pygame.mixer.music.set_volume(vol / 100)
                print(f"Changed {vol}%")
            except:
                print("Use That | vol 0~100")
        elif i.startswith("s/") or i.startswith("b/"):
            global uSel
            id = None
            try: id = int(i.replace('b/', ''))
            except: pass
            try: id = f"+{int(i.replace('s/', ''))}"
            except: pass
            if not id: print(f"Use That | s/1663512 | b/1919312"); continue
            if not os.path.isfile(f"{osu_path}osump3/audio/{id}"):
                audio = requests.get(f"https://b.redstar.moe/audio/{id}", headers=requestHeaders)
                if audio.status_code == 200:
                    if not os.path.isdir(f"{osu_path}osump3/audio"): os.makedirs(f"{osu_path}osump3/audio")
                    with open(f"{osu_path}osump3/audio/{id}", "wb") as f:
                        f.write(audio.content)

            uSel = f"{osu_path}osump3/audio/{id}"
            print(uSel)
            skip_song()
        elif i.lower() == "cho" or i.lower() == "c": os.system(f"start https://osu.ppy.sh/b/{bid}") if type(bid) == int else print("BeatmapID Not Found!")
        elif i.lower() == "redstar" or i.lower() == "red": os.system(f"start https://redstar.moe/b/{bid}") if type(bid) == int else print("BeatmapID Not Found!")
        elif i.lower() == "resume" or i.lower() == "r": toggle_pause()
        elif i.lower() == "pause" or i.lower() == "p": toggle_pause()
        elif i.lower() == "skip" or i.lower() == "s": skip_song()
        elif i.lower() == "exit" or i.lower() == "kill" or i.lower() == "x": pygame.mixer.music.stop(); pygame.quit(); os._exit(0)

# 콘솔 입력을 처리하는 스레드 시작
console_thread = threading.Thread(target=ccmd)
console_thread.start()

BeatmapSets = []
for i in os.listdir(f"{osu_path}Songs"):
    if os.path.isdir(f"{osu_path}Songs/{i}"): BeatmapSets.append(i)

while True:
    if uSel:
        np = uSel
        uSel = None
        id = np.split("/")
        id = id[len(id) - 1]
        if "+" in id:
            try: bid = int(requests.get(f"https://b.redstar.moe/filesinfo/{id.replace('+', '')}", headers=requestHeaders).json()["RedstarOSU"][1])
            except: bid = ""
        else: bid = int(id)

        music_thread = threading.Thread(target=mp3Play, args=(np,))
        music_thread.start()
        music_thread.join()
    else:
        Set = random.choice(BeatmapSets)
        Beatmap = [i for i in os.listdir(f"{osu_path}Songs/{Set}") if i.endswith(".osu")]
        Beatmap = random.choice(Beatmap)

        #mp3 파일명 추출
        with open(f"{osu_path}Songs/{Set}/{Beatmap}", 'r', encoding="utf-8") as f:
            bmd5 = calculate_md5.file(f"{osu_path}Songs/{Set}/{Beatmap}")
            try:
                bid = int(requests.get(f"https://cheesegull.redstar.moe/api/md5/{bmd5}", headers=requestHeaders).json()["BeatmapID"])
            except:
                bid = ""

            line = f.read()
            line = line[line.find("AudioFilename:"):]
            try:
                AudioFilename = line.split("\n")[:4][0].replace("AudioFilename:", "")
                AudioFilename = AudioFilename.replace(" ", "", 1) if AudioFilename.startswith(" ") else AudioFilename
            except:
                AudioFilename = None

        np = f"{osu_path}Songs/{Set}/{AudioFilename}"
        music_thread = threading.Thread(target=mp3Play, args=(np,))
        music_thread.start()
        music_thread.join()