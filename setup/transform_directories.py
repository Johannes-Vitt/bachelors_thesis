import glob
import os
import shutil

path_to_images = '/home/jetson/2019-johannes-vitt-bsc-thesis/data/images/'
print('this code needs to run inside the data directory')

# read the name of the diretory

directories = sorted(glob.glob(path_to_images + 'col_cam_2/**/'))

for directory_path in directories:
    directory = directory_path.split('/')
    #while we are at it we remove all blanks and replace them with underscores
    directory_name = directory[-2]
    new_directory_name = directory_name.replace(' ', '_')
    # create a new entry in the data/image directory
    path_to_new_directory = path_to_images + new_directory_name
    #os.mkdir(path_to_new_directory + '/col_cam_1/')
    #os.mkdir(path_to_new_directory + '/col_cam_2/')
    #os.mkdir(path_to_new_directory + '/ir_cam_1/')

    #collect all the files in the directory and copy them to the new directory
    old_images = sorted(glob.glob(directory_path + '*.png'))
    for image_path in old_images:
        image_name = image_path.split('/')[-1]
        print(image_name)
        shutil.copyfile(directory_path + image_name, path_to_new_directory + '/col_cam_2/' + image_name)
        shutil.copyfile(path_to_images + 'col_cam_1/' + directory_name + '/' + image_name, path_to_new_directory + '/col_cam_1/' + image_name)
        
    
