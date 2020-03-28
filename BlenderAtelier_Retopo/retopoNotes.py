import bpy, bmesh, time
from bpy.types import Operator, Panel, Header#, OperatorMousePath, PropertyGroup
from bpy.props import BoolProperty, FloatProperty, IntProperty
from mathutils import Vector, Matrix
import numpy as npy
from bpy_extras import view3d_utils

from pip._internal import main as pip

def install(package):
    pip(["install", package])

try:
    # Using Keyboard module in Python 
    import keyboard
except:
    install("keyboard")
    import keyboard

try:
    # Using Mouse module in Python 
    import mouse
except:
    install("mouse")
    import mouse
'''
class MousePath(OperatorMousePath):
    loc = [0, 0]
    time = [0, 0]

class MousePathGroup(PropertyGroup):
    custom_1: bpy.props.FloatProperty(name="My Float")
    custom_2: bpy.props.IntProperty(name="My Int")
'''
class BAR_PT_Retopo_Notes(Panel):
    bl_label = "   Retopo Notes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_context = "OBJECT"
    bl_category = 'Retopo'
    #bl_options = {'DEFAULT_CLOSED'}

    def draw_annotation_options(self, context):
        tool_settings = context.tool_settings
        view = context.space_data
        overlay = view.overlay
        box = self.layout.column().box()
        box.scale_y = 1.2
        _row = box.row()
        _row = _row.grid_flow(row_major=True, columns=3, align=False)
        if overlay.show_annotation:
            icon_show_annot = 'HIDE_OFF'
        else:
            icon_show_annot = 'HIDE_ON'
        _row.scale_x = 1.2
        _row.prop(overlay, "show_annotation", text="", icon=icon_show_annot)
        placement = _row.row(align=True)
        placement.scale_x = 1.2
        placement.prop(tool_settings, "annotation_stroke_placement_view3d", text="", expand=True)
        _row = _row.row(align=True)
        #_row.operator("nsmui.sculpt_notes_undo_stroke", text="", icon='LOOP_BACK')
        _row.operator("bar.clear_notes", text="Clear", icon='PANEL_CLOSE')

    def draw(self, context):
        self.draw_annotation_options(context)
        scn = context.scene
        obj = context.scene.rn_retopoObj

        layout = self.layout
        masterCol = layout.column(align=True)
        box = masterCol.box().column(align=True)
    #   TITULO 1
        title = box.row()
        title.scale_y = 0.8
        title.box().label(text="Retopo Mesh")
    #   PROPIEDADES SPLIT
        sProps = box.box()
        sProps.use_property_split = True
        sProps.prop(scn, 'rn_retopoObj_Color', text="Color")
        if obj != None:
            sProps.prop(obj, 'show_in_front', text="Show In Front")
            sProps.prop(obj, "display_type", text="Display As")
        sProps.prop(scn, 'rn_symmetrize', text="Symmetrize")
    #   TITULO 2
        box.separator()
        title = box.row()
        title.scale_y = 0.8
        title.box().label(text="Notes Settings")
    #   PROPIEDADES
        props = box.box()
        props.prop(scn, 'rn_limitAngle', text="Limit Angle (rad)")
        props.prop(scn, 'rn_minDistance', text="Distance Threshold")
        props.prop(scn, 'rn_preserveSharp', text="Sharp")
        props.prop(scn, 'rn_autoFaces', text="Auto-Faces")

        
        props.prop(scn, 'rn_afterGrab')
        props.prop(scn, 'rn_proportionalGrab')

        #layout.label(text="Run !")
        #layout.operator("bar.retopo_notes", text="RetopoNotes Mode", icon='PLAY')
    
    def draw_header(self, context):
        layout = self.layout
        layout.alert = context.scene.rn_isActive
        layout.operator("bar.retopo_notes", text="", icon='PLAY')

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class BAR_OT_Clear_Notes(Operator):
    bl_idname = "bar.clear_notes"
    bl_label = ""
    #bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear Notes"

    def execute(self, context):   
        try:
            noteData = context.scene.grease_pencil
            frame = noteData.layers.active.active_frame
            if len(frame.strokes) == 0:
                ShowMessageBox("No notes to clear", "Can't do this!", 'INFO')
            else:
                frame.clear()
                #frame.strokes.remove(frames.strokes[0])
        except:
            ShowMessageBox("No notes to clear", "Can't do this!", 'INFO')
        return {'FINISHED'}

