# Infrastructure

## Introduction

In this lab we will build the infrastructure that we will use to run the rest of the workshop.

The main four elements that we will be creating are:
- **Compute** instance using a Linux-based image from Oracle Cloud.
- **Autonomous JSON Database** where we'll allocate the JSON documents.
- **Data Science** session and notebook, to experiment with the newly-generated data using notebooks.

![Infrastructure](images/lol_infra.png)

We will use Cloud Shell to execute `start.sh` script that will call Terraform and Ansible to deploy all the infrastructure required and setup the configuration. If you don't know about Terraform or Ansible, don't worry, there is no need.

Terraform is an Open Source tool to deploy resources in the cloud with code. You declare what you want in Oracle Cloud and Terraform make sure you get the resources created.

Ansible is an Open Source tool to provision on top of the created resources. It automates the dependency installation, copy the source code, and config files so everything is ready for you to use.

Do you want to learn more? Fill free to check the code for terraform and ansible after the workshop.

Estimated Lab Time: xx minutes

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
3. The result will look like this
  ![Git Clone](images/git-clone.png)
4. Change directory with `cd` to `leagueoflegends-optimizer` directory:
    ```
    <copy>cd leagueoflegends-optimizer</copy>
    ```

## Task 2: Deploy with Terraform and Ansible

1. Change directory with `cd` to `dev` where all the Terraform and Ansible code lives.
    ```
    <copy>cd dev</copy>
    ```
2. You will extract some data needed to set up Terraform, make sure you take notes of the information.
3. Copy the output of the following command as the tenancy OCID:
    ```
    <copy>echo $OCI_TENANCY</copy>
    ```
4. Copy the output of the following command as the compartment OCID:
    ```
    <copy>echo $OCI_TENANCY</copy>
    ```

    > **Note only for experienced Oracle Cloud users:**<br>
    > Do you want to deploy the infrastructure on a specific compartment?<br>
    > You can get the Compartment OCID in different ways.<br>
    > The coolest one is with OCI CLI from the Cloud Shell.<br>
    > You have to change _`COMPARTMENT_NAME`_ for the compartment name you are looking for and run the command:
    ```
    <copy>oci iam compartment list --all --compartment-id-in-subtree true --query "data[].id" --name COMPARTMENT_NAME</copy>
    ```
5. Generate a SSH key pair, by default it will create a private key on _`~/.ssh/id_rsa`_ and a public key _`~/.ssh/id_rsa.pub`_.
    ```
    <copy>ssh-keygen -t rsa</copy>
    ```
6. We need the public key in our notes, so keep the result of the content of the following command in your notes.
    ```
    <copy>cat ~/.ssh/id_rsa.pub</copy>
    ```
7. From the previous lab, you should have the Riot Developer API Key. Keep it on your notes as well.
  ![Riot API Key](images/riot_api_key_gen.png)
8. Create a copy of the terraform variables file by running the following command.
    ```
    <copy>cp terraform/terraform.tfvars.template terraform/terraform.tfvars</copy>
    ```
9. Edit the values with `vim` or `nano` with your tenancy, compartment, ssh public key and Riot API key.
    ```
    <copy>vim terraform/terraform.tfvars</copy>
    ```
    ![Vim TF vars](images/vim-edit-tfvars.png)
10. After editing the file it should look like this.
    ![Vim TF vars edited](images/vim-edit-tfvars-edit.png)
11. Save the file and confirm the values are correct.
    ```
    <copy>cat terraform/terraform.tfvars</copy>
    ```

## Task 3: Start deployment

1. Run the `start.sh` script
    ```
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

## Task 3: Check deployment

1. Run the `ssh` command from the output of the script. It will look like this.
    ```
    <copy>ssh opc@PUBLIC_IP</copy>
    ```
2. In the new machine, run the python script `check.py` that makes sure everything is working.
    ```
    <copy>python src/check.py</copy>
    ```
3. The result will confirm database connection and Riot API works.
    ![Python Check OK](images/python-check-ok.png)
4. If you get an error, make sure the `terraform/terraform.tfvars` file from the previous task contains the correct values. In case of any error, just run the `start.sh` script again.


You may now [proceed to the next lab](#next).

## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** - Victor Martin, Product Strategy Director
* **Last Updated By/Date** - July 29th, 2022