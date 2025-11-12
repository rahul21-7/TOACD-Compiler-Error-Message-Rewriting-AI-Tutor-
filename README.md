
* for creating the virtual environment(on powershell)
`.\venv\Scripts\Activate.ps1`

    if it gives an error, use `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

use `pip install -r requirements`
    or follow this process

* downlaod the following packages

```
pip install torch
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
pip install transformers
pip install sentencepiece
pip install tensorboard
```

* start running the train.py using `python train.py`(ensure that you use the command, hitting the run button will runn it in the local pc)

* for getting the visualization
`tensorboard --logdir=runs`

for running compiling an existing file use
`python ./tutor.py `