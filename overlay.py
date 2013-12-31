""" UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports
from random import random
import sys

# ETS imports
import numpy as np

# ETS imports
from enable.api import ComponentEditor, BaseTool
from traits.api import Instance, Float, Enum, Int, Bool
from traitsui.api import ModelView, View, Item, ToolBar
from traitsui.menu import Action, OKCancelButtons, Menu, MenuBar,StandardMenuBar
from chaco.api import Plot, ArrayPlotData, jet, PlotAxis, create_scatter_plot,\
                        create_line_plot, Legend
from chaco.tools.api import PanTool, ZoomTool, LegendTool
from pyface.api import ImageResource

# Local imports
from twdb_datasource import WaterDataSource

############## Sample Action for Menu and Toolbar ########
def do_recalc():
    pass

recalc = Action(name = "Recalculate",
                action = "do_recalc",
                toolip = "Recalculate the results",
                image = ImageResource("recalc.png"))


################################################################################
# Custom Tools
################################################################################
class PickTool(BaseTool):
    ''' select core sample pts and move vertical line there

    '''
    vert_line_component_index = Int(3)

    def normal_left_down(self,event):
        print 'in pick nld'
        core = self.component
        mouse = (event.x, event.y)
        point = core.map_data(mouse)
        hitpt = core.hittest(mouse)
        print 'ms,pt=',mouse, point, hitpt
        #import ipdb; ipdb.set_trace()
        if hitpt:
            nearest_x, nearest_y = core.map_data(hitpt)
            print nearest_x, nearest_y
            vline = core.container.components[3]
            data = vline.value.get_data()
            print vline, data
            vline.value.set_data([nearest_x for value in data])
        print '\n ############  pick done\n'
        sys.stdout.flush()

class TraceTool(BaseTool):
    ''' Allows mouse update of impoundment boundary trace

    '''

    event_state = Enum('normal', 'edit')
    last_index = Int(np.nan)
    last_y = Float(np.nan)
    mouse_down = Bool(False)
    PROXIMITY = Int(100)

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
        ''' continuously change the impound line value to the current mouse pos
        '''
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

#    def normal_left_down(self, event):
#        print '\n ############  nleft_down'
#        # don't know how to access this plot by name.
#        corepts = self.component.components[2]
#        print corepts
#        corexy = corepts.map_screen((0,-50))
#        pxy = self.component.map_screen((0,-50))
#        print corexy, pxy
#        print corexy-pxy
#        (mx,my) = (event.x,event.y)
#        xdata,ydata = corepts.index.get_data(), corepts.value.get_data()
#        xydata = np.vstack((xdata,ydata))
#        screen = corepts.map_screen( xydata.T)
#        diff = screen-(mx,my)
#        dist_array = np.sum(diff**2, axis=1)
#        index = np.argmin(dist_array)
#        x,y = xdata[index], ydata[index]
#        print index,screen, (mx,my), [x,y]
#        vline = self.component.components[3]
#        data = vline.value.get_data()
#        vline.value.set_data([x for value in data])
#        import ipdb; ipdb.set_trace()
#
#        print '\n ############  nleft_down done\n'
#        sys.stdout.flush()
##        #(mx,my) = corepts.map_data((event.x,event.y))
##        nearest = corepts.get_closest_point((mx,my), self.PROXIMITY)
##        print nearest
##        print corepts.map_data((event.x,event.y))
##        if nearest:
##            [x,y,d] = nearest
##            newx,newy = corepts.map_data( (x, y))
##            print (event.x,event.y), [x,y],newx,newy
##            vline = self.component.components[3]
##            print vline
##            data = vline.value.get_data()
##            print data
##            vline.value.set_data([newx for value in data])
##
##
#        #xdata,ydata = self.data_xy
#        #xydata = vstack((xdata,ydata))
#        #screen = self.component.map_screen( xydata.T)
#        #diff = screen-(event.x,event.y)
#        #dist_array = sum(diff**2, axis=1)
#        #index = argmin(dist_array)
#


class AppWindow(ModelView):
    model = Instance(WaterDataSource)
    plots = Instance(Plot)
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
        plotsDict = {}
        # plot background sonar image and impound lines
        xbounds = self.model.survey_rng_m
        ybounds = self.model.depth_m
        plots.img_plot("sonarimg", colormap=jet,
                        xbounds=xbounds, ybounds=ybounds)
        ip = plots.plot(('impound1_X','impound1_Y'), type='line', marker='square')
        plotsDict['Impoundment line'] = ip
        plots.x_axis.title = 'Distance along survey line (m)'
        plots.y_axis.title = 'Depth (m)'

        # add core samples as scatter with separate y-axis
        corex = plotdata.get_data('coreX')
        corey = plotdata.get_data('coreY')
        scatter = create_scatter_plot((corex,corey), marker='diamond',
                                       color='red' )
        scatter.index_range = plots.index_range
        axis = PlotAxis(scatter, orientation='right')
        axis.title = 'Core sample dist from survey line (m)'
        scatter.underlays.append(axis)
        plots.add(scatter)

        vals1 = [0 for x in corey]
        vline = create_line_plot((corey,vals1), color='blue', orientation='v')
        #vline.index_range = scatter.index_range
        vline.value_range = scatter.index_range
        plots.add(vline)

        # Add Legend
        legend = Legend(component=plots, padding=10, align="ur")
        legend.tools.append(LegendTool(legend, drag_button="right"))
        legend.plots = plotsDict
        plots.overlays.append(legend)

        # Add tools
        scatter.tools.append(PickTool(scatter))
        plots.tools.append(TraceTool(plots))
        plots.tools.append(PanTool(plots))
        plots.tools.append(ZoomTool(plots))

        return plots



if __name__ == "__main__":
    window = AppWindow(model=WaterDataSource())
    window.configure_traits()
