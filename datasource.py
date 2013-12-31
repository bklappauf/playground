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
from chaco.tools.api import PanTool, ZoomTool


FILE_NAME = "two_d_seismic.npy"
NUM_CORE_SAMPLES = 10
NUM_SURVEY_PTS = 100
CORESMPL_MAX = 100

class WaterDataSource(HasTraits):
    ''' Data model for plot in View window

    Defines, provides and treats data to be plotted
    '''
    seismic_array = Array
    position_pts = Array
    layer_dict = Dict(Str,Array)
    depth_m = Tuple(Float,Float)
    survey_dist_m = Float
    coresample_max_dist = Float()
    coresample_pts = Array
    line = Property(depends_on=['seismic_array'])

    def __init__(self,filename=None, depth=(-100,0), survey_rng=(0,1300),
                    coresample_max_dist=CORESMPL_MAX, **kw):
        super(WaterDataSource, self).__init__(**kw)
        self.depth_m = depth
        self.coresample_max_dist = coresample_max_dist
        self.survey_dist_m = survey_rng[1]-survey_rng[0]
        self.position_pts = np.linspace(survey_rng[0],survey_rng[1],
                                        NUM_SURVEY_PTS)
        y = np.arange(*depth)
        y = y[:, np.newaxis]
        z = np.sin(x + y)**2



    def _seismic_array_default(self):
        ary = np.load(FILE_NAME, 'r').T #should use try
        return ary

    def _get_coresample_pts(self):
        ''' create simulated coresample positions

        create array representing horizontal postions along survey line vs
        perpendicular distance from survey line.  Don't know if this is usefull
        but its easy to scatter plot
        '''
        x0, xrng = self.position_pts[0], self.survey_dist_m
        y0, yrng = self.core_smpl_max_dist, 2 * self.core_smpl_max_dist
        pts = [(xrng*random(),yrng*random()) for i in range(NUM_CORE_SAMPLES)]
        coresample_pts = np.array([x0,y0])+np.array(pts)
        return coresample_pts

    def _get_line(self):
        yrng, xrng = self.seismic_array.shape
        x = np.array(range(xrng))
        y = np.sin(x)+(yrng/2.0)
        return np.vstack((x,y)).T

    def _layer_dict_default(self):
        return {'impound1':self.line}

    def _add_freq(self, T):
        ''' Multiply vertical axis by some function to simulate
        scan with a different freq
        '''

        width, hight = self.seismic_array.T.shape


if __name__ == "__main__":
    pass
