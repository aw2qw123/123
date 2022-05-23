import grpc
from util.GRPC.base_package import data_pb2_grpc, data_pb2

_HOST = 'localhost'
_PORT = '9955'


def run():
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = data_pb2_grpc.FormatDataStub(
        channel=conn
    )
    response = client.DoFormat(
        data_pb2.actionrequest(text='apple!')
    )
    print('received: ' + response.text)


if __name__ == '__main__':
    run()
