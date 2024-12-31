import asyncio
import logging
import pygame as pg
from time import monotonic

class PgApp:
    DESIRED_FPS = 30
    
    def __init__(self, width, height):
        pg.init()
        self._Surface = pg.display.set_mode((width, height),
                                            pg.DOUBLEBUF, 32)        
        self._EventHandlers = []
        self._DesiredFps = PgApp.DESIRED_FPS
        self._Running = True
        self._RenderTime = 0
        self._ReturnValue = 0

    def AddEventHandler(self, handler):
        self._EventHandlers.append(handler)

    def RemoveEventHandler(self, handler):
        self._EventHandlers.remove(handler)

    @property
    def DesiredFps(self):
        return self._DesiredFps

    async def OnStartup(self):
        """ Override """
        pass
   
    async def OnShutdown(self):
        """ Override """
        pass

    def OnEvent(self, event:pg.event.Event):
        """ Override """
        pass

    def OnUpdate(self, dt):
        """ Override """
        pass

    def OnDraw(self, surface:pg.Surface):
        """ Override """
        pass
        
    def OnStopRequested(self):
        """ Override """
        pass    

    def _HandleEvent(self, event:pg.event.Event):
        self.OnEvent(event)
        for handler in self._EventHandlers:
            handler(event)

    async def MainTask(self):
        await self.OnStartup()

        t0 = monotonic()

        while self.IsRunning():      
            t1 = monotonic()
            dt = t1 - t0
            t0 = t1

            # Handle events
            if pg.event.peek():
                for event in pg.event.get():
                    self._HandleEvent(event)

            # Update
            self.OnUpdate(dt)

            # Draw
            r0 = monotonic()
            self.OnDraw(self._Surface)
            self._RenderTime = monotonic() - r0
            pg.display.flip()

            # Keep framerate as constant as possible
            worktime = monotonic() - t1
            sleeptime = (1 / self.desired_fps) - worktime
            if (sleeptime > 0):
                await asyncio.sleep(sleeptime)
            else:
                logging.warning('Can\'t keep up framerate')
                # Release cooperative control even when framerate is too low
                await asyncio.sleep(0)

        logging.debug('Exiting pygame_task')       
        await self.OnShutdown()
        pg.quit()
        return self._ReturnValue

    def RenderTime(self):
        return self._RenderTime
            
    def RequestStop(self, returnValue=0):
        """ Do not override """
        logging.info('RequestStop')
        self._Running = False
        self._ReturnValue = returnValue
        self.OnStopRequested()
        
    def IsRunning(self):
        return self._Running
