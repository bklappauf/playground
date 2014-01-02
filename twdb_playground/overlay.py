""" UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports
from random import random
import sys

# other imports
import numpy as np

# ETS imports
from enable.api import ComponentEditor
from traits.api import Instance, Enum
from traitsui.api import ModelView, View, Item, ToolBar
from traitsui.menu import Action, OKCancelButtons, StandardMenuBar
from chaco.api import Plot, ArrayPlotData, jet, PlotAxis, create_scatter_plot,\
                        create_line_plot, Legend
from chaco.tools.api import PanTool, ZoomTool, LegendTool
from pyface.api import ImageResource

# Local imports
from twdb_datasource import WaterDataSource
from twdb_custom_tools import TraceTool,PickTool

############## Sample Action for Menu and Toolbar ########
def do_recalc():
    pass

recalc = Action(name = "Recalculate",
                action = "do_recalc",
                toolip = "Recalculate the results",
                image = ImageResource("recalc.png"))


class AppWindow(ModelView):
    """ Main GUI window handler for twdb_playground application

    """
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

        # create vertical line for indicating selected core sample position
        vals1 = [0 for x in corey]
        vline = create_line_plot((corey,vals1), color='blue', orientation='v')
        vline.value_range = scatter.index_range
        plots.add(vline)

        # Add Legend
        legend = Legend(component=plots, padding=10, align="ur")
        legend.tools.append(LegendTool(legend, drag_button="left"))
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
