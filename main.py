#!/usr/bin/env python
# -*- coding: utf-8 -*-

# break-wall.py
#

import wx
import random
import math

gVersion = "0.8.0"
gGameState = ("INIT","PLAYING","END")
gTimerInterval = 5 # [msec]
gFieldWidth = 640
gFieldHeight = 720
gFieldColor = (230,230,160)
gBarIniPos = (300, 640)
gBarSize = (120, 20)
gBarColor = (90, 170, 90)
gBarSpeed = 12 
gBallRadius = 8
gBallColor = (0, 0, 255)
gIniBallSpeed = 2
gBlkTop = 120
gBlkVCnt = 8
gBlkHCnt = 3
gBlkSize = (80, 40)
gBlkColor = ((255,0,0),(0,255,0),(0,0,255))

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'Break Wall :' + gVersion, \
                          size=(gFieldWidth + 4, gFieldHeight + 4), \
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.main_field = FieldPanel(self)

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_TIMER, self.onTimer)

        self.timer = wx.Timer(self)
        self.timer.Start(gTimerInterval)

    def onClose(self, event):
        self.timer.Stop()
        self.Destroy()

    def onTimer(self, event):
        self.main_field.update()


class FieldPanel(wx.Panel):
    def __init__(self, parent, pos=(2, 2), size=(gFieldWidth, gFieldHeight)):
        wx.Panel.__init__(self, parent, pos=pos, size=size)
        self.pos = pos
        self.size = size

        self.SetBackgroundColour(gFieldColor)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.bar = Bar(self, gBarIniPos[0], gBarIniPos[1])
        self.ball = Ball(self, gBarIniPos[0], (gBarIniPos[1] - gBallRadius))
        self.blocks = [[Block(i*gBlkSize[0], gBlkTop+j*gBlkSize[1], \
                              gBlkColor[(gBlkVCnt*j+i)%gBlkHCnt]) \
                        for i in range(gBlkVCnt)] for j in range(gBlkHCnt)]
        self.block_exist = [[1 for i in range(gBlkVCnt)] for j in range(gBlkHCnt)]
        self.state = gGameState[0]

        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)

    def update(self):
        self.ball.move()
        self.Refresh()

    def onPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        # Paint Bar
        dc.SetPen(wx.Pen(self.bar.color))
        dc.SetBrush(wx.Brush(self.bar.color))
        dc.DrawRectangle(self.bar.x, self.bar.y, self.bar.size[0], self.bar.size[1])
        # Paint Ball
        dc.SetPen(wx.Pen(self.ball.color))
        dc.SetBrush(wx.Brush(self.ball.color))
        dc.DrawCircle(self.ball.x, self.ball.y, self.ball.radius)
        # Paint Blovks
        for (i, b_list) in enumerate(self.blocks):
            for (j, b) in enumerate(b_list):
                if self.block_exist[i][j] == 1:
                    dc.SetPen(wx.Pen(b.color,1))
                    dc.SetBrush(wx.Brush(b.color))
                    dc.DrawRectangle(b.x, b.y, b.size[0], b.size[1])

    def onKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE:
            if self.state == "INIT":
                self.ball.shoot()
                self.state = gGameState[1]
            elif self.state == "END":
                self.initialize()
                self.state = gGameState[0]
        elif (keycode == wx.WXK_LEFT or keycode == ord('H')) and self.state != "END":
            self.bar.move(-1)
        elif (keycode == wx.WXK_RIGHT or keycode == ord('L')) and self.state != "END":
            self.bar.move(1)

    def initialize(self):
        self.bar.x = gBarIniPos[0]
        self.bar.y = gBarIniPos[1]
        self.ball.x = self.bar.x
        self.ball.y = self.bar.y - self.ball.radius
        self.ball.vec = [0, 0]
        self.block_exist = [[1 for i in range(gBlkVCnt)] for j in range(gBlkHCnt)]


class Bar(object):
    def __init__(self, parent, x, y, size=gBarSize, color=gBarColor, speed=gBarSpeed):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed

    def move(self, direction):
        if direction >= 0:
            self.x += self.speed
        elif direction < 0:
            self.x -= self.speed

        if self.x < self.parent.pos[0]:
            self.x = self.parent.pos[0]
        elif self.x > (self.parent.pos[0] + self.parent.size[0] - self.size[0]):
            self.x = self.parent.pos[0] + self.parent.size[0] - self.size[0]


