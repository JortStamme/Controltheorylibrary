# docs/source/manim_gallery.py
from pathlib import Path
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util import logging
import subprocess
import os
import shutil
import re 
import glob 
import time
import tempfile

logger = logging.getLogger(__name__)

# Get the directory of the currently executing script (manim_gallery.py)
SOURCE_DIR = Path(__file__).parent

def robust_rmtree(path, max_attempts=5, delay_seconds=0.5):
    """
    Attempts to remove a directory tree, retrying on PermissionError.
    This is a common issue on Windows where files remain locked briefly.
    """
    if not path.exists():
        return
        
    for attempt in range(max_attempts):
        try:
            shutil.rmtree(path)
            print(f"Successfully removed directory: {path}")
            return
        except PermissionError as e:
            print(f"DEBUG: Attempt {attempt + 1}/{max_attempts}: PermissionError on {path}. Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)
        except OSError as e:
            print(f"DEBUG: Attempt {attempt + 1}/{max_attempts}: OSError on {path}. Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)
    
    print(f"ERROR: Failed to remove directory after {max_attempts} attempts: {path}")
    print(f"ERROR: The directory or a file within it might be in use by another program.")
    raise # Re-raise the exception if all attempts fail

class ManimExampleDirective(Directive):
    """
    A Sphinx directive to display a Manim code snippet and its corresponding video or image.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    
    def run(self):
        example_name = self.arguments[0]
        code_content = '\n'.join(self.content)
        
        return self.create_example_node(code_content, example_name)
    
    def create_example_node(self, code_content, example_name):
        container = nodes.container()
        container['classes'] = ['manim-example']
        
        title = nodes.paragraph()
        title += nodes.strong(text=f"Example: {example_name}")
        container += title
        
        media_col = nodes.container()
        media_col['classes'] = ['sd-col-12']
        
        # Determine the scene name from the code
        match = re.search(r"class (\w+)\(Scene\):", code_content)
        if match:
            scene_name = match.group(1)
        else:
            scene_name = example_name
            print(f"WARNING: Could not find a Manim scene class in the code for example '{example_name}'. Falling back to using the example name as the scene name.")

        found_media_path = None
        
        # Define final paths for both video and image
        final_media_dir = SOURCE_DIR / '_static' / 'examples'
        final_video_path = final_media_dir / f'{example_name}.mp4'
        final_image_path = final_media_dir / f'{example_name}.png' # Assuming .png for static images
        
        # Check if the final media already exists
        if final_video_path.exists():
            found_media_path = final_video_path
            print(f"DEBUG: Found existing video at {found_media_path}")
        elif final_image_path.exists():
            found_media_path = final_image_path
            print(f"DEBUG: Found existing image at {found_media_path}")
        else:
            print(f"DEBUG: Media NOT found, attempting to generate with Manim.")
            manim_path = shutil.which("manim")
            if not manim_path:
                print("ERROR: Manim executable not found in PATH.")
                pass
            else:
                with open(SOURCE_DIR / f'temp_{example_name}.py', 'w') as f:
                    f.write(f"from manim import *\n\n{code_content}")
                
                project_root = SOURCE_DIR.parent.parent
                env = os.environ.copy()
                if 'PYTHONPATH' in env:
                    env['PYTHONPATH'] = f"{project_root}{os.pathsep}{env['PYTHONPATH']}"
                else:
                    env['PYTHONPATH'] = str(project_root)
                    
                # Use a temporary directory for Manim output
                with tempfile.TemporaryDirectory() as temp_dir_str:
                    temp_dir = Path(temp_dir_str)
                    
                    temp_output_file = temp_dir / f'{scene_name}.mp4'
                    
                    try:
                        command = [
                            manim_path,
                            "-ql",
                            str(SOURCE_DIR / f'temp_{example_name}.py'),
                            scene_name,
                            "--output_file",
                            str(temp_output_file),
                            "--renderer",
                            "opengl"
                        ]
                        print(f"DEBUG: Running command: {' '.join(command)}")
                        
                        result = subprocess.run(command, check=True, env=env, capture_output=True, text=True, cwd=SOURCE_DIR)
                        print("Manim STDOUT:")
                        print(result.stdout)
                        print("Manim STDERR:")
                        print(result.stderr)

                        # Check if a video was generated and move it
                        if temp_output_file.exists():
                            final_video_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(temp_output_file, final_video_path)
                            found_media_path = final_video_path
                            print(f"DEBUG: Video successfully generated and moved to {found_media_path}")
                        else:
                             print(f"ERROR: Video was not generated in the temporary directory.")
                             # If video generation fails, let's try to find a static image
                             temp_image_search_pattern = str(temp_dir / '**' / f'{scene_name}.png')
                             temp_image_paths = glob.glob(temp_image_search_pattern, recursive=True)
                             if temp_image_paths:
                                 temp_image_path = Path(temp_image_paths[0])
                                 final_image_path.parent.mkdir(parents=True, exist_ok=True)
                                 shutil.move(temp_image_path, final_image_path)
                                 found_media_path = final_image_path
                                 print(f"DEBUG: Image successfully generated and moved to {found_media_path}")

                    except subprocess.CalledProcessError as e:
                        print(f"ERROR: Manim subprocess failed: {e}")
                        print("Manim STDOUT (from error):")
                        print(e.stdout)
                        print("Manim STDERR (from error):")
                        print(e.stderr)
                    finally:
                        if (SOURCE_DIR / f'temp_{example_name}.py').exists():
                            os.remove(SOURCE_DIR / f'temp_{example_name}.py')
        
        if found_media_path:
            relative_path = os.path.relpath(found_media_path, SOURCE_DIR / '_static')
            web_path = f"_static/{relative_path.replace(os.path.sep, '/')}"
            
            if found_media_path.suffix == '.mp4':
                media_html = f'''
                <div class="manim-video-container">
                    <video controls width="100%" style="border-radius: 5px;">
                        <source src="{web_path}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                '''
            elif found_media_path.suffix == '.png':
                media_html = f'''
                <div class="manim-image-container">
                    <img src="{web_path}" alt="{example_name} Manim output" style="width: 100%; border-radius: 5px;">
                </div>
                '''
            print(f"DEBUG: Using web path: {web_path}")
        else:
            media_html = f'''
            <div class="manim-media-placeholder">
                <p style="color: #666; font-style: italic;">
                    Media not found.<br>
                    Manim command might have failed or not generated a video/image in the expected location.<br>
                    Please check the build log for any error messages.
                </p>
            </div>
            '''
            print(f"DEBUG: Final media NOT found.")

        media_node = nodes.raw('', media_html, format='html')
        media_col += media_node
        
        code_col = nodes.container()
        code_col['classes'] = ['sd-col-12']
        
        code_block = nodes.literal_block(code_content, code_content)
        code_block['language'] = 'python'
        code_col += code_block
        
        container += media_col
        container += code_col
        
        return [container]
