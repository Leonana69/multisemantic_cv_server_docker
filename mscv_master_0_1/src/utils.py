from PIL import Image

def resize_with_pad(image, target_size):
	old_w = image.size[0]
	old_h = image.size[1]
	r_w = target_size[0] / old_w
	r_h = target_size[1] / old_h
	if r_h < r_w:
		new_w = int(r_h * old_w)
		new_h = target_size[1]
	else:
		new_w = target_size[0]
		new_h = int(r_w * old_h)
	new_img = Image.new("RGB", (target_size[0], target_size[1]))
	new_img.paste(image.resize([new_w, new_h], Image.Resampling.LANCZOS), ((target_size[0] - new_w) // 2, (target_size[1] - new_h) // 2))
	return new_img
     

def get_pad_offset(image_size, target_size):
    r_w = target_size[0] / image_size[0]
    r_h = target_size[1] / image_size[1]
    if r_h < r_w:
        offset_w = (1.0 - image_size[0] * r_h / target_size[0]) / 2.0
        offset_h = 0.0
    else:
        offset_w = 0.0
        offset_h = (1.0 - image_size[1] * r_w / target_size[1]) / 2.0
    return [offset_w, offset_h]