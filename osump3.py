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
from pypresence import Presence, exceptions
import asyncio
import traceback
import sys
from pathToContentType import pathToContentType
from pydub import AudioSegment
import simpleaudio as sa
import math
import tkinter as tk
from tkinter import filedialog

version = "2.3.10"
ProcessName = os.popen(f'tasklist /svc /FI "PID eq {os.getpid()}"').read().strip().split("\n")[2].split(" ")[0]
ProcessPath = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0]) #환경 변수 세팅시에 경로가 cmd의 현재 경로로 설정되는 것 방지
version_hash = calculate_md5.file(ProcessPath) if ProcessName != "python.exe" else ""
requestHeaders = {"User-Agent": "osump3"}
pygame.init() #pygame 초기화
pygame.mixer.init()
np = bid = VolumeUniversal = VolumeMusic = uSel = rpc = ""
npList = BeatmapSets = []
songPause = isLoop = False
songStatus = "Stoped"; rpcStatus = "Discord Never Running"
vol = 10; jst = 0

def exceptionE(): e = f"\n{traceback.format_exc()}"; print(e); return e
def KillProgram(): os.system(f"taskkill /f /pid {os.getpid()}")

if os.name != "nt": input("This Program Is Work Only Windows System!!"); KillProgram()

def dl(link, Path):
    d = requests.get(link, headers=requestHeaders, stream=True, timeout=10)
    if d.status_code == 200:
        with open(Path, 'wb') as file:
            with tqdm(total=int(d.headers.get('Content-Length', 0)), unit='B', unit_scale=True, unit_divisor=1024, ncols=60) as pbar:
                for data in d.iter_content(1024):
                    file.write(data)
                    pbar.update(len(data))
    else: print(f"    Error! | status_code = {d.status_code} | {link}")
    return d

def per2dB(volume): return 20 * math.log10(volume / 100)

def osu_file_read(songname):
    Beatmap = random.choice([i for i in os.listdir(f"{osu_path}/Songs/{songname}") if i.endswith(".osu")])
    with open(f"{osu_path}/Songs/{songname}/{Beatmap}", 'r', encoding="utf-8") as f:
        line = f.read()
        line = line[line.find("AudioFilename:"):]
        try:
            AudioFilename = line.split("\n")[:4][0].replace("AudioFilename:", "")
            AudioFilename = AudioFilename.replace(" ", "", 1) if AudioFilename.startswith(" ") else AudioFilename
            if AudioFilename == "virtual": raise #실재 mp3 파일이 없는 매니아 에서 자주 쓰는 방법
        except: AudioFilename = None

        line = line[line.find("PreviewTime:"):]
        try:
            PreviewTime = line.split("\n")[:4][0].replace("PreviewTime:", "")
            PreviewTime = int(PreviewTime.replace(" ", "", 1) if PreviewTime.startswith(" ") else PreviewTime)
        except: PreviewTime = None

        bmd5 = calculate_md5.file(f"{osu_path}/Songs/{songname}/{Beatmap}")
        try: BeatmapID = int(requests.get(f"https://cheesegull.redstar.moe/api/md5/{bmd5}", headers=requestHeaders, timeout=10).json()["BeatmapID"])
        except:
            print("    md5 --> BeatmapID 못찾은 관계로 Firstbid 조회함...")
            try: BeatmapID = int(requests.get(f"https://b.redstar.moe/filesinfo/{int(songname.split(' ')[0])}", headers=requestHeaders, timeout=10).json()["RedstarOSU"][1])
            except:
                print("    filesinfo --> BeatmapID 못찾음!")
                line = line[line.find("BeatmapID:"):]
                try:
                    BeatmapID = line.split("\n")[:4][0].replace("BeatmapID:", "")
                    BeatmapID = int(BeatmapID.replace(" ", "", 1) if BeatmapID.startswith(" ") else BeatmapID)
                except: BeatmapID = ""; print(f"    {Beatmap} --> BeatmapID 못찾음!")

        line = line[line.find("//Background and Video events"):]
        try:
            BeatmapVideo = BeatmapBG = None
            lineSpilted = line.split("\n")[:4]
            for p in lineSpilted:
                t = pathToContentType(p, isInclude=True)
                if t["type"] == "video": BeatmapVideo = p[p.find('"') + 1 : p.find('"', p.find('"') + 1)]
                elif t["type"] == "image": BeatmapBG = p[p.find('"') + 1 : p.find('"', p.find('"') + 1)]
        except: BeatmapBG = BeatmapVideo = None
        return AudioFilename, PreviewTime, BeatmapID, BeatmapBG, BeatmapVideo