class BAR_OT_Retopo_Notes(Operator):
    bl_idname = "bar.retopo_notes"
    bl_label = "Retopo Notes"
    #bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Start retopo mode with notes"

    #@classmethod
    #def poll(cls, context):
    #    return (context.area.type == 'VIEW_3D'
    #            and context.mode == 'EDIT')

    def invoke(self, context, event):
        # FILTERS
        #if context.active_object.type != 'MESH':
        #    self.report({'WARNING'}, "Invalid Object - Only with Mesh Objects")
        #    return {'CANCELLED'}
        
        # GRAPHICS
        #if context.scene.rn_graphics:
        #    if not hasattr(self, '_handle'):
        #        self._handle = context.space_data.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
        if context.scene.rn_retopoObj == None:
            context.scene.rn_retopoObj = self.setup_retopo_mesh(context)
        if context.view_layer.objects.active != context.scene.rn_retopoObj:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            context.scene.rn_retopoObj.select_set(state=True)
            context.view_layer.objects.active = context.scene.rn_retopoObj
        if context.active_object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # SETUP TOOL
        bpy.ops.wm.tool_set_by_id(name="builtin.annotate")
        context.tool_settings.annotation_stroke_placement_view3d = 'SURFACE'

        #self.originalColor = context.active_gpencil_layer.color

        context.scene.rn_isActive = True
        # CALL MODAL
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    noteTools = {
        "builtin.annotate",
        "builtin.annotate_line",
        "builtin.annotate_polygon",
        "builtin.annotate_eraser"
    }

    omitir = False
    mousePos = (0, 0)
    #mousePath = [][]
    mousePath = ()
    poly = False
    polyGrab = False
    grabing = False
    extruding = False
    wasSelected = False
    eraser = False
    canGrab = False
    canExtrude = False
    eraseOn = False

    def modal(self, context, event):
        #   CHECK EVENT CONDITIONS
        self.key_events(context, event)
        self.key_conditions(context, event)

        if self.omitir: # cancel condition
            return {'PASS_THROUGH'}
        #   CHECK STROKE
        self.noteData = context.scene.grease_pencil
        try:
            if len(self.noteData.layers.active.active_frame.strokes) == 0:
                return {'PASS_THROUGH'}
        except:
            return {'CANCELLED'}
        bpy.ops.mesh.select_all(action='DESELECT')
        self.stroke2Mesh(context, event)
        context.area.tag_redraw()
        bpy.ops.bar.clear_notes()
        return {'PASS_THROUGH'}

    def key_events(self, context, event):
        '''
        if event.type in {'LEFT_SHIFT'} and event.value in {'PRESS'}:
            if event.type in {'LEFTMOUSE'} and event.value in {'PRESS'}:
                if event.type in {'MOUSEMOVE'}:
                    self.mouse_co = event.mouse_region_x, event.mouse_region_y
                    bpy.ops.view3d.select(location=self.mouse_co)
        '''
    # DOT TOOL
        if self.polyGrab:
            self.dot_tool(context, event)
    # ERASE TOOL
        elif self.eraser:
            self.erase_tool(context, event)
        # INICIA MODO 'DOT' PULSANDO SHIFT -> INSERTA UN PUNTO
        elif event.type in {'LEFT_SHIFT'} and event.value in {'CLICK'}:
            self.poly = True
            bpy.ops.wm.tool_set_by_id(name="builtin.annotate_polygon")
            mouse.click(button='left') #mouse.release(button='left')
        # SWITCH ERASE MODE
        elif event.alt:
            if not self.eraser:
                self.omitir = True
                self.eraser = True
                # cambia a edges y deselecciona
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
                context.active_gpencil_layer.color = (200, 0, 0)
            else:
                self.reset_erase_tool(context, False)

    #   ERASE EDGES AROUND THE MESH
    def erase_tool(self, context, event):
        #   CANCEL TOOL
        if event.type in {'RIGHTMOUSE'}:
            self.reset_erase_tool(context, True)
        #   SELECCIONA TODO A SU PASO SI ESTÁ CLICKANDO CON LMB
        if mouse.is_pressed(button='left'):
            self.eraseOn = True
            bpy.ops.view3d.select(extend=True, location=(event.mouse_region_x, event.mouse_region_y))
        elif self.eraseOn:
            bpy.ops.mesh.delete(type='EDGE')
            self.reset_erase_tool(context, True)
        else:
            self.eraseOn = False
    
    #   RESET VALUES // FOR ERASE MODE
    def reset_erase_tool(self, context, clear):
        if clear:
            bpy.ops.bar.clear_notes()
        self.omitir = False
        self.eraser = False
        self.eraseOn = False
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT', action='TOGGLE')
        context.active_gpencil_layer.color = (0, 0, 200)

    #   INSERTS A DOT WITH AFTER-GRAB AND EXTRUDE ALL WITH VARIABLE SNAPPING
    def dot_tool(self, context, event):
        #   CANCEL TOOL
        if event.type in {'RIGHTMOUSE'}:
            self.reset_dot_tool(context.tool_settings)
        #   CTRL -> SWITCH BETWEEN EDGE / VERTEX SNAP
        if event.ctrl:
            if self.snapVerts:
                context.tool_settings.snap_elements = {'VERTEX'} # EDGE_MIDPOINT
                self.snapVerts = False
            else:
                context.tool_settings.snap_elements = {'EDGE'}
                self.snapVerts = True
        #   AFTER GRAB OPTION IS ACTIVE
        if context.scene.rn_afterGrab:
            if self.grabing or self.extruding:
                if event.type in {'LEFTMOUSE'} and event.value in {'RELEASE'}:
                    self.reset_dot_tool(context.tool_settings)
            elif event.type in {'LEFTMOUSE'} and event.value in {'RELEASE'}:
                context.tool_settings.use_mesh_automerge = False
                context.tool_settings.use_mesh_automerge_and_split = False
                context.tool_settings.snap_elements = {'FACE'}
                if context.scene.rn_proportionalGrab:
                    context.tool_settings.use_proportional_edit = True
                    context.tool_settings.use_proportional_connected = True
                keyboard.press_and_release('g')
                self.grabing = True
                #print("Grab")
            elif event.type in {'INBETWEEN_MOUSEMOVE'}: # INBETWEEN (funciona bien y se diferencia bien) O... MOUSEMOVE (es más rápido al coger la pos. pero más sensible y difícil controlar) CON COMPROBACIÓN DE DIST ENTRE POS ORIGINAL AL PULSAR (OTRA COND.) Y POSICIÓN EN ESTA COND.
                self.extruding = True
                keyboard.press_and_release('e')
                #print("Extrude")
        return

    #   RESET VALUES // FOR AFTER GRAB / EXTRUDE OF DOT TOOL
    def reset_dot_tool(self, ts):
        self.polyGrab = False
        self.grabing = False
        self.extruding = False
        ts.use_mesh_automerge = False
        ts.use_mesh_automerge_and_split = False
        ts.use_snap = False
        ts.snap_elements = {'FACE'}
        ts.use_proportional_edit = False
        ts.use_proportional_connected = False
        keyboard.press_and_release('esc')
        bpy.ops.wm.tool_set_by_id(name="builtin.annotate")

    def key_conditions(self, context, event):
        if context.active_object.type != 'MESH':
            self.exit(context, {'CANCELLED'})
            return {'CANCELLED'}
        elif context.mode != 'EDIT':
            self.exit(context, {'CANCELLED'}) #context.window_manager.modal_handler_remove(self)
            return {'CANCELLED'}
        elif event.type in {'RET'}: # 'RIGHTMOUSE', 
            self.exit(context, {'FINISHED'})
            return {'FINISHED'}
        elif event.type in {'ESC', 'DEL', 'BACK_SPACE'}:
            self.exit(context, {'CANCELLED'})
            return {'CANCELLED'}
        else:
            pass

    def exit(self, context, exitMode):
        self.report({'WARNING'}, "EXITING RETOPO NOTES MODE")
        context.scene.rn_isActive = False
        if hasattr(self, '_handle'):
            context.space_data.draw_handler_remove(self._handle, 'WINDOW')
            del self._handle
        #return exitMode

    def setup_retopo_mesh(self, context):
        # FIND IT FIRST
        try:
            if bpy.data.objects[RetopoNotes_Mesh]:
                return bpy.data.objects[RetopoNotes_Mesh]
        except:
            pass
        # CREATE IT
        meshName = "RetopoNotes_Mesh"
        mesh = bpy.data.meshes.new(meshName)   # create a new mesh
        context.scene.rn_retopoMesh = mesh
        obj = bpy.data.objects.new(meshName, mesh)      # create an object with that mesh
        context.view_layer.active_layer_collection.collection.objects.link(obj) # link it to the active scene
        #context.scene.collection.objects.link(obj) # TEST
        obj.location = Vector((0,0,0)) # set it's origin to the world origin
        # display
        obj.color = context.scene.rn_retopoObj_Color
        return obj

    def stroke2Mesh(self, context, event):
        noteStrokes = self.noteData.layers.active.active_frame.strokes
        strPoints = noteStrokes[0].points
        numPoints = len(strPoints) - 1
        if numPoints < 5 and not self.poly:
            return
        #mesh = context.scene.rn_retopoMesh
        #print(mesh)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        #noteStrokes = self.noteData.layers.active.active_frame.strokes
        
        meshName = "Stroke"
        if context.scene.rn_strokeMesh == None:
            context.scene.rn_strokeMesh = bpy.data.meshes.new(meshName)   # create a new mesh
        obj = bpy.data.objects.new(meshName, context.scene.rn_strokeMesh)      # create an object with that mesh
        obj.location = Vector((0,0,0)) #by.context.scene.cursor_location   # position object at 3d-cursor
        # Link light object to the active collection of current view layer,
        # so that it'll appear in the current scene.
        context.view_layer.active_layer_collection.collection.objects.link(obj)

        vertices = []
        edges = []

        if self.eraser:
            vertices.append(strPoints[0].co)
            vertices.append(strPoints[numPoints].co)
            edges.append((0,1))
        else:
            #oldPoint = None
            #strPoints = noteStrokes[0].points
            #numPoints = len(strPoints) - 1
            p = 0 # RESET FOR NEXT STROKE
            #pop = False
            for point in strPoints:
                #if pop and p != numPoints:
                #    strPoints.pop(index=p)
                #    numPoints -= 1
                #else:
                vertices.append(point.co)
                edges.append((p-1, p))
                p += 1 # Increment for next point
                #pop = not pop

        # CALCULAR MÁXIMA DISTANCIA Y MÍNIMA, 
        # CALCULAR PROMEDIO DE DISTANCIA COMO EL AREA DEL DIBUJO, 
        # PARA ESTABLECER UN MERGE VARIABLE ACORDE AL TAMAÑO DEL QUAD

        #   UPDATE AND VALIDATE MESH
        try:
            context.scene.rn_strokeMesh.from_pydata(vertices, edges, []) # [] (empty) #   Fill the mesh with verts, edges, faces 
        except:
            pass
        context.scene.rn_strokeMesh.validate(verbose=False)

        #vertices.clear()
        #edges.clear()
        obj.select_set(state=True)
        context.scene.rn_retopoObj.select_set(state=True)
        context.view_layer.objects.active = context.scene.rn_retopoObj
        bpy.ops.object.join()

        context.scene.rn_strokeMesh.clear_geometry()
        self.clean_mesh(context, event)
        
    def clean_mesh(self, context, event):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT', action='TOGGLE') 
            #bpy.ops.mesh.select_all(action='SELECT')

        if not self.poly and not self.eraser:
            mesh = context.scene.rn_retopoMesh
            bm = bmesh.new()
            bm.from_mesh(mesh)

            # recorrer vertices y seleccionar vertices con is_wire o is_manifold (is_boundary cuando está en un edge en los bounds)
            # bm.select_flush(False) deseleccionar y recorrer vertices y seleccionar con select_set(True) los que link_edges sea 2 o menos, o sólo uno para seleccionar similares y luego el dissolve limit por angulo
        
            if context.scene.rn_preserveSharp:
            #   DISSOLVE BAD VERTICES
                # bpy.ops.mesh.dissolve_limited(angle_limit=context.scene.rn_limitAngle)
                bmesh.ops.dissolve_limit(bm, angle_limit=context.scene.rn_limitAngle, use_dissolve_boundaries=False, verts=bm.verts, edges=bm.edges, delimit={'NORMAL'})
            #   REMOVE DOUBLES MERGING BY DISTANCE  
            # # ANTES ARRIBA DE DISSOLVE POR LIMIT ANGLE 
            # # HACERLO DESPUÉS PRESERVA MEJOR LAS ESQUINAS, DE LA OTRA FORMA SALE MUY SUAVIZADO
                # bpy.ops.mesh.remove_doubles(threshold=context.scene.rn_minDistance)
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=context.scene.rn_minDistance)
            else:
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=context.scene.rn_minDistance)
                bmesh.ops.dissolve_limit(bm, angle_limit=context.scene.rn_limitAngle, use_dissolve_boundaries=False, verts=bm.verts, edges=bm.edges, delimit={'NORMAL'})
            #bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
            #vertices = [v for v in mesh.vertices if v.select]
            #bmesh.ops.contextual_create(bm, geom=bm.verts, mat_nr=0, use_smooth=False)
        #   NORMALS
            #bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            
        #   MIRROR
            #if context.scene.rn_symmetrize:
                #bmesh.ops.symmetrize(bm, input=bm.edges, direction='X', dist=0.04)
            ''' 
            if self.poly:
                bm.verts.ensure_lookup_table()
                selected_verts = [v for v in bm.verts if v.select]
                index = selected_verts[0].index
                bm.select_history.add(bm.verts[index])
            '''
            if context.scene.rn_autoFaces:
                selected_verts = [v for v in bm.verts if v.select]

        # BMESH TO MESH
            bpy.ops.object.mode_set(mode='OBJECT')
            bm.to_mesh(mesh)
            #mesh.update()
            bpy.ops.object.mode_set(mode='EDIT')
            
            if context.scene.rn_autoFaces:
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
                bpy.ops.mesh.delete_loose(use_verts=False, use_edges=True, use_faces=False)
                bpy.ops.mesh.select_non_manifold()
                bpy.ops.mesh.edge_face_add()

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT', action='TOGGLE')
                # VOLVER A SELECCIONAR VERTICES
                for v in selected_verts:
                    v.select=True
        

    #   SAVE SEELCTED VERTICES
        #selected_verts = [v for v in mesh.vertices if v.select]

    #   DELETE LOOSE GEOMETRY
        '''
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE') 
        bpy.ops.mesh.delete_loose(use_verts=False, use_edges=True, use_faces=False)
    #   SELECT NON-MANIFOLD
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
    #   FILL WIRENET    
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE', action='TOGGLE')
        try:
            bpy.ops.mesh.select_interior_faces()
            bpy.ops.mesh.dissolve_faces(use_verts=False)
        except:
            pass
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT', action='TOGGLE')
        # VOLVER A SELECCIONAR VERTICES
        for v in selected_verts:
            v.select=True
        '''
        
        if self.poly:
            self.mousePos = (event.mouse_region_x, event.mouse_region_y)
            keyboard.press_and_release('esc')
            keyboard.press_and_release('w')
            #bpy.ops.wm.tool_set_by_id(name="builtin.move")
            bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
            context.tool_settings.use_mesh_automerge = True
            context.tool_settings.use_mesh_automerge_and_split = True
            context.tool_settings.double_threshold = 0.01
            context.tool_settings.use_snap = True
            context.tool_settings.snap_elements = {'EDGE'}
            #selected_verts[0].co = Vector((selected_verts[0].co[0] + 0.001, selected_verts[0].co[1] + 0.001, selected_verts[0].co[2] + 0.001))
            keyboard.press_and_release('g')
            self.press = False
            self.polyGrab = True
            self.snapVerts = False
            self.poly = False
            #bmesh.ops.translate(bm, vec=Vector((0.001, 0.001, 0.001)), space=Matrix.Translation((0.001, 0.001, 0.001)), verts=bm.verts)
        #elif self.eraser:
            # FORMA FÁCIL, ADIOS A LAS INTERSECCIONES
            # Hemos creado un mouse path gracias a las anotaciones, aprovechemoslo para realizar una seleccion lazo gracias a este trazado
            #bpy.ops.view3d.select_lasso(path=None, mode='SET')



            # Detectar intersección entre vertices seleccionados (1 edge) y resto de edges

            # Remove vertices seleccionados y edge intersectado (seleccionar tmb y borrar seleccionados)

            # actualizar la malla

            # cambiar herramienta activa


    # free bmesh
        #bm.free()

import math
def calculateDistance(x1,y1,x2,y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist