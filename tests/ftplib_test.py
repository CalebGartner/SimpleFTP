import unittest
import ftplib


class FTPLibraryTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FTPLibraryTestCase, self).__init__(*args, **kwargs)
        self.filename = "test.png"
        self.packet = ftplib.PacketData()

    def test_packets(self):
        action = "START-REQUEST"
        ftp_request = ftplib.create_packet(self.filename, action)
        self.assertIsInstance(ftp_request, (bytes, bytearray))

        # Test Decoding
        self.packet.buffer += ftp_request
        ftplib.process_packet(self.packet)

        self.assertEqual(self.packet.content.decode(), self.filename)
        self.assertIsInstance(self.packet.header, dict)


if __name__ == '__main__':
    unittest.main()
