Installation
============

Mizuki works best with Python 3.13 or higher. Any version older than 3.13 will not be supported.

You can install the library from PyPI by doing:

.. code-block:: bash
    
    pip install mizuki
  
      
Managing Virtual Environments
-----------------------------

Using Virtual Environments or venvs are heavily recommended as they allow you to keep your project's dependencies separate from the system-wide installed packages.

``uv`` is a great tool for managing Virtual Environments and dependencies and is recommended over base ``venv`` commands.

Guide for installing uv: `Click Here! <https://docs.astral.sh/uv/>`_

.. note::
    
    ``venv`` is usually a builtin python module. However, on specific linux distributions it may be separated into a different package. If the command is unavailable, refer to your distribution's Python packaging documentation.
    
Setting up:
    
.. tab-set::
    :class: outline
    
    .. tab-item:: :iconify:`material-icon-theme:uv` uv
        
        .. code-block:: bash
        
            uv init
        
        This initializes your project and adds pyproject.toml, README.md, main.py.
        
        .. code-block:: bash
        
            uv add mizuki
        
        This creates a Virtual Environment and adds mizuki as one of its dependencies as well as install it.
        
    .. tab-item:: :iconify:`vscode-icons:file-type-python` venv
    
        .. code-block:: bash
        
            python -m venv .venv
            
        This creates a Virtual Environment at the folder .venv.
        
        After activating the venv (see below),
        
        .. code-block:: bash
        
            pip install mizuki
            
Activating venv:
    
.. tab-set::
    :class: outline
    
    .. tab-item:: Linux/Mac
    
        .. code-block:: bash
            
            source .venv/bin/activate
            
    .. tab-item:: Windows
    
        .. code-block:: bat
        
            .venv\Scripts\activate.bat
            

Now, doing ``python`` in your terminal will use the Virtual Environment we just created.

Congratulations! You have set up your Dev Environment.