try:
    print(f"\npid : {os.getpid()} | ProcessName : {ProcessName} | ProcessPath : {ProcessPath} | version : {version} | version_hash : {version_hash}")

    def update_osump3(): #자동 업데이트
        os.rename(ProcessPath, f"{ProcessPath.replace('osump3.exe', f'osump3-v{version}.exe')}")
        dl("https://github.com/skchqhdpdy/osump3/raw/main/osump3.exe", ProcessPath)
        #os.remove(f"{ProcessPath.replace('.exe', f'-v{version}.exe')}")
        input("\n신 버전으로 다시 키세요!"); KillProgram()
    nv = requests.get("https://github.com/skchqhdpdy/osump3/raw/main/version.txt", headers=requestHeaders, timeout=10).text.split("\n")
    if ProcessName != "python.exe": #개발시에 업데이트 체크 무시
        if version != nv[0]:
            print(f"업데이트 있음! \n현재버전 : {version} \n최신버전 : {nv[0]}")
            print("https://github.com/skchqhdpdy/osump3")
            if input("Update Program? (y/n) : ") != "y": os.system("start https://github.com/skchqhdpdy/osump3") #KillProgram()
            else: update_osump3()
        elif ProcessName != "python.exe" and version_hash != nv[1]:
            print(f"업데이트 있음! \n버전은 같지만 파일 Hash 값이 다름! \n현재 Hash 값 : {version_hash} \n최신 Hash 값 : {nv[1]}")
            print("https://github.com/skchqhdpdy/osump3")
            if input("Update Program? (y/n) : ") != "y": os.system("start https://github.com/skchqhdpdy/osump3") #KillProgram()
            else: update_osump3()
except:
    exceptionE()
    if input("version Check Fail! ignore? (y/n) : ") == "n": KillProgram()

#ffmpeg 설치확인
if os.system(f"ffmpeg -version > {'nul' if os.name == 'nt' else '/dev/null'} 2>&1") != 0:
    #if not ctypes.windll.shell32.IsUserAnAdmin() != 0: input("ffmpeg 설치를 위해 관리자 권한으로 실행하세요!"); KillProgram()
    print("https://aodd.xyz/file%20hosting/Downloads/ffmpeg.zip --> C:\\Program Files\\ffmpeg osump3")
    dl("https://aodd.xyz/file%20hosting/Downloads/ffmpeg.zip", "C:/Program Files/ffmpeg osump3.zip")
    zipfile.ZipFile("C:/Program Files/ffmpeg osump3.zip").extractall("C:/Program Files/ffmpeg osump3")
    os.remove(f"C:/Program Files/ffmpeg osump3.zip")
    print("Installed ffmpeg")
    #시스템 환경변수 Path의 키
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS)
    current_path = winreg.QueryValueEx(key, 'Path')[0] #현재 Path 값을 읽어옴
    if "C:\\Program Files\\ffmpeg osump3\\bin" not in current_path.split(";"):
        new_path = f"{current_path};C:\\Program Files\\ffmpeg osump3\\bin" #기존 Path에 새 경로 추가
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path) #변경된 Path 값을 설정
        print("Set ffmpeg System Environment Variables")
    else: print("Exist ffmpeg System Environment Variables")
    input("\n이제 이 프로그램을 껐다가 다시 키세요!"); KillProgram()

