""" Tools for UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports

# other imports
import numpy as np

# ETS imports
from enable.api import BaseTool
from traits.api import Float, Enum, Int, Bool

#==============================================================================
# Custom Tools
#==============================================================================

class PickTool(BaseTool):
    ''' select core sample pts and move vertical line there

    '''
    vert_line_component_index = Int(3)

    def normal_left_down(self,event):
        ''' Mouse action to select the nearest core point.

        Moves vertical line tool selected position
        '''

        core = self.component
        mouse = (event.x, event.y)
        hitpt = core.hittest(mouse)
        if hitpt:
            nearest_x, nearest_y = core.map_data(hitpt)
            vline = core.container.components[self.vert_line_component_index]
            data = vline.value.get_data()
            vline.value.set_data([nearest_x for value in data])

class TraceTool(BaseTool):
    ''' Allows mouse update of impoundment boundary trace
    '''

    event_state = Enum('normal', 'edit')
    last_index = Int(np.nan)
    last_y = Float(np.nan)
    mouse_down = Bool(False)
    PROXIMITY = Int(100)

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
            end = start + diff + 1
            xpts = [start,end]
            ypts = [self.last_y, newy]
            indices = range(*xpts)
            ys = np.interp(indices,xpts,ypts)
        else:
            indices = [current_index]
            ys = [newy]
        return np.array(indices), np.array(ys)

    def edit_mouse_move(self,event):
        ''' Continuously change the impound line value to the current mouse pos.

        While rt mouse button is down, this tracks the mouse movement to the
        right and changes the line value to the current mouse value at each
        index point recorded. If mouse moves too fast then the missing points
        are filled in.  If mouse is moved to the left then a straight line
        connects only the initial and final point.
        '''
        data = self.component.data
        newx, newy = self.component.map_data( (event.x, event.y))
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
            # save this mouse position as reference for further moves while
            # mouse_down is true.

            self.mouse_down = True
            self.last_index = current_index
            self.last_y = newy
