import server_Classes as Classes
import pickle
import time
import pygame

players = []
server = Classes.Serverconn("192.168.0.155")
listen_thread = Classes.Socket_Listen_Thread(server)

listen_thread.start()

while 1:
    pygame.time.Clock().tick(60)
    for player in listen_thread.players:
        if not player.player_tank.bullets:
            packet = Classes.SendPacket(player.player_tank.x, player.player_tank.y, player.player_tank.hp)
        else:
            for bullet in player.player_tank.bullets:
                bullet.Handle()
                if bullet.x > 810 or bullet.y > 810 or bullet.y < -10 or bullet.x < -10:
                    player.player_tank.bullets.remove(bullet)
            packet = Classes.SendPacket(player.player_tank.x, player.player_tank.y, player.player_tank.hp,player.player_tank.bullets)
        for pID in listen_thread.players:
            if player.IP == pID.IP:
                pass
            else:
                if not player.player_tank.bullets:
                    pass
                else:
                    for bullet in player.player_tank.bullets:
                        # print(bullet.bulletspr)
                        if bullet.bulletspr.colliderect(pID.player_tank.sprite):
                            pID.player_tank.hp -= player.player_tank.bd
                            if pID.player_tank.hp <= 0:
                                pID.dead = True
                            player.player_tank.bullets.remove(bullet)
                packet.others[str(pID.IP[1])]={"x":pID.player_tank.x,
                                               "y":pID.player_tank.y,
                                               "name":pID.player_tank.name,
                                               "bullets":pID.player_tank.bullets}
            if pID.dead == True:
                del pID
                listen_thread.thread_count -= 1
        data = pickle.dumps(packet)
        server.s.sendto(data,player.IP)
    time.sleep(0.01)