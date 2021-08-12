from asyncio.subprocess import Process
import subprocess
import logging
import sys, os, glob, asyncio

from subprocess import Popen, PIPE, STDOUT
import re
import svg_stack
import time


logging.basicConfig(filename='colortrace.log', level=logging.DEBUG)

#asynchronus implementation of color_trace.py 
class color_trace_dir():
       
    def __init__(self):
        logging.info('ColorTrace initializations details:')
        logging.info(f'Subprocess check: {subprocess.__file__}')
        logging.info(f'Directory: {os.getcwd()}')
        logging.info(f'Arguements {sys.argv[0]}{sys.argv[1]}{sys.argv[2]}{sys.argv[3]}{sys.argv[4]}')
        self.PNGNQ_PATH = '/usr/bin/pngnq'
        self.cwd = os.getcwd()
        self.IMAGEMAGICK_CONVERT_PATH = '/usr/bin/convert'
        self.IMAGEMAGICK_MOGRIFY_PATH = '/usr/bin/mogrify'
        #Need to grab trace.cpp from inkscape official gitlab
        self.POTRACE_PATH = '/usr/bin/potrace'
        
        self.srcdir = sys.argv[1]
        self.destdir = sys.argv[4]
        self.numcolors = sys.argv[3]
        logging.info(f'IMAGEMAGICK CONVERT PATH: {self.IMAGEMAGICK_CONVERT_PATH}')
        logging.info(f'IMAGEMAGICK MOGRIFY PATH: {self.IMAGEMAGICK_MOGRIFY_PATH}')

        success = False
        '''trace all images in srcdir to numcolors, output SVGs to destdir'''


    async def quantize(self, src, dest_palette, numcolors, destdir, ext="~quant.png"):
        
        do_quantize = { "build_pngnq" : 'sudo "{pngnq}" -f -d "{destdir}" -n {colors} -e {ext} "{src}"'.format(pngnq = self.PNGNQ_PATH, destdir=destdir, colors=numcolors, ext=ext, src=src)        }
        try:
            for k in do_quantize:
                #print("Current task:            \n" + str(do_quantize[k]))
                init_quantize = await asyncio.create_subprocess_shell(str(do_quantize[k]), 
                                                                                stdout=asyncio.subprocess.PIPE, 
                                                                                stderr=asyncio.subprocess.PIPE,
                                                                                shell=True
                                                                            )
                stdout, stderr = await init_quantize.communicate()
                #print(f'[{str(init_quantize[k])!r} exited with {str(init_quantize.returncode)}]')
                if stdout:
                    logging.info(f'[stdout]\n{stdout.decode()}')
                    print(f'[stdout]\n{stdout.decode()}')
                if stderr:
                    logging.info(f'[stderr]\n{stderr.decode()}')
                    quantize_attempt= False
                    sys.exit(1)
                quantized = os.path.splitext(src)[0] + ext
                quantized = os.path.join(destdir, os.path.basename(quantized))
            build_pallet = {
            "build_imagemagick pallete" : '"{convert}" "{palette_src}" -unique-colors -compress none "{palette_dest}"'.format(convert = self.IMAGEMAGICK_CONVERT_PATH, palette_src=quantized, palette_dest=dest_palette)
            }
            for k in build_pallet:
                #print(build_pallet[k])
                try:
                    #print("Current task:            \n" + str(build_pallet[k]))
                    init_pallet = await asyncio.create_subprocess_shell(str(build_pallet[k]), 
                                                                                stdout=asyncio.subprocess.PIPE, 
                                                                                stderr=asyncio.subprocess.PIPE,
                                                                                )
                    stdout, stderr = await init_pallet.communicate()
                    #print(f'[{str(init_pallet[k])!r} exited with {str(init_pallet.returncode)}]')
                    if stdout:
                        logging.info(f'[stdout]\n{stdout.decode()}')

                    if stderr:
                        logging.info(f'[stdout]\n{stderr.decode()}')
                        
                except Exception as e:
                    logging.info(e)
                    print(e)
                    sys.exit(1)

        except Exception as e:
            logging.info(e)
            sys.exit(1)


    async def get_nonpalette_color(self, palette, start_black=True, additional=None):
        '''return a color hex string not in palette

        additional: if specified, a list of additional colors to avoid returning'''
        if additional is None:
            palette_ = palette
        else:
            palette_ = palette + list(additional)
        if start_black:
            color_range = range(int('ffffff', 16))
        else:
            color_range = range(int('ffffff', 16), 0, -1)
        for i in color_range:
            color = "#{0:06x}".format(i)
            if color not in palette_:
                return color

    async def trace_dir(self):
        trace_dir_attempt = False
        destdir = sys.argv[4]
        tmp_palette = os.path.join(self.destdir, "~palette.ppm")
        tmp_quant   = "{0}~quant.png"
        tmp_layer   = "{0}~layer.ppm"
        tmp_trace   = "{0}~trace.svg"
        out_dest    = "{0}.svg"
        print('we arwe here 1')
        os.system('echo $PWD')
        logging.info('Checking Prerequisites...')
        try:
            #Check prereqs
            if os.path.exists(self.srcdir) and os.walk(self.srcdir).__sizeof__ == 0:
                logging.info('files not found')
                raise FileNotFoundError

            elif not os.path.exists(self.destdir):
                logging.info("Problem with dest directory")
                logging.info('Creating new destination directory...')
                os.makedirs(self.destdir)

        except FileNotFoundError:
            logging.info('There is no file in the starting directory',FileNotFoundError)
            sys.exit(0)

        
        filenames = list(glob.glob(os.path.join(self.srcdir, "*")))

        logging.info('Prerequisites checkout: Initializing async operations')
        for fname in filenames:
            try:
                # temporary and destination file paths
                rootname = os.path.basename(os.path.splitext(fname)[0])
                tmp_thisquant = os.path.join(destdir, tmp_quant.format(rootname))
                tmp_thislayer = os.path.join(destdir, tmp_layer.format(rootname))
                tmp_thistrace = os.path.join(destdir, tmp_trace.format(rootname))
                out_thisdest  = os.path.join(destdir, out_dest.format(rootname))

                quantize_attempt = await self.quantize(fname,tmp_palette, self.numcolors, destdir)
                print('we arwe here 12')
                logging.info(quantize_attempt)
                try:
                    print("its either self.tmp.pallete or self.src" + tmp_palette)
                    with open(tmp_palette, 'rt') as file:
                        # skip to 4th line and get color values
                        file.readline()
                        file.readline()
                        file.readline()
                        colorvals = []
                        for line in file:
                            colorvals.extend([int(s) for s in line.split()])
                    irange = range(0, len(colorvals), 3)
                    jrange = range(3, len(colorvals)+1, 3)
                    self.colors = []
                    for i,j in zip(irange,jrange):
                        self.colors.append(tuple(colorvals[i:j]))
                    
                    '''Turns list of 3-tuple colors to #rrggbb hex strings

                    For use as imagemagick & potrace arguments.'''
                    hex_strs = []
                    for r,g,b in self.colors:
                        hex_strs.append("#{0:02x}{1:02x}{2:02x}".format(r,g,b))
                    hex_strs.reverse() #so it will go from light to dark
                    print(self.colors)
                    print(hex_strs)
                    
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    logging.info(e)
                    sys.exit(1)

                    
                for i, color in enumerate(hex_strs):
                    print(i,color)
                    stacked=False
                    print(i)
                    #isolate_color(tmp_thisquant, tmp_thislayer, i, palette, stacked=True)
                    #src, destination, outcolor
                    #trace(tmp_thislayer, tmp_thistrace, color)
                    """
                    fills the specified color of src with black, all else is white

                    src: source image path. had better be quantized and match palette or else
                    coloridx: index of the specified color from palette
                    palette: list of #010101 etc. output from hex_colors_str
                    dest: path to save output image
                    stacked: if True, colors before coloridx are white, colors after are black
                    """
                    #Isolate the Color and trace
                    # copy src to dest (it will be edited in-place)
                    #print('made it this far' + tmp_thisquant)
                    #isolate_color(tmp_thisquant, tmp_thislayer, i, palette, stacked=True)

                    with open(tmp_thisquant, 'rb') as srcfile, open(tmp_thislayer, 'wb') as destfile:
                        destfile.write(srcfile.read())
                    #print(hex_strs)
                    background = await self.get_nonpalette_color(hex_strs, False, ["#000000", "#FFFFFF"])
                    foreground = await self.get_nonpalette_color(hex_strs, True, [background, "#000000", "#FFFFFF"])
                    for z, col in enumerate(hex_strs):
                        # fill this color with background or foreground?
                        

                        if z == i:
                            fill = foreground
                        elif z > i:
                            fill = foreground and stacked
                        else:
                            fill = background
                        
                    # isolate & trace for this color
                        #define isolate_logic
                        do_isolate_color = {
                            
                            "build_imagemagick" : '"{mogrify}" -fill {fill} -opaque "{color}" "{dest}"'.format(mogrify = self.IMAGEMAGICK_MOGRIFY_PATH, fill=fill, color=col, dest=tmp_thislayer),
                        }
                        for k in do_isolate_color:
                            print(z, i, col, fill)
                            #print("Current task:            \n" + str(do_isolate_color[k]))
                            init_isolate = await asyncio.create_subprocess_shell(str(do_isolate_color[k]), 
                                                                                        stdout=asyncio.subprocess.PIPE, 
                                                                                        stderr=asyncio.subprocess.PIPE,
                                                                                        shell=True
                                                                                        )
                            stdout, stderr = await init_isolate.communicate()
                            #print(f'[{str(do_isolate_color[k])!r} exited with {str(init_isolate.returncode)}]')
                            if stdout:
                                logging.info(f'[stdout]\n{stdout.decode()}')
                                #Do trace#src, destination, outcolor
                            if stderr:
                                print(fill)
                                print(k)
                                logging.info(f'[stderr]\n{stderr.decode()}')
                        #src, dest, outcolor
                        #tmp_thislayer, tmp_thistrace, color
                        do_trace = {
                            "color_forground_black_bk_white" : '"{mogrify}" -fill {fillbg} -opaque "{colorbg}" -fill {fillfg} -opaque {colorfg} "{dest}"'.format(mogrify = self.IMAGEMAGICK_MOGRIFY_PATH, fillbg="#FFFFFF", colorbg=background, fillfg="#000000", colorfg=foreground, dest=tmp_thislayer),
                            "trace": '"{potrace}" --svg --output "{dest}" --color "{outcolor}" --turdsize 2 "{src}"'.format(potrace = self.POTRACE_PATH, dest=tmp_thistrace, outcolor=color, src=tmp_thislayer)}
                        for k in do_trace:
                            try:
                                #print("Current task:            \n" + str(do_trace[k]))
                                init_trace = await asyncio.create_subprocess_shell(str(do_trace[k]), 
                                                                                            stdout=asyncio.subprocess.PIPE, 
                                                                                            stderr=asyncio.subprocess.PIPE,
                                                                                            shell=True
                                                                                            )
                                stdout, stderr = await init_trace.communicate()
                                #print(f'[{str(init_pallet[k])!r} exited with {str(init_pallet.returncode)}]')
                                if stdout:
                                    logging.info(f'[stdout]\n{stdout.decode()}')
                                if stderr:
                                    logging.info(f'[stdout]\n{stderr.decode()}')
                                    print(k)
                                    
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(exc_type, fname, exc_tb.tb_lineno)
                                logging.info(e)
                                sys.exit(1)
                    try:
                        if i == 0:
                        # first file in the composite svg, so copy it to dest start it off
                            print(out_dest)
                            with open(tmp_thistrace, 'rb') as srcfile, open(out_thisdest, 'wb') as destfile:
                                destfile.write(srcfile.read())
                        else:
                            try:
                            # layer on top of the composite svg
                                doc = svg_stack.Document()
                                layout = svg_stack.CBoxLayout()
                                layout.addSVG(out_thisdest)
                                layout.addSVG(tmp_thistrace)
                                doc.setLayout(layout)
                                with open(out_thisdest, 'w') as file:
                                    doc.save(file)
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(exc_type, fname, exc_tb.tb_lineno)
                                logging.info(e)
                                sys.exit(1)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                        logging.info(e)
                        sys.exit(1)
                # delete all temporary files except palette
                os.remove(tmp_thisquant)
                os.remove(tmp_thislayer)
                os.remove(tmp_thistrace)

                # delete temporary palette file
                os.remove(tmp_palette)



            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                logging.info(e)
                sys.exit(1)
                logging.info(e)
                print(e)
                sys.exit(0)

async def main():
    usage = """color_trace SRCDIR -colors n DESTDIR

    trace color images with potrace

    This will trace all images in SRCDIR to n colors (max 256) and output to destdir
    """
    pngtosvg = color_trace_dir()

    if len(sys.argv) != 5:
        print(usage)
        sys.exit(1)

    print(sys.argv[4])
    srcdir,destdir,colors = sys.argv[1], sys.argv[4], sys.argv[3]
    try:
        await pngtosvg.trace_dir()

    except Exception as e:
        print("Error:", e)
        sys.exit(2)
    
    sys.exit(0)
if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # if cleanup: 'RuntimeError: There is no current event loop..'
        loop = None

    if loop and loop.is_running():
        print('Async event loop already running')
        tsk = loop.create_task(main())
        # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
        tsk.add_done_callback(                                          # optional
            lambda t: print(f'Task done: '                              # optional
                            f'{t.result()=} << return val of main()'))  # optional (using py38)
    else:
        print('Starting new event loop')
        
        asyncio.run(main())

    