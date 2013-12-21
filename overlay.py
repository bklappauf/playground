""" play with npy file

"""
from random import random
import numpy as np

from traits.api import Instance, HasTraits, Array, Property, Float, Enum, Dict,\
                        Str, Int, Bool
                #, on_trait_change
from traitsui.api import ModelView, View, Item, ToolBar# Group,
from traitsui.menu import Action, OKCancelButtons, Menu, MenuBar
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
    core_pts = Property(depends_on=['seismic_array'])
    line = Property(depends_on=['seismic_array'])
    layer_dict = Dict(Str,Array)

    def _seismic_array_default(self):
        ary = np.load(FILE_NAME, 'r').T #should use try
        return ary

    def _get_core_pts(self):
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

class TraceTool(BaseTool):
    event_state = Enum('normal', 'edit')
    last_index = Int(np.nan)
    last_y = Float(np.nan)
    mouse_down = Bool(False)
    #def _event_state_default(self):
    #    return 'normal'
    #def _last_index_default(self):

    def switch(self):
        print self.event_state,'to',
        if self.event_state == 'normal':
            self.event_state = 'edit'
        else:
            self.event_state = 'normal'
        print self.event_state

    def normal_right_down(self,event):
        self.event_state = 'edit'

    def normal_right_up(self,event):
        self.event_state = 'normal'
        self.mouse_down = False

    def edit_right_down(self,event):
        self.event_state = 'edit'

    def edit_right_up(self,event):
        self.event_state = 'normal'
        self.mouse_down = False

    def edit_key_pressed(self,event):
        if event.character == "Esc":
            self._reset()

    def fill_in_missing_pts(self, current_index, newy, ydata):
        """ Fill in missing points if mouse goes to fast to capture all

        Find linear interpolation for each array point inbetween current mouse
        position and previously captured position.
        """
        diff = np.absolute(current_index - self.last_index)
        if diff > 1:
            start = min(current_index, self.last_index)
            end = start + diff +1
            xpts = [start,end]
            ypts = [self.last_y, newy]
            indices = range(*xpts)
            ys = np.interp(indices,xpts,ypts)
        else:
            indices = [current_index]
            ys = [newy]
        return np.array(indices), np.array(ys)

    def edit_mouse_move(self,event):
        data = self.component.data
        newx,newy = self.component.map_data( (event.x,event.y))
        print newx,newy
        xdata = data.get_data("boundary1X")
        current_index = np.searchsorted(xdata,newx)

        if self.mouse_down:
            ydata = data.get_data("boundary1Y")
            indices, ys = self.fill_in_missing_pts(current_index, newy, ydata)
            ydata[indices] = ys
            data.set_data("boundary1Y", ydata)
            self.last_index = indices[-1]
            self.last_y = ys[-1]
        else:
            self.mouse_down = True
            self.last_index = current_index
            self.last_y = newy





class AppWindow(ModelView):
    model = Instance(DataSource)
    #plots_container = Instance(OverlayPlotContainer)
    plots = Instance(Plot)
    #plotd = Instance(ArrayPlotData)
    plotd = Dict
    drawstyle = Enum('Pt_by_Pt', 'Continuous')
    traits_view = View(
                    Item('plots',editor=ComponentEditor(),
                            show_label=False),
                    'drawstyle',
                    menubar = MenuBar(
                                Menu( recalc,
                                        name = 'My Special Menu')),
                    toolbar = ToolBar(recalc),
                    buttons = OKCancelButtons,
                    width=1000, height=600,
                    resizable=True, title='Plot Overlay'
                   )

    def get_data_sets(self):
        ''' Assemble the relevant starting data in ArrayPlotData array

        Assuming we want 3 layers
            - Sonar image : image plot
            - Core sample points : scatter
            - Layer boundary designations : 1 or more line plots
        '''
        imgdat = self.model.seismic_array
        coredat = self.model.core_pts
        plotdata = ArrayPlotData(sonarimg=imgdat,#coredata=coredat.T)
                                coreX=coredat.T[0],coreY=coredat.T[1])
        for key,val in self.model.layer_dict.items():
            plotdata.arrays.update({key+'X':val.T[0],key+'Y':val.T[1]})
            plotdata = ArrayPlotData(**plotdata.arrays)
        return plotdata

    def _plots_default(self):
        plotdata = self.get_data_sets()
        plots = Plot(plotdata)
        self.plotd = plotdata.arrays
        plots.img_plot("sonarimg",colormap=jet,)
        plots.plot(('coreX','coreY'), type='scatter', marker='diamond',
                    color='red')
        plots.plot(('boundary1X','boundary1Y'), type='line', marker='square')
        plots.tools.append(TraceTool(plots))
        return plots



if __name__ == "__main__":
    window = AppWindow(model=DataSource())
    window.configure_traits()
