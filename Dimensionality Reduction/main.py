import glob
import os
import numpy as np
from PIL import Image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout

# Dependencies
# Make sure to install the additional dependencies noted in the requirements.txt using the following command:
# pip install -r requirements.txt

# You might want to implement a helper function for the update function below or you can do all the calculations in the
# update callback function.
def helper(rows):

    H_channel_row = H_channel_arr[rows, :, :]
    aggr_H = np.sum(H_channel_row, axis=0)
    aggr_H_channel = np.sum(aggr_H, axis=1)
    # I have decided to simply calculate the relative frequency of the pixels per channel, without normalizing to 1.
    # I hope that this is OK, in my opinion this makes the channel histogram more interpretable, as a histogram is
    # usually used to visualize a distribution, and the area under the distribution always sums up to 1.
    Frequency_r = aggr_H[0] / aggr_H_channel[0]
    Frequency_g = aggr_H[1] / aggr_H_channel[1]
    Frequency_b = aggr_H[2] / aggr_H_channel[2]

    return Frequency_r.tolist(),Frequency_g.tolist(),Frequency_b.tolist()

# Only do this once you've followed the rest of the instructions below and you actually reach the part where you have to
# configure the callback of the lasso select tool. The ColumnDataSource containing the data from the dimensionality
# reduction has an on_change callback routine that is triggered when certain parts of it are selected with the lasso
# tool. More specifically, a ColumnDataSource has a property named selected, which has an on_change routine that can be
# set to react to its "indices" attribute and will call a user defined callback function. Connect the on_change routine
# to the "indices" attribute and an update function you implement here.
# In simpler terms, each time you select a subset of image glyphs with the lasso tool, you want to adjust the source
# of the channel histogram plot based on this selection.
# Useful information:
# https://docs.bokeh.org/en/latest/docs/reference/models/sources.html
# https://docs.bokeh.org/en/latest/docs/reference/models/tools.html
# https://docs.bokeh.org/en/latest/docs/reference/models/selections.html#bokeh.models.selections.Selection
def update(attr, old, new):
    selected_rows = new

    # we don't want to do anything if nothing is selected
    if len(selected_rows) == 0:
        Frequency_r,Frequency_g,Frequency_b = helper(np.arange(N))
        source_channel.data = dict(
            bin=bin,
            Frequency_r=Frequency_r,
            Frequency_g=Frequency_g,
            Frequency_b=Frequency_b
        )
        return

    Frequency_r, Frequency_g, Frequency_b = helper(selected_rows)
    source_channel.data = dict(
        bin=bin,
        Frequency_r=Frequency_r,
        Frequency_g=Frequency_g,
        Frequency_b=Frequency_b
    )


# Fetch the number of images using glob or some other path analyzer
N = len(glob.glob("static/*.jpg"))

# Find the root directory of your app to generate the image URL for the bokeh server
ROOT = os.path.split(os.path.abspath("."))[1] + "/"

# Number of bins per color for the 3D color histograms
N_BINS_COLOR = 16
# Number of bins per channel for the channel histograms
N_BINS_CHANNEL = 50

# Define an array containing the 3D color histograms. We have one histogram per image each having N_BINS_COLOR^3 bins.
# i.e. an N * N_BINS_COLOR^3 array
H_color_arr = np.empty(shape=(N,N_BINS_COLOR**3))

# Define an array containing the channel histograms, there is one per image each having 3 channel and N_BINS_CHANNEL
# bins i.e an N x 3 x N_BINS_CHANNEL array
H_channel_arr = np.empty(shape=(N,3,N_BINS_CHANNEL))

# initialize an empty list for the image file paths
im_arr = []


# Compute the color and channel histograms
for idx, f in enumerate(glob.glob("static/*.jpg")):
    # open image using PILs Image package
    im = Image.open(f)

    # Convert the image into a numpy array and reshape it such that we have an array with the dimensions (N_Pixel, 3)
    np_im = np.array(im)
    N_Pixel = np_im.shape[0]*np_im.shape[1]
    np_im = np.reshape(np_im, (N_Pixel, 3))

    # Compute a multi dimensional histogram for the pixels, which returns a cube
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html
    H_im, edges = np.histogramdd(np_im, bins=N_BINS_COLOR, range = ((0,255),(0,255),(0,255)))

    # However, later used methods do not accept multi dimensional arrays, so reshape it to only have columns and rows
    # (N_Images, N_BINS^3) and add it to the color_histograms array you defined earlier
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.reshape.html
    H_im = np.reshape(H_im, (1,N_BINS_COLOR**3))
    H_color_arr[idx] = H_im

    # Append the image url to the list for the server
    url = ROOT + f
    im_arr.append(url)

    # Compute a "normal" histogram for each color channel (rgb)
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    H_r_im, edges_r = np.histogram(np_im[:,0], bins = N_BINS_CHANNEL,range = (0,255))
    H_g_im, edges_g = np.histogram(np_im[:, 1], bins=N_BINS_CHANNEL, range=(0, 255))
    H_b_im, edges_b = np.histogram(np_im[:, 2], bins=N_BINS_CHANNEL, range=(0, 255))

    # and add them to the channel_histograms
    H_channel_arr[idx][0] = H_r_im
    H_channel_arr[idx][1] = H_g_im
    H_channel_arr[idx][2] = H_b_im

