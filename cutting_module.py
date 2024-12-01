def get_coords_of_all_rect_real(img_width, img_height, canv_width, canv_height, cutting_grid_params):
    """
    Returns real coordinates of top left corner of each rectangle
    in the cutting grid
    """
    coords = []

    # Adjusting origin point to be in the top left corner of the image, not canvas
    origin_x = (canv_width - img_width) // 2
    origin_y = (canv_height - img_height) // 2
    cur_x = cutting_grid_params['top_left_rect_x'] + origin_x
    cur_y = cutting_grid_params['top_left_rect_y'] + origin_y

    for i in range(cutting_grid_params['num_vert_rect']):
        for j in range(cutting_grid_params['num_horiz_rect']):
            coords.append((cur_x, cur_y))
            cur_x += cutting_grid_params['rect_width'] + cutting_grid_params['rect_horiz_dist']
        cur_x = cutting_grid_params['top_left_rect_x'] + origin_x
        cur_y += cutting_grid_params['rect_height'] + cutting_grid_params['rect_vert_dist']

    return coords

def get_coords_of_all_rect_scaled(img_width, img_height, canv_width, canv_height, scaled_cutting_grid_params):
    """
    Returns scaled coordinates of top left corner of each rectangle
    in the cutting grid
    """
    coords = []

    # Adjusting origin point to be in the top left corner of the image, not canvas
    origin_x = (canv_width - img_width) // 2
    origin_y = (canv_height - img_height) // 2

    cur_x = scaled_cutting_grid_params['top_left_rect_x'] + origin_x
    cur_y = scaled_cutting_grid_params['top_left_rect_y'] + origin_y

    for i in range(scaled_cutting_grid_params['num_vert_rect']):
        for j in range(scaled_cutting_grid_params['num_horiz_rect']):
            coords.append((cur_x, cur_y))
            cur_x += scaled_cutting_grid_params['rect_width'] + scaled_cutting_grid_params['rect_horiz_dist']
        cur_x = scaled_cutting_grid_params['top_left_rect_x'] + origin_x
        cur_y += scaled_cutting_grid_params['rect_height'] + scaled_cutting_grid_params['rect_vert_dist']
    return coords


def check_if_cutting_grid_fits(img_width, img_height, cutting_grid_params):
    """
    Checks if cutting grid based on given parameters fits into the image
    """
    print(img_width,img_height)
    x0, y0 = cutting_grid_params['top_left_rect_x'], cutting_grid_params['top_left_rect_y']
    xn = x0 + (cutting_grid_params['num_horiz_rect'] * cutting_grid_params['rect_width'] +
               (cutting_grid_params['num_horiz_rect'] - 1) * cutting_grid_params['rect_horiz_dist'])
    yn = y0 + (cutting_grid_params['num_vert_rect'] * cutting_grid_params['rect_height'] +
               (cutting_grid_params['num_vert_rect'] - 1) * cutting_grid_params['rect_vert_dist'])

    print(x0, y0)
    print(xn,yn)
    return (0 <= x0 <= xn <= img_width) and (0 <= y0 <= yn <= img_height)


def convert_representation(x0, y0, cutting_grid_params):
    """
    Converts top-left corner rectangle representation to a
    box representation: coordinates of each edge
    """
    x_left_edge = x0
    x_right_edge = x0 + cutting_grid_params['rect_width']
    y_bottom_edge = y0
    y_top_edge = y_bottom_edge + cutting_grid_params['rect_height']
    return x_left_edge, y_bottom_edge, x_right_edge, y_top_edge


def perform_cuts(img_width, img_height, saving_folder, img_to_cut, cutting_grid_params, canv_width = None, canv_height=None):
    """
    Performs cuts on the image based on real cutting parameters
    and saves resutling images
    """
    if canv_width is None:
        canv_width = img_width
    if canv_height is None:
        canv_height = img_height

    origin_x = (canv_width - img_width) // 2
    origin_y = (canv_height - img_height) // 2


    for ind, el in enumerate(get_coords_of_all_rect_real(img_width, img_height, canv_width, canv_height, cutting_grid_params)):
        cur_x0, cur_y0 = el[0] - origin_x, el[1] - origin_y
        cut_box = convert_representation(cur_x0, cur_y0, cutting_grid_params)
        cropped_img = img_to_cut.crop(cut_box)
        cropped_img.save(f'{saving_folder}/img{ind}.png')