class Ball(object):
    def __init__(self, parent, x, y, radius=gBallRadius, vec=[0.0,0.0], \
                 color=gBallColor, speed=gIniBallSpeed):
        self.parent = parent
        self.x = x
        self.y = y
        self.radius = radius
        self.vec = vec
        self.color = color
        self.speed = speed

    def shoot(self):
        self.parent.state = gGameState[1]
        rand_x = random.randrange(1000, 5000)
        rand_y = random.randrange(2000, 5000)
        self.vec = (-1.0 * float(rand_x)/1000.0, -1.0 * float(rand_y)/1000.0)
        pass

    def move(self):
        if self.parent.state == "INIT":
            self.x = self.parent.bar.x
            self.y = self.parent.bar.y - self.radius
        elif self.parent.state == "END":
            pass
        else:
            unit = self.speed / math.sqrt(pow(self.vec[0],2) + pow(self.vec[1],2))
            self.x += (self.vec[0] * unit)
            self.y += (self.vec[1] * unit)
            self.collision()

    def collision(self):
        # Game Over
        if (self.y + self.radius) >= self.parent.size[1]:
            self.parent.state = gGameState[2]
            return

        # Bound at Bar
        if self.x >= self.parent.bar.x and \
           self.x <= (self.parent.bar.x + self.parent.bar.size[0]) and \
           self.y >= (self.parent.bar.y - self.radius) and \
           self.y <  (self.parent.bar.y + self.radius) and \
           self.vec[1] > 0:

            self.vec = [self.vec[0], -1*self.vec[1]]
            return

        # Bound at Frame
        #### left
        if self.vec[0] < 0 and \
           self.x <= (self.parent.pos[0] + self.radius):
            self.vec = [-1*self.vec[0], self.vec[1]]
            return
        #### right
        if self.vec[0] > 0 and \
           self.x >= (self.parent.pos[0] + self.parent.size[0] - self.radius):
            self.vec = [-1*self.vec[0], self.vec[1]]
            return

        #### ceiling 
        if self.y <= (self.parent.pos[1] + self.radius):
            self.vec = [self.vec[0], -1*self.vec[1]]
            return

        # Bound at Blocks
        no_block = 1
        for (i, b_exist_list) in enumerate(self.parent.block_exist):
            for (j, b_exist) in enumerate(b_exist_list):
                if b_exist == 1:
                    no_block = 0
                    tgt_block = self.parent.blocks[i][j]
                    # Ball cross the block edge
                    if self.x > (tgt_block.x - self.radius) and \
                       self.x < (tgt_block.x + tgt_block.size[0] + self.radius) and \
                       self.y > (tgt_block.y - self.radius) and \
                       self.y < (tgt_block.y + tgt_block.size[1] + self.radius):

                        self.parent.block_exist[i][j] = 0
                        # update vec
                        x0 = tgt_block.x + tgt_block.size[0] / 2
                        y0 = tgt_block.y + tgt_block.size[1] / 2
                        k = float(tgt_block.size[1]) / float(tgt_block.size[0])
                        #### top
                        if (self.vec[1] > 0) and \
                           (self.x < x0 and \
                            self.y < (k * (self.x - x0) + y0 - self.radius)) or \
                           (self.x > x0 and \
                            self.y < (-1 * k * (self.x - x0) + y0 - self.radius)):

                            self.vec = [self.vec[0], -1*self.vec[1]]
                        #### bottom
                        elif (self.vec[1] < 0) and \
                             (self.x < x0 and \
                              self.y > (-1 * k * (self.x - x0) + y0 + self.radius)) or \
                             (self.x > x0 and \
                              self.y > (k * (self.x - x0) + y0 + self.radius)):

                            self.vec = [self.vec[0], -1*self.vec[1]]
                        #### left
                        elif (self.vec[0] > 0) and (self.x < x0):
                            self.vec = [-1*self.vec[0], self.vec[1]]
                        ### right
                        elif (self.vec[0] < 0) and (self.x > x0):
                            self.vec = [-1*self.vec[0], self.vec[1]]

                        return

        if no_block == 1:
            # Game Clear
            self.parent.state = gGameState[2]


class Block(object):
    def __init__(self, x, y, color, size=gBlkSize):
        self.x = x
        self.y = y
        self.color = color
        self.size = size


if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame().Show()
    app.MainLoop()



