These are the instructions to assess the data scientist / machine vision engineer.
The use case is Virtual Try On using Generative Adversarial Networks (GANs).

### Dataset
You will use a specific dataset: [VITON_PLUS](https://1drv.ms/u/s!Ai8t8GAHdzVUiQQYX0azYhqIDPP6?e=4cpFTI)

### Solution tools suggestion
It is strongly advised to reuse existing codes. 
You can have a look at the CP-VTON+, 

- Link to the github: https://github.com/minar09/cp-vton-plus
- Article for further information: https://minar09.github.io/cpvtonplus/cvprw20_cpvtonplus.pdf
- Coding environment with GPU: https://colab.research.google.com
 
### Tasks
The tasks are the following:
- Work with data (wrangling, pre-processing)
    - Read some images and display them
    - Have some code for the pre-processing pipeline
- Modeling (Pytorch/Tensorflow)
    - Load a pre-trained network and have some code to make predictions
    - Select a metric and evaluate the pre-trained network on the test dataset
    - Train your own network (from scratch or using the pre-trained network) on the training dataset
    - Evaluate your network on the test dataset
- Bonus: build an API
- Couple of slides explaining
    - What did you do?
    - How you would deploy your model in production?
    
Remember, you are a data story teller ;)

We suggest to use the following template https://drivendata.github.io/cookiecutter-data-science/
when sending back your completed assessment.

Feel free to use the suggested tools, or use your own method, it is up to you!

### Evaluate the assessment
The evaluation is done in two parts:
- We will look at the code quality (production code), proficiency in writing best practice deep learning code.
You can use Jupyter notebooks with comments to provide the tasks' results based on your python scripts (commented).
- During the interview following the completion of the assessment, be ready
to explain your approach and also your intuitions behind the/your algorithms you used (how does it work?). 
The slides are to provide a good support to your argumentation.
