# Copyright (C) 2019 Juan Fran Matheu G.
# Contact: jfmatheug@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "BlenderAtelier_Retopo",
    "author" : "JFranMatheu",
    "description" : "",
    "blender" : (2, 81, 0),
    "version" : (0, 0, 2),
    "location" : "",
    "warning" : "Take care! You won't believe your eyes!",
    "category" : "Generic"
}

from . import auto_load

import bpy
from bpy.props import BoolProperty, FloatProperty, FloatVectorProperty, PointerProperty

def update_rn_retopoObj_Color(self, context):
    try:
        context.scene.rn_retopoObj.color = self.rn_retopoObj_Color
    except:
        pass
    return

auto_load.init()

def register():
    auto_load.register()

    scn = bpy.types.Scene
    scn.rn_isActive = BoolProperty(default=False, description="Retopo Notes is Active")
    scn.rn_retopoObj = PointerProperty(type=bpy.types.Object, name="Pointer to Retopo Object")
    scn.rn_retopoObj_Color = FloatVectorProperty(name="Color for the Retopo Object", subtype='COLOR', default=(0.2,0.3,1,0.65), size=4, min=0, max=1, description="", update=update_rn_retopoObj_Color)
    scn.rn_retopoMesh = PointerProperty(type=bpy.types.Mesh, name="Pointer to Retopo Mesh")
    scn.rn_strokeMesh = PointerProperty(type=bpy.types.Mesh, name="Pointer to Stroke Mesh")
    scn.rn_manualExec = BoolProperty(default=False, description="Merge Strokes to an Only One Stroke. This allow multiple strokes but you should execute it manually")
    scn.rn_symmetrize = BoolProperty(default=False, description="Symmetrize Strokes")
    scn.rn_limitAngle = FloatProperty(default=.7, description="Limit Angle to dissolve unused vertices")
    scn.rn_minDistance= FloatProperty(name="Distance Threshold", default=.032, min=.005, max=.1, subtype='DISTANCE', description="Minimum distance between vertices. This will reduce greatly the ammount of vertices")
    scn.rn_autoFaces = BoolProperty(default=True, description="Auto-Faces")
    scn.rn_preserveSharp = BoolProperty(default=True, description="Preserve Sharp")
    scn.rn_afterGrab = BoolProperty(default=True, description="After-Grab for Dot Tool", name="After-Grab")
    scn.rn_proportionalGrab = BoolProperty(default=True, description="Proportional Grab for Dot Tool", name="Proportional Grab")

    #scn.rn_mousePath = bpy.props.PointerProperty(type=MousePathGroup)

def unregister():
    auto_load.unregister()

    scn = bpy.types.Scene
    del scn.rn_isActive
    del scn.rn_retopoObj
    del scn.rn_retopoObj_Color
    del scn.rn_retopoMesh
    del scn.rn_manualExec
    del scn.rn_symmetrize
    del scn.rn_limitAngle
    del scn.rn_minDistance
    del scn.rn_autoFaces
    del scn.rn_preserveSharp
    del scn.rn_afterGrab
    del scn.rn_proportionalGrab