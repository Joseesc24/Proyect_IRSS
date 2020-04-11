from os import walk
from PIL import Image
from resizeimage import resizeimage

results_path = './image_bank_result'


def images_degradation(path, files_list, degradation_per):
    for image in files_list:
        image_name, file_ext = image.split(".")
        if file_ext in ["jpg", "png"]:
            path_input = path + '/' + image_name + "." + file_ext
            path_output = results_path + '/' + image_name + '(-' + str(degradation_per) + "%)." + file_ext
            degradation_fact = 1 / (degradation_per / 100)
            image = Image.open(open(path_input, 'r+b'))
            width, height = image.size
            new_image = resizeimage.resize_cover(image, [int(width * degradation_fact), int(height * degradation_fact)])
            new_image.save(path_output, image.format)


path, subfolders, files_list = list(walk('./image_bank_origin'))[0]
images_degradation(path, files_list, 250)
