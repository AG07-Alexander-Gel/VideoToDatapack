import os
import sys
import GPU_generate_frames
import configparser

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

frames_path = "/data/video/function/frames"
init_path = "/data/video/function/init"
check_path = "/data/video/function/check"
jsons_path = "/data/minecraft/tags/function"
template_dir = "common/template"

PACK_FORMAT = 61
DESCRIPTION = """ "Auto generated Datapack from video file" """.strip()

def delete_folder(pack_name):
    try:
        os.remove(pack_name)
        print(f"deleted: {pack_name}")
    except Exception as e:
        print("#")
        pass

def create_folder_structure(pack_name):

    os.makedirs(f"{pack_name}/data/global/advancements", exist_ok=True)
    os.makedirs(f"{pack_name}" + jsons_path, exist_ok=True)
    os.makedirs(f"{pack_name}" + check_path, exist_ok=True)
    os.makedirs(f"{pack_name}" + frames_path, exist_ok=True)
    os.makedirs(f"{pack_name}" + init_path, exist_ok=True)

    return os.path.abspath(f"{pack_name}")

def write_file(name,root_loc,data):
    fil_e = open(os.path.join(root_loc,name),"w+",encoding="utf-8")
    fil_e.write(data)
    fil_e.close()

def init_files(pack_name,name):
    origin = create_folder_structure(pack_name,name)

    #pack.mcmeta
    mc_meta = ("""{"pack": {"pack_format": """ + str(PACK_FORMAT) + ""","description": """ + DESCRIPTION + """} }""")
    write_file("pack.mcmeta",origin,mc_meta)

    #json files
    load = """{"replace": false,"values": ["video:init/load"]}"""
    write_file("load.json",os.path.join(f"{pack_name}" + jsons_path),load)

    slowc = """{"replace": false,"values": ["video:check/slowcheck"]}"""
    write_file("slowcheck.json",os.path.join(f"{pack_name}" + jsons_path),slowc)

    tick = """{"replace": false,"values": ["video:init/mainloop"]}"""
    write_file("tick.json",os.path.join(f"{pack_name}" + jsons_path),tick)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No args given")
    else:
        args = sys.argv[1:]
        if len(args) >= 3:
            DATAPACK_NAME = args[2]
        else:
            DATAPACK_NAME = "GenerateDatapack"
        
        

        delete_folder(DATAPACK_NAME)
        init_files(DATAPACK_NAME)
        name = "video"

        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        frames_path = os.path.join(script_dir,f"{DATAPACK_NAME}\\data\\{name}\\function\\frames")
        filename = args[0]

        config = configparser.ConfigParser()
        config.read('config.ini')

        DELAY = config.getint('video_gen','delay')
        REDUCE = config.getint('video_gen','reduce')
        OFFSET = config.getint('video_gen','offset')
        FRAMES_AMOUNT = config.getint('video_gen','g_frames')
        
        vg = GPU_generate_frames.videoGenMC(frames_path=frames_path,name=name,video_file=filename,scrpt_dir=script_dir,reduce=REDUCE,gpu_process=True)

        vg.clear_folder()

        amout_frames = vg.MAX_FRAME if FRAMES_AMOUNT == -1 else FRAMES_AMOUNT

        vg.gen_frames(offset=OFFSET,frames_amount=amout_frames,delay=DELAY)

        vg.create_clear_file()

        print("done")



