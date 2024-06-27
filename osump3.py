import winreg
import os
import random
import threading
from pynput import keyboard
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"; import pygame
import time
import requests
from tqdm import tqdm
from md5Check import calculate_md5
import zipfile
from pydub.utils import mediainfo
import ctypes
import pypresence
import asyncio
import traceback

version = "2.1.1"
requestHeaders = {"User-Agent": "osump3"}
pygame.init() #pygame 초기화
pygame.mixer.init()
np = bid = VolumeUniversal = VolumeMusic = uSel = rpc = ""
songPause = False
songStatus = "Stoped"; rpcStatus = "Never Running"
vol = 10

def exceptionE(): e = f"\n{traceback.format_exc()}"; print(e); return e
def KillProgram(): os.system(f"taskkill /f /pid {os.getpid()}")

if os.name != "nt": print("This Program Is Work Only Windows System!!"); KillProgram()

try:
    ProcessName = os.popen(f'tasklist /svc /FI "PID eq {os.getpid()}"').read().strip().split("\n")[2].split(" ")[0]
    version_hash = calculate_md5.file(ProcessName) if ProcessName != "python.exe" else ""
    print(f"\npid : {os.getpid()} | ProcessName : {ProcessName} | version_hash : {version_hash}")
    nv = requests.get("https://raw.githubusercontent.com/skchqhdpdy/osump3/main/version.txt", headers=requestHeaders).text.split("\n")
    if version != nv[0]:
        print(f"업데이트 있음! \n현재버전 : {version} \n최신버전 : {nv[0]}")
        print("https://github.com/skchqhdpdy/osump3")
        if input("Press Enter to exit...") != "ignore": KillProgram()
    elif ProcessName != "python.exe" and version_hash != nv[1]:
        print(f"업데이트 있음! \n버전은 같지만 파일 Hash 값이 다름! \n현재 Hash 값 : {version_hash} \n최신 Hash 값 : {nv[1]}")
        print("https://github.com/skchqhdpdy/osump3")
        if input("Press Enter to exit...") != "ignore": KillProgram()
except: exceptionE()

#ffmpeg 설치확인
if os.system(f"ffmpeg -version > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1") != 0:
    if not ctypes.windll.shell32.IsUserAnAdmin() != 0: input("ffmpeg 설치를 위해 관리자 권한으로 실행하세요!"); KillProgram()

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
    print("Installed ffmpeg")
    #시스템 환경변수 Path의 키
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS)
    current_path, _ = winreg.QueryValueEx(key, 'Path') #현재 Path 값을 읽어옴
    if "C:\\Program Files\\ffmpeg osump3\\bin" not in current_path:
        new_path = f"{current_path};C:\\Program Files\\ffmpeg osump3\\bin" #기존 Path에 새 경로 추가
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path) #변경된 Path 값을 설정
        print("Set ffmpeg System Environment Variables")
    else: print("Exist ffmpeg System Environment Variables")

def getOsupath():
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"osu\Shell\Open\Command")
        return winreg.QueryValue(key, None).strip('"').split("\\osu!.exe")[0].replace("\\", "/")
    except:
        exceptionE()
        return None
osu_path = getOsupath()
if not osu_path: osu_path = input("Error! Not Found osu! Path! \nInput osu! Root Folder Path : ").replace("\\", "/") + "/"

cfg = [i for i in os.listdir(osu_path) if i.endswith(".cfg")]
cfg = f"{osu_path}/osu!.{os.environ.get('USERNAME')}.cfg" if f"osu!.{os.environ.get('USERNAME')}.cfg" in cfg else None
if cfg:
    with open(cfg, "r", encoding="utf-8") as f:
        cfg = f.read()
        cfg = cfg[cfg.find("VolumeUniversal"):].split("\n")[:3]
        VolumeUniversal = int(cfg[0].replace("VolumeUniversal = ", ""))
        VolumeMusic = int(cfg[2].replace("VolumeMusic = ", ""))
        vol = round((VolumeUniversal / 100) * (VolumeMusic / 100) * 100, 2)
