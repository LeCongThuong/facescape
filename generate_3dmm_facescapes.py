import numpy as np
import os
from pathlib import Path
from toolkit.src.facescape_bm import facescape_bm
import random
import shutil
from tqdm import tqdm
import argparse
import json


class GenerateFullHeadMesh:
    def __init__(self, model_path, output_path, material_dir):
        self.model = facescape_bm(model_path)
        self.output_path = output_path
        self.mtl_path_list = list(Path(material_dir).rglob("*.mtl"))

    def generate_geometry_mesh(self, name_path, id):
        try:
            random_id_vec = np.random.normal(self.model.id_mean, np.sqrt(self.model.id_var))
            if random_id_vec[0]>0:
                random_id_vec = -random_id_vec
            # create random expression vector
            exp_vec = np.zeros(52)
            exp_vec[0] = 1
            exp_vec[np.random.randint(52)] = 1
            # generate full head mesh
            mesh_full = self.model.gen_full(random_id_vec, exp_vec)
            dest_dir = os.path.join(self.output_path, str(id))
            Path(dest_dir).mkdir(parents=True, exist_ok=True)
            mesh_full.export(dest_dir, name_path)
        except Exception as e:
            # remove the directory if the mesh generation fails, to avoid partial meshes
            shutil.rmtree(dest_dir)
            return False
        self._post_process(name_path, id)
        return True
    
    def _post_process(self, name_path, id):
        obj_file = os.path.join(self.output_path, str(id), name_path + ".obj")

        # Read the OBJ file
        with open(obj_file, "r") as file:
            lines = file.readlines()

        # Insert 'usemtl material_0' after 'mtllib' or before the first 'v' (vertex)
        output_lines = ["usemtl material_0\n"] + lines       
        # Write back to the OBJ file
        with open(obj_file, "w") as file:
            file.writelines(output_lines)

    
    def generate_texture_mesh(self, name_path, id, mtl_path, uv_map_path):
        try:
            # copy texture path .mtl to (self.output_path/str(id) and rename it to name_path
            dest_texture_file = os.path.join(self.output_path, str(id), name_path + ".mtl")
            shutil.copy(mtl_path, dest_texture_file)
            self._add_texture_to_mtl(uv_map_path, dest_texture_file)
        except Exception as e:
            print(e)
            # remove the directory if the mesh generation fails, to avoid partial meshes
            dest_dir = os.path.join(self.output_path, str(id))
            shutil.rmtree(dest_dir)
            return False
        return True
    
    def _add_texture_to_mtl(self, uv_img_path, dest_texture_file):
        # replace map_Kd png with name_path.jpg
        with open(dest_texture_file, "r") as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith("map_Kd"):
                lines[i] = f"map_Kd {uv_img_path}\n"
                break
        with open(dest_texture_file, "w") as file:
            file.writelines(lines)
    
    def generate_mesh(self, id, mtl_path, uv_map_path=None):
        if not self.generate_geometry_mesh(str(id), str(id)):
            return False
        if not self.generate_texture_mesh(str(id), str(id), mtl_path, uv_map_path):
            return False
        return True
    
    def _save_to_json(self, json_dict, output_json_file):
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, ensure_ascii=False, indent=4)
    
    def generate_meshes(self, start_idx=0, end_idx=10, output_json_file=None):
        outputs = {}
        for i in tqdm(range(start_idx, end_idx)):
            mtl_path = random.choice(self.mtl_path_list)
            mtl_name = mtl_path.stem.split(".")[0]

            uv_map_path = os.path.join(list(mtl_path.parents)[0], mtl_name + ".jpg")
            displacement_path = os.path.join(list(Path(mtl_path).parents)[1], "dpmap", mtl_name + ".png")

            isSuccess = self.generate_mesh(i, mtl_path, uv_map_path)
            if isSuccess:
                outputs[i] = {
                    "displacement_image": displacement_path
                }

        self._save_to_json(outputs, output_json_file=output_json_file)
        return True

def main():
    parser = argparse.ArgumentParser(description="Generate full head meshes from a model.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the 3D model file.")
    parser.add_argument("--output_path", type=str, required=True, help="Directory to save generated meshes.")
    parser.add_argument("--material_dir", type=str, required=True, help="Directory containing textures.")
    parser.add_argument("--start_idx", type=int, default=0, help="Start index for mesh generation.")
    parser.add_argument("--end_idx", type=int, default=10, help="End index for mesh generation.")
    parser.add_argument("--output_json", type=str, default=None, help="Path to save the output json file.")

    args = parser.parse_args()
    
    head_mesh = GenerateFullHeadMesh(args.model_path, args.output_path, args.material_dir)
    head_mesh.generate_meshes(start_idx=args.start_idx, end_idx=args.end_idx, output_json_file=args.output_json)

if __name__ == "__main__":
    main()


# python generate_3dmm_facescape.py --model_path "/media/hmi/Transcend/facescape_bilinear_model_v1_6/facescape_bm_v1.6_847_50_52_id_front.npz" \
#                  --output_path "/home/hmi/Downloads/temp_imgs_5" \
#                  --material_dir "/media/hmi/Transcend/facescape_tu/" \
#                  --start_idx 0 \
#                  --end_idx 10 \
#                  --output_json "/home/hmi/Downloads/temp_imgs_5/output.json"