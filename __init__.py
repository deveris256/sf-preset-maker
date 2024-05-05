import bpy, os

bl_info = {
    "name": "SMBP Module: Preset Maker",
    "author": "Deveris256",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "3D",
    "description": "Starfield Multi Batch Processor Module: TXT Morph preset maker for use in Starfield",
    "category": "Development"
}

morph_name_list = [
    "Overweight",
    "Thin",
    "Strong",
    "BreastsBig",
    "BreastsFlat",
    "ButtBig",
    "ButtFlat",
    "FootBig",
    "FootSmall",
    "HipsNarrow",
    "Type1Arms",
    "Type1Legs",
    "Type3Arms",
    "Type3Torso",
    "Type1Hips",
    "Type1Torso",
    "Type2Arms",
    "Type2Hips",
    "Type2Legs",
    "Type2Torso",
    "Type3Hips",
    "Type3Legs",
    "Type4Arms",
    "Type4Hips",
    "Type4Legs",
    "Type4Torso",
    "FingersBig",
    "FingersThin",
    "HipsWide"
]

class SMBP_ZeroShapeKeys(bpy.types.Operator):
    bl_idname = "smbp.zero_shape_keys"
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

class SMBP_SavePresetToTxt(bpy.types.Operator):
    bl_idname = "smbp.save_preset_to_txt"
    bl_label = "Save txt preset"
    bl_description = "Creates a txt preset for use with in-game bat command"

    def execute(self, event):
        outfit = bpy.context.view_layer.objects.active

        if outfit != None and outfit.type == "MESH":
            raw_path = bpy.context.scene.smbp_master_folder
            safe_path = safePath(raw_path)

            if safe_path == None:
                self.report({"ERROR"}, f"Invalid path: {raw_path}")
                return {'CANCELLED'}
            else:
                preset_folder = os.path.join(safe_path, "presets")
                
            if not os.path.isdir(preset_folder):
                os.makedirs(preset_folder)

            createTxtPreset(outfit, preset_folder, bpy.context.scene.txt_preset_name)

            self.report({"INFO"}, f"Saved {bpy.context.scene.txt_preset_name}")
        else:
            print("Invalid outfit")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class SMBP_PT_BatPreset(bpy.types.Panel):
    bl_idname = "SMBP_PT_BatPreset"

    bl_label = "Preset creation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Starfield"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "smbp_master_folder")
        layout.prop(context.scene, "txt_preset_name")
        
        active_obj = bpy.context.view_layer.objects.active
        if active_obj and active_obj != None and active_obj.type == "MESH" and active_obj.data.shape_keys != None:
            sk_amount = str(len(list(sk for sk in active_obj.data.shape_keys.key_blocks)))
            layout.label(text=f"Object: {active_obj.name}")
            layout.operator("smbp.zero_shape_keys")
            layout.label(text=f"Shape-key amount: {sk_amount}")
            layout.operator("smbp.save_preset_to_txt")
        else:
            layout.label(text="Select valid object")

def safePath(path_arg, is_dir=True):
    if path_arg == "":
        return None
    
    if path_arg.startswith("//"):
        path = bpy.path.abspath(path_arg)
    else:
        path = path_arg

    if path == "" or len(path.split(os.path.sep)) < 1:
        return None

    if is_dir and not os.path.isdir(path):
        print(f"Not a directory: {path}")
        return None
    elif is_dir == False and not os.path.isfile(path):
        return None

    return path

def createTxtPreset(outfit, preset_folder, preset_name):
    content_list = []

    for shape_key in outfit.data.shape_keys.key_blocks:
        if shape_key.name == "Basis":
            continue
        content_list.append(f"ApplyChargenMorph {shape_key.name} {shape_key.value}")
        
    for morph_name in morph_name_list:
        if morph_name not in [sk.name for sk in outfit.data.shape_keys.key_blocks]:
            content_list.append(f"ApplyChargenMorph {morph_name} 0.0")

    content_list.append("SwitchSkeleton 0")
    content_list.append("SwitchSkeleton 1")

    full_path = os.path.join(preset_folder, preset_name + ".txt")

    with open(full_path, mode='wt', encoding='utf-8') as preset_file:
        preset_file.write('\n'.join(content_list))

classes = [
    SMBP_SavePresetToTxt,
    SMBP_ZeroShapeKeys,

    SMBP_PT_BatPreset
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.smbp_master_folder = bpy.props.StringProperty(
        name = "Folder",
        subtype = "DIR_PATH",
        default = "")
    
    bpy.types.Scene.txt_preset_name = bpy.props.StringProperty(name = "Name")

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()