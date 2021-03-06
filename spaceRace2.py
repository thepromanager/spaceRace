import pygame
import os
import math
import time
import random
gameDisplay = pygame.display.set_mode((1200, 780))
background = pygame.image.load(os.path.join("textures", "map_1.png"))
background = pygame.transform.scale(background, (1000*3, 600*3))
blueprint =pygame.image.load(os.path.join("textures", "blueprint_1.png"))
blueprint = pygame.transform.scale(blueprint, (1000*3, 600*3))
miniMap =pygame.transform.scale(background, (100, 60))
clock = pygame.time.Clock()
screenWidth=1200
screenHeight=780
playerScreenWidth=400
scale=2
def blitRotate(surf,image, pos, originPos, angle,area):

    # calcaulate the axis aligned bounding box of the rotated image
    w, h       = image.get_size()
    box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot 
    pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (pos[0] - originPos[0] + min_box[0] - pivot_move[0], pos[1] - originPos[1] - max_box[1] + pivot_move[1])

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    surf.blit(rotated_image, origin,area=area)
class World():
    frictions={0:0.99,1:0.95,2:0.60}
    ships=[]
    cameras=[]
    def draw(image,x,y,a,center=[0,0]):
        for camera in World.cameras:
            camera.drawImage(image,x,y,a,center)
class Camera():

    def __init__(self,ship):
        self.x = 0
        self.y = 0
        self.ship=ship
        self.offset=ship.offset
    def update(self):
        ship=self.ship
        self.x = ship.x-playerScreenWidth//2+ship.center[0]*scale
        self.y = ship.y-screenHeight//2+ship.center[1]*scale
    def drawImage(self, image, x, y,a,center):
        screenX=x-self.x+self.offset
        screenY=y-self.y       
        if(screenX>self.offset and screenX<self.offset+playerScreenWidth):
            box=pygame.Rect(0,0,playerScreenWidth+self.offset-screenX,10000)
        elif(screenX<=self.offset):
            box=pygame.Rect(self.offset-screenX,0,playerScreenWidth,10000) 
            screenX=self.offset     
        #box=pygame.Rect((self.offset-screenX),max(-screenY,0),(500+self.offset)-screenX,max(600-screenY,0))         

        #pygame.draw.rect(gameDisplay,(self.offset//2,self.offset//2,self.offset//2),box)
        #gameDisplay.blit(image,(screenX,screenY))
        if(screenX<self.offset+playerScreenWidth):
            if(a>0):
                blitRotate(gameDisplay,image,[screenX+center[0]*scale,screenY+center[1]*scale],[center[0]*scale,center[1]*scale],a,box)
            else:
                gameDisplay.blit(image,(screenX,screenY),area=box)
        #blitRotate(gameDisplay,self.image,[ship.x+ship.center[0]*scale,ship.y+ship.center[1]*scale],[ship.center[0]*scale,ship.center[1]*scale],ship.r,ship.camera)
class Ship():   
    def __init__(self,offset):
        #print(offset)
        self.hurtbox = [0,0,1,1]
        self.xv = 0
        self.yv = 0
        self.rv = 0
        self.r=10*scale
        self.x = 300+random.random()*200
        self.y = 300+random.random()*200
        self.a = 0
        self.offset=offset
        self.weight=1
        self.thrusters=[]
        self.mapFlag=0
        self.lapCount=0
    def draw(self):
        World.draw(self.image,self.x,self.y,self.a,center=self.center)
        #blitRotate(gameDisplay,self.image,[self.x+self.center[0]*scale,self.y+self.center[1]*scale],[self.center[0]*scale,self.center[1]*scale],self.r,self.camera)
        for thruster in self.thrusters:
            thruster.draw()
        pygame.draw.rect(gameDisplay,(0,0,0),(playerScreenWidth+self.offset-100,screenHeight-60,100,60))
        gameDisplay.blit(miniMap,(playerScreenWidth+self.offset-100,screenHeight-60))
        for ship in World.ships:
            r=2
            if(ship==self):
                r=3
            pygame.draw.circle(gameDisplay,(255,0,0),(playerScreenWidth+self.offset-100+int(100*ship.x/(1000*3)),screenHeight-60+int(60*ship.y/(600*3))),r)
    def load(playerName):
        image = pygame.image.load(os.path.join("textures", playerName))
        image = pygame.transform.scale(image, (scale*32, scale*32))
        return image
    def update(self):
        self.x+=self.xv
        self.y+=self.yv
        self.a+=self.rv
        #self.x=(self.x+self.center[0])%1000-self.center[0]
        #self.y=(self.y+self.center[1])%600-self.center[1]
        self.a=self.a%360
        color=blueprint.get_at((int(self.x+self.center[0]), int(self.y+self.center[1])))
        self.rv*=World.frictions[color[0]] # är man i rymden eller inte??
        self.yv*=World.frictions[color[0]]
        self.xv*=World.frictions[color[0]]
        if(color[1]==self.mapFlag+1 or (self.mapFlag==5 and color[1]==1)):
            if(self.mapFlag==5):
                self.lapCount+=1
                print(self.__class__.__name__,self.lapCount)
                if(self.lapCount==3):
                    print(self.__class__.__name__,"won first")

            self.mapFlag=color[1]
        for ship in World.ships:
            if not ship==self:
                dist=math.sqrt((self.x-ship.x)**2+(self.y-ship.y)**2)
                if dist < (self.r+ship.r):
                   self.x-= (dist-(self.r+ship.r))*(1/2)*((self.x-ship.x)/dist)
                   self.y-= (dist-(self.r+ship.r))*(1/2)*((self.y-ship.y)/dist)
    def keys(self,pressed):
        for thruster in self.thrusters:
            thruster.update(pressed)

