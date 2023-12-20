from socket import *
from time import sleep
from util import *

class Receiver:
    def __init__(self):
        self.port = 11555  # define número da porta
        self.receiverSck = socket(AF_INET, SOCK_DGRAM)  # define o socket UDP do receptor
        self.receiverSck.bind(('', self.port))  # vincula o socket a uma porta específica
        self.packetNum = 1
        self.expectedSeqNum = 0
        self.prevSeqNum = -1

    def runForever(self):
        """
        esta função é um loop infinito no qual o receptor ficará esperando e recebendo pacotes
        do remetente para sempre.
        :return: Nenhum
        """
        print('\n' + '*' * 10 + ' RECEPTOR ativo e ouvindo ' + '*' * 10 + '\n')
        while True:
            # print(f'para fins de depuração: seq# esperado: {self.expectedSeqNum}')
            # receber pacote
            msg, senderAddr = self.receiverSck.recvfrom(4096)
            print(f'pacote num.{self.packetNum} recebido: {msg}')
            curSeqNumber = msg[11] & 1

            msgValid = verify_checksum(msg)
            if self.packetNum % 6 == 0:
                # caso: simular timeout
                print('simulando perda de pacote: aguardando um pouco para acionar o evento de timeout no lado do remetente...')
                sleep(4)  # aguarda 4s (timeout no remetente é 3s)
            elif not msgValid or self.packetNum % 3 == 0:
                # caso: simular erro de bit/pacote corrompido
                print('simulando erros de bit/pacote corrompido: ACK para o pacote anterior')
                ackPacket = make_packet('', 1, self.prevSeqNum)
                self.receiverSck.sendto(ackPacket, senderAddr)
            elif curSeqNumber != self.expectedSeqNum:
                # caso: número de sequência do pacote do remetente está incorreto
                # observe que esta lógica é improvável de ser executada se o lado do remetente estiver implementado corretamente
                print(f'número de seq# incorreto do pacote recebido... seq# é {curSeqNumber} mas '
                      f'seq# esperado é {self.expectedSeqNum}... ACK para o pacote atual')
                ackPacket = make_packet('', 1, curSeqNumber)
                self.receiverSck.sendto(ackPacket, senderAddr)
            else:
                # caso: tudo ok
                payload = bytes.decode(msg[12:], 'utf-8')
                print(f'pacote esperado, mensagem entregue: {payload}')
                print('pacote entregue, agora criando e enviando o pacote ACK...')
                ackPacket = make_packet('', 1, curSeqNumber)
                self.receiverSck.sendto(ackPacket, senderAddr)
                self.prevSeqNum = curSeqNumber  # atualiza o seq# anterior

                # atualiza seq# esperado
                if curSeqNumber == 0:
                    self.expectedSeqNum = 1
                else:
                    self.expectedSeqNum = 0
            print('tudo feito para este pacote!')
            print('\n')
            self.packetNum += 1


def main():
    receptor = Receiver()
    receptor.runForever()


if __name__ == '__main__':
    main()
