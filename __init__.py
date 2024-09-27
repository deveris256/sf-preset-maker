import bpy, os

bl_info = {
    "name": "Starfield txt Preset Maker",
    "author": "Deveris256",
    "version": (0, 0, 2),
    "blender": (4, 0, 0),
    "location": "3D",
    "description": "TXT Morph preset maker for use in Starfield with bat command",
    "category": "Development"
}

class ZeroShapeKeys(bpy.types.Operator):
    bl_idname = "sf.zero_shape_keys"
    bl_label = "Clear shape-key values"
    bl_description = "Makes all shape-key values 0.0"

    def execute(self, event):
        outfit = bpy.context.view_layer.objects.active

        if outfit != None and outfit.type == "MESH":
            for sk in outfit.data.shape_keys.key_blocks:
                sk.value = 0.0
            self.report({"INFO"}, f"Cleared values of {str(len(list(sk for sk in outfit.data.shape_keys.key_blocks)))} shape-keys")
        else:
            print("Invalid outfit")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class SavePresetToTxt(bpy.types.Operator):
    bl_idname = "sf.save_preset_to_txt"
    bl_label = "Save txt preset"
    bl_description = "Creates a txt preset for use with in-game bat command"

    filepath: bpy.props.StringProperty(options={'HIDDEN'})
    filename: bpy.props.StringProperty(default='untitled.txt')
    filter_glob: bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})

    def execute(self, event):
        outfit = bpy.context.view_layer.objects.active

        if outfit != None and outfit.type == "MESH":

            createTxtPreset(outfit, self.filepath)

            self.report({"INFO"}, f"Saved {self.filename}")
        else:
            print("Invalid object selected")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SF_PT_BatPreset(bpy.types.Panel):
    bl_idname = "SF_PT_BatPreset"

    bl_label = "Preset creation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Starfield"

    def draw(self, context):
        layout = self.layout
        
        active_obj = bpy.context.view_layer.objects.active

        if active_obj and active_obj != None and active_obj.type == "MESH" and active_obj.data.shape_keys != None:
            sk_amount = str(len([sk for sk in active_obj.data.shape_keys.key_blocks]) - 1)
            layout.label(text=f"Object: {active_obj.name}")
            layout.operator("sf.zero_shape_keys")
            layout.label(text=f"Shape-key amount: {sk_amount}")
            layout.operator("sf.save_preset_to_txt")
        else:
            layout.label(text="Select valid object")

def createTxtPreset(outfit, preset_path):
    content_list = []

    for idx, shape_key in enumerate(outfit.data.shape_keys.key_blocks):
        if idx == 0:
            continue

        content_list.append(f"ApplyChargenMorph {shape_key.name} {shape_key.value}")

    content_list.append("SwitchSkeleton 0")
    content_list.append("SwitchSkeleton 1")

    if not preset_path.endswith(".txt"):
        preset_path += ".txt"
    
    with open(preset_path, mode='wt', encoding='utf-8') as preset_file:
        preset_file.write('\n'.join(content_list))

classes = [
    SavePresetToTxt,
    ZeroShapeKeys,

    SF_PT_BatPreset
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()