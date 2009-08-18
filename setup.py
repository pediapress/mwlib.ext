#Copyright ReportLab Europe Ltd. 2000-2008
#see license.txt for license details
__version__=''' $Id$ '''
import os, sys, glob, ConfigParser, shutil
platform = sys.platform
pjoin = os.path.join
abspath = os.path.abspath
isfile = os.path.isfile
isdir = os.path.isfile
dirname = os.path.dirname
if __name__=='__main__':
    pkgDir=dirname(sys.argv[0])
else:
    pkgDir=dirname(__file__)
if not pkgDir:
    pkgDir=os.getcwd()
elif not os.path.isabs(pkgDir):
    pkgDir=os.path.abspath(pkgDir)
try:
    os.chdir(pkgDir)
except:
    print '!!!!! warning could not change directory to %r' % pkgDir
daily=os.environ.get('RL_EXE_DAILY','')

import distutils
from distutils.core import setup, Extension
from distutils import sysconfig

package_path = pjoin(sysconfig.get_python_lib(plat_specific=1), 'reportlab')

def get_version():
    if daily: return 'daily'
    #determine Version
    HERE = pkgDir
    if os.getcwd()!=HERE:
        if __name__=='__main__':
            HERE=os.path.dirname(sys.argv[0])
        else:
            HERE=os.path.dirname(__file__)

    #first try source
    FN = pjoin(HERE,'src','reportlab','__init__')
    try:
        for l in open(pjoin(FN+'.py'),'r').readlines():
            if l.startswith('Version'):
                exec l.strip()
                return Version
    except:
        pass

    #don't have source, try import
    import imp
    for desc in ('.pyc', 'rb', 2), ('.pyo', 'rb', 2):
        try:
            fn = FN+desc[0]
            f = open(fn,desc[1])
            m = imp.load_module('reportlab',f,fn,desc)
            return m.Version
        except:
            pass
    raise ValueError('Cannot determine ReportLab Version')

class config:
    def __init__(self):
        try:
            self.parser = ConfigParser.RawConfigParser()
            self.parser.read(pjoin(pkgDir,'setup.cfg'))
        except:
            self.parser = None

    def __call__(self,sect,name,default=None):
        try:
            return self.parser.get(sect,name)
        except:
            return default
config = config()

#this code from /FBot's PIL setup.py
def aDir(P, d, x=None):
    if d and os.path.isdir(d) and d not in P:
        if x is None:
            P.append(d)
        else:
            P.insert(x, d)

class inc_lib_dirs:
    L = None
    I = None
    def __call__(self):
        if self.L is None:
            L = []
            I = []
            if platform == "cygwin":
                aDir(L, os.path.join("/usr/lib", "python%s" % sys.version[:3], "config"))
            elif platform == "darwin":
                # attempt to make sure we pick freetype2 over other versions
                aDir(I, "/sw/include/freetype2")
                aDir(I, "/sw/lib/freetype2/include")
                # fink installation directories
                aDir(L, "/sw/lib")
                aDir(I, "/sw/include")
                # darwin ports installation directories
                aDir(L, "/opt/local/lib")
                aDir(I, "/opt/local/include")
            aDir(I, "/usr/local/include")
            aDir(L, "/usr/local/lib")
            aDir(I, "/usr/include")
            aDir(L, "/usr/lib")
            aDir(I, "/usr/include/freetype2")
            prefix = sysconfig.get_config_var("prefix")
            if prefix:
                aDir(L, pjoin(prefix, "lib"))
                aDir(I, pjoin(prefix, "include"))
            self.L=L
            self.I=I
        return self.I,self.L
inc_lib_dirs=inc_lib_dirs()

def getVersionFromCCode(fn):
    import re
    tag = re.search(r'^#define\s+VERSION\s+"([^"]*)"',open(fn,'r').read(),re.M)
    return tag and tag.group(1) or ''

class _rl_dir_info:
    def __init__(self,cn):
        self.cn=cn
    def __call__(self,dir):
        import stat
        fn = pjoin(dir,self.cn)
        try:
            return getVersionFromCCode(fn),os.stat(fn)[stat.ST_MTIME]
        except:
            return None

def _cmp_rl_ccode_dirs(a,b):
    return cmp(_rl_dir_info(b),_rl_dir_info(a))

def _find_rl_ccode(dn='rl_accel',cn='_rl_accel.c'):
    '''locate where the accelerator code lives'''
    _ = []
    for x in [
            pjoin('src','rl_addons',dn),
            pjoin('rl_addons',dn),
            pjoin('..','rl_addons',dn),
            pjoin('..','..','rl_addons',dn),
            dn,
            pjoin('..',dn),
            pjoin('..','..',dn),
            ] \
            + glob.glob(pjoin(dn+'-*',dn))\
            + glob.glob(pjoin('..',dn+'-*',dn))\
            + glob.glob(pjoin('..','..',dn+'-*',dn))\
            :
        fn = pjoin(pkgDir,x,cn)
        if isfile(fn):
            _.append(x)
    if _:
        _ = filter(_rl_dir_info(cn),_)
        if len(_):
            _.sort(_cmp_rl_ccode_dirs)
            return abspath(_[0])
    return None