# Get get the initial shape of the image, to make sure the aspect is not skewed
img = np.array(Image.open(f))
h, w = img.shape[:2]

# Calculate the indicated dimensionality reductions
# references:
# https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
tsne_im = TSNE(n_components=2).fit_transform(H_color_arr)
pca_im = PCA(n_components=2).fit_transform(H_color_arr)

# Construct a data source containing the dimensional reduction result for both the t-SNE and the PCA and the image paths
source_dict = {'image':im_arr,
               'tsne_x':tsne_im[:,0].tolist(),
               'tsne_y':tsne_im[:,1].tolist(),
               'pca_x':pca_im[:,0].tolist(),
               'pca_y':pca_im[:,1].tolist()
               }
source = ColumnDataSource(data=source_dict)

# Create a first figure for the t-SNE data. Add the lasso_select, wheel_zoom, pan and reset tools to it.
plot_1 = figure(x_axis_label='x', y_axis_label='y',
                tools='pan,lasso_select,wheel_zoom,reset', title='t-SNE')

# And use bokehs image_url to plot the images as glyphs
# reference: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/image_url.html
plot_1.image_url(url='image',x='tsne_x',y='tsne_y',h=h/10,w=w/10,anchor='center',source=source,
                 h_units="screen",w_units="screen")

# Since the lasso tool isn't working with the image_url glyph you have to add a second renderer (for example a circle
# glyph) and set it to be completely transparent. If you use the same source for this renderer and the image_url,
# the selection will also be reflected in the image_url source and the circle plot will be completely invisible.
plot_1.circle('tsne_x','tsne_y',alpha = 0,source=source)


# Create a second plot for the PCA result. As before, you need a second glyph renderer for the lasso tool.
# Add the same tools as in figure 1
plot_2 = figure(x_axis_label='x', y_axis_label='y',
                tools='pan,lasso_select,wheel_zoom,reset', title='PCA')
plot_2.image_url(url='image',x='pca_x',y='pca_y',h=h/10,w=w/10,anchor='center',source=source,
                 h_units="screen",w_units="screen")
plot_2.circle('pca_x','pca_y',alpha = 0,source=source)

# Construct a datasource containing the channel histogram data. Default value should be the selection of all images.
# Think about how you aggregate the histogram data of all images to construct this data source
bin = list(range(1,N_BINS_CHANNEL+1))
Frequency_r,Frequency_g,Frequency_b = helper(np.arange(N))
source_dict_channel = {'bin':bin,
                       'Frequency_r':Frequency_r,
                       'Frequency_g':Frequency_g,
                       'Frequency_b':Frequency_b
                       }
source_channel = ColumnDataSource(data=source_dict_channel)

# Construct a histogram plot with three lines.
# First define a figure and then make three line plots on it, one for each color channel.
# Add the wheel_zoom, pan and reset tools to it.
plot_3 = figure(x_axis_label='bin', y_axis_label='Frequency',
                y_range=(0,1),tools='pan,wheel_zoom,reset', title='Channel Histogram')
plot_3.line("bin", "Frequency_r", line_width=3,color="red", source=source_channel)
plot_3.line("bin", "Frequency_g", line_width=3,color="green", source=source_channel)
plot_3.line("bin", "Frequency_b", line_width=3,color="blue", source=source_channel)

# Connect the on_change routine of the selected attribute of the dimensionality reduction ColumnDataSource with a
# callback/update function to recompute the channel histogram. Also read the topmost comment for more information.
source.selected.on_change("indices", update)

# Construct a layout and use curdoc() to add it to your document.
lt = layout([[plot_1, plot_2, plot_3]], sizing_mode="stretch_width")
curdoc().add_root(lt)


# You can use the command below in the folder of your python file to start a bokeh directory app.
# Be aware that your python file must be named main.py and that your images have to be in a subfolder name "static"

# bokeh serve --show .
# python -m bokeh serve --show .

# dev option:
# bokeh serve --dev --show .
# python -m bokeh serve --dev --show .
