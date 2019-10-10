
def create_boxes(ir_image_widht, ir_image_height, total_col_frame_x, total_col_frame_y, total_col_frame_width, total_col_frame_height, box_side_length):
    number_rows = ir_image_widht / box_side_length
    number_columns = ir_image_height / box_side_length
    length_row_colored_image = int(total_col_frame_width / number_rows)
    length_column_colored_image = int(total_col_frame_height / number_columns)

    boxes_list = []
    for index in range(int(ir_image_height * ir_image_widht / (box_side_length * box_side_length))):
        row = int(index / number_columns)
        column = index % number_columns
        print(column)
        # this cuts out the boxes (as numpy arrays) and appends them to the result
        boxes_list.append((total_col_frame_x + row * length_row_colored_image, int(total_col_frame_height + total_col_frame_y - (total_col_frame_y + column *
                                                                                                                                 length_column_colored_image)), length_row_colored_image, length_column_colored_image))
    return boxes_list


test_boxes = create_boxes(154, 209, 600, 210, 500, 670, 11)

print(test_boxes)
