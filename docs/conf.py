import sys
import os
import re


def get_project_info_from_setup():
    curr_dir = os.path.dirname(__file__)
    setup_path = os.path.join(curr_dir, '..', 'setup.py')
    with open(setup_path, 'r') as f:
        content = f.read()
    
    name_match = re.search(r"name\s*=\s*['\"]([^'\"]*)['\"]", content)
    version_match = re.search(r"version\s*=\s*['\"]([^'\"]*)['\"]", content)
    url_match = re.search(r"url\s*=\s*['\"]([^'\"]*)['\"]", content)
    
    if not name_match or not version_match or not url_match:
        raise RuntimeError("Unable to find name, version, or url string.")
        
    return {
        'name': name_match.group(1),
        'version': version_match.group(1),
        'url': url_match.group(1)
    }


def setup(app):
    app.add_css_file('wide_theme.css')

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static'] 
html_css_files = ['wide_theme.css'] 

extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc', 'myst_parser', 'link_modifier']
# run from within an environment that has all requirements installed besides ROS2
autodoc_mock_imports = ["rclpy", "rclpy.node", "Parameter", "Node"]
source_suffix = ['.rst', '.md']
exclude_patterns = ["_build"]
# autodoc_mock_imports = ["rclpy", "rospy", "yarp", "cv2", "numpy", "yaml",
#                         "torch", "pandas", "tensorflow", "jax", "jaxlib", "mxnet", "paddle"]
# extract project info
project_info = get_project_info_from_setup()

project = project_info['name']
release = project_info['version']
version = '.'.join(release.split('.')[:2])
url = project_info['url']

# modify the latex cover page for pdf generation
latex_elements = {
    'preamble': r'''
\usepackage{titling}
\pretitle{%
  \begin{center}
  \vspace{\droptitle}
  \includegraphics[width=60mm]{../resources/wrapyfi.png}\\[\bigskipamount]
  \Large{\textbf{''' + project + '''}}\\
  \normalsize{v''' + release + '''}
}
\posttitle{\end{center}}
'''
}

sys.path.insert(0, os.path.abspath('../'))
sys.path.append(os.path.abspath('./_extensions'))
