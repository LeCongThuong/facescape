import numpy as np
import os
from pathlib import Path
from toolkit.src.facescape_bm import facescape_bm
import random
import shutil
from tqdm import tqdm

class GenerateFullHeadMesh:
    def __init__(self, model_path, output_path, texture_dir):
        self.model = facescape_bm(model_path)
        self.output_path = output_path
        self.texture_path_list = list(Path(texture_dir).rglob("*.mtl"))

    def generate_geometry_mesh(self, name_path, id, expression_idx=0):
        try:
            random_id_vec = np.random.normal(self.model.id_mean, np.sqrt(self.model.id_var))
            # create random expression vector
            exp_vec = np.zeros(52)
            exp_vec[expression_idx] = 1
            # generate full head mesh
            mesh_full = self.model.gen_full(random_id_vec, exp_vec)
            dest_dir = os.path.join(self.output_path, str(id))
            Path(dest_dir).mkdir(parents=True, exist_ok=True)
            mesh_full.export(dest_dir, name_path)
        except Exception as e:
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
    
    def generate_texture_mesh(self, name_path, id):
        # try:
        texture_path = random.choice(self.texture_path_list)
        texture_name = texture_path.stem.split(".")[0]

        # copy texture path .mtl to (self.output_path/str(id) and rename it to name_path
        dest_texture_file = os.path.join(self.output_path, str(id), name_path + ".mtl")
        shutil.copy(texture_path, dest_texture_file)
        # replace map_Kd png with name_path.jpg
        with open(dest_texture_file, "r") as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith("map_Kd"):
                lines[i] = f"map_Kd {name_path}.jpg\n"
                break
        with open(dest_texture_file, "w") as file:
            file.writelines(lines)
        # copy texture path .png to (self.output_path/str(id) and rename it to name_path.jpg
        dest_texture_file = os.path.join(self.output_path, str(id), name_path + ".jpg")
        shutil.copy(os.path.join(texture_path.parent, texture_name + ".jpg"), dest_texture_file)
        displacement_path = os.path.join(list(Path(texture_path).parents)[1], "dpmap", texture_name + ".png")
        # copy displacement map to (self.output_path/str(id) and rename it to name_path.jpg
        dest_displacement_file = os.path.join(self.output_path, str(id), name_path + ".png")
        shutil.copy(displacement_path, dest_displacement_file)
        # except Exception as e:
        #     print(e)
        #     return False
        return True
    
    def generate_mesh(self, id):
        for expression_idx in range(52):
            if not self.generate_geometry_mesh(f"{str(id)}_{str(expression_idx)}", f"{str(id)}_{str(expression_idx)}", expression_idx):
                return False
            print("Generate geometry mesh done!")
            if not self.generate_texture_mesh(f"{str(id)}_{str(expression_idx)}", f"{str(id)}_{str(expression_idx)}"):
                return False
            print("Generate texture mesh done!")

    def generate_meshes(self, num_meshes):
        for i in tqdm(range(num_meshes)):
            if not self.generate_mesh(i):
                return False
        return True

    
if __name__ == "__main__":
    model_path = "/media/hmi/Transcend/facescape_bilinear_model_v1_6/facescape_bm_v1.6_847_50_52_id_front.npz"
    output_path = "/home/hmi/Downloads/temp_imgs_5"
    texture_dir =  "/media/hmi/Transcend/facescape_tu/" 
    # GenerateFullHeadMesh(model_path, output_path, texture_dir).generate_mesh("test", 1)
    head_mesh = GenerateFullHeadMesh(model_path, output_path, texture_dir)
    head_mesh.generate_meshes(10)