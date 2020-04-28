__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

from direct.showbase import DirectObject
import panda3d.core as pcore


class gridProjection(DirectObject.DirectObject):
    
    def __init__(self, arena, screen, beamer, lens, key, color):
        
        self.arena = arena
        self.screen = screen
        self.beamer = beamer
        self.lens = lens
        self.color = color
        
        self.accept(key, self.switch_on_off)     
        self.grid_visible = False
        
    def project(self):
        
        # project field of view of beamer
        N_x = int(self.arena.omega_h*3);
        N_y = int(self.arena.omega_v*3);
        grid_image = pcore.PNMImage(N_x, N_y)
        for i in range(N_x-2):
            for j in range(N_y-2):
                grid_image.setXelA(i+1,j+1,0,0,0,1)  
        for i in range(N_x):
            grid_image.setXelA(i,0,1,1,1,1)  
            grid_image.setXelA(i,int(N_y/2),1,1,1,1)  
            grid_image.setXelA(i,N_y-1,1,1,1,1) 
        for i in range(N_y):
            grid_image.setXelA(0,i,1,1,1,1)  
            grid_image.setXelA(int(N_x/2),i,1,1,1,1) 
            grid_image.setXelA(N_x-1,i,1,1,1,1)                 
           
        self.tex_grid = pcore.Texture()
        self.tex_grid.load(grid_image)        
        self.tex_grid.setMagfilter(pcore.Texture.FTNearest) 
               
        self.proj = render.attachNewNode(pcore.LensNode('proj'))
        self.proj.node().setLens(self.lens)
        self.proj.reparentTo(self.beamer)
               
        self.ts = pcore.TextureStage('ts_proj')
        self.ts.setMode(pcore.TextureStage.MBlend)
        self.ts.setColor(pcore.Vec4(self.color[0], self.color[1], self.color[2], self.color[3]))
        self.tex_grid.setWrapU(pcore.Texture.WMBorderColor)
        self.tex_grid.setWrapV(pcore.Texture.WMBorderColor)
       
        self.screen.projectTexture(self.ts, self.tex_grid, self.proj)
               
        self.proj.node().showFrustum()
        self.proj.find('frustum').setColor(self.color[0], self.color[1], self.color[2], self.color[3])   
        
        
    def switch_on_off(self):
         
         if self.grid_visible == False: 
             self.project()
             self.grid_visible = True
         else:
             self.screen.clearTexture(self.ts)
             self.grid_visible = False   
             self.proj.node().hideFrustum()
      