try: #프로그램을 시스템 환경변수에 등록
    PEP = os.path.dirname(ProcessPath)
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS)
    try: osump3_path = winreg.QueryValueEx(key, 'osump3_path')[0]
    except FileNotFoundError: osump3_path = None
    current_path = winreg.QueryValueEx(key, 'Path')[0] #현재 Path 값을 읽어옴
    new_path = ""
    for i in current_path.split(";"):
        if i == osump3_path: new_path += f"{PEP};"
        else: new_path += f"{i};"
    new_path = new_path[:-1]
    if osump3_path and f";{osump3_path}" in current_path:
        #winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, f"{current_path.replace(f';{osump3_path}', f';{PEP}')}")
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, f"{new_path}")
        print("Update osump3.exe System Environment Variables")
    else:
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, f"{current_path};{PEP}")
        print("Set osump3.exe System Environment Variables")
    winreg.SetValueEx(key, "osump3_path", 0, winreg.REG_SZ, PEP) #osump3_path 키 만들기 및 값 설정
    print("Update osump3.exe Folder System Environment Variables")
except: exceptionE()

def getOsupath():
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"osu\Shell\Open\Command")
        return winreg.QueryValue(key, None).strip('"').split("\\osu!.exe")[0].replace("\\", "/")
    except:
        exceptionE()
        return None
osu_path = getOsupath()
if not osu_path:
    root = tk.Tk().withdraw()  # Tkinter 창 숨기기
    osu_path = filedialog.askopenfilename(title="Error! Not Found osu! Path! | Select osu!.exe", filetypes=[("osu! executable", "osu!.exe")]).replace("/osu!.exe", "")

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
def mp3Play():
    def mp3Play2():
        global songPause, songStatus, jst
        pygame.mixer.music.load(np)
        pygame.mixer.music.set_volume(vol / 100)
        pygame.mixer.music.play()
        songPause = False; songStatus = "Playing"; jst = 0
        while pygame.mixer.music.get_busy() or songPause: pygame.time.Clock().tick(10)
    music_thread = threading.Thread(target=mp3Play2)
    music_thread.start()
    music_thread.join()

def rewind_song():
    global uSel
    if npList:
        nLI = npList.index(f"{np}|{bid}")
        uSel = npList[nLI - 1:].copy() if nLI > 0 else npList.copy()
    else: uSel = npList.copy()
    print(f"    {uSel}")
    skip_song()

def resume_song():
    global songPause, songStatus, jst
    if songPause: pygame.mixer.music.unpause()
    else: pygame.mixer.music.play(); jst = 0
    songPause = False; songStatus = "Playing"

def pause_song():
    global songPause, songStatus
    if not songPause:
        pygame.mixer.music.pause()
        songPause = True; songStatus = "Paused"

def skip_song():
    global songPause, songStatus
    pygame.mixer.music.stop()
    songPause = False; songStatus = "Skipped"

def stop_song():
    global songPause, songStatus, jst
    pygame.mixer.music.play()
    pygame.mixer.music.pause()
    pygame.mixer.music.rewind()
    songPause = True; songStatus = "Stoped"; jst = 0

def jump_song(t: int):
    global jst
    jst = t
    pygame.mixer.music.play(start=jst)

def song_process():
    #█
    now = int(pygame.mixer.music.get_pos() / 1000) if not jst else int(pygame.mixer.music.get_pos() / 1000) + jst
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
        if key == keyboard.Key.f1: rewind_song()
        elif key == keyboard.Key.f2: resume_song() #resume
        elif key == keyboard.Key.f3: pause_song() #pause
        elif key == keyboard.Key.f4: stop_song() #stop
        elif key == keyboard.Key.f5: skip_song() #skip
        elif key == keyboard.Key.f6: print(f"    {DRP_np()}") #np?
    except AttributeError: pass