print(f"Default Volume : {vol} | (VolumeUniversal : {VolumeUniversal}, VolumeMusic : {VolumeMusic})")

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

def DRP_np(customNp = None):
    if customNp: Nnp = customNp
    else: Nnp = np
    try:
        SP = song_process()
        return f"{songStatus} | {Nnp} | {SP[0]}/{SP[1]} {SP[2]}"
    except: return f"{songStatus} | {Nnp} | ?/? ?%"

def on_press(key):
    global songPause
    try:
        if key == keyboard.Key.f2: toggle_pause() #resume
        elif key == keyboard.Key.f3: toggle_pause() #pause
        elif key == keyboard.Key.f4: stop_song() #stop
        elif key == keyboard.Key.f5: skip_song() #skip
    except AttributeError: pass
listener = keyboard.Listener(on_press=on_press)
listener.start()

#콘솔 입력 처리 함수
def ccmd():
    global vol, songPause, songStatus
    while True:
        try:
            i = input("command : ")
            if i.lower() == "help" or i.lower() == "h":
                print("\n    help (h) || command list"); print("    np (n) || Now Playing"); print("    vol (v) 1~100 || Volume Check/Setting")
                print("    resume (r) || resume song ('F2' Key same this)"); print("    pause (p) || pause song ('F3' Key same this)"); print("    skip (s) || skip ('F5' Key same this)")
                print("    s/{BeatmapSetID} || Play Song With BeatmapSetID"); print("    b/{BeatmapSetID} || Play Song With BeatmapID"); print("    cho (c) || Open Bancho Link")
                print("    redstar (red) || Open Redstar Link"); print("    discord (rpc) || Check Discord Rich Presence Status"); print("    exit (kill, x) || exit this program")
                print()

            elif i.lower() == "np" or i.lower() == "n": print(f"    {DRP_np()}")
            elif i.lower() == "vol" or i.lower() == "v": print(f"    {vol}%")
            elif i.startswith("vol") or i.startswith("v "):
                try:
                    vol = int(i.split(" ")[1])
                    if not 0 <= vol <= 100: raise
                    pygame.mixer.music.set_volume(vol / 100)
                    print(f"    Changed {vol}%")
                except:
                    print("    Use That | vol 0~100")
            elif i.startswith("s/") or i.startswith("b/"):
                global uSel
                id = None
                try: id = int(i.replace('b/', ''))
                except: pass
                try: id = f"+{int(i.replace('s/', ''))}"
                except: pass
                if not id: print(f"    Use That | s/534054 | b/3395864"); continue
                if not os.path.isfile(f"{osu_path}/osump3/audio/{id}"):
                    audio = requests.get(f"https://b.redstar.moe/audio/{id}", headers=requestHeaders)
                    if audio.status_code == 200:
                        if not os.path.isdir(f"{osu_path}/osump3/audio"): os.makedirs(f"{osu_path}/osump3/audio")
                        with open(f"{osu_path}/osump3/audio/{id}", "wb") as f:
                            f.write(audio.content)

                uSel = f"{osu_path}/osump3/audio/{id}"
                print(f"    {uSel}")
                skip_song()
            elif i.lower() == "cho" or i.lower() == "c": os.system(f"start https://osu.ppy.sh/b/{bid}") if type(bid) == int else print("    BeatmapID Not Found!")
            elif i.lower() == "redstar" or i.lower() == "red": os.system(f"start https://redstar.moe/b/{bid}") if type(bid) == int else print("    BeatmapID Not Found!")
            elif i.lower() == "resume" or i.lower() == "r": toggle_pause()
            elif i.lower() == "pause" or i.lower() == "p": toggle_pause()
            elif i.lower() == "skip" or i.lower() == "s": skip_song()
            elif i.lower() == "discord" or i.lower() == "rpc": print(f"    {rpcStatus}")
            elif i.lower() == "exit" or i.lower() == "kill" or i.lower() == "x": KillProgram()
        except KeyboardInterrupt: print("ctrl + c"); KillProgram()
        except: exceptionE(); continue
