# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# ################################################################
# Init
# ################################################################

# To support reload properly, try to access a package var, 
# if it's there, reload everything

if "bpy" in locals():
    import imp
    if "export_threejs" in locals():
        imp.reload(export_threejs)
    if "import_threejs" in locals():
        imp.reload(import_threejs)

import bpy
from bpy.props import *
from io_utils import ExportHelper, ImportHelper

# ################################################################
# Custom properties
# ################################################################

bpy.types.Object.THREE_castsShadow = bpy.props.BoolProperty()
bpy.types.Object.THREE_meshCollider = bpy.props.BoolProperty()

bpy.types.Material.THREE_useVertexColors = bpy.props.BoolProperty()

class OBJECT_PT_hello( bpy.types.Panel ):
    
    bl_label = "THREE"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.label(text="Selected object: " + obj.name )

        row = layout.row()
        row.prop( obj, "THREE_castsShadow", text="Casts shadow" )

        row = layout.row()
        row.prop( obj, "THREE_meshCollider", text="Mesh collider" )


class MATERIAL_PT_hello( bpy.types.Panel ):
    
    bl_label = "THREE"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
 
    def draw(self, context):
        layout = self.layout
        mat = context.material
        
        row = layout.row()
        row.label(text="Selected material: " + mat.name )

        row = layout.row()
        row.prop( mat, "THREE_useVertexColors", text="Use vertex colors" )

# ################################################################
# Importer
# ################################################################

class ImportTHREEJS(bpy.types.Operator, ImportHelper):
    '''Load a Three.js ASCII JSON model'''

    bl_idname = "import.threejs"
    bl_label = "Import Three.js"

    filename_ext = ".js"
    filter_glob = StringProperty(default="*.js", options={'HIDDEN'})

    option_flip_yz = BoolProperty(name="Flip YZ", description="Flip YZ", default=True)
    recalculate_normals = BoolProperty(name="Recalculate normals", description="Recalculate vertex normals", default=True)

    def execute(self, context):
        import io_mesh_threejs.import_threejs
        return io_mesh_threejs.import_threejs.load(self, context, **self.properties)


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self.properties, "option_flip_yz")

        row = layout.row()
        row.prop(self.properties, "recalculate_normals")


# ################################################################
# Exporter - settings
# ################################################################

SETTINGS_FILE_EXPORT = "threejs_settings_export.js"

import os
import json

def file_exists(filename):
    """Return true if file exists and accessible for reading.
    
    Should be safer than just testing for existence due to links and 
    permissions magic on Unix filesystems.
    
    @rtype: boolean
    """
    
    try:
        f = open(filename, 'r')
        f.close()
        return True
    except IOError:
        return False
    
def get_settings_fullpath():
    return os.path.join(bpy.app.tempdir, SETTINGS_FILE_EXPORT)

def save_settings_export(properties):

    settings = {
    "option_export_scene" : properties.option_export_scene,

    "option_flip_yz"      : properties.option_flip_yz,

    "option_materials"       : properties.option_materials,
    "option_normals"         : properties.option_normals,
    "option_colors"          : properties.option_colors,
    "option_uv_coords"       : properties.option_uv_coords,
    "option_edges"           : properties.option_edges,

    "option_truncate"     : properties.option_truncate,
    "option_scale"        : properties.option_scale,

    "align_model"         : properties.align_model
    }
    
    fname = get_settings_fullpath()
    f = open(fname, "w")
    json.dump(settings, f)
    
def restore_settings_export(properties):
    
    settings = {}

    fname = get_settings_fullpath()
    if file_exists(fname):
        f = open(fname, "r")
        settings = json.load(f)
    
    properties.option_export_scene = settings.get("option_export_scene", False)

    properties.option_flip_yz = settings.get("option_flip_yz", True)

    properties.option_materials = settings.get("option_materials", True)
    properties.option_normals = settings.get("option_normals", True)
    properties.option_colors = settings.get("option_colors", True)
    properties.option_uv_coords = settings.get("option_uv_coords", True)
    properties.option_edges = settings.get("option_edges", False)
    
    properties.option_truncate = settings.get("option_truncate", False)
    properties.option_scale = settings.get("option_scale", 1.0)
    
    properties.align_model = settings.get("align_model", "None")

# ################################################################
# Exporter
# ################################################################

class ExportTHREEJS(bpy.types.Operator, ExportHelper):
    '''Export selected object / scene for Three.js (ASCII JSON format).'''

    bl_idname = "export.threejs"
    bl_label = "Export Three.js"

    filename_ext = ".js"

    option_flip_yz = BoolProperty(name = "Flip YZ", description = "Flip YZ", default = True)

    option_vertices = BoolProperty(name = "Vertices", description = "Export vertices", default = True)
    option_faces = BoolProperty(name = "Faces", description = "Export faces", default = True)
    option_normals = BoolProperty(name = "Normals", description = "Export normals", default = True)
    option_edges = BoolProperty(name = "Edges", description = "Export edges", default = False)

    option_colors = BoolProperty(name = "Colors", description = "Export vertex colors", default = True)
    option_uv_coords = BoolProperty(name = "UVs", description = "Export texture coordinates", default = True)
    option_materials = BoolProperty(name = "Materials", description = "Export materials", default = True)

    option_export_scene = BoolProperty(name = "Scene", description = "Export scene", default = False)

    option_truncate = BoolProperty(name = "Truncate", description = "Truncate decimals", default = False)
    option_scale = FloatProperty(name = "Scale", description = "Scale data", min = 0.01, max = 1000.0, soft_min = 0.01, soft_max = 1000.0, default = 1.0)

    align_types = [("None","None","None"), ("Center","Center","Center"), ("Bottom","Bottom","Bottom"), ("Top","Top","Top")]
    align_model = EnumProperty(name = "Align model", description = "Align model", items = align_types, default = "None")

    def invoke(self, context, event):
        restore_settings_export(self.properties)
        return ExportHelper.invoke(self, context, event)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("Selected: " + context.active_object.name)

        if not self.properties.filepath:
            raise Exception("filename not set")

        save_settings_export(self.properties)

        filepath = self.filepath
        import io_mesh_threejs.export_threejs
        return io_mesh_threejs.export_threejs.save(self, context, **self.properties)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self.properties, "option_export_scene")
        layout.separator()

        row = layout.row()
        row.prop(self.properties, "option_flip_yz")
        layout.separator()

        row = layout.row()
        row.prop(self.properties, "align_model")
        layout.separator()

        row = layout.row()
        row.prop(self.properties, "option_vertices")
        row.prop(self.properties, "option_normals")
        row = layout.row()
        row.prop(self.properties, "option_faces")
        row.prop(self.properties, "option_edges")
        layout.separator()

        row = layout.row()
        row.prop(self.properties, "option_uv_coords")
        row.prop(self.properties, "option_colors")
        row = layout.row()
        row.prop(self.properties, "option_materials")
        layout.separator()

        row = layout.row()
        row.prop(self.properties, "option_truncate")
        row.prop(self.properties, "option_scale")


# ################################################################
# Common
# ################################################################

def menu_func_export(self, context):
    default_path = bpy.data.filepath.replace(".blend", ".js")
    self.layout.operator(ExportTHREEJS.bl_idname, text="Three.js (.js)").filepath = default_path

def menu_func_import(self, context):
    self.layout.operator(ImportTHREEJS.bl_idname, text="Three.js (.js)")

def register():
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
