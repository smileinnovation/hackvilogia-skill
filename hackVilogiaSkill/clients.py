class ClientMock:
    __clients = {
        '101': {
            'firstName': 'émile',
            'lastName': 'Zola',
            'phone': '0706101101',
            'email': 'Emile.Zola@monmail.fr',
            'collectivePremise': False,
            'heatingType': 'individual',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi59',
            'contractProvider': 'Depanne59',
            'afterSaleProvider': ''
        },
        '202': {
            'firstName': 'Honoré',
            'lastName': 'De Balzac',
            'phone': '0706202202',
            'email': 'Honore.DeBalzac@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi59',
            'contractProvider': 'Depanne59',
            'afterSaleProvider': ''
        },
        '303': {
            'firstName': 'Denis',
            'lastName': 'Diderot',
            'phone': '0706303303',
            'email': 'Denis.Diderot@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi59',
            'contractProvider': 'Depanne59',
            'afterSaleProvider': 'EGBSAV'
        },
        '404': {
            'firstName': 'Victor',
            'lastName': 'Hugo',
            'phone': '0706404404',
            'email': 'Victor.Hugo@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi13',
            'contractProvider': 'Depanne13',
            'afterSaleProvider': ''
        },
        '505': {
            'firstName': 'Jeanne',
            'lastName': 'Rowling',
            'phone': '0706505505',
            'email': 'Joanne.Rowling@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': True,
            'multiserviceProvider': 'Multi75',
            'contractProvider': 'Depanne75',
            'afterSaleProvider': ''
        },
        '606': {
            'firstName': 'Agatha',
            'lastName': 'Christie',
            'phone': '0706606606',
            'email': 'Agatha.Christie@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi93',
            'contractProvider': 'Depanne93',
            'afterSaleProvider': ''
        },
        '707': {
            'firstName': 'Stephen',
            'lastName': 'King',
            'phone': '0706707707',
            'email': 'Stephen.King@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi93',
            'contractProvider': 'Depanne93',
            'afterSaleProvider': 'EGBSAV'
        },
        '808': {
            'firstName': 'Amélie',
            'lastName': 'Nothomb',
            'phone': '0706808808',
            'email': 'Amelie.Nothomb@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi67',
            'contractProvider': 'Depanne67',
            'afterSaleProvider': ''
        },
        '909': {
            'firstName': 'Sidonie',
            'lastName': 'Colette',
            'phone': '0706909909',
            'email': 'Sidonie.Colette@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi33',
            'contractProvider': 'Depanne33',
            'afterSaleProvider': ''
        },
        '1101': {
            'firstName': 'Alexandre',
            'lastName': 'Dumas',
            'phone': '0711011101',
            'email': 'Alexandre.Dumas@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi69',
            'contractProvider': 'Depanne69',
            'afterSaleProvider': ''
        },
        '1202': {
            'firstName': 'Françoise',
            'lastName': 'Sagan',
            'phone': '0712021202',
            'email': 'Françoise.Sagan@monmail.fr',
            'collectivePremise': False,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi44',
            'contractProvider': 'Depanne44',
            'afterSaleProvider': ''
        },
        '1303': {
            'firstName': 'Marguerite',
            'lastName': 'Duras',
            'phone': '0713031303',
            'email': 'Marguerite.Duras@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi54',
            'contractProvider': 'Depanne54',
            'afterSaleProvider': ''
        },
        '1404': {
            'firstName': 'Françoise',
            'lastName': 'Dolto',
            'phone': '0714041404',
            'email': 'Françoise.Dolto@monmail.fr',
            'collectivePremise': True,
            'heatingType': 'collective',
            'condoOwnerShip': False,
            'multiserviceProvider': 'Multi59',
            'contractProvider': 'Depanne59',
            'afterSaleProvider': ''
        }
    }

    @staticmethod
    def client_by_id(id):
        if id in ClientMock.__clients:
            return ClientMock.__clients[id]
        else:
            return None