class Astari(Ship):
    image=Ship.load("astari/astari.png")
    def __init__(self,controls,offset):
        super(Astari, self).__init__(offset)
        self.hurtbox=[9,1,23,22]
        self.center=[16,14]
        self.weight=100
        self.thrusters=[
        Thruster(self,controls[0],x=8.5,y=22,power=2,image="astari/thruster1.png"),
        Thruster(self,controls[1],x=16,y=22,power=3,image="astari/thruster2.png"),
        Thruster(self,controls[2],x=23.5,y=22,power=2,image="astari/thruster3.png")
        ]
class Rotum(Ship):
    image=Ship.load("rotum/rotum.png")
    def __init__(self,controls,offset):
        super(Rotum, self).__init__(offset)
        self.hurtbox=[1,7,31,20]
        self.center=[16,13.5]
        self.weight=120
        self.thrusters=[
        Thruster(self,controls[0],x=11,y=18,a=45,power=6,image="rotum/thruster2.png"),
        Thruster(self,controls[1],x=16,y=7,a=180,power=8,image="rotum/thruster1.png"),
        Thruster(self,controls[2],x=21,y=18,a=-45,power=6,image="rotum/thruster3.png")
        ]
class Valeria(Ship):
    image=Ship.load("valeria/valeria.png")
    def __init__(self,controls,offset):
        super(Valeria, self).__init__(offset)
        self.hurtbox=[8,2,24,30]
        self.center=[16,16]
        self.weight=200
        self.thrusters=[
        Thruster(self,controls[0],x=7,y=8,a=-40,power=7,image="valeria/thruster1.png"),
        Thruster(self,controls[1],x=10,y=27,a=-60,power=5,image="valeria/thruster2.png"),
        Thruster(self,controls[2],x=22,y=27,a=60,power=5,image="valeria/thruster4.png"),
        Thruster(self,controls[3],x=25,y=8,a=40,power=7,image="valeria/thruster3.png"),
        ]
class Zerti(Ship):
    image=Ship.load("zerti/zerti.png")
    def __init__(self,controls,offset):
        super(Zerti, self).__init__(offset)
        self.hurtbox=[10,6,24,26]
        self.center=[17.5,19.5]
        self.weight=90
        self.thrusters=[
        Fluster(self,controls[0],x=8,y=19,a=-120,power=150,image="zerti/thruster3.png",rotPowerFactor=1/3),
        Thruster(self,controls[1],x=16,y=26,a=-45,power=3.5,image="zerti/thruster1.png"),
        Thruster(self,controls[2],x=19,y=26,a=45,power=3.5,image="zerti/thruster2.png"),
        Fluster(self,controls[3],x=27,y=19,a=120,power=150,image="zerti/thruster4.png",rotPowerFactor=1/3),
        ]
class Wio(Ship):
    image=Ship.load("wio/wio.png")
    def __init__(self,controls,offset):
        super().__init__(offset)
        self.hurtbox=[10,6,24,26]
        self.center=[16,16]
        self.weight=70
        self.thrusters=[
        Buster(self,controls[0],x=10,y=19,a=0,power=3,image="wio/buster1.png",rotPowerFactor=0.1),
        Thruster(self,controls[1],x=12,y=26,a=135,power=3,image="valeria/thruster1.png"),
        Thruster(self,controls[2],x=20,y=26,a=-135,power=3,image="valeria/thruster3.png"),
        Buster(self,controls[3],x=22,y=19,a=0,power=3,image="wio/buster2.png",rotPowerFactor=0.1),
        ]
