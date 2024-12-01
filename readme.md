# Image Cutter
## Description
Image Cutter is an interactive image processing tool designed to simplify the task of defining and saving cut parameters for images. This application provides a user-friendly graphical interface, allowing users to visually place and adjust multiple rectangular cut regions on an image. These defined parameters can then be saved and reapplied to other images, making repetitive image processing tasks efficient and consistent.

Image Cutter was my final project for a university course
## Features
- **Interactive Edit View** - Users can place and adjust multiple rectangular regions over a loaded image
- **Cutting Functionality** - Save the defined regions as individual image files 
- **Parameter Management** - Save and load cut parameters for reuse on different images
## Usage
1. Load an Image
<p style="border: 1px solid gray; display: inline-block;">
  <img src="./Resources/main%20menu.png" alt="Image Description" />
</p>
2. Place rectangles by manually entering or uploading parameters
<p style="border: 1px solid gray; display: inline-block;">
  <img src="./Resources/image%20uploaded.png" alt="Image Description" />
</p>
3. Adjust parameters by dragging the grid or changing their value in the entries fields
<p style="border: 1px solid gray; display: inline-block;">
  <img src="./Resources/edit%20view.png" alt="Image Description" />
</p>
4. Save parameters if needed in a json file

5.Press the cut button
<p style="border: 1px solid gray; display: inline-block;">
  <img src="./Resources/filled%20edit%20view.png" alt="Image Description" />
</p>
6. Check out the results
<p>
  <span style="border: 1px solid black; display: inline-block; margin-right: 10px;">
    <img src="./Resources/img0.png" alt="Image 1" style="display: block;">
  </span>
  <span style="border: 1px solid black; display: inline-block;">
    <img src="./Resources/img1.png" alt="Image 2" style="display: block;">
  </span>
</p>



**OR**

1. Automated Cut: Load an image and load saved parameters to perform an automated cut
<p>
  <span style="border: 1px solid black; display: inline-block; margin-right: 10px;">
    <img src="./Resources/yt_screen.png" alt="Image 1" style="display: block;">
  </span>
  <span style="border: 1px solid black; display: inline-block;">
    <img src="./Resources/auto_cut.png" alt="Image 2" style="display: block;">
  </span>
</p>
2. Enjoy the results :)
<p>
  <span style="border: 1px solid black; display: inline-block; margin-right: 10px;">
    <img src="./Resources/au1.png" alt="Image 1" style="display: block;">
  </span>
  <span style="border: 1px solid black; display: inline-block;">
    <img src="./Resources/au2.png" alt="Image 2" style="display: block;">
  </span>
  <span style="border: 1px solid black; display: inline-block; margin-right: 10px;">
    <img src="./Resources/au3.png" alt="Image 1" style="display: block;">
  </span>
  <span style="border: 1px solid black; display: inline-block;">
    <img src="./Resources/au4.png" alt="Image 2" style="display: block;">
  </span>
</p>

## Tech Stack
- **Tkinter** for simple user-friendly UI
- **Pillow** for image cutting features

## Potential Improvements
- **Batch Processing**\
Add functionality to upload and process multiple images using saved parameters for automated cuts. This would significantly enhance the tool's efficiency for users dealing with large sets of images.