from socket import *
from util import *


class Sender:
    def __init__(self):
        """
        Seu construtor não deve esperar nenhum argumento,
        pois um objeto será inicializado da seguinte forma:
        sender = Sender()

        Consulte o main.py para uma referência de como sua função será chamada.
        """

        self.packetNum = 1
        self.seqNum = 0
        self.receiverPort = 11555  # número da porta do receptor
        self.senderSocket = socket(AF_INET, SOCK_DGRAM)  # cria um socket UDP para o remetente

    def sendPacket(self, packet, app_msg_str):
        """
        envia o pacote para o receptor e lida com a resposta do receptor
        :param packet: o pacote a ser entregue ao receptor
        :param app_msg_str: a carga útil em string
        :return: None
        """

        # prepara e envia o pacote para o receptor
        destino = ('localhost', self.receiverPort)  #
        self.senderSocket.sendto(packet, destino)
        print(f'pacote nº {self.packetNum} foi enviado com sucesso para o receptor.')
        self.packetNum += 1

        # cria um timeout
        self.senderSocket.settimeout(3)  # timeout de 3 segundos por enquanto

        # lida com a resposta do receptor
        try:
            udpTuple = self.senderSocket.recvfrom(4096)
            resposta = udpTuple[0]
            isResponseValid = verify_checksum(resposta)

            # processa o número de ack
            ackNum = resposta[11] & 1

            # valida o número de ack
            if ackNum == self.seqNum and isResponseValid:
                # caso: ack = seq -> entrega de dados bem-sucedida, resposta válida do receptor
                print(f'pacote recebido corretamente: seq. num {self.seqNum} = ACK num {ackNum}. Tudo feito!')
                print('\n')
                # atualiza o número de sequência
                if self.seqNum == 0:
                    self.seqNum = 1
                else:
                    self.seqNum = 0
            else:
                # caso: número de sequência e número de ack não correspondem
                print('receptor confirmou o pacote anterior, reenviar!')
                print('\n')
                print(f'[ACK-Retransmissão anterior]: {app_msg_str}')
                # print('tentando forçar um timeout aqui')

                # reinicia o temporizador - permite que o remetente aguarde o pacote ACK correto do receptor
                self.senderSocket.settimeout(3)
                try:
                    # aguardando o pacote ACK correto do receptor - forçando um timeout
                    # observe: o receptor NÃO reenviará o pacote ACK - sempre leva a um timeout
                    self.senderSocket.recvfrom(4096)
                except timeout:
                    # nenhum pacote ACK correto recebido, reenviar o pacote
                    # print('forçou com sucesso um timeout ao aguardar o pacote ACK...')
                    self.sendPacket(packet, app_msg_str)
        except timeout:
            # caso: nenhuma resposta recebida, tempo limite!
            print('tempo limite do socket! Reenviar!')
            print('\n')
            print(f'[Timeout-Retransmissão]: {app_msg_str}')
            self.sendPacket(packet, app_msg_str)

    def rdt_send(self, app_msg_str):
        """envia de forma confiável uma mensagem para o receptor (DEVE TER NÃO ALTERE)

        Args:
            app_msg_str: a string da mensagem (a ser colocada no campo de dados do pacote)

        """

        # cria o pacote
        print(f'mensagem original em string: {app_msg_str}')
        pacote = make_packet(app_msg_str, 0, self.seqNum)
        print(f'pacote criado: {pacote}')

        # envia o pacote
        self.sendPacket(pacote, app_msg_str)


def main():
    sender = Sender()
    for i in range(1, 10):
        # aqui é onde o rdt_send será chamado
        sender.rdt_send('msg' + str(i))


if __name__ == '__main__':
    main()

    ####### Sua classe Sender em sender.py DEVE ter o rdt_send(app_msg_str)  #######
    ####### função, que será chamada por um aplicativo para                 #######
    ####### enviar uma mensagem. NÃO altere o nome da função.               #######
    ####### Você pode ter outras funções, se necessário.                   #######
