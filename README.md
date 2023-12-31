# StitchIT
Program to create section images from high-res DMT CoreScan3 images

This program is designed for images of drill core taken using a DMT CoreScan3 in high-resolution mode (40 pixels/mm) that were collected and curated using the techniques outlined in the methods chapter of IODP Expedition 390/393.

Images will need to have been cropped and aligned so that the red cutting line drawn along the length of the core is in the centre of the image.

Piece logs will need to be downloaded from LIMS and placed in the piece_logs folder and named using standard IODP convention:

    For piece logs of a single section, name the log; expedition-site-core-section.csv e.g. 390-U1556B-30R-1.csv

    For a piece log of an entire hole just name it using the site name; e.g. U1556B.csv

If making a plot that aligns the DMT image next to a section half image taken using the SHIL, cropped section half images should be downloaded from LIMS and placed in the section_half folder, there is no need to change the SHIL image file name. (this section will need to be uncommented and is found at the bottom of each script)

The folder for section half images should be; section_half/>site</>core-section</>image.jpg< e.g. section_img/U1556B/55R-2/image.jpg
