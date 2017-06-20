# coding=utf-8
# !/usr/bin/env python
import json
import sys

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import Behaviour, ACLTemplate


class StockExchange(Agent):
    class OpenStockExchange(Behaviour):
        msg = None

        def _process(self):
            try:
                print "HELLO STOCK"
                self.msg = self._receive(True)

                if self.msg:
                    request = json.loads(self.msg.content)

                    if request['request_type'] == 'request_one':
                        print "msg"

                    if request['request_type'] == 'request_two':
                        print "msg"

                    if request['request_type'] == 'request_three':
                        print "msg"

                    if request['request_type'] == 'request_four':
                        print "msg"

                    else:
                        print "bump"
                        pass

            except (KeyboardInterrupt, SystemExit):
                self.stop_agent()

        def stop_agent(self):
            self.kill()
            sys.exit()

        def broadcast_message(self, content):

            # for agency_id in agencies_ids:
            address = "broker%i@127.0.0.1" % 1
            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)
            # print '\nMessage %s sent to %s' % (content, address)

        def send_message(self, message):
            client = "broker@127.0.0.1"
            address = "xmpp://" + client
            receiver = spade.AID.aid(name=client, addresses=[address])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("travel")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(receiver)
            self.msg.setContent(message)

            self.myAgent.send(self.msg)
            # print "\nMessage sent to: %s !" % client

    def _setup(self):
        print "\nTravel agency\t%s\tis up" % self.getAID().getAddresses()

        template = ACLTemplate()
        template.setOntology('stock')

        behaviour = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(self.OpenStockExchange(), behaviour)


if __name__ == "__main__":
    try:
        StockExchange('stock@127.0.0.1', 'stock').start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
