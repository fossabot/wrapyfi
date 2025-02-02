import setuptools


def check_cv2(default_python="opencv-python"):
    UPGRADE_CV2 = False
    REQUIRED_CV2_VERSION = "4.2.0"
    try:
        import pkg_resources
        from packaging import version
        import cv2
        if version.parse(cv2.__version__) < version.parse(REQUIRED_CV2_VERSION):
            UPGRADE_CV2 = True
            raise ImportError(f"OpenCV version must be at least {REQUIRED_CV2_VERSION}")
    except ImportError as e:
        import pkg_resources
        if UPGRADE_CV2:
            print(e, "Will try to upgrade OpenCV")
            if "opencv-python" in [p.project_name for p in pkg_resources.working_set]:
                additional_packages = [f"opencv-python>={REQUIRED_CV2_VERSION}"]
            elif "opencv-contrib-python" in [p.project_name for p in pkg_resources.working_set]:
                additional_packages = [f"opencv-contrib-python>={REQUIRED_CV2_VERSION}"]
            elif "opencv-python-headless" in [p.project_name for p in pkg_resources.working_set]:
                additional_packages = [f"opencv-python-headless>={REQUIRED_CV2_VERSION}"]
            else:
                raise ImportError(f"Unknown OpenCV package installed. Please upgrade manually to version >={REQUIRED_CV2_VERSION}")
        else:
            print(f"OpenCV not found. Will try to install {default_python}")
            additional_packages = [f"{default_python}>={REQUIRED_CV2_VERSION}"]
    else:
        print("OpenCV found. Will not install it")
        additional_packages = []
    return additional_packages


setuptools.setup(
    name             = 'wrapyfi',
    version          = '0.4.31',
    description      = 'Wrapyfi is a wrapper for simplifying Middleware communication',
    url              = 'https://github.com/fabawi/wrapyfi/blob/main/',
    project_urls={
        'Documentation': 'https://wrapyfi.readthedocs.io/en/latest/',
        'Source':        'https://github.com/fabawi/wrapyfi/',
        'Tracker':       'https://github.com/fabawi/wrapyfi/issues',
    },
    author           = 'Fares Abawi',
    author_email     = 'f.abawi@outlook.com',
    maintainer       = 'Fares Abawi',
    maintainer_email = 'f.abawi@outlook.com',
    packages         = setuptools.find_packages(),
    extras_require   ={'docs': ['sphinx', 'sphinx_rtd_theme', 'myst_parser'], 
                       'pyzmq': ['pyzmq>=19.0.0'],
                       'numpy': ['numpy>=1.19.2'],
                       'headless': ['wrapyfi[pyzmq]', 'wrapyfi[numpy]'] + check_cv2("opencv-python-headless"),
                       'all': ['wrapyfi[pyzmq]', 'wrapyfi[numpy]'] + check_cv2("opencv-contrib-python")},
    install_requires = ['pyyaml>=5.1.1'],
    python_requires  = '>=3.6',
    setup_requires   = ['cython>=0.29.1']
)
