# Benchmark for SVFR methods
*This is a beta version*.  We present a benchmark to evaluate the accuracy of single-view face 3D reconstruction (SVFR) methods on our in-the-wild data and in-the-lab data. Different from [NoW benchmark](https://ringnet.is.tue.mpg.de/challenge.html) that evaluates the shape recovery for the expression-free canonical face, our benchmark takes various poses, expressions, environments and focal lengths into consideration. More details about the benchmark can be found in Sec. 6 in our [journal paper](https://arxiv.org/abs/2111.01082).

### Environment

The code is tested on Ubuntu with python 3.x. [Anaconda](https://www.anaconda.com/products/individual) is recommended to build a virtual environment:
```
conda create -n fs_eval python=3.6 -y
conda activate fs_eval
```
Install the required packages:
```
pip install --upgrade pip
pip install -r ../requirements.txt
```

Install pyembree to accelerate the intersection check, otherwise the evaluation will be very slow:
```
conda install -c conda-forge pyembree
```

Install [psbody-mesh](https://github.com/MPI-IS/mesh) following its instruction.

### Download Benchmark Data
The benchmark data (207 MB) that contains images, meshes, and parameters can be downloaded from NJU Drive:
```
cd data
./download_data.sh
```
or be downloaded from [Google Drive](https://drive.google.com/file/d/1-aZjHXpofKsDEa-rNunE2HsgUMlilKAY/view?usp=share_link). Using these data indicates that you have to obey the [License Agreement](https://github.com/zhuhao-nju/facescape/blob/master/doc/License_Agreement.pdf) of FaceScape.

### Show Pre-evaluated Results
The quantitative evaluations are put in './eval_result/'. You may show the quantitative results in command-line:
```
cd code
python show.py
```
or save the quantitative results as csv table:
```
cd code
python export.py
```

The heat meshes have been generated where the distance error is visualized as vertex color. 

### Run Evaluation Code

The evaluation code can be validated by running for the 14 reported methods, and the results should be the same as the pre-evaluated results above.

Firstly, download the result models of the 14 methods (14.3 GB) from NJU Drive:
```
cd pred
./download_pred.sh
```
or from Google Drive ([lab_pred.zip](https://drive.google.com/file/d/1catZZb8XTCIess_aea-46VieL197tzNh/view?usp=share_link), [wild_pred.zip](https://drive.google.com/file/d/1pY0Asfal7SPBfdRX4D4ecPQfXEhPo1R_/view?usp=share_link)).

Then run the following code to get the evaluation results:
```
cd code
./batch_eval.sh
```
This will take a few hours and the results will be saved to './eval_result/'.

### Evaluate a New Method
As various SVR methods output the resulting model in different formats and settings, we define the specific function for each method in 'pred_loader.py' to load the result models and process them. The process aims at projecting the result 3D model to align the source image using the standard projecting parameters, which involves scaling and depth-shift but no rotation.

To evaluate the methods on in-the-wild data, the resulting model should be placed in an orthogonal camera coordinate as used in trimesh(https://github.com/mikedh/trimesh). The orthogonal space is normalized to a cube in [-1, -1, -1] ~ [1, 1, 1].
To evaluate the methods on in-the-wild data, the resulting model should be placed in a perspective camera coordinate with the ground-truth focal length. The depth will be automatically shifted to align the resulting model and ground-truth model. As some methods use orthogonal projection while others use perspective projection, an approximate transforming between orthogonal and perspective is required in the loader function. Please refer to the existing 14 loader functions to write and register a new loader, then run the evaluation code for the specific method:
```
# in-the-wild evaluation
python ./evaluator.py --dataset fswild --method $METHOD_NAME$
# in-the-lab evaluation
python ./evaluator.py --dataset fslab --method $METHOD_NAME$
```
Use the option '--heat_mesh False' if the heat mesh is not required. Use the option '--num $IDX$' to evaluate only one tuple with index = $IDX$.

### Visualize

The quantitative evaluations are plotted as:

<img src="/figures/benchmark_eval.jpg" width="800">

Please note:
* The ground-truth shape for evaluation was normalized in scale. Specifically, all the pupil distances are scaled to 62.85mm, which is a statistical mean value of pupil distance.
* The main difference to [NoW Benchmark](https://ringnet.is.tue.mpg.de/challenge.html) is that our evaluation takes predicted pose and expression into account, while NoW benchmark mainly evaluates neutralized face, excluding the influence of facial expressions and poses.