def BIGENDIAN(macname,value=None):
    'define a macro if bigendian'
    return sys.byteorder=='big' and [(macname,value)] or []

def pfxJoin(pfx,*N):
    R=[]
    for n in N:
        R.append(os.path.join(pfx,n))
    return R

INFOLINES=[]
def infoline(t):
    print t
    INFOLINES.append(t)

reportlab_files= [
        'fonts/00readme.txt',
        'fonts/bitstream-vera-license.txt',
        'fonts/DarkGarden-copying-gpl.txt',
        'fonts/DarkGarden-copying.txt',
        'fonts/DarkGarden-readme.txt',
        'fonts/DarkGarden.sfd',
        'fonts/DarkGardenMK.afm',
        'fonts/DarkGardenMK.pfb',
        'fonts/Vera.ttf',
        'fonts/VeraBd.ttf',
        'fonts/VeraBI.ttf',
        'fonts/VeraIt.ttf',
        ]

def main():
    #test to see if we've a special command
    if 'tests' in sys.argv or 'tests-preinstall' in sys.argv:
        if len(sys.argv)!=2:
            raise ValueError('tests commands may only be used alone')
        cmd = sys.argv[-1]
        PYTHONPATH=[pkgDir]
        if cmd=='tests-preinstall':
            PYTHONPATH.insert(0,pjoin(pkgDir,'src'))
        os.environ['PYTHONPATH']=os.pathsep.join(PYTHONPATH)
        os.chdir(pjoin(pkgDir,'tests'))
        os.system("%s runAll.py" % sys.executable)
        return

    SPECIAL_PACKAGE_DATA = {}
    RL_ACCEL = _find_rl_ccode('rl_accel','_rl_accel.c')
    LIBS = []
    LIBRARIES=[]
    EXT_MODULES = []
    if not RL_ACCEL:
        infoline( '***************************************************')
        infoline( '*No rl_accel code found, you can obtain it at     *')
        infoline( '*http://www.reportlab.org/downloads.html#_rl_accel*')
        infoline( '***************************************************')
    else:
        infoline( '################################################')
        infoline( '#Attempting install of _rl_accel, sgmlop & pyHnj')
        infoline( '#extensions from %r'%RL_ACCEL)
        infoline( '################################################')
        fn = pjoin(RL_ACCEL,'hyphen.mashed')
        SPECIAL_PACKAGE_DATA = {fn: pjoin('lib','hyphen.mashed')}
        EXT_MODULES += [
                    Extension( '_rl_accel',
                                [pjoin(RL_ACCEL,'_rl_accel.c')],
                                include_dirs=[],
                            define_macros=[],
                            library_dirs=[],
                            libraries=LIBS, # libraries to link against
                            ),
                    Extension( 'sgmlop',
                            [pjoin(RL_ACCEL,'sgmlop.c')],
                            include_dirs=[],
                            define_macros=[],
                            library_dirs=[],
                            libraries=LIBS, # libraries to link against
                            ),
                    Extension( 'pyHnj',
                            [pjoin(RL_ACCEL,'pyHnjmodule.c'),
                             pjoin(RL_ACCEL,'hyphen.c'),
                             pjoin(RL_ACCEL,'hnjalloc.c')],
                            include_dirs=[],
                            define_macros=[],
                            library_dirs=[],
                            libraries=LIBS, # libraries to link against
                            ),
                    ]
    RENDERPM = _find_rl_ccode('renderPM','_renderPM.c')
    LIBS = []
    if not RENDERPM:
        infoline( '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        infoline( '!No rl_accel code found, you can obtain it at     !')
        infoline( '!http://www.reportlab.org/downloads.html          !')
        infoline( '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    else:
        infoline( '################################################')
        infoline( '#Attempting install of _renderPM')
        infoline( '#extensions from %r'%RENDERPM)
        LIBART_DIR=pjoin(RENDERPM,'libart_lgpl')
        MACROS=[('ROBIN_DEBUG',None)]
        MACROS=[]
        def libart_version():
            K = ('LIBART_MAJOR_VERSION','LIBART_MINOR_VERSION','LIBART_MICRO_VERSION')
            D = {}
            for l in open(pjoin(LIBART_DIR,'configure.in'),'r').readlines():
                l = l.strip().split('=')
                if len(l)>1 and l[0].strip() in K:
                    D[l[0].strip()] = l[1].strip()
                    if len(D)==3: break
            return (sys.platform == 'win32' and '\\"%s\\"' or '"%s"') % '.'.join(map(lambda k,D=D: D.get(k,'?'),K))
        LIBART_VERSION = libart_version()
        SOURCES=[pjoin(RENDERPM,'_renderPM.c')]
        LIBART_SRCS=glob.glob(pjoin(LIBART_DIR, 'art_*.c'))
        GT1_DIR=pjoin(RENDERPM,'gt1')
        LIBS = []       #assume empty libraries list

        if platform=='win32':
            FT_LIB=config('FREETYPE','lib',r'C:\devel\freetype-2.1.5\objs\freetype214.lib')
            if FT_LIB:
                FT_INC_DIR=config('FREETYPE','incdir')
                FT_MACROS = [('RENDERPM_FT',None)]
                FT_LIB_DIR = [dirname(FT_LIB)]
                FT_INC_DIR = [FT_INC_DIR or pjoin(dirname(FT_LIB_DIR[0]),'include')]
                FT_LIB = [os.path.splitext(os.path.basename(FT_LIB))[0]]
                infoline('# installing with win32 freetype %r' % FT_LIB[0])
            else:
                FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
        else:
            FT_LIB_DIR=config('FREETYPE','libdir')
            FT_INC_DIR=config('FREETYPE','incdir')
            I,L=inc_lib_dirs()
            ftv = None
            for d in I:
                if isfile(pjoin(d, "ft2build.h")):
                    ftv = 21
                    FT_INC_DIR=[d,pjoin(d, "freetype2")]
                    break
                d = pjoin(d, "freetype2")
                if isfile(pjoin(d, "ft2build.h")):
                    ftv = 21
                    FT_INC_DIR=[d]
                    break
                if isdir(pjoin(d, "freetype")):
                    ftv = 20
                    FT_INC_DIR=[d]
                    break
            if ftv:
                FT_LIB=['freetype']
                FT_LIB_DIR=L
                FT_MACROS = [('RENDERPM_FT',None)]
                infoline('# installing with freetype version %d' % ftv)
            else:
                FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
        if not FT_LIB:
            infoline('# installing without freetype no ttf, sorry!')

        LIBRARIES+= [
                    ('_renderPM_libart',
                    {
                    'sources':  LIBART_SRCS,
                    'include_dirs': [RENDERPM,LIBART_DIR,],
                    'macros': [('LIBART_COMPILATION',None),]+BIGENDIAN('WORDS_BIGENDIAN')+MACROS,
                    #'extra_compile_args':['/Z7'],
                    }
                    ),
                    ('_renderPM_gt1',
                    {
                    'sources':  pfxJoin(GT1_DIR,'gt1-dict.c','gt1-namecontext.c','gt1-parset1.c','gt1-region.c','parseAFM.c'),
                    'include_dirs': [RENDERPM,GT1_DIR,],
                    'macros': MACROS,
                    #'extra_compile_args':['/Z7'],
                    }
                    ),
                    ]

        EXT_MODULES +=  [Extension( '_renderPM',
                                        SOURCES,
                                        include_dirs=[RENDERPM,LIBART_DIR,GT1_DIR]+FT_INC_DIR,
                                        define_macros=FT_MACROS+[('LIBART_COMPILATION',None)]+MACROS+[('LIBART_VERSION',LIBART_VERSION)],
                                        library_dirs=[]+FT_LIB_DIR,

                                        # libraries to link against
                                        libraries=LIBS+FT_LIB,
                                        #extra_objects=['gt1.lib','libart.lib',],
                                        #extra_compile_args=['/Z7'],
                                        extra_link_args=[]
                                        ),
                            ]
        infoline('################################################')

    #copy some special case files into place so package_data will treat them properly
    PACKAGE_DIR = {'reportlab': pjoin('src','reportlab')}
    for fn,dst in SPECIAL_PACKAGE_DATA.iteritems():
        shutil.copyfile(fn,pjoin(PACKAGE_DIR['reportlab'],dst))
        reportlab_files.append(dst)

    try:
        setup(
            name="reportlab",
            version=get_version(),
            license="BSD license (see license.txt for details), Copyright (c) 2000-2008, ReportLab Inc.",
            description="The Reportlab Toolkit",
            long_description="""The ReportLab Toolkit. An Open Source Python library for generating PDFs and graphics.""",

            author="Robinson, Watters, Lee, Precedo, Becker and many more...",
            author_email="info@reportlab.com",
            url="http://www.reportlab.com/",
            packages=[
                    'reportlab',
                    'reportlab.graphics.charts',
                    'reportlab.graphics.samples',
                    'reportlab.graphics.widgets',
                    'reportlab.graphics.barcode',
                    'reportlab.graphics',
                    'reportlab.lib',
                    'reportlab.pdfbase',
                    'reportlab.pdfgen',
                    'reportlab.platypus',
                    ],
            package_dir = PACKAGE_DIR,
            package_data = {'reportlab': reportlab_files},
            libraries = LIBRARIES,
            ext_modules =   EXT_MODULES,
            )
        print
        print '########## SUMMARY INFO #########'
        print '\n'.join(INFOLINES)
    finally:
        for dst in SPECIAL_PACKAGE_DATA.itervalues():
            os.remove(pjoin(PACKAGE_DIR['reportlab'],dst))
            reportlab_files.remove(dst)

if __name__=='__main__':
    main()
