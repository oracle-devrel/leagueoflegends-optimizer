Development
==========

This section covers development guidelines and processes for the League of Legends Optimizer.

Setting Up the Development Environment
------------------------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
      cd leagueoflegends-optimizer

2. Install dependencies with Poetry:

   .. code-block:: bash

      poetry install

3. Activate the virtual environment:

   .. code-block:: bash

      poetry shell

4. Create a ``config.yaml`` file with your Riot API key.

Code Style
---------

The League of Legends Optimizer follows these code style guidelines:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting
- **mypy**: For static type checking

You can run these tools with the following commands:

.. code-block:: bash

    # Format code with Black
    black leagueoptimizer

    # Sort imports with isort
    isort leagueoptimizer

    # Lint with flake8
    flake8 leagueoptimizer

    # Type check with mypy
    mypy leagueoptimizer

Running Tests
-----------

Run the tests with pytest:

.. code-block:: bash

    # Run all tests
    pytest

    # Run with coverage report
    pytest --cov=leagueoptimizer

    # Run specific test file
    pytest leagueoptimizer/tests/test_config.py

    # Run tests with specific marker
    pytest -m unit

Building Documentation
-------------------

The documentation is built using Sphinx. To build the documentation locally:

1. Install the documentation dependencies:

   .. code-block:: bash

      poetry install --with docs

2. Build the documentation:

   .. code-block:: bash

      cd docs
      make html

3. View the documentation:

   .. code-block:: bash

      # On Linux/macOS
      open build/html/index.html

      # On Windows
      start build/html/index.html

Publishing Documentation to ReadTheDocs
-------------------------------------

The documentation is hosted on `Read the Docs <https://readthedocs.org/>`_. To publish the documentation:

1. Create an account on ReadTheDocs if you don't have one.

2. Import your GitHub repository:

   a. Go to your `ReadTheDocs dashboard <https://readthedocs.org/dashboard/>`_.
   b. Click "Import a Project".
   c. Click "Import Manually".
   d. Fill in the project details:
      - Name: ``leagueoflegends-optimizer``
      - Repository URL: ``https://github.com/oracle-devrel/leagueoflegends-optimizer.git``
      - Repository type: ``Git``
   e. Click "Next".
   f. On the next page, click "Build version".

3. Configure the project:

   a. Go to the "Admin" tab of your project.
   b. Under "Advanced Settings", make sure "Install Project" is checked.
   c. Under "Documentation Type", select "Sphinx".
   d. Click "Save".

4. Trigger a build:

   a. Go to the "Builds" tab.
   b. Click "Build version".

5. View your documentation:

   a. Once the build is complete, click "View docs" to see your published documentation.

Automatic Builds
~~~~~~~~~~~~~~

ReadTheDocs will automatically build your documentation when you push changes to your repository. You can configure this behavior in the "Admin" tab of your project.

Custom Domain
~~~~~~~~~~~

You can configure a custom domain for your documentation:

1. Go to the "Admin" tab of your project.
2. Under "Domains", click "Add Domain".
3. Enter your domain name and click "Add".
4. Follow the instructions to configure your DNS settings.

Versioning
~~~~~~~~~

You can create different versions of your documentation:

1. Create a new branch or tag in your repository.
2. Go to the "Versions" tab of your project.
3. Activate the branch or tag.
4. ReadTheDocs will build the documentation for that version.

Pull Request Process
------------------

1. Fork the repository and create a new branch for your feature or bug fix.
2. Make your changes, following the code style guidelines.
3. Add tests for your changes.
4. Run the tests to ensure they pass.
5. Update the documentation if necessary.
6. Submit a pull request with a clear description of the changes.

Commit Message Guidelines
-----------------------

Please follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Release Process
-------------

1. Update the version number in ``pyproject.toml``.
2. Update the changelog in ``CHANGELOG.md``.
3. Create a new release on GitHub with release notes.
4. Publish the package to PyPI:

   .. code-block:: bash

      poetry build
      poetry publish 