class Podracer(Ship):
    image=Ship.load("podracer/podracer.png")
    def __init__(self,controls,offset):
        super().__init__(offset)
        self.hurtbox=[10,6,24,26]
        self.center=[15,14]
        self.weight=70
        self.thrusters=[
        Muster(self,controls[0],x=10,y=19,a=0,power=2,image="zerti/thruster3.png",rotPowerFactor=1),
        Fluster(self,controls[1],x=15,y=26,a=0,power=100,image="zerti/thruster1.png"),
        Muster(self,controls[2],x=20,y=19,a=0,power=2,image="zerti/thruster4.png",rotPowerFactor=1),
        ]

class Thruster():
    def __init__(self,ship,key,x=0,y=0,power=1,a=0,image="",rotPowerFactor=1):
        self.ship = ship
        self.key = key
        self.x=x
        self.y=y
        self.power=power
        self.a=a
        self.image=Ship.load(image)
        self.active=False
        self.rotPowerFactor=rotPowerFactor
    def update(self, pressed):
        if(pressed[self.key]):
            self.activate()
    def activate(self):

        #calculate torque
        dx=self.x-ship.center[0]
        dy=self.y-ship.center[1]
        torque=self.power*dx*math.cos(math.radians(self.a))-self.power*dy*math.sin(math.radians(self.a))
        ship.rv+=torque/ship.weight*self.rotPowerFactor

        #calculate directional forces
        vx=self.power*math.cos(math.radians(self.a))
        vy=self.power*math.sin(math.radians(self.a))
        
        #recalculate forces based on rotation of ship
        vx2=math.cos(math.radians(ship.a))*vx-math.sin(math.radians(ship.a))*vy
        vy2=math.sin(math.radians(ship.a))*vx+math.cos(math.radians(ship.a))*vy
        ship.yv-=vx2/ship.weight
        ship.xv-=vy2/ship.weight
        self.active=True
    def draw(self):
        if(self.active):
            self.active=False
            World.draw(self.image,self.ship.x,self.ship.y,self.ship.a,self.ship.center)
            #blitRotate(gameDisplay,self.image,[ship.x+ship.center[0]*scale,ship.y+ship.center[1]*scale],[ship.center[0]*scale,ship.center[1]*scale],ship.r,ship.camera)
class Fluster(Thruster):
    def __init__(self,ship,key,x=0,y=0,power=1,a=0,image="",rotPowerFactor=1,cooldown=30):
        super().__init__(ship,key,x,y,power,a,image,rotPowerFactor)
        self.timer = 0
        self.cooldown = cooldown
        self.lastKey = False
    def update(self,pressed):
        if(pressed[self.key]):
            if(not self.lastKey):
                if not self.timer:
                    self.activate()
                    self.timer=self.cooldown
                else:
                    self.timer+=5
            self.lastKey=True
        else:
            self.lastKey=False
        if self.timer:
            self.timer-=1
class Buster(Thruster):
    def __init__(self, ship, key,x=0,y=0,power=1,a=0,image="",rotPowerFactor=1):
        super(Buster, self).__init__(ship,key,x,y,power,a,image,rotPowerFactor)
        self.chargeSpeed = self.power
        self.maxPower = self.power*200
        self.currentPower = 0
    def update(self,pressed):
        if(pressed[self.key]):
            if self.currentPower<self.maxPower:
                self.currentPower+=self.chargeSpeed
        elif self.currentPower>1:
            self.power=self.currentPower
            self.activate()
            self.currentPower*=0 # 0 is too hard and frame perfect
class Muster(Thruster):
    def __init__(self, ship, key,x=0,y=0,power=1,a=0,image="",rotPowerFactor=1):
        super().__init__(ship,key,x,y,power,a,image,rotPowerFactor)
        self.basePower = power
        self.power = self.basePower
        self.speedUp = 0.002
    def update(self, pressed):
        if(pressed[self.key]):
            self.activate()
            self.power+=self.speedUp
        else:
            self.power=self.basePower

World.ships.append(Wio([pygame.K_q,pygame.K_w,pygame.K_e,pygame.K_r],000))
World.ships.append(Podracer([pygame.K_z,pygame.K_x,pygame.K_c,pygame.K_v],400))
World.ships.append(Rotum([pygame.K_u,pygame.K_i,pygame.K_o,pygame.K_p],800))
for ship in World.ships:
    World.cameras.append(Camera(ship))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)

    # DO THINGS
    pressed = pygame.key.get_pressed()
    for ship in World.ships:
        ship.keys(pressed)
        ship.update()
    for camera in World.cameras:
        camera.update()


    # DRAW
    gameDisplay.fill((1,25,45))
    World.draw(background,0,0,0)
    for ship in World.ships:      
        ship.draw()

    pygame.display.update() # flip?

pygame.quit()
quit()

#hastighetsmark
#damage och respawn
#Banor att racea på
#autogenererad utforskning
#låsa upp skepp

#endless mode
#timetrials
#race

"""
motorer:
hålla inne är bra acceleration
tap med delay
charga upp
"""