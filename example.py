from piconnect_client import PiconnectClient, PiconnectEvent
import threading
import pygame



def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    x, y = 100, 100
    vx, vy = 0, 0
    z, w = 150, 150
    vz, vw = 0, 0
    clock = pygame.time.Clock()

    picoclient = PiconnectClient()
    thread_picoclient = threading.Thread(target=picoclient.run, daemon=True)
    thread_picoclient.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for event in picoclient.drain_queue():
            if event.name == "pico1":
                if event.d == 3:
                    vx, vy = 2, 0
                elif event.d == 7:
                    vx, vy = -2, 0
                elif event.d == 1:
                    vx, vy = 0, -2
                elif event.d == 5:
                    vx, vy = 0, 2
                elif event.d == 0:
                    vx, vy = 0, 0
            elif event.name == "pico2":
                if event.d == 3:
                    vz, vw = 2, 0
                elif event.d == 7:
                    vz, vw = -2, 0
                elif event.d == 1:
                    vz, vw = 0, -2
                elif event.d == 5:
                    vz, vw = 0, 2
                elif event.d == 0:
                    vz, vw = 0, 0
        
        x += vx
        y += vy
        z += vz
        w += vw

        screen.fill("black")
        pygame.draw.rect(screen, "red", (x, y, 20, 20))
        pygame.draw.rect(screen, "green", (z, w, 20, 20))
        pygame.display.flip()
        clock.tick(24)
    pygame.quit()



if __name__ == "__main__":
    main()