# Enter your code here
import cv2
import numpy as np


# Validate if the selected region lies within the boundries of the image.
def validate_region(in_shape, in_pos, in_size):
    pr = in_pos[1] - (in_size / 2 - 1)
    pc = in_pos[0] - (in_size / 2 - 1)
    pr2 = pr + in_size
    pc2 = pc + in_size
    if 0 <= pr < in_shape[0] and 0 <= pr2 < in_shape[0] and 0 <= pc < in_shape[1] and 0 <= pc2 < in_shape[1]:
        return True
    else:
        return False


# Validate if the position of a patch lies within the boundries of the image
def validate_patch(in_shape, row, col, in_size):
    row2 = row + in_size
    col2 = col + in_size
    if 0 <= row < in_shape[0] and 0 <= col < in_shape[1] and 0 <= row2 < in_shape[0] and 0 <= col2 < in_shape[1]:
        return True
    else:
        return False


def mouse_get_patch(action, x, y, flags, userdata):
    global idx
    if action == cv2.EVENT_LBUTTONDOWN:
        n = userdata["patch_size"]
        dim = userdata["image"].shape

        if validate_region(dim, (x, y), n):
            central_corner = (int(y - n / 2 - 1), int(x - n / 2 - 1))
            rows = [central_corner[0] - n, central_corner[0], central_corner[0] + n]
            cols = [central_corner[1] - n, central_corner[1], central_corner[1] + n]
            global_min = 1000
            for r, row in enumerate(rows):
                for c, col in enumerate(cols):
                    if not (r == 0 and c == 0):
                        if validate_patch(dim, row, col, n):
                            mean_x = np.mean(np.abs(cv2.Sobel(userdata["image"][row: row + n, col: col + n],
                                                              cv2.CV_32F, 1, 0, ksize = 5)))
                            mean_y = np.mean(np.abs(cv2.Sobel(userdata["image"][row: row + n, col: col + n],
                                                              cv2.CV_32F, 0, 1, ksize = 5)))
                            if mean_y < mean_x:
                                if mean_y < global_min:
                                    global_min = mean_y
                                    rr = row
                                    cc = col
                            else:
                                if mean_x < global_min:
                                    global_min = mean_x
                                    rr = row
                                    cc = col
            if global_min == 1000:
                print("No patch could be set.")
            else:
                source_image = userdata["image"][rr: rr + n, cc: cc + n].copy()
                mask = (cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n)) * 255).astype(np.uint8)
                src_mask = cv2.merge([mask, mask, mask])
                userdata["image"] = cv2.seamlessClone(source_image, userdata["image"],
                                                      src_mask, (x, y), cv2.NORMAL_CLONE).copy()
                if len(history) == 10:
                    history.pop(0)
                history.append(userdata["image"])
                idx = len(history) - 1


if __name__ == "__main__":

    global mouse_dict
    global history

    history     = []
    in_path     = "./images"
    out_path    = "./output"
    input_name  = "blemish"
    input_ext   = ".png"
    original    = cv2.imread(in_path + "/" + input_name + input_ext, cv2.IMREAD_COLOR)
    mouse_dict  = {"image":      original,
                   "patch_size": 30}
    history.append(original)

    window = "Blemish Remover"
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, mouse_get_patch, mouse_dict)

    print("Click on the blemish you would like to remove from the image.")
    print("Press ESC to exit the program.")
    print("Press + for a bigger patch size.")
    print("Press - for a bigger patch size.")
    print("Press z to undo a patch.")
    print("Patch size: 30")

    k = 0
    savings = 0
    idx = len(history) - 1
    while k != 27:
        cv2.imshow(window, history[idx])
        k = cv2.waitKey(20)

        if k == 43 and mouse_dict["patch_size"] < 60:
            mouse_dict["patch_size"] += 5
            print("Patch size: ", str(mouse_dict["patch_size"]))

        if k == 45 and mouse_dict["patch_size"] > 0:
            mouse_dict["patch_size"] -= 5
            print("Patch size: ", str(mouse_dict["patch_size"]))

        if (k == 90 or k == 122) and idx > 0:
            history.pop(idx)
            idx = len(history) - 1
            mouse_dict["image"] = history[idx]

        if (k == 83 or k == 115) and idx > 0:
            savings += 1
            out_name = input_name + "_" + str(savings) + input_ext
            cv2.imwrite(out_path + "/" + out_name, mouse_dict["image"])
            print("Image saved as ", out_name)

    cv2.destroyAllWindows()