listener = keyboard.Listener(on_press=on_press)
listener.start()

#콘솔 입력 처리 함수
def ccmd():
    global vol, songPause, songStatus, uSel, isLoop
    while True:
        try:
            i = input("command : ")
            if i.lower() == "help" or i.lower() == "h":
                print("\n    help (h) || command list"); print(f"    status (stat) || Check Status"); print("    np (n) || Now Playing ('F6' Key same this)")
                print("    vol (v) {1~100} || Volume Check/Setting"); print("    rewind (rew) || rewind song ('F1' Key same this)"); print("    resume (r) || resume song ('F2' Key same this)")
                print("    pause (p) || pause song ('F3' Key same this)"); print("    stop (st) || stop song ('F4' Key same this)"); print("    skip (s) || skip ('F5' Key same this)")
                print("    jump (j) {Second} || Go to the Sec you entered")
                print("    s/{BeatmapSetID} || Play Song With BeatmapSetID"); print("    b/{BeatmapSetID} || Play Song With BeatmapID"); print("    search {Text} || Search From Your osu!Songs Path")
                print("    loop (l) || Loop song For Now Playing"); print("    cho (c) || Open Bancho Link"); print("    redstar (red) || Open Redstar Link")
                print(f'    openfolder (of) || Open BeatmapSet Folder for Now Playing | "{npDir}"'); print(f'    bg || Open Background Image in BeatmapSet Folder for Now playing | "{npDir}/{BeatmapBG}"'); print(f'    video (vi) || Open Background Video in BeatmapSet Folder for Now playing | "{npDir}/{BeatmapVideo}"')
                print(f"    restart (rs) || Restart This Program"); print(f"    remove (rm) || Remove '{osu_path}/osump3' Folder")
                print("    exit (kill, x) || exit this program \n")
            elif i.lower() == "status" or i.lower() == "stat":
                nt = time.time()
                print(f"    pid : {os.getpid()} | ProcessName : {ProcessName} | ProcessPath : {ProcessPath} | version : {version} | version_hash : {version_hash}")
                print(f"    {songStatus} | {rpcStatus} | {int((nt - st) // 3600):02}:{int(((nt - st) % 3600) // 60):02}:{int((nt - st) % 60):02} | ")
                print(f"    현재버전 : {version} | 최신버전 : {nv[0]}")
                print(f"    현재 Hash 값 : {version_hash} | 최신 Hash 값 : {nv[1]}")
                print(f"    volume : {vol} | np : {np} | bid : {bid} | loop = {isLoop}")
            elif i.lower() == "np" or i.lower() == "n": print(f"    {DRP_np()}")
            elif i.lower() == "vol" or i.lower() == "v": print(f"    {vol}%")
            elif i.lower().startswith("vol") or i.lower().startswith("v "):
                try:
                    vol = int(i.split(" ")[1])
                    if not 0 <= vol <= 100: raise
                    pygame.mixer.music.set_volume(vol / 100)
                    print(f"    Changed {vol}%")
                except: print("    Use That | vol 0~100")
            elif i.lower().startswith("s/") or i.lower().startswith("b/"): #type(uSel) = str
                try: id = int(i.replace('b/', ''))
                except: id = None
                try: id = f"+{int(i.replace('s/', ''))}"
                except: id = None
                if not id: print(f"    Use That | s/534054 | b/3395864"); continue
                if not os.path.isfile(f"{osu_path}/osump3/audio/{id}"):
                    if dl(f"https://b.redstar.moe/audio/{id}", f"{osu_path}/osump3/audio/{id}").status_code != 200: continue
                uSel = f"{osu_path}/osump3/audio/{id}"
                print(f"    {uSel}")
                if int(input("    바로 재생 = 1, 바로 다음 대기열 = 2 : ")) == 1: skip_song()
            elif i.lower().startswith("search "): #type(uSel) = dict
                q = i.lower().replace("search ", "")
                if q:
                    sni = 1; sn = []
                    for bs in BeatmapSets:
                        if q in bs.lower(): print(f"    {sni}. | {bs}"); sn.append(bs); sni += 1
                    if sn:
                        try:
                            sn = sn[int(input("\n    재생할 곡의 번호를 입력하세요! : ")) - 1]
                            option = int(input("    바로 재생 = 1, 바로 다음 대기열 = 2, 미리듣기 = 3, 이미지 보기 = 4, 동영상 보기 = 5 : "))
                            AudioFilename_search, PreviewTime_search, BeatmapID_search, BeatmapBG_search, BeatmapVideo_search = osu_file_read(sn) if option != 1 and option != 2 else (None, None, None, None, None)
                            if option == 1: uSel = {"sn": sn}; skip_song()
                            elif option == 2: uSel = {"sn": sn}
                            elif option == 3:
                                pause_song()
                                def preview(): #다른 모듈 사용
                                    sound = AudioSegment.from_file(f"{osu_path}/Songs/{sn}/{AudioFilename_search}")
                                    sound = sound.apply_gain(per2dB(vol))
                                    sound = sound[PreviewTime_search:PreviewTime_search + 30000]
                                    play_obj = sa.play_buffer(sound.raw_data, num_channels=sound.channels,
                                        bytes_per_sample=sound.sample_width,
                                        sample_rate=sound.frame_rate)
                                    #print((PreviewTime_search, vol, per2dB(vol), sound.dBFS))
                                    stop_event = threading.Event()  # Stop event 생성
                                    def get_input():
                                        while not stop_event.is_set():
                                            if input() == "1": stop_event.set(); break
                                    threading.Thread(target=get_input).start()
                                    for i in range(30):
                                        if not play_obj.is_playing() or stop_event.is_set(): play_obj.stop(); break
                                        print(f"\r({i+1}) | 미리듣기 종료 = 1 : ", end="")
                                        time.sleep(1)
                                    stop_event.set()
                                pr_thread = threading.Thread(target=preview)
                                pr_thread.start(); pr_thread.join()
                                resume_song()
                            elif option == 4: os.system(f'start "" "{osu_path}/Songs/{sn}/{BeatmapBG_search}"')
                            elif option == 5: os.system(f'start "" "{osu_path}/Songs/{sn}/{BeatmapVideo_search}"')
                        except: pass
            elif i.lower() == "loop" or i.lower() == "l": isLoop = not isLoop; print(f"    Loop = {isLoop} {f'| {np}' if isLoop else ''}")
            elif i.lower() == "cho" or i.lower() == "c": os.system(f"start https://osu.ppy.sh/b/{bid}") if type(bid) == int else print("    BeatmapID Not Found!")
            elif i.lower() == "redstar" or i.lower() == "red": os.system(f"start https://redstar.moe/b/{bid}") if type(bid) == int else print("    BeatmapID Not Found!")
            elif i.lower() == "rewind" or i.lower() == "rew": rewind_song() #type(uSel) = list
            elif i.lower() == "resume" or i.lower() == "r": resume_song()
            elif i.lower() == "pause" or i.lower() == "p": pause_song()
            elif i.lower() == "stop" or i.lower() == "st": stop_song()
            elif i.lower() == "skip" or i.lower() == "s": skip_song()
            elif i.lower().startswith("jump ") or i.lower().startswith("j "):
                try: jump_song(int(i.split(" ")[1]))
                except: print("    다시 입력하세요!")
            elif i.lower() == "openfolder" or i.lower() == "of": os.system(f'start "" "{npDir}"')
            elif i.lower() == "bg": os.system(f'start "" "{npDir}/{BeatmapBG}"')
            elif i.lower() == "video" or i.lower() == "vi": os.system(f'start "" "{npDir}/{BeatmapVideo}"')
            elif i.lower() == "restart" or i.lower() == "rs":
                if ProcessName != "python.exe": os.execv(sys.executable, [sys.executable] + sys.argv)
                else: print("    .py 파일은 restart가 금지되어 있습니다! | .exe 파일에서만 작동합니다!")
            elif i.lower() == "remove" or i.lower() == "rm": 
                if input(f'    진짜로 "{osu_path}/osump3" 폴더를 삭제 하시겠습니까? (y/n) : ').lower() == "y":
                    os.system(f'rd /s /q "{osu_path}/osump3"')
                    print("    삭제완료!") if not os.path.isdir(f"{osu_path}/osump3") else print("    Error! | 여전히 폴더가 존재함!")
                else: print("    취소")
            elif i.lower() == "exit" or i.lower() == "kill" or i.lower() == "x": KillProgram()
            elif i.lower() == "d": print(f"Debug | npList = {npList}") #debug
        except (KeyboardInterrupt, EOFError): print("Ctrl + C"); KillProgram()
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
            rpc = Presence(1255696229439111169) #디스코드 애플리케이션의 클라이언트 ID
            rpc.connect()
            rpc.clear()
            #loop.run_forever() #이벤트 루프를 실행합니다.
            print("\n    Connected To Discord!"); rpcStatus = "Discord Is Running"
            return rpc
        except exceptions.DiscordNotFound: rpcStatus = "Discord Is Not Running"
        except exceptions.DiscordError: rpcStatus = "Discord Is Not Running"
        except: rpcStatus = exceptionE()
        time.sleep(1)
