from os import walk
from PIL import Image
from resizeimage import resizeimage

results_path = './image_bank_result'


def images_degradation(path, files_list):
    for image in files_list:
        image_name, file_ext = image.split(".")
        if file_ext in ["jpg", "png"]:
            path_input = path + '/' + image_name + "." + file_ext
            path_output = results_path + '/' + image_name + '_downgraded.png'
            image = Image.open(open(path_input, 'r+b'))
            new_image = resizeimage.resize_cover(image, [320, 134])
            new_image.save(path_output, image.format)


path, subfolders, files_list = list(walk('./image_bank_origin'))[0]
images_degradation(path, files_list)
