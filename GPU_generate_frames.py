import av
import os
import sys
import time
import numpy
import cupy as cpy

#-minecraft values
col = {
    "black" : "minecraft:black_concrete",
    "white" :"minecraft:white_concrete",
    "gray" : "minecraft:gray_concrete",
    "empty" : "minecraft:air",
    "light-gray" : "minecraft:light_gray_concrete"
}

idIDX = {
    0:  "minecraft:white_concrete",
    1: "minecraft:black_concrete",
    2: "minecraft:light_gray_concrete",
    3: "minecraft:gray_concrete",
    4: "minecraft:light_gray_concrete_powder",
    5: 5
}

toText = {
    0: " ",
    1: "#",
    2: "-",
    3: "/",
    4: " ",
    5: " "
}

class videoGenMC():
    def armor_stand(self,tag):
        return """{Invisible:True,Invulnerable:True,NoGravity:True,Tags:""" + f"[{tag}]" + """}"""
    
    def atEntity(self,tag):
        return f"@e[tag={tag}]"
    
    def command_kill(self,tag):
        return f"kill {self.atEntity(tag)}\n"
    
    def nextframe(self,i : int,delay : int):
        next_frame = f"\nschedule function {self.name}:frames/frame{i} {delay}t\n"
        return next_frame
    
    def gen_dimensions_framecount(self):
        container = av.open(os.path.join(self.script_dir,self.video_file))

        vid = container.decode(video=0)
        i = 0
        for oneFrame in vid:
            i+=1
        height = oneFrame.height
        width = oneFrame.width
        return (i,height,width)
    
    #clear folder
    def clear_folder(self):
        for file in os.listdir(self.frames_path):
            try:
                os.remove(os.path.join(frames_path,file))
            except(Exception) as e:
                pass
        time.sleep(0.5)

    def __init__(self,frames_path,name,video_file,scrpt_dir,reduce = 3,gpu_process = True,):
        self.frames_path = frames_path
        self.name = name
        self.video_file = video_file
        self.script_dir = scrpt_dir
        self.gpu_process = gpu_process
        self.reduce = 3

        self.MAX_FRAME , self.height , self.width = self.gen_dimensions_framecount()
        self.n_height = int(self.height/reduce)
        self.n_width = int(self.width/reduce)

    #I/0
    def gen_file(self,i,full : bool):
        if not full:
            mcfuncname = f"frame{i}.mcfunction"
        else:
            mcfuncname = f"{i}.mcfunction"

        try:
            frame = open(os.path.join(self.frames_path,mcfuncname),"w+",encoding="utf-8")
        except(Exception) as e:
            print(e)
        return frame

    def open_frame(self,i):
        mcfuncname = f"frame{i}.mcfunction"
        return open(os.path.join(self.frames_path,mcfuncname),"r+",encoding="utf-8")

    def delete_frame(self,i):
        mcfuncname = f"frame{i}.mcfunction"
        try:
            os.remove(os.path.join(self.frames_path,mcfuncname))
        except Exception as e:
            print(e)
            print(f"didnt delete frame{i}")
            pass

    def replace_string(self,i,old_string,new_string):
        f = self.open_frame(i)
        content = f.read()
        content = content.replace(old_string,new_string)

        f.close()
        self.delete_frame(i)

        f_new = self.gen_file(i,False)
        f_new.write(content)
    #-

    def frame0(self):
        frame_mcfunc = self.gen_file(0,False)
        #layer 1 frame 0
        frame_mcfunc.write("#replace and kill old armor stand\n")
        frame_mcfunc.write(f"tp Shortax7 ~89 ~70 ~70 -180 90\n")
        frame_mcfunc.write(f"execute as {self.atEntity(origin_tag)} run execute at {self.atEntity(origin_tag)} run summon armor_stand ~ ~ ~ {self.armor_stand(player_tag)}\n\n")
        frame_mcfunc.write(f"execute as {self.atEntity(origin_tag)} run execute at {self.atEntity(origin_tag)} run summon armor_stand ~ ~ ~ {self.armor_stand(cc_tag)}\n\n")
        frame_mcfunc.write(f"execute as {self.atEntity(origin_tag)} run kill {self.atEntity(origin_tag)}\n")
        frame_mcfunc.write("#layer1\n")
        frame_mcfunc.write(f"fill ~ ~ ~ ~{self.n_width-1} ~ ~{self.n_height-1} {col['black']}\n")
        frame_mcfunc.write("\n")
        frame_mcfunc.write("\n")
        return frame_mcfunc                        

    def gen_frames(self,offset,frames_amount,delay):
        container = av.open(os.path.join(self.script_dir,self.video_file))
        vid = container.decode(video=0)

        i = -1
        frame_counter = 0

        maximum = offset+frames_amount

        if self.gpu_process:
            pcs_type = cpy
        else:
            pcs_type = numpy
        
        #operations - Beginning
        videoArray = pcs_type.zeros((frames_amount,self.height,self.width,3),dtype=cpy.uint8)

        for oneFrame in vid:
            i+=1
            if i >= maximum:
                break
            if i >= offset+frame_counter:    
                pixels = oneFrame.to_ndarray(format='bgr24')
                videoArray[frame_counter] = pcs_type.asarray(pixels)
                frame_counter+=1

        finished_frames = GENERATE(videoArray,self.reduce,pcs_type)
        if self.gpu_process:
            cpu_frames = pcs_type.asnumpy(finished_frames)
        else:
            cpu_frames = finished_frames
        #operations - End

        
        block_names = numpy.array([idIDX[i] for i in range(6)], dtype=object)
        named_frames = block_names[cpu_frames]

        h, w = cpu_frames.shape[1], cpu_frames.shape[2]
        z_coords, x_coords = numpy.meshgrid(numpy.arange(h), numpy.arange(w), indexing='ij')

        frame_counter = 0
        i = 0
        frame_mcfunc = self.frame0()
        for singl_frame in named_frames:
            if i != 0:
                frame_mcfunc = self.gen_file(i+offset,False)

            mask = singl_frame != 5
            valid_x = x_coords[mask]
            valid_z = z_coords[mask]
            valid_blocks = singl_frame[mask]

            commands = [
                f"execute at @e[tag={player_tag}] run setblock ~{x} ~1 ~{z} {block}\n"
                for x, z, block in zip(valid_x, valid_z, valid_blocks)
            ]

            frame_mcfunc.writelines(commands)
            frame_mcfunc.write("\n")
            frame_counter+=1
            if i >= frames_amount-1:
                frame_mcfunc.write(self.command_kill(player_tag))
            else:
                frame_mcfunc.write(self.nextframe(i+offset+1,delay))
            i+=1
            frame_mcfunc.write(f"say frame{i+offset}")
            frame_mcfunc.close()

    def setblock(x,z,block):
        return f"execute at @e[tag={player_tag}] run setblock ~{x} ~1 ~{z} {block}\n"

    #mcfunction to delete everything
    def create_clear_file(self):
        c_file = "clear"
        cc_file = "cc"
        clear_mcfunc = self.gen_file(c_file,True)
        cc_mcfunc = self.gen_file(cc_file,True)

        clear_mcfunc.write("#kill armor stand\n")
        clear_mcfunc.write(f"execute as {self.atEntity(cc_tag)} run execute at @s run function {self.name}:frames/{cc_file}\n")    
        clear_mcfunc.write(f"execute as {self.atEntity(clear_tag)} run {self.command_kill(clear_tag)}\n")
        clear_mcfunc.close()

        cc_mcfunc.write("#kill armor stand\n")
        cc_mcfunc.write(f"execute as {self.atEntity(cc_tag)} run {self.command_kill(cc_tag)}\n")
        cc_mcfunc.write(f"execute as {self.atEntity(player_tag)} run execute at @s run {self.command_kill(player_tag)}\n\n")

        cc_mcfunc.write("#clear everything\n")
        cc_mcfunc.write(f"fill ~ ~ ~ ~{self.n_width-1} ~ ~{self.n_height-1} {col['empty']}\n\n")
        for replaceable in col.values():
            if "air" not in replaceable:      
                cc_mcfunc.write(f"fill ~ ~1 ~ ~{self.n_width-1} ~1 ~{self.n_height-1} {col['empty']} replace {replaceable}\n")
        
        cc_mcfunc.close()
    
    def slice_frame_to_txt(self,frame):
        try:
            os.remove(os.path.join(script_dir,"frame.txt"))
        except(FileNotFoundError) as e:
            
            pass
        finally:
            txt = open(os.path.join(script_dir,"frame.txt"),"x",encoding="utf-8")
        
        erg = ""
        lines = 0
        pxls = 0
        for y in range(0,frame.shape[0]):
            for x in range(0,frame.shape[1]):
                erg +=toText[int(frame[y][x])]
                pxls +=1
            erg+="\n"
            txt.write(erg)
            lines+=1
            erg = ""
        txt.close()