console_thread = threading.Thread(target=ccmd) #콘솔 입력을 처리하는 스레드 시작
console_thread.start()

st = time.time()
def rcpConn():
    global rpc, rpcStatus; rpc = None
    print("\n    Discord Is Not Running!")
    while not rpc:
        try:
            loop = asyncio.new_event_loop() #현재 스레드에 이벤트 루프를 생성하고 설정합니다.
            asyncio.set_event_loop(loop)
            rpc = pypresence.Presence(1255696229439111169) #디스코드 애플리케이션의 클라이언트 ID
            rpc.connect()
            rpc.clear()
            #loop.run_forever() #이벤트 루프를 실행합니다.
            print("\n    Connected To Discord!"); rpcStatus = "Running"
            return rpc
        except pypresence.exceptions.DiscordNotFound: rpcStatus = "Not Running"
        except pypresence.exceptions.DiscordError: rpcStatus = "Not Running"
        except: rpcStatus = exceptionE()
        time.sleep(1)
def rpcUpdate(details):
    rpc.update(
        start=st,
        state=f"https://redstar.moe/b/{bid}",
        details=details,
        large_image=f"https://b.redstar.moe/bg/{bid}",
        large_text=f"https://b.redstar.moe/bg/{bid}",
        small_image="https://raw.githubusercontent.com/skchqhdpdy/osump3/main/icon.jpg",
        small_text="https://github.com/skchqhdpdy/osump3",
        buttons=[
            {"label": "Bancho", "url": f"https://osu.ppy.sh/b/{bid}"},
            {"label": "Redstar", "url": f"https://redstar.moe/b/{bid}"}
        ]
    )
def DiscordRichPresence():
    rcpConn()
    while rpc:
        try:
            Nnp = np.replace(f"{osu_path}", "")
            details = DRP_np(Nnp)
            if len(details) > 128:
                details = DRP_np(Nnp[Nnp.find(" - ") + 3:])
            rpcUpdate(details)
        except pypresence.exceptions.InvalidID: rcpConn()
        except pypresence.exceptions.ServerError: rpcUpdate(f"{songStatus} | Error! (np Error!)")
        except: exceptionE()
        time.sleep(1)
DRP = threading.Thread(target=DiscordRichPresence)
DRP.start()

BeatmapSets = []
for i in os.listdir(f"{osu_path}/Songs"):
    if os.path.isdir(f"{osu_path}/Songs/{i}"): BeatmapSets.append(i)

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
        Beatmap = [i for i in os.listdir(f"{osu_path}/Songs/{Set}") if i.endswith(".osu")]
        Beatmap = random.choice(Beatmap)

        #mp3 파일명 추출
        with open(f"{osu_path}/Songs/{Set}/{Beatmap}", 'r', encoding="utf-8") as f:
            #### A:/osu!/Songs/beatmap-637515017600437735-Camellia - SECRET BOSS/audio.mp3 | 83/273 30.4% | Playing
            bmd5 = calculate_md5.file(f"{osu_path}/Songs/{Set}/{Beatmap}")
            try:
                bid = int(requests.get(f"https://cheesegull.redstar.moe/api/md5/{bmd5}", headers=requestHeaders).json()["BeatmapID"])
            except:
                print("    bid 못찾은 관계로 Firstbid 조회함...")
                try: bid = int(requests.get(f"https://b.redstar.moe/filesinfo/{int(Set.split(' ')[0])}", headers=requestHeaders).json()["RedstarOSU"][1])
                except: bid = ""; print("    bid 못찾음!")

            line = f.read()
            line = line[line.find("AudioFilename:"):]
            try:
                AudioFilename = line.split("\n")[:4][0].replace("AudioFilename:", "")
                AudioFilename = AudioFilename.replace(" ", "", 1) if AudioFilename.startswith(" ") else AudioFilename
            except:
                AudioFilename = None

        np = f"{osu_path}/Songs/{Set}/{AudioFilename}"
        music_thread = threading.Thread(target=mp3Play, args=(np,))
        music_thread.start()
        music_thread.join()