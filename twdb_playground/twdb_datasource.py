""" Data source module for overlay UI


"""
from random import random
import numpy as np

from traits.api import Instance, HasTraits, Array, Property, Float, Enum, Dict,\
                        Str, Int, Bool,Tuple
                #, on_trait_change
from traitsui.api import ModelView, View, Item, ToolBar# Group,
from traitsui.menu import Action, OKCancelButtons, Menu, MenuBar,StandardMenuBar
from enable.api import ComponentEditor, BaseTool
from chaco.api import Plot, ArrayPlotData, OverlayPlotContainer, jet, PlotAxis
from pyface.api import ImageResource
from chaco.tools.api import PanTool, ZoomTool


FILE_NAME = "two_d_seismic.npy"
NUM_CORE_SAMPLES = 10
CORESMPL_MAX = 100

class WaterDataSource(HasTraits):
    ''' Data model for plot in View window

    Defines, provides and treats data to be plotted

    :Parameters:
        seismic_array : 2d seismic array image loaded from file

        depth_m : Depth tuple giving min and max depth value relative to water
                  level.  Used to scale y axis

        survey_rng : Distance tuple for start and stop of x axis in meters, ie
                     track of survey boat.

        coresample_pts : Randomly generated set of coresample pts given as
                         Nx2 array where y axis represents perpendicular dist
                         from survey line.

        coresample_max_dist : Float used to generate y-value range of
                              coresample_pts

        layer_dict : Dictionary of impoundment layer lines in case more than one
                     is desired. This way they can be labled like 'auto
                     generated', or 'manually updated' etc.



    '''
    seismic_array = Array
    depth_m = Tuple(Float,Float)
    survey_rng_m = Tuple(Float, Float)
    coresample_pts = Array
    coresample_max_dist_m = Float()
    layer_dict = Dict(Str,Array)

    #survey_dist_m = Float
    #position_pts = Array
    #line = Property(depends_on=['seismic_array'])

    def __init__(self,filename=None, depth=(-100,0), survey_rng=(0,1300),
                    coresample_max_dist=CORESMPL_MAX, **kw):
        ''' Intialize scaling values.

        Takes optional inputs for setting physical ranges and creates
        some internal attributes based on these or their defaults.  Determines
        x and y scales on plots.
        '''
        super(WaterDataSource, self).__init__(**kw)

        self.depth_m = depth
        self.survey_rng_m = survey_rng
        self._survey_dist_m = survey_rng[1]-survey_rng[0]
        self.coresample_max_dist_m = coresample_max_dist
#
#        self._position_pts = np.linspace(survey_rng[0],survey_rng[1],
#                                        NUM_SURVEY_PTS)

        #y = np.arange(*depth)
        #y = y[:, np.newaxis]
        #z = np.sin(x + y)**2



    def _seismic_array_default(self):
        ary = np.load(FILE_NAME, 'r').T #should use try
        return ary

    def _coresample_pts_default(self):
        ''' create simulated coresample positions

        create array representing horizontal postions along survey line vs
        perpendicular distance from survey line.  Don't know if this is usefull
        but its easy to scatter plot
        '''
        x0, xrng = self.survey_rng_m[0], self._survey_dist_m
        y0, yrng = -self.coresample_max_dist_m, 2 * self.coresample_max_dist_m
        pts = [(xrng*random(),yrng*random()) for i in range(NUM_CORE_SAMPLES)]
        coresample_pts = np.array([x0,y0])+np.array(pts)
        return coresample_pts

    def _get_line(self):
        num_pts = self.seismic_array.shape[0]
        print num_pts
        x= np.linspace(self.survey_rng_m[0], self.survey_rng_m[1], num_pts)
        y = np.sin(x)+(self.depth_m[0]/2.0)
        return np.vstack((x,y)).T

    def _layer_dict_default(self):
        return {'impound1':self._get_line()}

    #def _add_freq(self, f):
    #    ''' Multiply vertical axis by some function to simulate
    #    scan with a different freq
    #    '''
    #    #y = np.arange(*depth)
    #    #y = y[:, np.newaxis]
    #    #z = np.sin(x + y)**2
    #    width, hight = self.seismic_array.T.shape


if __name__ == "__main__":
    pass
