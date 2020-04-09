import os
import cv2
import pandas as pd
from collections import namedtuple
from pprint import pprint
from configparser import ConfigParser

# namedtuple: just to save data for each sample and then put it into a data frame
LabelImages = namedtuple("LabelImages", "base_path filename label shape commit")

# Initialize a master list to save the information for each image
LIST = [] 


def help_iter(COUNTER_ITER, TOTAL):
    print("-"*20)
    print(f"{COUNTER_ITER}/{TOTAL} iterations")
    print("To stop and save, type EXIT")
    print("-"*20)


def default_options():
    print(" - To add commits, type COMMIT")
    print(" - To stop and save, type EXIT")
    print(" - To ask for your progress, type PROGRESS")

def help_labels(DICT_LABELS):
    for key,value in DICT_LABELS.items():
        print(f" - For {value} type {key.upper()}")

def help(DICT_LABELS):
    print("-"*30)    
    # Default options: Commit and exit
    print("[DEFAULT OPTIONS]")
    default_options()

    # Labels
    print("\n[LABELS]")
    help_labels(DICT_LABELS)

    print("\n[HINT]")
    print("Upper and lowercase are treated as equal.")
    print("Examples:\n - Y and y are the same.\n - exit, Exit and EXIT are the same.")
    print("\nTo show this block again, type HELP")
    print("-"*30)


def loadLabelImage(filename, 
                    WIDTH, HEIGHT,
                    PATH_PNG_FOLDER, 
                    INPUT_TEXT,
                    ACCEPTED_ANSWERS,
                    TOTAL, DICT_LABELS, 
                    COUNTER_ITER):
    """load an image and label it

    Arguments:
        filename {tuple} -- name of the image with extension.
    """    
    # Load image
    path_img = os.path.join("./images", filename)
    img = cv2.imread(path_img)
    shape = img.shape
    cv2.namedWindow(filename, cv2.WINDOW_GUI_EXPANDED)
    cv2.resizeWindow(filename,WIDTH, HEIGHT)
    cv2.imshow(filename,img)
    cv2.moveWindow(filename,0,0)
    cv2.waitKey(32)

    # Get label
    bool_correct_label = False
    commit = ""
    while not bool_correct_label:
        # Ask for the label
        label = str(input(INPUT_TEXT))
            
        # Corroboration of the answer
        if label.upper() in ACCEPTED_ANSWERS:
            bool_correct_label = True
        elif label.upper() == "COMMIT":
            commit = str(input("Commit: "))
        elif label.upper() == "EXIT":
            bool_images = False
            return bool_images
        elif label.upper() == "HELP":
            help(DICT_LABELS)
        elif label.upper() == "PROGRESS":
            help_iter(COUNTER_ITER, TOTAL)
        else:
            print(f"Please press one of the next options:\n")
            help_labels(DICT_LABELS)
            print("\nor type HELP for more information")
    
    # Save info of the image
    tuple_img = LabelImages(PATH_PNG_FOLDER, filename, label, shape, commit)
    
    # Append result to the master list
    LIST.append(tuple_img)
    
    # Destroy window
    cv2.destroyWindow(filename)

    return True

def genImg(tuple_images,
                WIDTH, HEIGHT,
                PATH_PNG_FOLDER, 
                INPUT_TEXT,
                ACCEPTED_ANSWERS,
                TOTAL, DICT_LABELS,
                COUNTER_ITER):
    '''Generator'''
    for COUNTER_ITER, tuple_image in enumerate(tuple_images):
        yield COUNTER_ITER, loadLabelImage(tuple_image,
                    WIDTH, HEIGHT,
                    PATH_PNG_FOLDER, 
                    INPUT_TEXT,
                    ACCEPTED_ANSWERS,
                    TOTAL, DICT_LABELS,
                    COUNTER_ITER)

def run():
    '''
    Run Process
    '''
    COUNTER_ITER = 0
    # Start
    print("*"*30)
    print("Welcome to the Labeler".center(28, " "))

    # Load ini
    config_file = "label_images.ini"
    cp = ConfigParser()
    cp.read(config_file)
    print("*"*30)
    
    # Get labels: keys and description
    DICT_LABELS = {}
    for key in cp["LABELS"]:
        DICT_LABELS[key] = str(cp["LABELS"][key])


    # HEIGHT, WIDTH
    WIDTH  = int(cp["IMAGE SETTINGS"].get("WIDTH"))
    HEIGHT = int(cp["IMAGE SETTINGS"].get("HEIGHT"))

    # Accepted answers
    ACCEPTED_ANSWERS = DICT_LABELS.keys()

    # Process the answers to work with uppercase
    ACCEPTED_ANSWERS = {answer.upper() for answer in ACCEPTED_ANSWERS}

    # Structure
    LABEL = cp["LABEL SETTINGS"].get("LABEL") + " " 

    # Text to show in input()
    INPUT_TEXT = LABEL + " " +  "/".join(["[" + str(answer) + "]" for answer in ACCEPTED_ANSWERS]) + " : "

    # Assuming images are saved in a some path like "path/to/png/study/series/sop.png"
    PATH_PNG_FOLDER = cp["INPUTS"].get("PATH_PNG_FOLDER")
  
    tuple_images = os.listdir(PATH_PNG_FOLDER)

    TOTAL = len(tuple_images)
    print(f"TOTAL IMAGES TO LABEL: {TOTAL}")
    
    # Get the generator
    generator = genImg(tuple_images, 
                    WIDTH, HEIGHT,
                    PATH_PNG_FOLDER, 
                    INPUT_TEXT,
                    ACCEPTED_ANSWERS,
                    TOTAL, DICT_LABELS,
                    COUNTER_ITER)

    # Run Process
    bool_images = True

    help(DICT_LABELS)
    while bool_images:
        try:
            COUNTER_ITER, bool_images = next(generator)
        except:
            bool_images = False
            print("\nNo more images to label")

    # Save data
    df = pd.DataFrame(LIST)
    try: 
        df.to_csv("df_manually_label.csv")
        print("\n ** df_manually_label.csv successfully saved in", os.getcwd())
    except:
        print("\n # Problems while saving df_manually_label.csv")
        
    try:
        df.to_excel("df_manually_label.xlsx")
        print("\n ** df_manually_label.xlsx successfully saved in", os.getcwd())
    except:
        print("\n # Problems while saving df_manually_label.xlsx \n")

    #TODO: Add summary with labeled images, total time spent, average time spent per image, etc
    print("*"*20)
    print("*"*20)
    print("\n\nSUMMARY PER LABEL\n")
    print(df.groupby("label").size())

if __name__ == '__main__':
    run()