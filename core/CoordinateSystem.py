__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

from direct.showbase import DirectObject
import panda3d.core as pcore
import math

class CoordinateSystem(DirectObject.DirectObject):
    
    
     def __init__(self, refNode, length, key):
          self.cosy = pcore.NodePath('cosy')
          self.cosy_visible = False
          self.refNode = refNode
          self.length = length
          
          #for i in range(0,51):
              #x_axis = self.printText("X", "|", (1,0,0)).setPos(i,0,0)  # note that "X" is the name of the TextNode, not its content.
          ##Also note that we are going up in increments of 1.
          #for i in range(0,51):
              #y_axis = self.printText("Y", "|", (0,1,0)).setPos(0,i,0)  
          #for i in range(-50,51):
              #z_axis = self.printText("Z", "-", (0,0,1)).setPos(0,0,i)    
              
              
          (self.x_axis, _, self.x_axis_points, _) = self.drawLine(0, 0, 0, self.length, 0, 0)
          self.x_axis.setColor(1,0,0,1)
          
          (self.y_axis, _, self.y_axis_points, _) = self.drawLine(0, 0, 0, 0, self.length, 0)
          self.y_axis.setColor(0,1,0,1)
          
          (self.z_axis, _, self.z_axis_points, _) = self.drawLine(0, 0, 0, 0, 0, self.length)
          self.z_axis.setColor(0,0,1,1)
              
          x_label = self.printText("XL", "X", (0,0,0)).setPos(self.length/3.,0,0) 
          y_label = self.printText("YL", "Y", (0,0,0)).setPos(0,self.length/3.,0.5) 
          z_label = self.printText("YL", "Z", (0,0,0)).setPos(0,0,self.length/3.)   
          
          self.accept(key, self.switch_on_off)   
          
          
     def switch_on_off(self):
          
          if self.cosy_visible == False: 
                    self.cosy.reparentTo(self.refNode)    
                    self.cosy_visible = True
          else:
                    self.cosy.detachNode()    
                    self.cosy_visible = False                    
     
          
          
     def printText(self, name, message, color): 
         text = pcore.TextNode(name) # create a TextNode. Note that 'name' is not the text, rather it is a name that identifies the object.
         text.setText(message) # Here we set the text of the TextNode
 
         x,y,z = color # break apart the color tuple
         text.setTextColor(x,y,z, 1) # Set the text color from the color tuple
     
         text3d = pcore.NodePath(text) # Here we create a NodePath from the TextNode, so that we can manipulate it 'in world'
         text3d.reparentTo(self.cosy) # This is important. We reparent the text NodePath to the 'render' tree. 
         text3d.setTwoSided(True)   
                 
         # The render tree contains what is going to be rendered into the 3D WORLD. 
         # If we reparented it to 'render2d' instead, it would appear in the 2D WORLD. 
         # The 2D WORLD, from the documentation, is as if someone had written on your computer screen.
         
         return text3d # return the NodePath for further use        
    
    
     def drawLine(self, x1, y1, z1, x2, y2, z2):
                   
          # axis
          vdata_line = pcore.GeomVertexData('vdata_line', pcore.GeomVertexFormat.getV3(), pcore.Geom.UHDynamic)
          vertex_writer = pcore.GeomVertexWriter(vdata_line, 'vertex')

          prim_line = pcore.GeomLines(pcore.Geom.UHStatic)   
     
          vertex_writer.addData3f(x1, y1, z1)
          vertex_writer.addData3f(x2, y2, z2)    
          
          prim_line.addConsecutiveVertices(0, 2)
          prim_line.closePrimitive()          
          
          geom_line = pcore.Geom(vdata_line)
          geom_line.addPrimitive(prim_line)  
          
          line = self.cosy.attachNewNode("line")
          
          line_geomnode = pcore.GeomNode("line")
          line_geomnode.addGeom(geom_line)
                      
          line_model = line.attachNewNode(line_geomnode)
          
          line.setRenderModeThickness(2)
          
          # points
          length = math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
          u1 = (x2-x1)/length
          u2 = (y2-y1)/length
          u3 = (z2-z1)/length
          
          vdata_points = pcore.GeomVertexData('vdata_points', pcore.GeomVertexFormat.getV3(), pcore.Geom.UHDynamic)
          point_writer = pcore.GeomVertexWriter(vdata_points, 'vertex')
          prim_points = pcore.GeomPoints(pcore.Geom.UHStatic)
                   
          for i in range(int(length)):
               point_writer.addData3f(i*u1, i*u2, i*u3)
               prim_points.addConsecutiveVertices(i, 1)
               prim_points.closePrimitive()
     
          #prim_points.addConsecutiveVertices(0, int(length))
          #prim_points.closePrimitive()
          
          geom_points = pcore.Geom(vdata_points)
          geom_points.addPrimitive(prim_points)
          
          points = self.cosy.attachNewNode("points")
          
          points_geomnode = pcore.GeomNode("points")
          points_geomnode.addGeom(geom_points)
          
          points_model = points.attachNewNode(points_geomnode)
          
          points.setRenderModeThickness(3)
               
          return (line, line_model, points, points_model)            