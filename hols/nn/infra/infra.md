# Infrastructure

## Introduction

In this lab we will build the infrastructure that we will use to run the rest of the workshop.

The main element that we will be creating is a **Data Science** session and notebook, to experiment with the newly-generated data using notebooks.

![Infrastructure](images/lol_infra.png)

We will use Cloud Shell to execute _`start.sh`_ script that will call Terraform to deploy all the infrastructure required and setup the configuration. If you don't know about Terraform, don't worry, there is no need. Also, there are no installation requirements: we will use Cloud Shell (which has Terraform installed by default) to deploy our infrastructure. 

Terraform is an Open Source tool to deploy resources in the cloud with code. You declare what you want in Oracle Cloud and Terraform make sure you get the resources created.

> Note: in the figure above, there's also a compute instance and autonomous database deployed automatically by Terraform. These resources are completely optional and you can run the workshop without them. However, if you're interested in integrating everything that we'll talk about in the workshop with **your own datasets**, this is the way to do it. You can check out more information on this [in this workshop](https://oracle-devrel.github.io/leagueoflegends-optimizer/hols/workshops/dataextraction/index.html).

Do you want to learn more? Feel free to check [Terraform's code in this repository](../../../dev/terraform/) after the workshop.

Estimated Lab Time: 15 minutes

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.


## Task 1: Cloud Shell

1. From the Oracle Cloud Console, click on **Cloud Shell**.
  ![Cloud Shell Button](images/cloud-shell-button.png)

2. As soon as the Cloud Shell is loaded, you can download the assets to run this lab.
    ```
    <copy>git clone --branch livelabs https://github.com/oracle-devrel/leagueoflegends-optimizer.git</copy>
    ```

3. The result will look like this:
  ![Git Clone](images/git-clone.png)

4. Change directory with `cd` to `leagueoflegends-optimizer` directory:
    ```
    <copy>cd leagueoflegends-optimizer/dev</copy>
    ```
5. Terraform uses a file called `tfvars` that contains the variables Terraform uses to talk to Oracle Cloud and set up your deployment the way you want it. You are going to copy a template we provide to use your own values. Run on Cloud Shell the following command.

    ```
    <copy>cp terraform/terraform.tfvars.template terraform/terraform.tfvars</copy>
    ```

## Task 2: Deploy with Terraform

1. Click on **Code Editor**. Next to the Cloud Shell one.
    ![Cloud Code Editor](images/cloud-code-editor.png)

2. On the **Code Editor**, inside the Explorer section on the left panel, expand your username and navigate onto _`dev/terraform`_. You should see the file **`terraform.tfvars`**. Click on it: 
    ![Go To File](images/code-editor-go-to-file.png)

3. The file will open and you can copy values you will get from running commands on Cloud Shell and paste it on the Code Editor.

4. Copy the output of the following command as the tenancy OCID:
    ```
    <copy>echo $OCI_TENANCY</copy>
    ```

    ![Paste Tenancy OCID](images/paste-tenancy-ocid.png)

5. Copy the output of the same command as the compartment OCID:
    ```
    <copy>echo $OCI_TENANCY</copy>
    ```
    
    > Note: we can paste the same OCID here in both tenancy and compartment because the root compartment in a tenancy is equal to the tenancy's OCID.

    ![Paste Compartment OCID](images/paste-compartment-ocid.png)

    > You can deploy the infrastructure **on a specific compartment**<br>
    > You can get the Compartment OCID in different ways.<br>
    > The coolest one is with OCI CLI from the Cloud Shell.<br>
    > You have to change _`COMPARTMENT_NAME`_ for the actual compartment name you are looking for and run the command:
    > ```
    > <copy>oci iam compartment list --all --compartment-id-in-subtree true --query "data[].id" --name COMPARTMENT_NAME</copy>
    > ```

6. Save the file in the Code Editor.
    ![Code Editor Save](images/code-editor-save.png)


## Task 3: Start Deployment

1. Run the `start.sh` script
    ```
    <copy>./start.sh</copy>
    ```

2. The script will run and it looks like this.
    ![Start SH beginning](images/start-sh-beginning.png)

3. Terraform will create resources for you, and during the process it will look like this.
    ![Start SH terraform](images/start-sh-terraform.png)

4. The final part of the script is to print the output of all the work done.
    ![Start SH output](images/start-sh-output.png)

5. Copy the Data Science notebook URL from the output variable _`ds_notebook_session`_. This is the URL we will use to connect to our Data Science environment.
    ![Start SH output](images/start-sh-ssh.png)

    > Note: login credentials for the Data Science notebook are the same as the ones used to access Oracle Cloud Infrastructure.


## Task 4: Accessing Notebook

Having just created our OCI Data Science environment, we need to install the necessary Python dependencies to execute our code. For that, we'll access our environment.

- The easiest way is to access into the notebook **through the URL** that we previously copied from Terraform's output.

    ![Start SH output](images/start-sh-ssh.png)

    If you have done it this way, make sure to **skip through to the next task**.

- (Optionally) We can also access to the notebook via the OCI console, on the top left hamburger menu:

    ![](./images/select_data_science.png)

    > You may find the Data Science section by also searching in the top left bar, or in the Analytics & AI tab, if it doesn't appear in "Recently visited" for you:

    ![](images/analyticstab.png)

    Now, we have access to a [list of our Data Science projects launched within OCI.](https://cloud.oracle.com/data-science/projects) We access our project, and inside our project we'll find the notebook.

    > The name of the notebook may be different than shown here in the screenshot.

    ![](./images/open-notebook.png)

    ![](./images/open-notebook2.png)

    You should now see the Jupyter environment

    ![](./images/notebook.png)




## Task 5: Setting up Data Science Environment

We now need to load our notebook into our environment.
1. Opening a **Terminal** inside the _'Other'_ section the console and re-downloading the repository again:

    ![](./images/open_terminal.png)

2. Then, we re-clone the repository using this command:

    ```
    <copy>git clone --branch livelabs https://github.com/oracle-devrel/leagueoflegends-optimizer.git</copy>
    ```

3. Finally, execute these commands to install required Python dependencies:

    ```
    <copy>
    conda install -y python=3.8
    pip install -r leagueoflegends-optimizer/requirements_nn.txt
    </copy>
    ```

After this command, all requirements will be fulfilled and we're ready to execute our notebooks with our newly created conda environment.


## Task 6: Accessing our Notebooks

We should now see the repository / files in our file explorer:

![](./images/file_explorer.png)

![](./images/file_explorer_2.png)

We navigate to the _`leagueoflegends-optimizer/notebooks/`_ directory and open each one of the notebooks. These two notebooks are the ones we will review during this workshop:
- [_`nn_offline_model.ipynb`_](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/nn_offline_model.ipynb)
- [_`nn_live_model.ipynb`_](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/nn_live_model.ipynb)

You may now [proceed to the next lab](#next).


## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** - Victor Martin - Product Strategy Director
* **Last Updated By/Date** - September 16th, 2022