import asyncio
import logging
import pygame as pg
from time import monotonic

class FPSCounter:
    MAX_SAMPLES = 10

    def __init__(self):
        self._AverageFPS = 0
        self._Samples = 0
        self._Time = 0
        self._StartTime = monotonic()

    def Count(self):
        if self._Samples == FPSCounter.MAX_SAMPLES:
            self._AverageFPS = FPSCounter.MAX_SAMPLES / (monotonic() - self._StartTime)
            self._Samples = 0
            self._StartTime = monotonic()
        self._Samples += 1

    def GetAverage(self):
        return self._AverageFPS


class PgApp:
    TARGET_FPS = 30
    
    def __init__(self, width, height, flags=0, target_fps=TARGET_FPS):
        pg.init()
        self._DispFlags = flags | pg.DOUBLEBUF
        self._ColorDepth = 32
        self._Surface = pg.display.set_mode((width, height),
                                            self._DispFlags, self._ColorDepth)
        self._EventHandlers = []
        self.SetTargetFPS(target_fps)
        self._Running = True
        self._RenderTime = 0
        self._ReturnValue = 0

        self._FPSCounter = FPSCounter()

    def Resize(self, width, height):
        del self._Surface
        self._Surface = pg.display.set_mode((width, height),
                                             self._DispFlags, self._ColorDepth)

    def AddEventHandler(self, handler):
        self._EventHandlers.append(handler)

    def RemoveEventHandler(self, handler):
        self._EventHandlers.remove(handler)

    def GetFPS(self):
        return self._FPSCounter.GetAverage()

    def GetTargetFPS(self):
        return self._TargetFPS

    def SetTargetFPS(self, fps):
        self._TargetFPS = max(0, fps)

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
            for event in pg.event.get():
                self._HandleEvent(event)

            # Update
            self.OnUpdate(dt)

            # Draw
            r0 = monotonic()
            self.OnDraw(self._Surface)
            self._RenderTime = monotonic() - r0
            pg.display.flip()
            self._FPSCounter.Count()

            if self._TargetFPS > 0:
                # Keep framerate as constant as possible
                worktime = monotonic() - t1
                sleeptime = (1 / self._TargetFPS) - worktime
                if (sleeptime > 0):
                    await asyncio.sleep(sleeptime)
                else:
                    actual_fps = self._FPSCounter.GetAverage()
                    if actual_fps < self._TargetFPS - 1:
                        logging.warning(f'Can\'t keep up framerate. Actual: {actual_fps:.1f} FPS. Target: {self._TargetFPS:.1f} FPS')
                    # Release cooperative control even when framerate is too low
                    await asyncio.sleep(0)
            else:
                await asyncio.sleep(0)

        logging.debug('Exiting pygame_task')       
        await self.OnShutdown()
        pg.quit()
        return self._ReturnValue

    def RenderTime(self):
        return self._RenderTime
            
    def RequestStop(self, returnValue=0):
        """ Do not override """
        if self._Running:
            logging.info('RequestStop')
            self._Running = False
            self._ReturnValue = returnValue
            self.OnStopRequested()
        
    def IsRunning(self):
        return self._Running


def get_event_loop():
    import sys
    import asyncio
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    return loop

def runApp(app:PgApp):
    return get_event_loop().run_until_complete(app.MainTask())
