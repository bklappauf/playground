""" play with npy file

"""
import numpy as np

from traits.api import Instance, HasTraits, Array, Property, Float, Enum#, on_trait_change
from traitsui.api import ModelView, View, Item, ToolBar# Group,
from traitsui.menu import Action, OKCancelButtons, Menu, MenuBar
from enable.api import ComponentEditor
from chaco.api import Plot, ArrayPlotData, OverlayPlotContainer, jet, PlotAxis
from pyface.api import ImageResource

def do_recalc():
    pass

recalc = Action(name = "Recalculate",
                action = "do_recalc",
                toolip = "Recalculate the results",
                image = ImageResource("recalc.png"))


FILE_NAME = "two_d_seismic.npy"

class DataSource(HasTraits):
    xrng = Float
    yrng = Float
    seismic_array = Array()
    line = Property(depends_on=['xrng'])
    trace = Array

    def _seismic_array_default(self):
        ary = np.load(FILE_NAME, 'r') #should use try
        print ary.shape
        self.yrng, self.xrng = ary.shape
        return ary

    def _get_line(self):
        return 100*np.sin(np.arange(self.xrng)/100.)



class AppWindow(ModelView):
    model = Instance(DataSource)
    plots_container = Instance(OverlayPlotContainer)
    plot1 = Instance(Plot)
    plot2 = Instance(Plot)
    plot3 = Instance(Plot)
    drawstyle = Enum('Pt_by_Pt', 'Continuous')
    traits_view = View(
                    Item('plots_container',editor=ComponentEditor(),
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

    def _plot1_default(self):
        print self.model.seismic_array
        plotdata = ArrayPlotData(imagedata = self.model.seismic_array)
        imgplot = Plot(plotdata)
        imgplot.img_plot("imagedata",colormap=jet)
        return imgplot

    def _plot2_default(self):
        plotdata = ArrayPlotData(y=self.model.line)
        lineplot = Plot(plotdata)
        lineplot.plot('y', type='scatter',marker='square', marker_size = 1.0
                        ,color='blue')
        plotaxis = PlotAxis(lineplot,orientation='right')
        lineplot.underlays.append(plotaxis)
        return lineplot

    def _plot3_default(self):
        plotdata = ArrayPlotData(y=self.model.line)
        lineplot = Plot(plotdata)
        lineplot.plot('y', style='scatter',marker='square',color='blue',)
        return lineplot

    def _plots_container_default(self):
        return OverlayPlotContainer(self.plot1,self.plot2)



if __name__ == "__main__":
    window = AppWindow(model=DataSource())
    window.configure_traits()
