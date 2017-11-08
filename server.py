import server_Classes as Classes
import pickle
import time

players = []
server = Classes.Serverconn("192.168.0.155")
listen_thread = Classes.Socket_Listen_Thread(server)

listen_thread.start()

while 1:
    for player in listen_thread.players:
        packet = Classes.SendPacket(player.x,player.y)
        for pID in listen_thread.players:
            if player.IP == pID.IP:
                pass
            else:
                packet.others[str(pID.IP[1])]={"x":pID.x,
                                          "y":pID.y}
        data = pickle.dumps(packet)
        server.s.sendto(data,player.IP)
    time.sleep(0.01)