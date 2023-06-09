# Infrastructure

Estimated Time: 15-20 minutes

## Introduction

In this lab, we will build the infrastructure that we will use to run the rest of the workshop.

The main four elements that we will be creating are:

- **Compute** instance using a Linux-based image from Oracle Cloud.
- **Autonomous JSON Database** where we'll allocate the JSON documents.
- **Data Science** session and notebook, to experiment with the newly-generated data using notebooks.

![Infrastructure](images/lol_infra.png)

We will use Cloud Shell to execute `start.sh` script, which will call Terraform and Ansible to deploy all the infrastructure required and setup the configuration. If you don't know about Terraform or Ansible, don't worry, there is no need.

- Terraform is an Open Source tool to deploy resources in the cloud with code. You declare what you want in Oracle Cloud and Terraform make sure you get the resources created.
- Ansible is an Open Source tool to provision on top of the created resources. It automates the dependency installation, copies the source code, and config files so everything is ready for you to use.

Do you want to learn more? Feel free to check the code for terraform and ansible after the workshop [in our official repository.](https://github.com/oracle-devrel/leagueoflegends-optimizer/)

### Prerequisites

- An Oracle Free Tier, Paid or LiveLabs Cloud Account
- Active Oracle Cloud Account with available credits to use for Data Science service.

### Objectives

In this lab, you will learn how to:

- Use Oracle Cloud Infrastructure for your Compute needs
- Deploy resources using Terraform and Ansible
- Learn about federation, and what's necessary to authenticate a Terraform request
- Download the datasets we will use

## Task 1: Cloud Shell

First, we need to download the official repository to get access to all the code (Terraform and Ansible code for this step).

1. From the Oracle Cloud Console, click on **Cloud Shell**.
  ![Cloud Shell Button](images/cloud-shell-button.png)

2. As soon as the Cloud Shell is loaded, you can download the assets to run this lab.

    ```bash
    <copy>git clone --branch livelabs https://github.com/oracle-devrel/leagueoflegends-optimizer.git</copy>
    ```

3. The result will look like this
  ![Git Clone](images/git-clone.png)

4. Change directory with `cd` to `leagueoflegends-optimizer` directory:

    ```bash
    <copy>
    cd leagueoflegends-optimizer/dev
    </copy>
    ```

5. Terraform uses a file called `tfvars` that contains the variables Terraform uses to talk to Oracle Cloud and set up your deployment the way you want it. You are going to copy a template we provide to use your own values. Run on Cloud Shell the following command:

    ```bash
    <copy>
    cp terraform/terraform.tfvars.template terraform/terraform.tfvars
    </copy>
    ```

## Task 2: Deploy with Terraform and Ansible

1. Click on **Code Editor**. Next to the Cloud Shell one.
    ![Cloud Code Editor](images/cloud-code-editor.png)

    > **Note**: for **Safari** users:<br>
    > First, it isn't the recommended browser for OCI. Firefox or Chrome are fully tested and are recommended.<br>
    > With Safari, if you get a message _Cannot Start Code Editor_, go to _**Settings** > **Privacy**_ and disable _**Prevent cross-site tracking**_.<br>
    > Then open Code Editor again.

2. On the **Code Editor**, go to _**File** > **Open**_.
    ![Open menu](images/code-editor-open-menu.png)

3. On the pop-up, edit the path by clicking the pencil icon:
    ![Open Pop Up](images/code-editor-open-popup.png)

4. Append, at the end, the path to the `terraform.tfvars`
    ![Path to tfvars](images/code-editor-path.png)

    ```bash
    <copy>/leagueoflegends-optimizer/dev/terraform/terraform.tfvars</copy>
    ```

5. Type _[ENTER]_ to select, click on the `terraform.tfvars` file and click Open.

    ![TFVars Open](images/code-editor-open-tfvars.png)

6. The file will open and you can copy values you will get from running commands on Cloud Shell and paste it on the Code Editor.

7. Copy the output of the following command as the region:

    ```bash
    <copy>echo $OCI_REGION</copy>
    ```

    ![Paste Region](images/paste-region.png)

8. Copy the output of the following command as the tenancy OCID:

    ```bash
    <copy>echo $OCI_TENANCY</copy>
    ```

    ![Paste Tenancy OCID](images/paste-tenancy-ocid.png)

9. Copy the output of the same command as the compartment OCID:

    ```bash
    <copy>echo $OCI_TENANCY</copy>
    ```

    ![Paste Compartment OCID](images/paste-compartment-ocid.png)

    > **Note**: for experienced Oracle Cloud users:<br>
    > Do you want to deploy the infrastructure on a specific compartment?<br>
    > You can get the Compartment OCID in different ways.<br>
    > The coolest one is with OCI CLI from the Cloud Shell.<br>
    > You have to change _`COMPARTMENT_NAME`_ for the compartment name you are looking for and run the following command:

    ```bash
    <copy>
    oci iam compartment list --all --compartment-id-in-subtree true --query "data[].id" --name COMPARTMENT_NAME
    </copy>
    ```

10. Generate a SSH key pair, by default it will create a private key on _`~/.ssh/id_rsa`_ and a public key _`~/.ssh/id_rsa.pub`_.
    It will ask to enter the path, a passphrase and confirm again the passphrase; type _[ENTER]_ to continue all three times.

    ```bash
    <copy>ssh-keygen -t rsa</copy>
    ```

    > **Note**: If there isn't a public key already created, run the following command to create one:
    > ```
    > <copy>ssh-keygen</copy>
    > ```
    > And select all defaults. Then, try running the command again.

11. We need the public key in our notes, so keep the result of the content of the following command in your notes.

    ```bash
    <copy>cat ~/.ssh/id_rsa.pub</copy>
    ```

    ![Paste Public SSH Key](images/paste-public-ssh-key.png)

12. From the previous lab, you should have the Riot Developer API Key.

  ![Riot API Key](images/riot_api_key_gen.png)

  Paste the Riot API Key on the `riotgames_api_key` entry of the file.
  
  ![Paste Riot API Key](images/paste-riot-api-key.png)

13. Save the file.

    ![Code Editor Save](images/code-editor-save.png)

## Task 3: Start Deployment

1. Run the `start.sh` script

    ```bash
    <copy>./start.sh</copy>
    ```

2. The script will run and it looks like this.

    ![Start SH beginning](images/start-sh-beginning.png)

3. Terraform will create resources for you, and during the process it will look like this.

    ![Start SH terraform](images/start-sh-terraform.png)

4. Ansible will continue the work as part of the `start.sh` script. It looks like this.

    ![Start SH ansible](images/start-sh-ansible.png)

5. The final part of the script is to print the output of all the work done.

    ![Start SH output](images/start-sh-output.png)

6. Copy the ssh command from the output variable `compute`.

    ![Start SH output](images/start-sh-ssh.png)

## Task 4: Check Deployment

1. Run the `ssh` command from the output of the script. It will look like this.

    ```bash
    <copy>ssh opc@PUBLIC_IP</copy>
    ```

2. In the new machine, run the python script `check.py` that makes sure everything is working.

    ```bash
    <copy>python src/check.py</copy>
    ```

3. The result will confirm database connection and Riot API works.

    ![Python Check OK](images/python-check-ok.png)

4. If you get an error, make sure the _`terraform/terraform.tfvars`_ file from the previous task contains the correct values. In case of any error, just run the _`start.sh`_ script again.

## Task 5: Setting up Data Science Environment

Once we have set up our Cloud shell to extract data, we also need to prepare a Data Science environment to work with the data once it's been collected.
To achieve this, we need to load this workshop's notebook into our environment through the official repository.

We now need to load our notebook into our environment.

1. Opening a **Terminal** inside the _'Other'_ section the console and re-downloading the repository again:

    ![open terminal](./images/open_terminal.png)

2. Then, we re-clone the repository:

    ```bash
    <copy>
    git clone --branch livelabs https://github.com/oracle-devrel/leagueoflegends-optimizer.git
    </copy>
    ```

3. Install the conda environment specifying the Python version we want (you can choose between 3.8, 3.9 and 3.10)

    ```bash
    <copy>conda create -n myconda python=3.9</copy>
    ```

    ![proceed](./images/proceed.png)

4. Activate the newly-created conda environment:

    ```bash
    <copy>
    conda activate myconda
    </copy>
    ```

5. Install conda dependencies, so our environment shows up in the Kernel selector:

    ```bash
    <copy>
    conda install nb_conda_kernels
    </copy>
    ```

6. Install Python dependencies:

    ```bash
    <copy>
    pip install -r leagueoflegends-optimizer/deps/requirements_2023.txt
    </copy>
    ```

> Note: make sure to accept prompts by typing 'y' as in 'Yes' when asked.

After these commands, all requirements will be fulfilled and we're ready to execute our notebooks with our newly created conda environment.

Once we execute any notebook in this Data Science environment, remember that we'll need to select the correct conda environment under the _Kernel_ dropdown menu.

## Task 6: Downloading DataSets

We now need to load our datasets into our environment. For that, we reuse the terminal we created in the previous step:

![open terminal](./images/open_terminal.png)

Then, we execute the following command, which will download all necessary datasets:

```bash
<copy>
wget https://objectstorage.eu-frankfurt-1.oraclecloud.com/p/FcwFW-_ycli9z8O_3Jf8gHbc1Fr8HkG9-vnL4I7A07mENI60L8WIMGtG5cc8Qmuu/n/axywji1aljc2/b/league-hol-ocw-datasets/o/league_ocw_2023.zip && unzip league_ocw_2023.zip -d /home/datascience/.
</copy>
```

![unzip result](./images/unzip_result.png)

## Task 7: Accessing our Notebooks

We should now see the repository / files in our file explorer:

![file explorer - 1](./images/file_explorer.png)

We navigate to the _`leagueoflegends-optimizer/notebooks/`_ directory and the notebook [_`models_2023.ipynb`_](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/models_2023.ipynb) is the one we will review during this workshop.

![file explorer - 2](./images/file_explorer_2.png)

Let's open it. You may now [proceed to the next lab](#next).

## Acknowledgements

- **Author** - Nacho Martinez, Data Science Advocate @ DevRel
- **Contributors** - Victor Martin, Product Strategy Director
- **Last Updated By/Date** - May 31st, 2023
