""" Data source module for overlay UI


"""
from random import random
import numpy as np

from traits.api import Instance, HasTraits, Array, Property, Float, Enum, Dict,\
                        Str, Int, Bool
                #, on_trait_change
from traitsui.api import ModelView, View, Item, ToolBar# Group,
from traitsui.menu import Action, OKCancelButtons, Menu, MenuBar,StandardMenuBar
from enable.api import ComponentEditor, BaseTool
from chaco.api import Plot, ArrayPlotData, OverlayPlotContainer, jet, PlotAxis
from pyface.api import ImageResource

############## Sample Action for Menu and Toolbar ########
def do_recalc():
    pass

recalc = Action(name = "Recalculate",
                action = "do_recalc",
                toolip = "Recalculate the results",
                image = ImageResource("recalc.png"))
##########################################################

FILE_NAME = "two_d_seismic.npy"
NUM_CORE_SAMPLES = 10
class DataSource(HasTraits):
    ''' Data model for plot in View window

    Defines, provides and treats data to be plotted
    '''
    seismic_array = Array
    coresample_pts = Property(depends_on=['seismic_array'])
    line = Property(depends_on=['seismic_array'])
    layer_dict = Dict(Str,Array)

    def _seismic_array_default(self):
        ary = np.load(FILE_NAME, 'r').T #should use try
        return ary

    def _get_coresample_pts(self):
        yrng, xrng = self.seismic_array.shape
        pts = [(xrng*random(),yrng*random()) for i in range(NUM_CORE_SAMPLES)]
        return np.array(pts)

    def _get_line(self):
        yrng, xrng = self.seismic_array.shape
        x = np.array(range(xrng))
        y = np.sin(x)+(yrng/2.0)
        return np.vstack((x,y)).T

    def _layer_dict_default(self):
        return {'boundary1':self.line}


if __name__ == "__main__":
    pass
