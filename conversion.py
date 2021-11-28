import math

import gui_model
import simulation
from gui_constants import GUIConstants


def gui_to_sim_rect(map_height_px, gui_rect: gui_model.RectangleObject) -> simulation.Rectangle:
    rot = gui_rect.rot % (2 * math.pi)
    return simulation.Rectangle(
        (gui_rect.gui_pos[0] * GUIConstants.PX_TO_M, (map_height_px - gui_rect.gui_pos[1]) * GUIConstants.PX_TO_M),
        gui_rect.height * GUIConstants.PX_TO_M,
        gui_rect.width * GUIConstants.PX_TO_M,
        gui_rect.rot
    )


def gui_to_sim_circle(map_height_px, gui_circle: gui_model.CircleObject) -> simulation.Circle:
    return simulation.Circle(
        (gui_circle.gui_pos[0] * GUIConstants.PX_TO_M, (map_height_px - gui_circle.gui_pos[1]) * GUIConstants.PX_TO_M),
        gui_circle.radius * GUIConstants.PX_TO_M
    )
