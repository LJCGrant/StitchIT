from PIL import Image, ImageDraw, ImageFont, ImageFile
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import contextlib
import shutil
import cv2

#USER INPUT
section_length = 150 #cm
resolution = 40 #px/mm
extension = ".BMP"
desired_extension = ".jpg"

expedition = "390"
site = "U1556B"

image_files = os.listdir(site)

#________________________________________________________________________
@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """Context manager to patch joblib to report into tqdm progress bar
    given as argument
    """

    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()


def listdir_nohidden(path):
        for f in os.listdir(path):
            if not f.startswith('.'):
                yield f

def vconcat_resize(img_list, interpolation = cv2.INTER_CUBIC):
    # take minimum width|
    w_min = min(img.shape[1] 
                for img in img_list)
    
    # resizing images
    im_list_resize = [cv2.resize(img,
                    (w_min, int(img.shape[0] * w_min / img.shape[1])),
                                interpolation = interpolation)
                    for img in img_list]
    # return final image
    return cv2.vconcat(im_list_resize)


def make_images(section):

    stitch_folder = (site + "/"+section+"/stitched/")
    if os.path.exists(stitch_folder):#deletes existing stitched folder
        shutil.rmtree(stitch_folder, ignore_errors=True)
    os.makedirs(stitch_folder)#makes new stitched folder

    Image.MAX_IMAGE_PIXELS = None #disables PIL's default image size limit
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    label = expedition+"-"+site+"-"+section
    path = site +"/"+section
    piece_log = pd.read_csv("./piece_logs/"+site+".csv").set_index("Label identifier")
    
    #extract BMP files from input folder and store in list
    lst = []
    subfolder = section
    folder = listdir_nohidden(site +"/"+ subfolder) #changed from os.listdir
    piece_log["file_name"] = str(np.nan)
    for i in folder:
        if i.endswith(extension):
            lst.append(i)

    dic = {}#create dictionary of piece label - images of piece and it's subpieces key - value pairs
    scanned_df = piece_log.copy() 
    for i, row in scanned_df.iterrows():
        bin_list = []
        dic[i] = []
        for j in lst:
            f = j.replace("Pc", "") #make file name same syntax as piece log label
            
            # identify piece images with a name that corresponds to the label identifier in piece log
            if i+extension == f[0:-4]+extension:   
                dic[i].append(j)
                bin_list.append(i)
            
            # checks if images is a sub-piece 
            elif f[-5].isdigit() == False and i+extension == f[0:-6]+extension:
                dic[i].append(j)
                bin_list.append(i)
                
            #checks if images is one of a cropped set 
            elif f[-5] == "x" and i+extension == f[0:-7]+extension or i+extension == f[0:-9]+extension:
                dic[i].append(j)
                bin_list.append(i)
            else:
                continue

    # remove empty key value pairs from dic and remove those pieces from dataframe so only scanned pieces remain 
    remove_lst = []
    for key in dic: 
        if dic[key] == []:
            scanned_df.drop([key], inplace=True)
            remove_lst.append(key)

    for empty_key in remove_lst:
        del dic[empty_key]


    #sorts peice images based on subpiece letter (A, B, C etc) in file name. May cause issue with A-1, A-1 multi scans       
    def sort_letter(letter):
        return letter[-5]

    def sort_frame(letter):
        return letter[-6]

    def sort_number(letter):
        return letter[-5]



    for key in dic:
        lst = dic[key]
        if lst[0][-5] == "x":
        
            dic[key].sort(key=sort_frame)
        
        elif lst[0][-5].isdigit() == True:
            dic[key].sort(key=sort_number)
        
        else: 
            dic[key].sort(key=sort_letter)

    for key in dic: 
        if dic[key] == []:
            scanned_df.drop([key], inplace=True)

    #sorts peice images based on subpiece letter (A, B, C etc) in file name. May cause issue with A-1, A-1 multi scans       
    def sort_letter(letter):
        return letter[-5]

    def sort_number(letter):
        return letter[-7]

    for key in dic:
        #dic[key].sort(key=sort_letter)
        
    #else:
        dic[key].sort(key=sort_number)
             
    for i, row in scanned_df.iterrows():
        scanned_df.at[i, "file_name"] = dic[i]      
    
    scanned_df["file_name"]

    for i, row in scanned_df.iterrows():
        file_list = []
        
        for piece_img in dic[i]:
            img = cv2.imread(path+"/"+piece_img)
            orientated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            file_list.append(orientated)
            
            
            #orientated = cv2.rotate(im, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            #file_list.append(orientated)
            
        img_v_resize = vconcat_resize(file_list)
        
    
        #os.makedirs(stitch_folder, exist_ok=True)
        #if not os.path.exists(stitch_folder):
            #os.mkdir(stitch_folder)
   
        cv2.imwrite(stitch_folder+ i + desired_extension, img_v_resize)
    
    patch_folder = path+"/"+"stitched/"
    img_objects = []
    img_dict = {}
    for p in listdir_nohidden(patch_folder):
        if str(patch_folder+p).endswith(desired_extension):
            p.replace(desired_extension, "")
            binned = Image.open(patch_folder+p)
            img_dict[p] = binned
            img_objects.append(binned)
        else:
            continue

    # get smallest width from the list of bin images
    #add an error message here that tells you to check the file names of the current section. Gives an empty sequence error for min() if no files matched the criteria
    w_min = min(img.size[0] 
            for img in img_objects)
            
    section_image = Image.new('RGB', (w_min, (section_length*(resolution*10))))


    #for i in bin_list and j in os.listdir(subfolder):
    for key in img_dict:
        img = img_dict[key]
        img = img.resize((w_min, img.height), Image.NEAREST)
        label_identifier = key.replace(desired_extension, "")#changed from 'extension'
        top_offset = (scanned_df.loc[label_identifier, "Top offset (cm)"])*(resolution*10)
        section_image.paste(img, (0, int(top_offset)))
    
    
    compiled_images = "final sections/"+site+"/"
    os.makedirs(compiled_images, exist_ok=True)
    CCI_images = "CCI_images/"+site+"/"
    os.makedirs(CCI_images, exist_ok=True)
    section_image.save(compiled_images+label+desired_extension)
    scanned_df.to_csv(patch_folder + "scanned_piece_list.csv")

    #construct scale bar with 10cm intervals
    height = section_length*(resolution*10)
    scale = Image.new('RGB', (5800, height+2000), color="White")

    bar_top = (5200, 500)
    verticle = 5200
    draw = ImageDraw.Draw(scale)
    draw.line((bar_top, (verticle, height+500)), fill="black", width =100)


    depth = 0
    for i in range(500,(height+1500), 4000):
        draw.line(((verticle, i), (height, i)), fill="black", width =100)
        font = ImageFont.truetype("Arial Unicode.ttf", size=1500)
        if depth == 0:
            draw.text(((verticle-1700), i-800), str(depth), (0,0,0), font=font) #was vertical-1200 and i-400
            depth += 0.1
            depth = round(depth, 2)
        else:
            draw.text(((verticle-2500), i-1200), str(depth), (0,0,0), font=font) #was vertical-2000 and i-800
            depth += 0.1
            depth = round(depth, 2)

    #for depth text along side of axis
    """text=Image.new('RGB', (14000,2000), color="White")
    font2 = ImageFont.truetype("Arial Unicode.ttf", size=1500)
    d = ImageDraw.Draw(text)
    d.text( (0, 0), "Depth [m]", (0,0,0),  font=font2)
    text = text.transpose (Image.ROTATE_90) 
    Image.Image.paste(scale, text,(200,20000)) """

    SHIL_path = "section_img/"+path+"/"
    SHIL_img_unfiltered = os.listdir(SHIL_path)
    SHIL_img = [item for item in SHIL_img_unfiltered if not item.startswith(".")]
    half_round_img = Image.open(SHIL_path+SHIL_img[0])
    width = scale.size[0] + section_image.size[0] + section_image.size[0] + 5000
    height = scale.size[1]
    figure = Image.new("RGB", (width, height+500), color="White") #was 2000
    Image.Image.paste(figure, section_image, (section_image.size[0], 500))
    Image.Image.paste(figure, scale, (0, 0))
    
    #get section bottom depth from piece log
    grouped_by_section = piece_log.groupby(["Core", "Sect"]).agg(list) #group by section
    for i in grouped_by_section.index:
        core_number = str(i[0])
        core_type = grouped_by_section.loc[i, "Type"][0]
        sect_number = str(i[1])
        sect = core_number+core_type+"-"+sect_number
        if sect in path:
            bottom_of_section = max(grouped_by_section.loc[i, "Bottom offset (cm)"])
            top_of_section = min(grouped_by_section.loc[i, "Top depth CSF-A (m)"])
        else:
            continue
    
    bottom_of_section = int(bottom_of_section * (resolution*10))

    top_left_x = (scale.size[0] + section_image.size[0]+3000)
    img = half_round_img.resize((int(section_image.size[0]/2), bottom_of_section))
    Image.Image.paste(figure, img, (top_left_x, 500))

    new_width = 2000
    new_height = 6000
    resized_figure = figure.resize((new_width, new_height), Image.Resampling.NEAREST)
    
    #Construct column headings as an image thats rotated and put above scale and images
    headings = Image.new('RGB', (resized_figure.width, 1600), color="White")
    sect_name_and_depth = Image.new('RGB', (headings.width, 300), color="White")
    text=Image.new('RGB', (1500, resized_figure.width), color="White")
    font2 = ImageFont.truetype("Arial Unicode.ttf", size=120)
    font3 = ImageFont.truetype("Arial Unicode.ttf", size=120)
    title = ImageDraw.Draw(sect_name_and_depth)
    title.text( (400, 0), label, (0,0,0),  font=font2)
    title.text( (200, 150), "Top depth: "+str(top_of_section)+" CSF-A (m)" , (0,0,0),  font=font3)
    d = ImageDraw.Draw(text)
    d.text( (0, 200), "Depth in section (m)", (0,0,0),  font=font2)
    d.text( (0, 590), "Moderate resolution", (0,0,0),  font=font2)
    d.text( (0, 700), "core exterior image", (0,0,0),  font=font2)
    d.text( (0, 1160), "Archive-half cut", (0,0,0),  font=font2)
    d.text( (0, 1270), "surface image", (0,0,0),  font=font2)
    text = text.transpose (Image.ROTATE_90) 
    
    Image.Image.paste(headings, text,(100,0)) #was 900 ,(1000,16000)
    Image.Image.paste(headings, sect_name_and_depth,(0,0)) 

    final_image = Image.new('RGB', (resized_figure.width, (resized_figure.height + headings.height)), color="White")
    
    Image.Image.paste(final_image, headings, (0, 0))
    Image.Image.paste(final_image, resized_figure, (0,headings.height))

    final_image.save(CCI_images+label+desired_extension)
    



for frames in tqdm(image_files):
    print(frames)
    if not frames.startswith("."):
        cci_image = "./CCI_images/"+site+"/"+expedition+"-"+site+"-"+frames+desired_extension
        print(cci_image)
        if not os.path.exists(cci_image):
            make_images(frames)
        else:
            continue
    else:
        continue
