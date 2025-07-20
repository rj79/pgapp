from pgapp import PgApp, runApp
import pygame as pg

class TestApp(PgApp):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.Time = 0
        self.NextPrint = 0


    def OnEvent(self, event):
        if event.type == pg.QUIT:
            self.RequestStop()
        else:
            print(event)

    def OnKeyDown(self, key, mod, unicode, scancode):
        print('KEYDOWN', key, mod, unicode, scancode)
        if key == pg.K_ESCAPE:
            self.RequestStop()
    
    def OnKeyUp(self, key, mod, unicode, scancode):
        print('KEYUP', key, mod, unicode, scancode)
    
    def OnMouseMotion(self, pos, rel, buttons, touch):
        print('MOUSEMOTION', pos, rel, buttons, touch)

    def OnMouseButtonDown(self, pos, button, touch):
        print('MOUSEBUTTONDOWN', pos, button, touch)

    def OnMouseButtonUp(self, pos, button, touch):
        print('MOUSEBUTTONUP', pos, button, touch)

    def OnUpdate(self, dt):
        self.Time += dt

    def OnDraw(self, surface):
        if self.Time > self.NextPrint:
            fps = self.GetFPS()
            print(f'FPS: {fps:.2f}')
            self.NextPrint += 1
        
    def OnStopRequested(self):
        print('OnStopRequested')
    
    
runApp(TestApp(800, 600))
