# StitchIT
Program to create section images from high-res DMT CoreScan3 images

This program is designed for images of drill core taken using a DMT CoreScan3 in high-resolution mode (40 pixels/mm) that were collected and curated using the techniques outlined in the methods chapter of IODP Expedition 390/393. Please use Grant et al. (2024) as a guide when using this software and all uses of StitchIT should include the following citation:

Grant, L.J.C., Evans, A.D., Coggon, R.M., Estep, J.D., McIntyre, A., Slagle, A., Widlansky, S.J., Albers, E., Harris, M., Teagle, D.A.H., Sylvan, J.B., Reece, J.S., and the Expedition 390/393 Scientists, 2024. Data report: high-resolution digital imaging of whole-round hard rocks collected during IODP Expeditions 390C, 395E, 390, and 393, South Atlantic Transect, using a DMT CoreScan3. In Coggon, R.M., Teagle, D.A.H., Sylvan, J.B., Reece, J., Estes, E.R., Williams, T.J., Christeson, G.L., and the Expedition 390/393 Scientists, South Atlantic Transect.  Proceedings of the International Ocean Discovery Program, 390/393: College Station, TX (International Ocean Discovery Program). https://doi.org/10.14379/iodp.proc.390393.209.2024

Images will need to have been cropped and aligned so that the red cutting line drawn along the length of the core is in the centre of the image.

Piece logs will need to be downloaded from LIMS and placed in the piece_logs folder and named using standard IODP convention:

For piece logs of a single section, name the log; expedition-site-core-section.csv e.g. 390-U1556B-30R-1.csv

For a piece log of an entire hole just name it using the site name; e.g. U1556B.csv

If making a plot that aligns the DMT image next to a section half image taken using the SHIL, cropped section half images should be downloaded from LIMS and placed in the section_half folder, there is no need to change the SHIL image file name. (this section will need to be uncommented and is found at the bottom of each script)

The folder for section half images should be; section_half/>site</>core-section</>image.jpg< e.g. section_img/U1556B/55R-2/image.jpg

Image normalization:
If overlapping image frames are available, first define the x-axis pixel coordinates for the overlapping regions and input these coordinates into the overlap.csv template. 
