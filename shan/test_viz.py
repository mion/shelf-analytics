import sys
import os
import cv2
import numpy as np

def draw_detail(image, orig, label, value, value_text_color=(255, 255, 255)):
    FONT_SCALE = 1.0
    FONT_THICKNESS = 1
    FONT_LINE = cv2.LINE_AA
    FONT_TYPE = cv2.FONT_HERSHEY_PLAIN
    LABEL_TEXT_COLOR = (175, 175, 175)
    SPACE_AFTER_LABEL = 5
    label_size, _ = cv2.getTextSize(label, FONT_TYPE, FONT_SCALE, FONT_THICKNESS)
    label_width, _ = label_size
    cv2.putText(image, label, orig, FONT_TYPE, FONT_SCALE, LABEL_TEXT_COLOR, FONT_THICKNESS, FONT_LINE)
    cv2.putText(image, value, (orig[0] + label_width + SPACE_AFTER_LABEL, orig[1]), FONT_TYPE, FONT_SCALE, value_text_color, FONT_THICKNESS, FONT_LINE)
    value_size, _ = cv2.getTextSize(value, FONT_TYPE, FONT_SCALE, FONT_THICKNESS)
    value_width, _ = value_size
    return label_width + value_width + SPACE_AFTER_LABEL

def draw_watermark(image, orig, text):
    FONT_SCALE = 0.75
    FONT_THICKNESS = 1
    FONT_LINE = cv2.LINE_AA
    FONT_TYPE = cv2.FONT_HERSHEY_PLAIN
    cv2.putText(image, text, orig, FONT_TYPE, FONT_SCALE, (200, 200, 200), FONT_THICKNESS, FONT_LINE)

def main():
    # Load the image
    FRAME_IMAGE_PATH = "/Users/gvieira/shan/video-42-p_03/frames_events/frame-0020.png"
    img = cv2.imread(FRAME_IMAGE_PATH)
    height, width, channels = img.shape

    print("Height: {0}".format(str(height)))
    print("Width: {0}".format(str(width)))
    print("Channels: {0}".format(str(channels)))

    # Add footer
    ROW_PADDING = 10
    COL_PADDING = 20
    ROW_LINE_HEIGHT = 5
    ROW_HEIGHT = 30
    FOOTER_HEIGHT = 3 * ROW_HEIGHT
    img_with_footer = np.zeros((height + FOOTER_HEIGHT, width, channels), np.uint8)
    img_with_footer[0:(height - 1), 0:(width - 1)] = img[0:(height - 1), 0:(width - 1)]

    # Draw details
    detail_widths = []
    detail_widths.append(draw_detail(img_with_footer, (ROW_PADDING, height + 1 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Produto:", "GARRAFAS PET 2L ESQ"))
    detail_widths.append(draw_detail(img_with_footer, (ROW_PADDING, height + 2 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Conversao:", "1,04% (ult. 30 dias)"))
    detail_widths.append(draw_detail(img_with_footer, (ROW_PADDING, height + 3 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Sell Out:", "63,2% (ult. 30 dias)"))
    max_width = max(detail_widths)
    second_col_x = max_width + ROW_PADDING + COL_PADDING
    draw_detail(img_with_footer, (second_col_x, height + 1 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Loja:", "PREZUNIC BOTAFOGO")
    draw_detail(img_with_footer, (second_col_x, height + 2 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Camera:", "CORREDOR BEBIDAS SEC 3")
    draw_detail(img_with_footer, (second_col_x, height + 3 * (ROW_HEIGHT - ROW_LINE_HEIGHT)), "Data:", '25/05/2018 13:32:09 GMT-3')

    # Add water mark
    draw_watermark(img_with_footer, (ROW_PADDING, 2 * ROW_PADDING), "Shelf Analytics (v1.0.9)  |  Copyright (c) 2018 TonetoLabs Inc. All rights reserved.")
    # draw_watermark(img_with_footer, (ROW_PADDING, 2 * ROW_PADDING), "shelf-analytics-v1.0.9")
    # draw_watermark(img_with_footer, (ROW_PADDING, 4 * ROW_PADDING), "Copyright (c) 2018 TonetoLabs Inc. All rights reserved.")

    cv2.imshow('image with footer', img_with_footer)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()