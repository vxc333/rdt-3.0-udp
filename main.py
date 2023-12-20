from sender import Sender

sender = Sender() 

for i in range(1, 10):
    # aqui é onde o rdt_send será chamado
    sender.rdt_send('msg' + str(i))