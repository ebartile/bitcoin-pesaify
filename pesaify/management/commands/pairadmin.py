from django.core.management.base import BaseCommand, CommandError
from pesaify import crypto
from pesaify.client import PesaifyClient
from django.conf import settings

class Command(BaseCommand):
    help = 'Storing the client object for later'

    def handle(self, *args, **options):

        while True:
            print("On Admin server > business > access tokens > create new token, copy and paste pairing code:")
            pair = input("Enter pair Code:")
            if pair:
                break

        privkey = crypto.generate_privkey()
        client = PesaifyClient(host=settings.BITCOIN_URL, pem=privkey)
        print("PRIVKEY\n{}".format(privkey))
        print("TOKENS\n{}".format(client.pair_client(pair)))