def GENERATE(videoArray,reduce,prcs):
    def optimize_for_change(videoArray):
        mask = videoArray[0].copy()
        for i in range(1, videoArray.shape[0]):
            current_frame = videoArray[i]

            same_mask = current_frame == mask
            
            current_frame[same_mask] = 5
            
            mask = prcs.where(same_mask, mask, current_frame)

    def reduce_size(video):
        return video[:, ::reduce, ::reduce, :]

    def parse_color(B,G,R):
        color_index = prcs.full_like(B, fill_value=1, dtype=prcs.int8)

        White = (B >= 185) | (G >= 185) | (R >= 185)
        color_index[White] = 0

        Black = (B <= 25 ) | (G <= 25) | (R <= 25)
        color_index[Black] = 1
        
        LightGray = ((B >= 125 ) | (G >= 125) | (R >= 125)) & ~Black & ~White
        color_index[LightGray] = 2

        Gray = ~White & ~Black & ~LightGray   
        color_index[Gray] = 3

        return color_index

    def convert_to_color_index(video_array):
        b_ = video_array[:, :, :, 0]
        g_ = video_array[:, :, :, 1]
        r_ = video_array[:, :, :, 2]

        return parse_color(b_ ,g_ ,r_ )

    videoArray = reduce_size(videoArray)
    video_color_idx = convert_to_color_index(videoArray)
    del videoArray
    optimize_for_change(video_color_idx)

    if prcs != numpy:
        return video_color_idx.get()
    else:
        return video_color_idx

origin_tag = "origin_location"
clear_tag = "clear_location"
player_tag = "player_video"
cc_tag = "cc_clear"



if __name__ == "__main__":
    name = "shortax"

    REDUCE = 3
    OFFSET = 0
    FRAMES_AMOUNT = 6500
    DELAY = 3

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    frames_path = os.path.join(script_dir,"Bad Apple\\data\\shortax\\function\\frames")
    filename = "video.mp4"

    vg = videoGenMC(frames_path=frames_path,name=name,video_file=filename,scrpt_dir=script_dir,reduce=REDUCE,gpu_process=True)
    vg.clear_folder()
    vg.gen_frames(offset=OFFSET,frames_amount=vg.MAX_FRAME,delay=DELAY)
    vg.create_clear_file()
    #print(gen_time_and_frame())
