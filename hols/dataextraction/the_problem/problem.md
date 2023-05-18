# How to think like a Machine

## What Data can I get and how?

League API is where we need to look first

New endpoint 
    - last year's structure
    - this year's structure 

also mention live client api
-> also show the data that's available there
-> not so much, so I need a model with few variables.
  

## Is any of this data useful?
-> AutoML is my favorite way to go in general, since it saves me time and makes looking at raw datasets less painful

 tool mljar-supervised, but give full link of repositories that do this, like featuretools

#### Machine Learning

* [TPOT - Data Science Assistant](https://github.com/EpistasisLab/tpot) - A Python Automated Machine Learning tool that optimizes machine learning pipelines using genetic programming. http://epistasislab.github.io/tpot/

* [Featuretools](https://github.com/Featuretools/featuretools) - An open source python framework for automated feature engineering. https://www.featuretools.com

* [Auto-sklearn](https://github.com/automl/auto-sklearn) - Automated Machine Learning with scikit-learn<sup>1</sup>. https://automl.github.io/auto-sklearn

* [Lightwood](https://github.com/mindsdb/lightwood) - Lightwood is Legos for Machine Learning.

* [MindsDB Native](https://github.com/mindsdb/mindsdb) - Machine Learning in one line of code. http://mindsdb.com

* [mljar-supervised](https://github.com/mljar/mljar-supervised) - Automated Machine Learning for Supervised Tasks: Binary Classification, MultiClass Classification and Regression (work in progress). https://mljar.com

#### Deep learning

* [Auto-Keras](https://github.com/keras-team/autokeras) - Accessible AutoML for deep learning. http://autokeras.com/

* [NNI](https://github.com/microsoft/nni) - An open source AutoML toolkit for neural architecture search and hyper-parameter tuning. https://nni.readthedocs.io/en/latest/

* [AdaNet](https://github.com/tensorflow/adanet) - Fast and flexible AutoML with learning guarantees. https://adanet.readthedocs.io

* [Ludwig](https://github.com/uber/ludwig) - Ludwig is a toolbox built on top of TensorFlow that allows to train and test deep learning models without the need to write code. http://ludwig.ai

* [darts](https://github.com/quark0/darts) - Differentiable architecture search for convolutional and recurrent networks. https://arxiv.org/abs/1806.09055

#### Hybrid solutions

* [automl-gs](https://github.com/minimaxir/automl-gs) - Provide an input CSV and a target field to predict, generate a model + code to run it. https://github.com/minimaxir/automl-gs

* [MLBox](https://github.com/AxeldeRomblay/MLBox) - MLBox is a powerful Automated Machine Learning python library. https://mlbox.readthedocs.io/en/latest/

* [mindsdb](https://github.com/mindsdb/mindsdb) - In-Database Machine Learning. MindsDB automates and abstracts machine learning models through virtual AI Tables.



## Learning from visualizations

This part: talk about what kind of info I get from mljar supervised - what kind of data to expect. -> most important variables

death per minute... talk about why league of legends is a problem that can be solved with normalizing data per minute.

take these variables, I'll create independent model to harmonize with live client api, which is my final objective, so people can actually use this github project at home

## building models

How many models, (as many as possible), train them with AutoML as well, but the library must be parametrizable enough so that, if I'm unhappy with e.g. provided default hyperparameters, I can change them just like I would in scikit-learn

## Explaining the flow of the final problem

A bit the data that's going from one place to the other,
which variables to call
we will need to deploy this model so people use it -> Model Deployment
And **now** it's time to extract data. Notice that data engineering is really important when trying to find a way to advance in a big project, as well as having solutions that make sense.
