""" UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports
from random import random

# ETS imports
import numpy as np
from traits.api import Instance, HasTraits, Array, Property, Float, Enum, Dict,\
                                Str, Int, Bool
                #, on_trait_change
from traitsui.api import ModelView, View, Item, ToolBar# Group,
from traitsui.menu import Action, OKCancelButtons, Menu, MenuBar,StandardMenuBar
from enable.api import ComponentEditor, BaseTool
from chaco.api import Plot, ArrayPlotData, OverlayPlotContainer, jet, PlotAxis,\
                    add_default_axes, create_scatter_plot
from pyface.api import ImageResource
from chaco.tools.api import PanTool, ZoomTool

# Local imports
from twdb_datasource import WaterDataSource

############## Sample Action for Menu and Toolbar ########
def do_recalc():
    pass

recalc = Action(name = "Recalculate",
                action = "do_recalc",
                toolip = "Recalculate the results",
                image = ImageResource("recalc.png"))
##########################################################

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
        xdata = data.get_data("impound1_X")
        current_index = np.searchsorted(xdata,newx)

        if self.mouse_down:
            ydata = data.get_data("impound1_Y")
            indices, ys = self.fill_in_missing_pts(current_index, newy, ydata)
            ydata[indices] = ys
            data.set_data("impound1_Y", ydata)
            self.last_index = indices[-1]
            self.last_y = ys[-1]
        else:
            self.mouse_down = True
            self.last_index = current_index
            self.last_y = newy






class AppWindow(ModelView):
    model = Instance(WaterDataSource)
    plots = Instance(Plot)
    plotd = Dict
    drawstyle = Enum('Pt_by_Pt', 'Continuous')
    traits_view = View(
                    Item('plots',editor=ComponentEditor(),
                            show_label=False),
                    'drawstyle',
                    # menubar = MenuBar(
                    #             Menu( recalc,
                    #                    name = 'My Special Menu')),
                    menubar = StandardMenuBar,
                    toolbar = ToolBar(recalc),
                    buttons = OKCancelButtons,
                    width=1000, height=600,
                    resizable=True, title='Plot Overlay'
                   )

    def _drawstyle_default(self):
        return 'Continuous'

    def get_data_sets(self):
        ''' Assemble the relevant starting data in ArrayPlotData array

        Assuming we want 3 layers
            - Sonar image : image plot
            - Core sample points : scatter
            - Layer boundary designations : 1 or more line plots
        '''
        imgdat = self.model.seismic_array
        coredat = self.model.coresample_pts
        plotdata = ArrayPlotData(sonarimg=imgdat,#coredata=coredat.T)
                                coreX=coredat.T[0],coreY=coredat.T[1])
        for key,val in self.model.layer_dict.items():
            plotdata.arrays.update({key+'_X':val.T[0],key+'_Y':val.T[1]})
            plotdata = ArrayPlotData(**plotdata.arrays)
        return plotdata

    def _plots_default(self):
        plotdata = self.get_data_sets()
        plots = Plot(plotdata)

        plotd = plotdata.arrays
        xbounds = self.model.survey_rng_m
        ybounds = self.model.depth_m
        plots.img_plot("sonarimg", colormap=jet,
                        xbounds=xbounds, ybounds=ybounds)
        plots.plot(('impound1_X','impound1_Y'), type='line', marker='square')
        ##---------------------------------------------------------------------
        # Plot core samples on separate vert axis
        #xbounds#---------------------------------------------------------------------
        # method 0
        #   set plots.y_axis.orientation to 'right' but then true for all
        ##---------------------------------------------------------------------
        ##---------------------------------------------------------------------
        # method 1  -  works
        #   Makes scatter plot object but with no Axis i think.
        #   Intended to be added to Plot or container.
        #   This seems to work by rescaling the scatter axis to the screen size
        #   of the Plot it was added to
        ##---------------------------------------------------------------------
        scatter = create_scatter_plot((plotd['coreX'],plotd['coreY']), marker='diamond',
                                       color='red')
        axis = PlotAxis(scatter, orientation='right')
        scatter.underlays.append(axis)
        plots.add(scatter)

        ##---------------------------------------------------------------------
        # Method 2
        # Try to modify a scatter plot already in the Plot object by adding axis
        #
        ##---------------------------------------------------------------------
        #scatter = plots.plot(('coreX','coreY'), type='scatter', marker='diamond',
        #       color='red')
        #scatterc = Plot(plotdata)
        #scatter = scatterc.plot(('coreX','coreY'), type='scatter', marker='diamond',
        #               color='red')
            #scatter.y_axis.orientation = 'right'
#        plots.y_axis.orientation = 'right'
        #scatter = create_scatter_plot((plotd['coreX'],plotd['coreY']), marker='diamond',
        #                                color='red')
        #scatter.index_range = plots.index_range
        #scatter.range2d = plots.range2d
        #left, bottom = add_default_axes(scatter)
        #plots.add(scatter)
        #axis = PlotAxis(scatter, orientation = 'right')
        #scatter.underlays.append(axis)
        #left.orientation = 'right'
        print 'scatter is ',scatter
        plots.tools.append(TraceTool(plots))
        plots.tools.append(PanTool(plots))
        plots.tools.append(ZoomTool(plots))
        return plots



if __name__ == "__main__":
    window = AppWindow(model=WaterDataSource())
    window.configure_traits()
