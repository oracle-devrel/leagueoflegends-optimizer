# Infrastructure

## Introduction

In this lab we will build the infrastructure that we will use to run the rest of the workshop.

The main three elements that we will be creating are a Virtual Cloud Network which helps you define your own data center network topology inside the Oracle Cloud by defining some of the following components (Subnets, Route Tables, Security Lists, Gateways, etc.), Compute instance using an image from the Oracle Cloud based on Linux engien. And finally an Autonomous JSON Database where we will allocate the JSON documents.

Estimated Lab Time: xx minutes

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.


## Task 1: Create Virtual Cloud Network (VCN)

1. Login to Oracle cloud console: [cloud.oracle.com](https://cloud.oracle.com/)

    - Cloud Account Name: oci-tenant
    - **Next**

    ![cloud Account Name](./images/task1/cloud-account-name.png)

    - User Name: oci-username - email address provided
    - Password: oci-password
    - **Sign In**

    ![User Name & Password](./images/task1/username-password.png)

2. Click on main menu ≡, then Networking > **Virtual Cloud Networks**. Select your Region and Compartment assigned by the instructor. 

    >**Note**: Use **Root** Compartment, oci-tenant(root), to create all resources for this workshop.

    ![Oracle Console Networking](./images/task1/oracle-console-networking.png)

3. Select your Region and Compartment assigned by the instructor. Click **Start VCN Wizard**.

    ![Oracle Console Networking Start Wizard](./images/task1/oracle-console-networking-start-wizard.png)

4. Select **Create VCN with Internet Connectivity**. Start **VCN Wizard**.

   ![Create VCN with Internet Connectivity](./images/task1/create-vcn-with-internet-connectivity.png)

5. Provide the following information:

    - VCN Name:**LOLVCN**
    ```
    <copy>LOLVCN</copy>
    ```
    - Compartment: Be sure you have selected the correct one for this workshop purpose. **Root** is the recommended one
    - Click **Next**

    ![vcnName & Compartment](./images/task1/vcn-name-compartment.png)

6. Review the information in the 'Review and Create Page' and Click **Create**.

    ![vcn Creation](./images/task1/vcn-creation.png)

7. The Resources have being created on the next page. Click **View Virtual Cloud Network** to access to the vcn.

    ![View vcn Page](./images/task1/view-vcn-page.png)
    ![DEVCN Detail](./images/task1/lolvcn-detail.png)


## Task 2: Provision Compute Node for development

1. From the main menu on the top left corner select **Compute >> Instances**.

  ![OCI Console](./images/task2/compute.png)

2. In the compartment selector on the bottom left corner, select the same compartment where you created the VCN. **Root** is the recommended one. Click on the **Create Instance** blue button to create the compute instance.

  ![Compute Instance Dashboard](./images/task2/create-compute.png)

3. Fill the following information to create the compute instance:

    - Name:**LOL-COMPUTE**. This name will be used also as internal FQDN.
        ```
        <copy>LOL-COMPUTE</copy>
        ```

    - The **Placement** section is the section where you can change Availability Domain. For the scope of this workshop leave it as default.

        ![Compute Instance creation](./images/task2/create-compute-domain.png)

    - The **Image and shape** section is the section where you can change Image to be used, and Shape of resources. For the scope of this workshop leave everything as default.

        ![Compute instance creation](./images/task2/create-compute-shape.png)

    - The **Networking** section, check that your previously created **LOLVCN** is selected, and select your PUBLIC subnet **Public Subnet-LOLVCN(Regional)** from the dropdown menu. For the scope of this workshop leave the rest of options as default.

        ![Compute instance creation](./images/task2/create-compute-networking.png)

    - The **Add SSH Keys** section, make sure you **DOWNLOAD** the proposed private key. You will use it to connect to the compute instance later on. Once done, click **Create**.

        ![Compute instance creation](./images/task2/create-compute-create.png)


4. Wait for Compute Instance to finish provisioning, and have status Available (click browser Refresh button). On the Instance Details page, **copy Public IP Address** in your notes.

    ![Compute Provisioning](./images/task2/compute-provisioning.png)
    ![Compute Running](./images/task2/compute-running.png)

> Note: On the Instance Details page, copy **Public IP Address** in your notes.


## Task 3: Create an Autonomous Database

We'll also need to create an autonomous database. We'll use it as our storage for our generated datasets and access points as a whole.

1. **Click** on main menu ≡, then Oracle Database > **Autonomous JSON Database**. **Create Autonomous Database**.

    ![Oracle Console AJD](./images/task3/oracle-console-ajson.png)

2. Click **Create Autonomous Database**.

    ![Create AJD](./images/task3/create-ajson.png)

3. Provide the following information:

    - Comparment: Be sure you have selected the correct one for this workshop purpose. **Root** is the recommended one.
    - Display name: **LOL**
        ```
        <copy>LOL</copy>
        ```
    - Database name: **LOL**
        ```
        <copy>LOL</copy>
        ```
    - Choose a workload type: JSON
    - Choose a deployment type: Shared Infrastructure
    - Choose database version: 19c
    - OCPU count: 1
    - OCPU auto scaling: On
    - Storage (TB): 1 or 0.02 if you are using a Trial account
    - Storage auto scaling: Off

    ![Creation AJD Dashboard](./images/task3/creation-ajson-dashboard.png)

4. Under **Create administrator** credentials:

    - Password: Remember to take a note of this password as it is the one that we will use later on
    - Confirm Password

5. Under **Choose network access**:

    - Access Type: Secure access from everywhere

    ![Creation AJD Network](./images/task3/creation-ajson-network.png)

6. Under **Choose a license type**:

    - License included

    ![Creation AJD License](./images/task3/creation-ajson-license.png)

7. Click **Create Autonomous Database**.

    ![Creation AJD Create](./images/task3/creation-ajson-create.png)

8. Wait for Lifecycle State to become **Available** from Provisioning (click browser Refresh button).

    ![AJD Provisioning](./images/task3/ajson-provisioning.png)
    ![AJD Available](./images/task3/ajson-available.png)

9. Next to the big green box, click **DB Connection**.

    ![AJD DB Connection](./images/task3/ajson-db-connection.png)

10. Click **Download wallet**.

    ![Download Wallet](./images/task3/download-wallet.png)

11. Type the following information:

    - Password: Type the password that we created previously
    - Confirm Password: Confirm the password that we created previously
    - Click **Download**

    ![Download Wallet Password](./images/task3/download-wallet-password.png)

12. Click **Save file** and **OK**.

13. We will modify a couple of network settings to allow us to connect using TLS instead of m-TLS (mutual TLS). Long story short, using TLS instead of mTLS will make the task of connecting to the database easier (and additionally, it makes it possible to connect and use the __python-oracledb__ thin client if we want to, instead of only using the Thick client).

    > **Note**: Activating TLS as the authentication mechanism doesn't restrict us from connecting using mTLS still, it just expands our possibilities of connecting
    > mTLS will use port 1522 by default and TLS will use port 1521. If you're in a machine with firewall activated, make sure that in/egress firewall rules are suited for those ports.

14. Go to the Autonomous JSON Home Page, Network section and click **edit** in the **Access Control List: Disabled** menu.

    ![AJD Available](./images/task3/ajson-network.png)

15. Modify the **Access Control List (ACL)** to allow our own IP address to connect to the database (or whichever IP you want). Add the most unrestrictive CIDR block, so that anyone can make a request with the proper username/password/connection string, by adding the CIDR block 0.0.0.0/0 (all IPs):
    - IP notation type: Select **CIDR Block**
    - Values: **0.0.0.0/0**
        ```
        <copy>0.0.0.0/0</copy>
        ```
    - **Save Changes**
    ![Access Control List Menu](images/task3/access-control-list.png)

16. Disable the parameter that `requires` us to connect through mTLS, and make TLS authentication also possible. Go to the Autonomous JSON Home Page, Network section and click **edit** in the **Mutual TLS (mTLS) Authentication: Required** menu.

    - Require mutual TLS (mTLS) authentication: **Enable**
    - **Save Changes**

    ![AJD Available](./images/task3/ajson-network-mtls.png)
    ![Disable mTLS menu](./images/task3/mtls.png)

17. Once the database has finished updating, we can copy the database connection strings. Click **DB Connection** once more.

    ![AJD DB Connection](./images/task3/ajson-db-connection.png)

18. Go to the **Connection Strings** section. You can use any of the connection strings available, just note that the __tpurgent__ connection strings supports parallel calls and many more operations per second compared to all other connection strings. It's reserved for urgent operations, but since we're the only ones who are going to use the database, and just for this use case, let's not worry about prioritizing our tasks for now.

    ![AJD DB Connection](./images/task3/lol-tpurgnet-connection-string.png)

    > Note: We want our TLS connection strings (not mTLS connection strings) as they are different.

19. Take a note of the connection string, we will need to add this to our configuration file later on. An example connection string would be:

    ```bash
    (description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=XXXXXXXXXXXX))(connect_data=(service_name=XXXXXXXXXXXXXXXX))(security=(ssl_server_dn_match=yes)(ssl_server_cert_dn="CN=XXXXXXXXXXXXX, OU=XXXXX, O=XXXXX XXXXXX, L=Redwood XXXXX, ST=XXXX, C=XXXX")))
    ```

//////

## Task 4: Install Instant Client and Upload Wallet

As we're going to want to connect to our newly created Autonomous Database, we also need to consider the supporting Oracle packages required to support this connection. This is facilitated by Oracle Instant Client, which we'll need to install. 

1. Depending on the Operating System where you are, you'll need to download your respective binary files from [this link](https://www.oracle.com/database/technologies/instant-client/downloads.html). After installing Instant Client, we'll need to unzip the file into a directory (and remember the directory in which we put the unzipped file, we'll need to use it as a configuration parameter).

2. In the end, your installation should look something like this:
    ![instant client](images/lab1-instantclient.png)

3. And, in my case, my path to my instant client installation would be:
    ```bash
    D:\Programs\instantclient
    ```

4. Which is what we'll use in our configuration file.
5. After setting up the Autonomous Database, we need to download the client credentials (required by design for mTLS connections).
6. After downloading it, we'll copy all the contents that we found inside our Instant Client installation folder.
7. Recalling the directory:
    ```bash
    D:\Programs\instantclient
    ```

8. So, in my case, I'd paste the contents of the wallet into:
    ```bash
    D:\Programs\instantclient\network\admin\
    ```

9. Finally, I'll modify the contents of **sqlnet.ora** to make sure that the Python thick client can find the files it needs to connect through mTLS. 
10. By default, the file has these contents:
    ```bash
    WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="?/network/admin")))
    SSL_SERVER_DN_MATCH=yes
    ```

11. I'll replace this with the specified directory where my wallet has been placed, and leave no place for error:
    ```bash
    WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="D:/Programs/instantclient/network/admin")))
    SSL_SERVER_DN_MATCH=yes
    ```

You may now [proceed to the next lab](#next).

## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** -