def rpcUpdate(details):
    rpc.update(
        start=st,
        state=f"https://redstar.moe/b/{bid}",
        details=details,
        large_image=f"https://b.redstar.moe/bg/{bid}",
        large_text=f"https://b.redstar.moe/bg/{bid}",
        small_image="https://github.com/skchqhdpdy/osump3/raw/main/icon.jpg",
        small_text="https://github.com/skchqhdpdy/osump3",
        buttons=[
            {"label": "Redstar", "url": f"https://redstar.moe/b/{bid}"},
            {"label": "Bancho", "url": f"https://osu.ppy.sh/b/{bid}"}
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
        except exceptions.InvalidID: rcpConn()
        except exceptions.ServerError: rpcUpdate(f"{songStatus} | Error! (np Error!)")
        except: exceptionE()
        time.sleep(1)
DRP = threading.Thread(target=DiscordRichPresence)
DRP.start()

while True:
    BeatmapSets = [i for i in os.listdir(f"{osu_path}/Songs") if os.path.isdir(f"{osu_path}/Songs/{i}")]
    if isLoop: mp3Play()
    elif uSel and type(uSel) is str: #s/, b/
        id = uSel.split("/")
        id = id[-1]
        if "+" in id:
            try: bid = int(requests.get(f"https://b.redstar.moe/filesinfo/{id.replace('+', '')}", headers=requestHeaders, timeout=10).json()["RedstarOSU"][1])
            except: bid = ""
        else: bid = int(id)
        np = uSel; npList.append(f"{np}|{bid}") #이거 써야되나?
        uSel = None
        mp3Play()
    elif uSel and type(uSel) is list: #rew
        np, bid = uSel.pop(0).split("|")
        mp3Play()
    else:
        if uSel and type(uSel) is dict: Set = uSel["sn"]; uSel = None #search
        else: Set = random.choice(BeatmapSets) #default

        #mp3 파일명 추출
        AudioFilename, PreviewTime, bid, BeatmapBG, BeatmapVideo = osu_file_read(Set)

        npDir = f"{osu_path}/Songs/{Set}"
        np = f"{npDir}/{AudioFilename}"; npList.append(f"{np}|{bid}")
        mp3Play()